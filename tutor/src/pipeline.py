"""
Main Pipeline - End-to-end error explanation system
"""

from typing import Optional, Dict
from dataclasses import dataclass

try:
    from .error_capture import ErrorCapture
    from .ast_parser import ASTContextExtractor
    from .model import ErrorExplainerModel, FallbackExplainer
except ImportError:
    from error_capture import ErrorCapture
    from ast_parser import ASTContextExtractor
    from model import ErrorExplainerModel, FallbackExplainer


@dataclass
class ExplanationResult:
    """Result from the error explanation pipeline."""
    success: bool
    error_type: Optional[str]
    raw_error: Optional[str]
    friendly_explanation: Optional[str]
    suggested_fix: Optional[str]
    code_context: Optional[str]
    line_number: Optional[int]
    similar_names: list
    security_warnings: list


class AIErrorTutor:
    """Main pipeline for AI-powered error explanations."""

    def __init__(self, model_path: Optional[str] = "./models/error_tutor_model", use_ai: bool = True):
        """
        Initialize the AI Error Tutor.

        Args:
            model_path: Path to fine-tuned model (if available)
            use_ai: Whether to use AI model (False for fallback only)
        """
        self.error_capture = ErrorCapture()
        self.ast_extractor = ASTContextExtractor()
        self.fallback = FallbackExplainer()

        self.use_ai = use_ai
        self.model = None

        if use_ai:
            try:
                import os
                # Verify folder actually exists locally
                if model_path and not os.path.exists(model_path):
                    raise FileNotFoundError(f"Model folder not found at: {model_path}")
                
                # Pass the path directly when initializing!
                self.model = ErrorExplainerModel(model_path=model_path)
                print("✓ AI model loaded successfully")
            except Exception as e:
                print(f"⚠ AI model not available: {e}")
                print("  Using fallback explanations")
                self.use_ai = False

    def analyze_code(self, code: str) -> ExplanationResult:
        """
        Analyze code and provide friendly error explanations.

        Args:
            code: Python code to analyze

        Returns:
            ExplanationResult with error details and friendly explanation
        """
        # Step 1: Execute and capture errors (security check happens inside)
        success, error_info = self.error_capture.execute_code(code)

        # Collect any security warnings
        sec_warnings = []
        if error_info and 'security_warnings' in error_info:
            sec_warnings = error_info['security_warnings']

        if success:
            return ExplanationResult(
                success=True,
                error_type=None,
                raw_error=None,
                friendly_explanation="✓ Your code ran successfully! ",
                suggested_fix=None,
                code_context=None,
                line_number=None,
                similar_names=[],
                security_warnings=sec_warnings
            )

        # Step 1.5: Handle security blocks separately
        if error_info.get('error_type') == 'SecurityError':
            return ExplanationResult(
                success=False,
                error_type='SecurityError',
                raw_error=error_info['message'],
                friendly_explanation=(
                    "🚫 Your code was blocked because it contains potentially "
                    "dangerous operations. In a learning environment, operations "
                    "like system commands, file deletion, or dynamic code execution "
                    "are not allowed for your safety."
                ),
                suggested_fix=(
                    "Remove the dangerous imports/functions and focus on "
                    "the programming concept you're trying to learn."
                ),
                code_context=error_info.get('code_context', ''),
                line_number=error_info.get('line_number'),
                similar_names=[],
                security_warnings=sec_warnings
            )

        # Step 2: Extract AST context
        ast_context = self.ast_extractor.analyze_error_context(error_info)

        # Step 3: Generate explanation
        if self.use_ai and self.model:
            explanation = self._generate_ai_explanation(error_info, ast_context)
        else:
            explanation = self._generate_fallback_explanation(error_info, ast_context)

        # Attach security warnings to the result
        explanation.security_warnings = sec_warnings

        return explanation

    def _get_clean_code_context(self, error_info: Dict) -> str:
        """
        Extract clean code context for the AI model (no >>> markers or line numbers).

        Uses the raw source code and error line number to get a clean snippet
        matching the format the model was trained on.
        """
        full_code = error_info.get('full_code', '')
        line_number = error_info.get('line_number')

        if not line_number or not full_code:
            return error_info.get('code_context', '')

        lines = full_code.split('\n')
        # Get up to 3 lines of context around the error
        start = max(0, line_number - 2)
        end = min(len(lines), line_number + 2)
        return '\n'.join(lines[start:end]).strip()

    def _generate_ai_explanation(self, error_info: Dict,
                                 ast_context: Dict) -> ExplanationResult:
        """Generate explanation using AI model."""
        try:
            # Send clean code to the model, not the formatted display context
            clean_context = self._get_clean_code_context(error_info)

            full_explanation = self.model.generate_explanation(
                error_type=error_info['error_type'],
                error_message=error_info['message'],
                code_context=clean_context
            )

            # Parse explanation and fix
            if ' FIX: ' in full_explanation:
                parts = full_explanation.split(' FIX: ', 1)
                explanation = parts[0]
                fix = parts[1] if len(parts) > 1 else None
            else:
                explanation = full_explanation
                fix = self._generate_basic_fix(error_info, ast_context)

            return ExplanationResult(
                success=False,
                error_type=error_info['error_type'],
                raw_error=error_info['message'],
                friendly_explanation=explanation,
                suggested_fix=fix,
                code_context=error_info['code_context'],
                line_number=error_info['line_number'],
                similar_names=ast_context.get('similar_names', []),
                security_warnings=[]
            )

        except Exception as e:
            print(f"AI generation failed: {e}, using fallback")
            return self._generate_fallback_explanation(error_info, ast_context)

    def _generate_fallback_explanation(self, error_info: Dict,
                                       ast_context: Dict) -> ExplanationResult:
        """Generate explanation using rule-based fallback."""
        explanation = self.fallback.explain(
            error_info['error_type'],
            error_info['message']
        )

        # Enhance with AST context
        similar = ast_context.get('similar_names', [])
        if similar:
            explanation += f" Did you mean: {', '.join(similar)}?"

        fix = self._generate_basic_fix(error_info, ast_context)

        return ExplanationResult(
            success=False,
            error_type=error_info['error_type'],
            raw_error=error_info['message'],
            friendly_explanation=explanation,
            suggested_fix=fix,
            code_context=error_info['code_context'],
            line_number=error_info['line_number'],
            similar_names=similar,
            security_warnings=[]
        )

    def _generate_basic_fix(self, error_info: Dict, ast_context: Dict) -> str:
        """Generate basic fix suggestions."""
        error_type = error_info['error_type']
        suggestions = ast_context.get('suggestions', [])

        if suggestions:
            return suggestions[0]

        fix_templates = {
            'SyntaxError': "Check for missing colons, parentheses, or quotes",
            'NameError': "Verify the variable name is spelled correctly and defined",
            'TypeError': "Check type compatibility and use conversion functions",
            'IndexError': "Verify the index is within the valid range",
            'KeyError': "Use .get() method or verify the key exists"
        }

        return fix_templates.get(error_type, "Review the code at the indicated line")

    def explain_error(self, code: str) -> str:
        """
        Convenience method to get a formatted explanation string.

        Args:
            code: Python code to analyze

        Returns:
            Formatted explanation string
        """
        result = self.analyze_code(code)

        if result.success:
            output = result.friendly_explanation
            # Still show warnings even if code ran successfully
            if result.security_warnings:
                warned = [w for w in result.security_warnings if w.level == 'WARNING']
                if warned:
                    output += "\n\n⚠️  Security Notes:"
                    for w in warned:
                        output += f"\n  Line {w.line_number}: {w.message}"
            return output

        output = []

        # Show security block prominently
        if result.error_type == 'SecurityError':
            output.append("🚫 SECURITY BLOCK")
            output.append("=" * 40)
            output.append(result.friendly_explanation)
            output.append("")
            if result.suggested_fix:
                output.append(f"🔧 {result.suggested_fix}")
            output.append("")
            # Show detailed warnings
            if result.security_warnings:
                for w in result.security_warnings:
                    if w.level == 'BLOCKED':
                        output.append(f"  ❌ Line {w.line_number}: {w.message}")
                        output.append(f"     Code: {w.code_snippet}")
            return '\n'.join(output)

        output.append(f"🔴 Error Type: {result.error_type}")
        output.append(f"📍 Line:  {result.line_number}")
        output.append("")
        output.append(f"💡 Explanation: {result.friendly_explanation}")
        output.append("")

        if result.suggested_fix:
            output.append(f"🔧 Suggested Fix: {result.suggested_fix}")

        if result.similar_names:
            output.append(f"❓ Did you mean: {', '.join(result.similar_names)}?")

        # Show security warnings if any
        if result.security_warnings:
            warned = [w for w in result.security_warnings if w.level == 'WARNING']
            if warned:
                output.append("")
                output.append("⚠️  Security Notes:")
                for w in warned:
                    output.append(f"  Line {w.line_number}: {w.message}")

        output.append("")
        output.append("📄 Code Context:")
        output.append(result.code_context)

        return '\n'.join(output)
