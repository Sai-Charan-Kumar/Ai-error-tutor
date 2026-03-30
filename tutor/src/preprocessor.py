"""
Data Preprocessor - Prepares data for model training
"""

import pandas as pd
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class TrainingExample:
    """Represents a single training example."""
    input_text: str
    target_text: str
    error_type: str


class DataPreprocessor:
    """Preprocesses error data for transformer model training."""

    def __init__(self, max_input_length: int = 256, max_target_length: int = 128):
        self.max_input_length = max_input_length
        self.max_target_length = max_target_length

    def load_dataset(self, csv_path: str) -> pd.DataFrame:
        """Load and validate the error dataset."""
        df = pd.read_csv(csv_path)

        required_columns = ['error_type', 'raw_error', 'code_context',
                            'friendly_explanation', 'suggested_fix']

        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        return df

    def create_training_examples(self, df: pd.DataFrame) -> List[TrainingExample]:
        """Convert dataframe rows to training examples."""
        examples = []

        for _, row in df.iterrows():
            input_text = self._format_input(
                error_type=row['error_type'],
                raw_error=row['raw_error'],
                code_context=row['code_context']
            )

            target_text = self._format_output(
                explanation=row['friendly_explanation'],
                fix=row['suggested_fix']
            )

            examples.append(TrainingExample(
                input_text=input_text,
                target_text=target_text,
                error_type=row['error_type']
            ))

        return examples

    def _format_input(self, error_type: str, raw_error: str,
                      code_context: str) -> str:
        """Format input for the model."""
        # Clean and normalize
        raw_error = self._clean_text(raw_error)
        code_context = self._truncate(code_context, 150)

        return (f"explain error: {error_type} | "
                f"message: {raw_error} | "
                f"code: {code_context}")

    def _format_output(self, explanation: str, fix: str) -> str:
        """Format target output for the model."""
        return f"{explanation} FIX: {fix}"

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove file paths for generalization
        text = re.sub(r'File "[^"]+",', 'File "<code>",', text)
        return text.strip()

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to max length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    def prepare_for_training(self, examples: List[TrainingExample],
                             tokenizer) -> Dict:
        """
        Tokenize examples for model training.

        Args:
            examples: List of TrainingExample objects
            tokenizer:  Hugging Face tokenizer

        Returns:
            Dictionary with tokenized inputs and labels
        """
        inputs = [ex.input_text for ex in examples]
        targets = [ex.target_text for ex in examples]

        # Tokenize inputs
        model_inputs = tokenizer(
            inputs,
            max_length=self.max_input_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        # Tokenize targets (no context manager needed for T5 — same tokenizer)
        labels = tokenizer(
            targets,
            max_length=self.max_target_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        model_inputs['labels'] = labels['input_ids']

        return model_inputs

    def split_dataset(self, examples: List[TrainingExample],
                      train_ratio: float = 0.8) -> Tuple[List, List]:
        """Split examples into train and validation sets."""
        split_idx = int(len(examples) * train_ratio)
        return examples[:split_idx], examples[split_idx:]

    def augment_examples(self, examples: List[TrainingExample]) -> List[TrainingExample]:
        """
        Augment training data with variations.

        Creates variations of error messages to improve model robustness.
        """
        augmented = list(examples)  # Keep originals

        for ex in examples:
            # Add variation with different formatting
            variation = TrainingExample(
                input_text=ex.input_text.lower(),
                target_text=ex.target_text,
                error_type=ex.error_type
            )
            augmented.append(variation)

        return augmented


if __name__ == "__main__":
    # Test preprocessor
    preprocessor = DataPreprocessor()

    # Create sample data
    sample_data = {
        'error_type': ['NameError', 'TypeError'],
        'raw_error': [
            "NameError: name 'prnt' is not defined",
            "TypeError:  unsupported operand type(s) for +: 'int' and 'str'"
        ],
        'code_context': [
            "prnt('Hello')",
            "x = 5 + 'hello'"
        ],
        'friendly_explanation': [
            "You have a typo.  'prnt' should be 'print'.",
            "You can't add a number and text directly."
        ],
        'suggested_fix': [
            "print('Hello')",
            "x = 5 + int('hello') or x = str(5) + 'hello'"
        ]
    }

    df = pd.DataFrame(sample_data)
    examples = preprocessor.create_training_examples(df)

    for ex in examples:
        print(f"Input: {ex.input_text}")
        print(f"Target: {ex.target_text}")
        print("-" * 50)
