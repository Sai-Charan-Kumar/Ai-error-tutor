# 🎓 AI Error Tutor

An intelligent Python error message rewriter that transforms cryptic compiler errors into friendly, educational explanations.

## 🌟 Features

- **Smart Error Capture**: Catches Python errors with full context
- **AST Analysis**: Uses Abstract Syntax Tree for deep code understanding
- **AI-Powered Explanations**: Fine-tuned T5 model generates human-friendly messages
- **Intelligent Suggestions**: Provides fix recommendations and similar name detection
- **Fallback System**: Rule-based explanations when AI is unavailable

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/ai-error-tutor.git
cd ai-error-tutor
pip install -r requirements.txt
```

### Usage

```bash
# Interactive mode
python main. py

# Analyze a file
python main.py --file your_code.py

# Demo mode
python main. py --demo

# Without AI (fallback only)
python main.py --no-ai
```

### As a Library

```python
from src.pipeline import AIErrorTutor

tutor = AIErrorTutor()
result = tutor.analyze_code("prnt('Hello')")
print(result. friendly_explanation)
```

## 📊 Supported Errors

- SyntaxError
- IndentationError
- NameError
- TypeError
- ValueError
- IndexError
- KeyError
- AttributeError
- ImportError
- ModuleNotFoundError
- ZeroDivisionError
- FileNotFoundError
- UnboundLocalError
- RecursionError

## 🏗️ Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Error Capture   │────▶│   AST Parser     │────▶│    AI Model      │
│   (traceback)    │     │   (ast module)   │     │   (T5-small)     │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                                          │
                                                          ▼
                                                  ┌──────────────────┐
                                                  │ Friendly Output  │
                                                  └──────────────────┘
```

## 🔧 Training Your Own Model

1.  Prepare dataset in `data/error_dataset.csv`
2. Open `notebooks/train_model.ipynb` in Google Colab
3. Upload your dataset
4. Run training cells
5. Download trained model

## 📈 Performance

| Metric | Value |
|--------|-------|
| Error Detection Accuracy | 65%+ |
| Average Response Time | <50ms |
| Supported Error Types | 10 |

## 📄 License

MIT License
