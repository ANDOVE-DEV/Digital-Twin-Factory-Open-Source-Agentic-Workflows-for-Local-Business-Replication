import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import sqlite3
import os

class TemperatureDTO:
    def __init__(self, db_path="dto_storage.db", history_size=100):
        self.history_size = history_size
        self.db_path = db_path
        self.data = pd.DataFrame(columns=['timestamp', 'temperature', 'is_anomaly'])
        self.model_anomaly = IsolationForest(contamination=0.1)
        self.model_trend = LinearRegression()
        
        # Internal state for closed-loop
        self.external_influence = 0.0 # Used by BPA to lower/raise temp
        
        self._init_db()
        self._load_from_db()

    def _init_db(self):
        """Initialize SQLite database for persistent storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                temperature REAL,
                is_anomaly INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def _load_from_db(self):
        """Load recent history from database on startup."""
        try:
            conn = sqlite3.connect(self.db_path)
            # Load only the last 500 records to keep it fast
            query = "SELECT timestamp, temperature, is_anomaly FROM readings ORDER BY id DESC LIMIT 500"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                # Reverse to get chronological order
                self.data = df.iloc[::-1].reset_index(drop=True)
                self.data['is_anomaly'] = self.data['is_anomaly'].astype(bool)
        except Exception as e:
            print(f"Error loading DB: {e}")

    def add_reading(self, temperature):
        timestamp = datetime.now()
        new_row = {'timestamp': timestamp, 'temperature': temperature, 'is_anomaly': False}
        
        # Check for anomaly if we have enough data (at least 20 samples)
        if len(self.data) > 20:
            X = self.data['temperature'].values.reshape(-1, 1)
            self.model_anomaly.fit(X)
            prediction = self.model_anomaly.predict([[temperature]])
            new_row['is_anomaly'] = True if prediction[0] == -1 else False
        
        # Append to memory
        self.data = pd.concat([self.data, pd.DataFrame([new_row])], ignore_index=True)
        
        # Save to SQLite
        self._save_to_db(timestamp, temperature, new_row['is_anomaly'])
        
        # Keep only latest history in memory for performance
        if len(self.data) > self.history_size:
            self.data = self.data.iloc[-self.history_size:]
            
    def _save_to_db(self, ts, temp, is_anomaly):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO readings (timestamp, temperature, is_anomaly) VALUES (?, ?, ?)",
                (ts.isoformat(), temp, 1 if is_anomaly else 0)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving to DB: {e}")

    def predict_trend(self, steps=10):
        if len(self.data) < 10:
            return None
        
        X = np.array(range(len(self.data))).reshape(-1, 1)
        y = self.data['temperature'].values
        self.model_trend.fit(X, y)
        
        future_X = np.array(range(len(self.data), len(self.data) + steps)).reshape(-1, 1)
        future_y = self.model_trend.predict(future_X)
        
        return future_y.tolist()

    def get_sma(self, window=10):
        """Calculate Simple Moving Average."""
        if len(self.data) < window:
            return None
        return round(float(self.data['temperature'].tail(window).mean()), 2)

    def apply_bpa_intervention(self, delta):
        """Allows BPA to influence the twin's state (Feedback Loop)."""
        self.external_influence += delta

    def get_status(self):
        if self.data.empty:
            return "Initializing..."
        
        latest = self.data.iloc[-1]
        if latest['is_anomaly']:
            return "ALARM: Anomaly Detected!"
        return "Normal"

    def get_data_summary(self):
        return {
            "current_temp": round(float(self.data.iloc[-1]['temperature']), 2) if not self.data.empty else None,
            "status": self.get_status(),
            "history_count": len(self.data),
            "anomalies_count": int(self.data['is_anomaly'].sum()),
            "sma": self.get_sma()
        }
