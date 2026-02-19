import time
import random
import numpy as np
from datetime import datetime

class PlantDT:
    def __init__(self, plant_type="Digital Fern"):
        self.plant_type = plant_type
        # Physical State
        self.soil_moisture = 60.0 # Percentage
        self.humidity = 45.0      # Air humidity
        self.nutrients = 100.0    # 0-100
        self.health = 100.0       # 0-100
        self.growth_stage = 0.0   # 0-100% (Maturity)
        self.light_intensity = 0.0 # lux proxy
        self.temperature = 22.0
        
        # Internal Constants
        self.evaporation_rate = 0.8 # moisture lost per second/lux unit
        self.growth_rate = 0.08    # growth units per tick under ideal conditions
        self.irrigation_amount = 25.0 # increase in moisture when watered
        self.nutrient_consumption = 0.05 # per growth tick
        
        self.last_update = time.time()
        self.is_watering = False

    def simulate_tick(self):
        """Biological Simulation Step."""
        now = time.time()
        dt = (now - self.last_update)
        
        # 1. Environment Simulation (Circadian Rhythm)
        hour = datetime.now().hour
        # Peak light at 14:00, zero at night
        self.light_intensity = float(max(0.0, 100.0 * np.sin(np.pi * (float(hour) - 6.0) / 12.0))) 
        self.temperature = float(20.0 + 5.0 * np.sin(np.pi * (float(hour) - 8.0) / 12.0) + random.uniform(-0.5, 0.5))
        self.humidity = float(max(20.0, 50.0 - (self.temperature - 20.0) * 2.0 + random.uniform(-2.0, 2.0)))

        # 2. Water Dynamics (Evapotranspiration proxy)
        # Faster evaporation with more light, temperature and low humidity
        humidity_factor = (100.0 - self.humidity) / 50.0
        loss = (self.evaporation_rate * (self.light_intensity / 50.0) * (self.temperature / 20.0) * humidity_factor) * dt
        self.soil_moisture = float(max(0.0, self.soil_moisture - loss))
        
        # 3. Growth & Health Logic
        # Plant grows only if moisture is between 30% and 80% and nutrients > 0
        if 30.0 < self.soil_moisture < 80.0 and self.nutrients > 0.0:
            growth_boost = self.growth_rate * (self.light_intensity / 100.0) * (self.nutrients / 100.0)
            self.growth_stage = float(min(100.0, self.growth_stage + growth_boost))
            self.health = float(min(100.0, self.health + 0.2))
            self.nutrients = float(max(0.0, self.nutrients - self.nutrient_consumption * (growth_boost / self.growth_rate)))
        else:
            # Stress reduces health
            self.health = float(max(0.0, self.health - 0.3))
            
        # 4. Death Prevention (Simulated Resilience)
        if self.health < 20.0:
             self.growth_stage = float(max(0.0, self.growth_stage - 0.1))

        self.last_update = now
        return self.get_state()

    def irrigate(self):
        """Actuator command: Water the plant."""
        self.is_watering = True
        self.soil_moisture = min(100, self.soil_moisture + self.irrigation_amount)
        time.sleep(1) # Simulation of water flow
        self.is_watering = False
        return True

    def get_state(self):
        return {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "soil_moisture": round(float(self.soil_moisture), 2),
            "humidity": round(float(self.humidity), 2),
            "nutrients": round(float(self.nutrients), 2),
            "health": round(float(self.health), 2),
            "growth_stage": round(float(self.growth_stage), 4),
            "light": round(float(self.light_intensity), 2),
            "temp": round(float(self.temperature), 2),
            "status": "THIRSTY" if self.soil_moisture < 35.0 else ("MALNOURISHED" if self.nutrients < 20.0 else ("HEALTHY" if self.health > 80.0 else "STRESSED")),
            "is_watering": self.is_watering
        }

    def predict_growth(self, hours=24):
        """ML/Mathematical projection of growth based on current bio-state."""
        # Simplified linear projection for the dashboard
        future_growth = []
        sim_health = self.health
        sim_growth = self.growth_stage
        
        for i in range(hours):
            if sim_health > 50:
                sim_growth += self.growth_rate * 60 # per hour
            future_growth.append(min(100, sim_growth))
            
        return future_growth
