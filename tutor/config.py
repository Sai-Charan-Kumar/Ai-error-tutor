import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
"""Configuration file for AI Error Tutor"""

# Target Python Errors to Handle
TARGET_ERRORS = [
    "SyntaxError",
    "IndentationError",
    "NameError",
    "TypeError",
    "ValueError",
    "IndexError",
    "KeyError",
    "AttributeError",
    "ImportError",
    "ModuleNotFoundError",
    "ZeroDivisionError",
    "FileNotFoundError",
    "UnboundLocalError",
    "RecursionError",
    "StopIteration"
]

# Model Configuration
MODEL_CONFIG = {
    "base_model": "t5-small",
    "max_input_length": 256,
    "max_output_length":  128,
    "batch_size": 8,
    "learning_rate": 3e-4,
    "epochs": 5
}

# Paths
DATA_PATH = "data/error_dataset.csv"
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "models", "error_tutor_model")
