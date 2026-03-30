"""
AI Model Module - T5-based error explanation model
"""

import torch
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq
)
from torch.utils.data import Dataset
from typing import List, Dict, Optional
import os


class ErrorDataset(Dataset):
    """PyTorch Dataset for error examples."""

    def __init__(self, encodings):
        self.encodings = encodings

    def __len__(self):
        return len(self.encodings['input_ids'])

    def __getitem__(self, idx):
        return {
            'input_ids': self.encodings['input_ids'][idx],
            'attention_mask': self.encodings['attention_mask'][idx],
            'labels': self.encodings['labels'][idx]
        }


class ErrorExplainerModel:
    """T5-based model for generating friendly error explanations."""

        # Replace your current __init__ with this:
    def __init__(self, model_path: str = None):
        import torch
        from transformers import AutoTokenizer, T5ForConditionalGeneration

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        load_path = model_path if model_path else "t5-small"
        self.model_name = load_path
        
        # AutoTokenizer smartly loads tokenizer.json!
        self.tokenizer = AutoTokenizer.from_pretrained(load_path)
        self.model = T5ForConditionalGeneration.from_pretrained(load_path)
        self.model.to(self.device)

    # Note: You can delete the `def load_model(self, path: str):` method entirely now!

    def train(self, train_dataset: Dataset, eval_dataset: Dataset,
              output_dir: str = "./models/error_tutor_model", epochs: int = 5,
              batch_size: int = 8, learning_rate: float = 3e-4):
        """
        Fine-tune the model on error explanation data.

        Args:
            train_dataset: Training dataset
            eval_dataset: Evaluation dataset
            output_dir: Directory to save model checkpoints
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
        """
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir=f'{output_dir}/logs',
            logging_steps=10,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            learning_rate=learning_rate
        )

        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer,
            model=self.model
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer
        )

        trainer.train()
        return trainer

    def generate_explanation(self, error_type: str, error_message: str,
                             code_context: str, max_length: int = 256) -> str:
        """
        Generate a friendly explanation for an error.

        Args:
            error_type:  Type of error (e.g., 'NameError')
            error_message: The raw error message
            code_context: Code context around the error
            max_length: Maximum output length

        Returns:
            Human-friendly error explanation with fix
        """
        input_text = (f"explain error: {error_type} | "
                      f"message: {error_message} | "
                      f"code: {code_context}")

        inputs = self.tokenizer(
            input_text,
            max_length=256,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        ).to(self.device)

        outputs = self.model.generate(
            input_ids=inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            max_length=256,
            num_beams=4,
            early_stopping=True
        )

        explanation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return explanation

    def save_model(self, path: str):
        """Save the fine-tuned model."""
        os.makedirs(path, exist_ok=True)
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        print(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load a fine-tuned model."""
        self.model = T5ForConditionalGeneration.from_pretrained(path)
        self.tokenizer = T5Tokenizer.from_pretrained(path)
        self.model.to(self.device)
        print(f"Model loaded from {path}")


class FallbackExplainer:
    """Rule-based fallback when AI model isn't available."""

    EXPLANATIONS = {
        'SyntaxError': {
            'pattern': 'invalid syntax',
            'explanation': "There's a syntax error in your code. Common causes include: missing colons, unmatched parentheses, or incorrect indentation."
        },
        'NameError': {
            'pattern': 'is not defined',
            'explanation': "You're trying to use a variable or function that doesn't exist. Check for typos or make sure it's defined before use."
        },
        'TypeError': {
            'pattern': 'unsupported operand',
            'explanation': "You're trying to perform an operation with incompatible types. Check if you need to convert types using str(), int(), or float()."
        },
        'IndexError': {
            'pattern': 'out of range',
            'explanation': "You're trying to access an index that doesn't exist in the list. Remember, Python lists start at index 0!"
        },
        'KeyError': {
            'pattern': '',
            'explanation': "You're trying to access a dictionary key that doesn't exist. Use .get() method or check if the key exists first."
        },
        'ValueError': {
            'pattern': 'invalid literal',
            'explanation': "The value you provided isn't valid for this operation. Check that your input matches the expected format."
        },
        'ZeroDivisionError': {
            'pattern': 'division by zero',
            'explanation': "You're trying to divide by zero, which is mathematically undefined. Check that your divisor is not zero."
        },
        'AttributeError': {
            'pattern': 'has no attribute',
            'explanation': "You're trying to use a method or property that doesn't exist for this type of object. Check the object type and available methods."
        },
        'IndentationError': {
            'pattern': 'unexpected indent',
            'explanation': "Your code indentation is inconsistent. Use 4 spaces for each indentation level and make sure all lines in the same block match."
        },
        'SecurityError': {
            'pattern': '',
            'explanation': "Your code was blocked because it contains potentially dangerous operations that are not allowed in a learning environment."
        },
    }

    def explain(self, error_type: str, error_message: str) -> str:
        """Generate a fallback explanation."""
        if error_type in self.EXPLANATIONS:
            return self.EXPLANATIONS[error_type]['explanation']
        return f"An error occurred: {error_message}. Please review your code carefully."


if __name__ == "__main__":
    # Test model initialization
    print("Initializing model...")
    model = ErrorExplainerModel("t5-small")

    # Test generation (untrained model will give poor results)
    result = model.generate_explanation(
        error_type="NameError",
        error_message="name 'prnt' is not defined",
        code_context="prnt('Hello')"
    )
    print(f"Generated (untrained): {result}")

    # Test fallback
    fallback = FallbackExplainer()
    print(f"Fallback:  {fallback.explain('NameError', 'name prnt is not defined')}")
