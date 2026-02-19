from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import time
from core.factory_engine import FactoryTwin

app = Flask(__name__, template_folder='../templates')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

twin = FactoryTwin()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/state')
def get_state():
    return jsonify(twin.get_factory_state())

@app.route('/api/optimize', methods=['POST'])
def optimize():
    data = request.json
    action = data.get("action")
    
    if action == "REDUCE_SPEED_ECO_MODE":
        twin.set_factory_speed(0.5)
    elif action == "BOOST_PRODUCTION":
        twin.set_factory_speed(1.5)
    elif action == "NORMAL_MODE":
        twin.set_factory_speed(1.0)
        
    print(f"BPA/N8N OPTIMIZATION APPLIED: {action}")
    socketio.emit('bpa_log', {"message": f"Optimization Applied: {action}", "speed": twin.factory_speed})
    return jsonify({"status": "success", "new_speed": twin.factory_speed})

def background_simulation():
    """Background task for factory simulation."""
    print("🧵 Background Simulation Thread Started")
    
    def broadcast_state(state):
        socketio.emit('factory_update', state)

    twin.run_simulation_loop(broadcast_state)

if __name__ == '__main__':
    # Flask-SocketIO background task
    socketio.start_background_task(background_simulation)
    
    print("🚀 OpenFactoryTwin Server Starting on http://localhost:5001")
    socketio.run(app, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
