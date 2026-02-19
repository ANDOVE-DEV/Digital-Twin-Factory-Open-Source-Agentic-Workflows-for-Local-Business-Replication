from flask import Flask, render_template, send_file
from flask_socketio import SocketIO
import numpy as np
import io
import threading
import time
import random
import pandas as pd
from datetime import datetime
from core.dto_engine import TemperatureDTO
from core.bpa_alert_handler import TemperatureBPA

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = 'dt-factory-ultra-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize DTO and then BPA with DTO reference
dto = TemperatureDTO(db_path="dto_storage.db", history_size=50)
bpa = TemperatureBPA(dto_instance=dto)

# Global simulation state
simulation_running = True

def sensor_simulator():
    """Improved simulator with Feedback Loop support."""
    base_temp = 22.0
    while simulation_running:
        # 1. Physics: Base cycle + noise
        hour = datetime.now().hour
        daily_cycle = 5 * np.sin(np.pi * (hour - 6) / 12)
        noise = random.uniform(-0.3, 0.3)
        
        # 2. Add BPA Influence (Closed Loop)
        current_temp = base_temp + daily_cycle + noise + dto.external_influence
        
        if abs(dto.external_influence) > 0.1:
            dto.external_influence *= 0.95
        else:
            dto.external_influence = 0
            
        # 3. Inject occasional anomaly
        if random.random() < 0.05:
            spike = random.uniform(5.0, 10.0) * (1 if random.random() > 0.4 else -1)
            current_temp += spike

        # 4. SENSE: Update DTO
        dto.add_reading(float(current_temp))
        
        # 5. THINK/ACT
        latest_status = dto.get_data_summary()
        bpa_result = None
        if latest_status['status'].startswith("ALARM"):
            bpa_result = bpa.process_event("dto.kpi.anomaly_detected", {
                "current_value": round(float(current_temp), 2),
                "timestamp": datetime.now().isoformat()
            })
        
        # 6. EMIT: Send data to Chart.js
        socketio.emit('new_reading', {
            'temperature': round(float(current_temp), 2),
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'summary': latest_status,
            'bpa_action': bpa.get_latest_action(),
            'bpa_last_result': bpa_result,
            'predictions': dto.predict_trend(steps=8)
        })
        
        time.sleep(2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/history')
def get_history():
    """Read from persistent SQLite storage."""
    import sqlite3
    conn = sqlite3.connect("dto_storage.db")
    df = pd.read_sql_query("SELECT * FROM readings ORDER BY id DESC LIMIT 100", conn)
    conn.close()
    return df.to_json(orient="records")

if __name__ == '__main__':
    sim_thread = threading.Thread(target=sensor_simulator)
    sim_thread.daemon = True
    sim_thread.start()
    
    print("🚀 DTO Factory Server starting on http://localhost:5000")
    socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
