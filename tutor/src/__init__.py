"""
AI Error Tutor - A friendly Python error message rewriter using AI

This package provides tools to capture Python errors and transform
cryptic compiler messages into human-friendly explanations.
"""

from .error_capture import ErrorCapture, capture_error
from .ast_parser import ASTContextExtractor
from .preprocessor import DataPreprocessor, TrainingExample
from .model import ErrorExplainerModel, FallbackExplainer, ErrorDataset
from .pipeline import AIErrorTutor, ExplanationResult
from .security import CodeSecurityValidator, SecurityWarning

__version__ = "1.0.0"
__author__ = "Sai Charan Kumar"

__all__ = [
    # Error Capture
    "ErrorCapture",
    "capture_error",

    # AST Parser
    "ASTContextExtractor",

    # Preprocessor
    "DataPreprocessor",
    "TrainingExample",

    # Model
    "ErrorExplainerModel",
    "FallbackExplainer",
    "ErrorDataset",

    # Pipeline
    "AIErrorTutor",
    "ExplanationResult",

     # Security
    "CodeSecurityValidator",
    "SecurityWarning",
]
