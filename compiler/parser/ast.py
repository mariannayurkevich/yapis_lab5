from dataclasses import dataclass, field
from typing import List, Optional, Union, Any
from enum import Enum

from errors.base import SourceLocation

class AccessModifier(Enum):
    PUBLIC = "PUBLIC"
    PROTECTED = "PROTECTED"
    PRIVATE = "PRIVATE"

class TypeKind(Enum):
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    IMAGE = "image"
    COLOR = "color"
    PIXEL = "pixel"
    STRING = "string"
    STRUCT = "struct"
    VOID = "void"

@dataclass
class Type:
    kind: TypeKind
    struct_name: Optional[str] = None

    def __str__(self) -> str:
        if self.kind == TypeKind.STRUCT:
            return self.struct_name or "struct"
        return self.kind.value

@dataclass
class SourceInfo:
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None

@dataclass(kw_only=True)
class ASTNode:
    source_info: Optional[Any] = None

@dataclass(kw_only=True)
class Expression(ASTNode):
    pass

@dataclass(kw_only=True)
class LiteralExpr(Expression):
    value: Union[int, float, bool, str]
    type: Any

@dataclass(kw_only=True)
class CastExpr(Expression):
    target_type: Type
    expr: Expression

@dataclass(kw_only=True)
class VariableExpr(Expression):
    name: str
    type: Optional[Any] = None

@dataclass
class BinaryExpr(Expression):
    left: Expression
    op: str
    right: Expression
    type: Optional[Type] = None

@dataclass
class UnaryExpr(Expression):
    op: str
    expr: Expression
    type: Optional[Type] = None

@dataclass(kw_only=True)
class CallExpr(Expression):
    func_name: str
    args: List[Expression]
    receiver: Optional[Expression] = None
    type: Optional[Type] = None

@dataclass
class MemberAccessExpr(Expression):
    obj: Expression
    member: str
    type: Optional[Type] = None

@dataclass
class ConstructorExpr(Expression):
    struct_name: str
    args: List[Expression]
    type: Optional[Type] = None

class Statement(ASTNode):
    pass

@dataclass
class VariableDecl(Statement):
    var_type: Type
    variables: List['VariableEntry']

@dataclass
class VariableEntry:
    name: str
    initializer: Optional[Expression] = None

@dataclass
class Assignment(Statement):
    target: Union[VariableExpr, MemberAccessExpr]
    value: Expression

@dataclass
class IfStatement(Statement):
    condition: Expression
    then_block: 'Block'
    else_block: Optional['Block'] = None

@dataclass
class WhileLoop(Statement):
    condition: Expression
    body: 'Block'

@dataclass
class ForLoop(Statement):
    init: Optional[VariableDecl]
    condition: Optional[Expression]
    update: Optional[Assignment]
    body: 'Block'

@dataclass
class DoUntilLoop(Statement):
    body: 'Block'
    condition: Expression

@dataclass
class ReturnStatement(Statement):
    value: Optional[Expression] = None

@dataclass
class ExpressionStatement(Statement):
    expr: Expression

class Declaration(ASTNode):
    pass

@dataclass
class FunctionDecl(Declaration):
    name: str
    params: List['Parameter']
    return_type: Type
    body: 'Block'
    modifiers: List[str] = field(default_factory=list)

@dataclass
class StructDecl(Declaration):
    name: str
    parent: Optional[str]
    members: List['MemberDecl']
    access_modifier: AccessModifier = AccessModifier.PUBLIC

@dataclass
class MemberDecl(ASTNode):
    access: AccessModifier = field(default=AccessModifier.PUBLIC)
    decl: Union['FieldDecl', 'MethodDecl'] = field(default=None)

@dataclass
class FieldDecl(ASTNode):
    field_type: Type = field(default=None)
    name: str = field(default="")

@dataclass
class MethodDecl(FunctionDecl):
    pass

@dataclass(kw_only=True)
class Parameter(ASTNode):
    param_type: Any
    name: str
    kind: str = "value"

@dataclass
class Block(ASTNode):
    statements: List[Statement]

@dataclass
class Program(ASTNode):
    declarations: List[Declaration]
    statements: List[Statement]