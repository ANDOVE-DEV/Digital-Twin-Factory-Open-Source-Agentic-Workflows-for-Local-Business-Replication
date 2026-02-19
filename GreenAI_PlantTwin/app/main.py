from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import threading
import time
from core.plant_engine import PlantDT

app = Flask(__name__, template_folder='../templates')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize the Bio-Twin
plant = PlantDT("Super-Sustainer Fern")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/water', methods=['POST'])
def manual_water():
    success = plant.irrigate()
    return jsonify({"status": "success", "moisture": plant.soil_moisture})

@app.route('/api/state')
def get_state():
    return jsonify(plant.get_state())

@app.route('/api/fertilize', methods=['POST'])
def fertilize():
    plant.nutrients = min(100.0, plant.nutrients + 30.0)
    return jsonify({"status": "success", "nutrients": plant.nutrients})

def background_bio_loop():
    """Continuous simulation thread."""
    print("🌿 Bio-Twin High-Fidelity Simulation loop started.")
    while True:
        state = plant.simulate_tick()
        
        # Smart BPA Logic: Low Nutrients or Low Moisture
        if state['soil_moisture'] < 30 and not state['is_watering']:
            socketio.emit('bpa_alert', {"message": "Critical Drought! Activating Smart Irrigation."})
            plant.soil_moisture += 20.0
        
        if state['nutrients'] < 15:
            socketio.emit('bpa_alert', {"message": "Nutrient Depletion! Model indicates growth stunted."})
            
        socketio.emit('bio_update', state)
        time.sleep(1.5)

if __name__ == '__main__':
    socketio.start_background_task(background_bio_loop)
    print("🚀 GreenAI PlantTwin Server Online: http://localhost:5002")
    socketio.run(app, host='0.0.0.0', port=5002, allow_unsafe_werkzeug=True)
