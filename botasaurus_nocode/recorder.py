"""Action Recorder - Records browser interactions"""

class ActionRecorder:
    """Records user actions in browser for workflow generation"""

    def __init__(self):
        self.actions = []

    def start_recording(self):
        """Start recording browser actions"""
        self.actions = []

    def record_action(self, action_type: str, data: dict):
        """Record a single action"""
        self.actions.append({"type": action_type, "data": data})

    def stop_recording(self) -> list:
        """Stop recording and return actions"""
        return self.actions
