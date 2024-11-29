# printer_config.py
import os
import json

class PrinterConfig:
    def __init__(self):
        self.config_file = "printer_config.json"
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'selected_printers': [],
            'last_sizes': {},
            'last_paths': {}
        }

    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)

    def get_config(self):
        return self.config
