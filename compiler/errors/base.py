from dataclasses import dataclass
from typing import Optional

@dataclass
class SourceLocation:
    line: int
    column: int
    length: int = 1
    end_line: Optional[int] = None  
    end_column: Optional[int] = None
    
    def __post_init__(self):
        if self.end_line is None:
            self.end_line = self.line
        if self.end_column is None:
            self.end_column = self.column + self.length - 1
    
    def __str__(self) -> str:
        return f"{self.line}:{self.column}"

class CompilerError(Exception):
    def __init__(self, 
                 message: str, 
                 location: Optional[SourceLocation] = None,
                 severity: str = "error"):
        self.message = message
        self.location = location
        self.severity = severity
        super().__init__(self.formatted_message())
    
    def formatted_message(self) -> str:
        if self.location:
            return f"[{self.location.line}:{self.location.column}] {self.message}"
        return self.message

class SyntaxError(CompilerError):
    pass

class InternalCompilerError(CompilerError):
    """Ошибка внутри компилятора (баг)"""
    pass