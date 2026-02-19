from datetime import datetime

class TemperatureBPA:
    """
    Business Process Automation per il Sensore di Temperatura.
    Interviene quando il DTO rileva anomalie e AGISCE sul sistema (Closed-Loop).
    """
    def __init__(self, dto_instance, log_file="bpa_actions.log"):
        self.dto = dto_instance
        self.log_file = log_file
        self.last_action = "None"

    def process_event(self, event_type, payload):
        """Gestisce gli eventi provenienti dal DTO."""
        if event_type == "dto.kpi.anomaly_detected":
            return self.trigger_emergency_protocol(payload)
        return None

    def trigger_emergency_protocol(self, data):
        """Esegue azioni correttive reali sul Digital Twin."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        temp = data.get('current_value', 0)
        
        # Sceglie l'azione correttiva
        action = "None"
        influence_delta = 0.0

        if temp > 28:
            action = "ACTIVATE_COOLING_SYSTEM"
            influence_delta = -2.0 # Abbassa la temperatura di 2 gradi
        elif temp < 15:
            action = "ACTIVATE_HEATING_UNIT"
            influence_delta = 2.0  # Alza la temperatura di 2 gradi
        else:
            action = "EQUIPMENT_CHECK_LOGGED"

        self.last_action = action
        
        # APPLICA L'INTERVENTO (Feedback Loop)
        if influence_delta != 0:
            self.dto.apply_bpa_intervention(influence_delta)
        
        log_message = f"[{timestamp}] BPA ACTION: {action} (Temp was {temp}°C). Feedback: {influence_delta} delta applied.\n"
        
        with open(self.log_file, "a") as f:
            f.write(log_message)
        
        print(f"BPA EXECUTED: {action}")
        return {
            "action": action,
            "delta": influence_delta,
            "timestamp": timestamp
        }

    def get_latest_action(self):
        return self.last_action
