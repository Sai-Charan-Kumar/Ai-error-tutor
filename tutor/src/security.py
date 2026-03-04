"""
Security Module - Code safety validation before execution
Week 7: Security Risk & Robustness Analysis

This module performs static analysis on user-submitted code to detect
potentially dangerous patterns BEFORE execution. It addresses:
  - FR-13: Basic static checks before execution
  - FR-14: Block potentially dangerous code patterns

Security Risks Addressed:
  1. File system access (read/write/delete files)
  2. System command execution (os.system, subprocess)
  3. Network access (socket, urllib, requests)
  4. Code injection (exec, eval, compile on dynamic input)
  5. Process/environment manipulation (sys.exit, env vars)
  6. Module import of dangerous libraries
"""

import ast
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class SecurityWarning:
    """Represents a single security warning."""
    level: str          # 'BLOCKED' or 'WARNING'
    category: str       # e.g., 'file_access', 'system_command'
    message: str        # Human-friendly description
    line_number: int    # Line where the issue was found
    code_snippet: str   # The problematic code


class CodeSecurityValidator:
    """
    Validates user code for security risks before execution.

    Uses both AST-based analysis (for parseable code) and
    regex-based analysis (as a fallback for all code including
    code with syntax errors).
    """

    # Modules that should NEVER be imported in a learning environment
    BLOCKED_MODULES = {
        # System command execution
        'subprocess', 'commands',
        # Low-level OS access
        'ctypes', 'multiprocessing',
        # Network access
        'socket', 'http', 'urllib', 'requests', 'ftplib',
        'xmlrpc', 'smtplib', 'poplib', 'imaplib',
        # Code manipulation
        'importlib', 'code', 'codeop',
        # System internals
        'signal', 'resource',
    }

    # Dangerous functions that get BLOCKED
    BLOCKED_FUNCTIONS = {
        'exec', 'eval', 'compile',      # Dynamic code execution
        '__import__',                     # Dynamic imports
        'globals', 'locals',             # Scope manipulation
        'breakpoint',                     # Debugger access
    }

    # Dangerous method calls on specific modules — these get BLOCKED
    BLOCKED_MODULE_CALLS = {
        'os': ['system', 'popen', 'exec', 'execl', 'execle', 'execlp',
               'execv', 'execve', 'execvp', 'execvpe', 'spawn', 'spawnl',
               'spawnle', 'spawnlp', 'spawnlpe', 'spawnv', 'spawnve',
               'spawnvp', 'spawnvpe', 'fork', 'kill', 'killpg',
               'remove', 'unlink', 'rmdir', 'removedirs',
               'rename', 'renames', 'replace',
               'chmod', 'chown', 'chroot', 'link', 'symlink',
               'environ', 'putenv', 'unsetenv'],
        'shutil': ['rmtree', 'move', 'copy', 'copy2', 'copytree',
                   'disk_usage', 'chown'],
        'sys': ['exit', '_exit'],
        'pathlib': ['unlink', 'rmdir', 'rename', 'replace', 'chmod',
                    'symlink_to', 'link_to'],
    }

    # Patterns that generate WARNINGs (not blocked, but flagged)
    WARNING_PATTERNS = {
        'file_open': r'\bopen\s*\(',
        'file_write': r'\.(write|writelines)\s*\(',
    }

    def __init__(self):
        self.warnings: List[SecurityWarning] = []

    def validate(self, code: str) -> Tuple[bool, List[SecurityWarning]]:
        """
        Validate code for security risks.

        Args:
            code: The Python source code to validate

        Returns:
            Tuple of (is_safe: bool, warnings: list of SecurityWarning)
            is_safe is False if any BLOCKED-level issues are found
        """
        self.warnings = []

        # Try AST-based scan first (more accurate)
        ast_scan_done = False
        try:
            tree = ast.parse(code)
            self._ast_scan(tree, code)
            ast_scan_done = True
        except SyntaxError:
            # Code has syntax errors — fall back to regex scan
            pass

        if not ast_scan_done:
            # Only use regex scan when AST parsing fails
            # This avoids duplicate warnings from both scans
            self._regex_scan(code)
        else:
            # AST scan succeeded — still do regex for WARNING-level patterns
            # (file open/write) since AST scan doesn't check those
            self._regex_warning_scan(code)

        is_safe = not any(w.level == 'BLOCKED' for w in self.warnings)
        return is_safe, self.warnings

    def _regex_scan(self, code: str) -> None:
        """
        Full regex scan — used only when AST parsing fails.
        Checks both blocked imports and warning patterns.
        """
        lines = code.split('\n')

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip comments and empty lines
            if stripped.startswith('#') or not stripped:
                continue

            # Check for dangerous module imports via regex
            import_match = re.match(
                r'(?:from\s+(\S+)\s+import|import\s+(\S+))', stripped
            )
            if import_match:
                module = import_match.group(1) or import_match.group(2)
                root_module = module.split('.')[0]
                if root_module in self.BLOCKED_MODULES:
                    self.warnings.append(SecurityWarning(
                        level='BLOCKED',
                        category='dangerous_import',
                        message=(f"Import of '{module}' is not allowed. "
                                 f"This module can access system resources "
                                 f"outside the learning environment."),
                        line_number=line_num,
                        code_snippet=stripped
                    ))

            # Check for warning-level patterns
            for pattern_name, pattern in self.WARNING_PATTERNS.items():
                if re.search(pattern, stripped):
                    self.warnings.append(SecurityWarning(
                        level='WARNING',
                        category=pattern_name,
                        message=self._get_warning_message(pattern_name),
                        line_number=line_num,
                        code_snippet=stripped
                    ))

    def _regex_warning_scan(self, code: str) -> None:
        """
        Regex scan for WARNING-level patterns only.
        Used alongside AST scan (which handles BLOCKED items).
        """
        lines = code.split('\n')

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            if stripped.startswith('#') or not stripped:
                continue

            for pattern_name, pattern in self.WARNING_PATTERNS.items():
                if re.search(pattern, stripped):
                    self.warnings.append(SecurityWarning(
                        level='WARNING',
                        category=pattern_name,
                        message=self._get_warning_message(pattern_name),
                        line_number=line_num,
                        code_snippet=stripped
                    ))

    def _ast_scan(self, tree: ast.AST, code: str) -> None:
        """Scan the AST for dangerous constructs."""
        lines = code.split('\n')

        for node in ast.walk(tree):
            # Check function calls
            if isinstance(node, ast.Call):
                self._check_call(node, lines)

            # Check imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split('.')[0]
                    if root in self.BLOCKED_MODULES:
                        self.warnings.append(SecurityWarning(
                            level='BLOCKED',
                            category='dangerous_import',
                            message=(f"Import of '{alias.name}' is not allowed. "
                                     f"This module can access system resources "
                                     f"outside the learning environment."),
                            line_number=node.lineno,
                            code_snippet=self._safe_get_line(lines, node.lineno)
                        ))

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root = node.module.split('.')[0]
                    if root in self.BLOCKED_MODULES:
                        self.warnings.append(SecurityWarning(
                            level='BLOCKED',
                            category='dangerous_import',
                            message=(f"Import from '{node.module}' is not allowed. "
                                     f"This module can access system resources "
                                     f"outside the learning environment."),
                            line_number=node.lineno,
                            code_snippet=self._safe_get_line(lines, node.lineno)
                        ))

    def _check_call(self, node: ast.Call, lines: List[str]) -> None:
        """Check if a function call is dangerous."""
        # Direct function calls: exec(), eval(), etc.
        if isinstance(node.func, ast.Name):
            if node.func.id in self.BLOCKED_FUNCTIONS:
                self.warnings.append(SecurityWarning(
                    level='BLOCKED',
                    category='dangerous_function',
                    message=(f"Use of '{node.func.id}()' is not allowed. "
                             f"This function can execute arbitrary code "
                             f"and is a security risk."),
                    line_number=node.lineno,
                    code_snippet=self._safe_get_line(lines, node.lineno)
                ))

        # Method calls: os.system(), shutil.rmtree(), etc.
        elif isinstance(node.func, ast.Attribute):
            method_name = node.func.attr

            if isinstance(node.func.value, ast.Name):
                obj_name = node.func.value.id

                if obj_name in self.BLOCKED_MODULE_CALLS:
                    blocked_methods = self.BLOCKED_MODULE_CALLS[obj_name]
                    if method_name in blocked_methods:
                        self.warnings.append(SecurityWarning(
                            level='BLOCKED',
                            category='dangerous_method',
                            message=(f"Call to '{obj_name}.{method_name}()' "
                                     f"is not allowed. This can modify system "
                                     f"resources outside the learning environment."),
                            line_number=node.lineno,
                            code_snippet=self._safe_get_line(lines, node.lineno)
                        ))

    def _safe_get_line(self, lines: List[str], line_number: int) -> str:
        """Safely get a line from the source code."""
        if 1 <= line_number <= len(lines):
            return lines[line_number - 1].strip()
        return ""

    def _get_warning_message(self, pattern_name: str) -> str:
        """Get a human-friendly warning message for a pattern."""
        messages = {
            'file_open': ("File access detected. Be careful when opening files — "
                          "make sure you're not reading sensitive data."),
            'file_write': ("File write detected. Writing to files can overwrite "
                           "important data. Make sure this is intentional."),
        }
        return messages.get(pattern_name, "Potentially risky operation detected.")

    def format_warnings(self) -> str:
        """Format all warnings into a human-readable string."""
        if not self.warnings:
            return "✅ No security issues detected."

        output = []
        blocked = [w for w in self.warnings if w.level == 'BLOCKED']
        warned = [w for w in self.warnings if w.level == 'WARNING']

        if blocked:
            output.append("🚫 BLOCKED — Code will NOT be executed:\n")
            for w in blocked:
                output.append(f"  Line {w.line_number}: {w.message}")
                output.append(f"    Code: {w.code_snippet}")
                output.append("")

        if warned:
            output.append("⚠️  WARNINGS — Code will run, but review these:\n")
            for w in warned:
                output.append(f"  Line {w.line_number}: {w.message}")
                output.append(f"    Code: {w.code_snippet}")
                output.append("")

        return '\n'.join(output)


if __name__ == "__main__":
    validator = CodeSecurityValidator()

    # Test 1: Dangerous code
    dangerous_code = """
import subprocess
import os

os.system('rm -rf /')
subprocess.run(['ls'])
eval(input("Enter code: "))
exec("print('hacked')")
"""
    print("=== Test 1: Dangerous Code ===")
    is_safe, warnings = validator.validate(dangerous_code)
    print(f"Safe: {is_safe}")
    print(f"Warning count: {len(warnings)}")
    print(validator.format_warnings())

    # Test 2: Safe code
    safe_code = """
x = 10
y = 20
print(x + y)

def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
"""
    print("\n=== Test 2: Safe Code ===")
    is_safe, warnings = validator.validate(safe_code)
    print(f"Safe: {is_safe}")
    print(validator.format_warnings())

    # Test 3: Code with warnings (not blocked)
    warning_code = """
f = open('data.txt', 'r')
content = f.read()
f.close()
print(content)
"""
    print("\n=== Test 3: Warning Code ===")
    is_safe, warnings = validator.validate(warning_code)
    print(f"Safe: {is_safe}")
    print(validator.format_warnings())