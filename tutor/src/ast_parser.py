"""
AST Parser Module - Extracts code context using Abstract Syntax Tree
Week 6
"""

import ast
from typing import Dict, List, Optional, Any


class ASTContextExtractor:
    """Extracts contextual information from Python code using AST."""

    def __init__(self):
        self.tree: Optional[ast.AST] = None
        self.source_lines: List[str] = []

    def parse(self, code: str) -> bool:
        """
        Parse code into AST.

        Returns:
            True if parsing successful, False otherwise
        """
        self.source_lines = code.split('\n')
        try:
            self.tree = ast.parse(code)
            return True
        except SyntaxError:
            # Can't parse invalid syntax
            self.tree = None
            return False

    def get_context_at_line(self, line_number: int) -> Dict[str, Any]:
        """
        Get AST context for a specific line.

        Args:
            line_number: The line number to analyze

        Returns:
            Dictionary with context information
        """
        if not self.tree:
            return self._get_basic_context(line_number)

        context = {
            'line_number': line_number,
            'line_content': self._get_line(line_number),
            'enclosing_function': None,
            'enclosing_class': None,
            'node_type': None,
            'variables_in_scope': [],
            'imports': [],
            'function_calls': []
        }

        # Track whether the target line is inside a function
        inside_function = False

        for node in ast.walk(self.tree):
            if not hasattr(node, 'lineno'):
                continue

            # Set node_type for the node at the target line
            # Use 'is None' guard so only the first (outermost) node sets it
            if node.lineno == line_number and context['node_type'] is None:
                context['node_type'] = type(node).__name__

            if isinstance(node, ast.FunctionDef):
                if self._node_contains_line(node, line_number):
                    context['enclosing_function'] = node.name
                    context['variables_in_scope'].extend(
                        self._get_function_variables(node)
                    )
                    inside_function = True

            elif isinstance(node, ast.ClassDef):
                if self._node_contains_line(node, line_number):
                    context['enclosing_class'] = node.name

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                context['imports'].extend(self._get_imports(node))

            elif isinstance(node, ast.Call) and node.lineno == line_number:
                context['function_calls'].append(self._get_call_info(node))

        if not inside_function:
            context['variables_in_scope'] = self._get_module_level_variables(line_number)

        return context

    def _get_module_level_variables(self, up_to_line: int) -> List[str]:
        """
        Collect names defined at module level up to the given line.

        Uses ast.iter_child_nodes(Module) to only get TOP-LEVEL statements,
        not variables buried inside functions or classes.
        """
        variables = []
        if not self.tree:
            return variables

        for node in ast.iter_child_nodes(self.tree):
            if not hasattr(node, 'lineno') or node.lineno > up_to_line:
                continue

            # Module-level variable assignments
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id not in variables:
                        variables.append(target.id)

            # Function and class names are also in module scope
            elif isinstance(node, ast.FunctionDef):
                if node.name not in variables:
                    variables.append(node.name)

            elif isinstance(node, ast.ClassDef):
                if node.name not in variables:
                    variables.append(node.name)

        return variables

    def get_all_definitions(self) -> Dict[str, List[str]]:
        """Get all function and class definitions in the code."""
        if not self.tree:
            return {'functions': [], 'classes': [], 'variables': []}

        definitions = {
            'functions': [],
            'classes': [],
            'variables': []
        }

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                definitions['functions'].append(node.name)
            elif isinstance(node, ast.ClassDef):
                definitions['classes'].append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        definitions['variables'].append(target.id)

        return definitions

    def analyze_error_context(self, error_info: Dict) -> Dict[str, Any]:
        """
        Analyze error context to provide better explanations.

        Args:
            error_info: Error information from ErrorCapture

        Returns:
            Enhanced context dictionary
        """
        code = error_info.get('full_code', '')
        line_num = error_info.get('line_number')

        self.parse(code)

        enhanced_context = {
            'error_type': error_info.get('error_type'),
            'error_message': error_info.get('message'),
            'line_number': line_num,
            'ast_context': self.get_context_at_line(line_num) if line_num else {},
            'definitions': self.get_all_definitions(),
            'similar_names': self._find_similar_names(error_info),
            'suggestions': self._generate_suggestions(error_info)
        }

        return enhanced_context

    def _get_line(self, line_number: int) -> str:
        """Get a specific line from source."""
        if 1 <= line_number <= len(self.source_lines):
            return self.source_lines[line_number - 1]
        return ""

    def _node_contains_line(self, node: ast.AST, line: int) -> bool:
        """Check if a node's range contains the given line."""
        if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
            return False
        return node.lineno <= line <= (node.end_lineno or node.lineno)

    def _get_function_variables(self, func_node: ast.FunctionDef) -> List[str]:
        """Extract variable names from a function."""
        variables = [arg.arg for arg in func_node.args.args]

        for node in ast.walk(func_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)

        return variables

    def _get_imports(self, node: ast.AST) -> List[str]:
        """Extract import names."""
        imports = []
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.extend(alias.name for alias in node.names)
        return imports

    def _get_call_info(self, node: ast.Call) -> Dict:
        """Get information about a function call."""
        call_info = {'name': None, 'args_count': len(node.args)}

        if isinstance(node.func, ast.Name):
            call_info['name'] = node.func.id
        elif isinstance(node.func, ast.Attribute):
            call_info['name'] = node.func.attr

        return call_info

    def _get_basic_context(self, line_number: int) -> Dict:
        """Get basic context when AST parsing fails."""
        return {
            'line_number': line_number,
            'line_content': self._get_line(line_number),
            'parse_failed': True
        }

    def _find_similar_names(self, error_info: Dict) -> List[str]:
        """Find similar variable/function names for NameError."""
        if error_info.get('error_type') != 'NameError':
            return []

        # Extract undefined name from error message
        message = error_info.get('message', '')
        if "name '" in message:
            undefined = message.split("'")[1]
            definitions = self.get_all_definitions()
            all_names = (definitions['functions'] +
                         definitions['classes'] +
                         definitions['variables'])

            return [name for name in all_names
                    if self._levenshtein_distance(name, undefined) <= 2]

        return []

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _generate_suggestions(self, error_info: Dict) -> List[str]:
        """Generate fix suggestions based on error type."""
        suggestions = []
        error_type = error_info.get('error_type', '')

        suggestion_map = {
            'SyntaxError': [
                "Check for missing colons after if/for/while/def/class statements",
                "Ensure all parentheses, brackets, and braces are properly closed",
                "Check for proper string quote matching"
            ],
            'IndentationError': [
                "Use consistent indentation (4 spaces recommended)",
                "Ensure code inside functions/loops is properly indented"
            ],
            'NameError': [
                "Check for typos in variable/function names",
                "Ensure the variable is defined before use",
                "Check if you need to import a module"
            ],
            'TypeError': [
                "Check the types of operands in operations",
                "Use type conversion functions (str(), int(), float())",
                "Verify function arguments match expected types"
            ]
        }

        return suggestion_map.get(error_type, ["Review the error message carefully"])


if __name__ == "__main__":
    # Test AST parser
    code = """
def calculate_sum(a, b):
    result = a + b
    return result

x = 10
y = "20"
total = calculate_sum(x, y)
"""

    extractor = ASTContextExtractor()
    extractor.parse(code)

    print("Definitions:", extractor.get_all_definitions())

    # Line 3 is inside calculate_sum → should show function variables
    print("\nContext at line 3:", extractor.get_context_at_line(3))