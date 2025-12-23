from typing import List
from .base import CompilerError

class ErrorFormatter:
    def __init__(self, source_code: str = ""):
        self.source_code = source_code.splitlines() if source_code else []
    
    def format_error(self, error: CompilerError) -> str:
        lines = []
        
        if error.location and error.location.line <= len(self.source_code):
            line_num = error.location.line
            col = error.location.column
            line = self.source_code[line_num - 1]
            
            lines.append(f"  {line_num:4} | {line}")
            lines.append("       | " + " " * (col - 1) + "^" * max(1, error.location.length))
        
        lines.append(f"{error.severity.upper()}: {error.message}")
        return "\n".join(lines)
    
    def format_all(self, errors: List[CompilerError]) -> str:
        return "\n\n".join(self.format_error(e) for e in errors)