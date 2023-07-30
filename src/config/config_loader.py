import os
import yaml

class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                config = yaml.safe_load(file)
                return config
        except FileNotFoundError:
            raise Exception(f"Error: Config file '{self.config_file}' not found.")
        except Exception as e:
            raise Exception(f"Error loading config: {str(e)}")

    def set_environment_variables(self):
        config = self.load_config()
        for key, value in config.items():
            if not value:
                raise Exception(f"Error: Value for '{key}' is not defined.")
            os.environ[key] = value