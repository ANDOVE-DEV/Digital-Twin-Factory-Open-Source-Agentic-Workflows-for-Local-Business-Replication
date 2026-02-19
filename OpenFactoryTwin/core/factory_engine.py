import time
import random
import threading
import sqlite3
from datetime import datetime

class Machine:
    def __init__(self, machine_id, name, energy_consumption_idle=0.5):
        self.machine_id = machine_id
        self.name = name
        self.status = "IDLE" # IDLE, WORKING, BLOCKED, MAINTENANCE
        self.energy_consumption_idle = energy_consumption_idle
        self.energy_consumption_working = 5.0
        self.current_consumption = energy_consumption_idle
        self.production_count = 0
        self.total_energy_kwh = 0.0
        self.last_update = time.time()
        
    def work(self):
        """Simulate work cycle."""
        if self.status == "IDLE":
            self.status = "WORKING"
            self.current_consumption = self.energy_consumption_working + random.uniform(-0.5, 0.5)
            # Simulate processing time
            processing_time = random.uniform(2, 5)
            time.sleep(processing_time)
            
            self.production_count += 1
            self.status = "IDLE"
            self.current_consumption = self.energy_consumption_idle
            
    def update_energy(self):
        now = time.time()
        duration_hrs = (now - self.last_update) / 3600
        self.total_energy_kwh += self.current_consumption * duration_hrs
        self.last_update = now

class FactoryTwin:
    def __init__(self, db_path="factory_twin.db"):
        self.db_path = db_path
        self.machines = {
            "M1": Machine("M1", "Laser-Cutter"),
            "M2": Machine("M2", "Robotic-Assembler", energy_consumption_idle=0.8),
            "M3": Machine("M3", "Smart-Packer", energy_consumption_idle=0.4)
        }
        self.factory_speed = 1.0 # Multiplier for production frequency
        self.energy_limit = 12.0 # Threshold for n8n intervention
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS factory_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                machine_id TEXT,
                status TEXT,
                consumption REAL,
                total_energy REAL,
                production_count INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def run_simulation_loop(self, callback):
        """Main engine loop to be run in a thread."""
        while True:
            total_current_power = 0
            for mid, m in self.machines.items():
                # Randomly start production based on speed
                if m.status == "IDLE" and random.random() < (0.2 * self.factory_speed):
                    threading.Thread(target=m.work).start()
                
                m.update_energy()
                total_current_power += m.current_consumption
                
            # Log to DB occasionally
            if random.random() < 0.1:
                for m in self.machines.values():
                    self._log_state(m)
            
            state = self.get_factory_state()
            state['total_power_kw'] = round(float(total_current_power), 2)
            callback(state)
            time.sleep(1)

    def set_factory_speed(self, speed):
        """Allows external systems (n8n/BPA) to control factory throughput."""
        self.factory_speed = max(0.1, min(2.0, speed))
        print(f"DTO ACTION: Factory Speed set to {self.factory_speed}")

    def _log_state(self, m):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO factory_logs (timestamp, machine_id, status, consumption, total_energy, production_count) VALUES (?,?,?,?,?,?)",
            (datetime.now().isoformat(), m.machine_id, m.status, m.current_consumption, m.total_energy_kwh, m.production_count)
        )
        conn.commit()
        conn.close()

    def get_factory_state(self):
        total_energy = sum(m.total_energy_kwh for m in self.machines.values())
        total_prod = sum(m.production_count for m in self.machines.values())
        return {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "total_energy_kwh": round(float(total_energy), 4),
            "total_production": total_prod,
            "sustainability_score": self.calculate_sustainability(total_energy, total_prod),
            "factory_speed": self.factory_speed,
            "machines": {mid: {
                "name": m.name,
                "status": m.status,
                "consumption": round(float(m.current_consumption), 2),
                "production": m.production_count
            } for mid, m in self.machines.items()}
        }

    def calculate_sustainability(self, energy, prod):
        if prod == 0: return 0
        efficiency = prod / (energy + 0.1)
        return round(min(100, efficiency * 10), 2)
