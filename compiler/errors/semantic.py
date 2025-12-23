from .base import CompilerError, SourceLocation

class SemanticError(CompilerError):
    """Базовый класс для семантических ошибок"""
    pass

class TypeMismatchError(SemanticError):
    def __init__(self, expected: str, actual: str, location: SourceLocation):
        super().__init__(
            f"Type mismatch: expected '{expected}', got '{actual}'",
            location
        )

class UndefinedSymbolError(SemanticError):
    def __init__(self, name: str, location: SourceLocation):
        super().__init__(
            f"Undefined symbol: '{name}'",
            location
        )

class RedeclarationError(SemanticError):
    def __init__(self, name: str, location: SourceLocation):
        super().__init__(
            f"Redeclaration of symbol: '{name}'",
            location
        )

class InvalidOperationError(SemanticError):
    def __init__(self, operation: str, operand_type: str, location: SourceLocation):
        super().__init__(
            f"Invalid operation '{operation}' for type '{operand_type}'",
            location
        )

class ArgumentCountError(SemanticError):
    def __init__(self, name: str, expected: int, actual: int, location: SourceLocation):
        super().__init__(
            f"Function '{name}' expects {expected} arguments, got {actual}",
            location
        )

class InvalidReturnError(SemanticError):
    def __init__(self, expected: str, actual: str, location: SourceLocation):
        super().__init__(
            f"Invalid return type: expected '{expected}', got '{actual}'",
            location
        )

class AccessViolationError(SemanticError):
    def __init__(self, member: str, access: str, location: SourceLocation):
        super().__init__(
            f"Cannot access {access} member '{member}' from this context",
            location
        )

class InheritanceCycleError(SemanticError):
    def __init__(self, struct_name: str, location: SourceLocation):
        super().__init__(
            f"Cyclic inheritance detected for struct '{struct_name}'",
            location
        )