from typing import Dict, Optional, List, Any
from enum import Enum
from parser.ast import Type, AccessModifier

class SymbolKind(Enum):
    VARIABLE = "variable"
    FUNCTION = "function"
    STRUCT = "struct"
    FIELD = "field"
    METHOD = "method"
    PARAMETER = "parameter"

class Symbol:
    def __init__(self, 
                 name: str, 
                 kind: SymbolKind,
                 symbol_type: Type,
                 scope_level: int,
                 source_info: Optional[Any] = None):
        self.name = name
        self.kind = kind
        self.type = symbol_type
        self.scope_level = scope_level
        self.source_info = source_info
        self.references: List[Any] = []
        
        self.params: List[Symbol] = []
        self.return_type: Optional[Type] = None
        self.is_virtual: bool = False
        self.is_override: bool = False
        
        self.parent: Optional[str] = None
        self.fields: Dict[str, Symbol] = {}
        self.methods: Dict[str, Symbol] = {}
        self.access: AccessModifier = AccessModifier.PUBLIC
        
        self.access_modifier: AccessModifier = AccessModifier.PUBLIC

class Scope:
    def __init__(self, parent: Optional['Scope'] = None):
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.level = parent.level + 1 if parent else 0
    
    def define(self, symbol: Symbol) -> bool:
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True
    
    def resolve(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.resolve(name)
        return None
    
    def resolve_local(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)

class SymbolTable:
    def __init__(self):
        self.current_scope = Scope()
        self.global_scope = self.current_scope
        self.structs: Dict[str, Symbol] = {}
        self.functions: Dict[str, Symbol] = {}
    
    def enter_scope(self):
        self.current_scope = Scope(self.current_scope)
    
    def exit_scope(self):
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def define_symbol(self, 
                     name: str, 
                     kind: SymbolKind, 
                     symbol_type: Type,
                     source_info=None) -> Symbol:
        symbol = Symbol(name, kind, symbol_type, self.current_scope.level, source_info)
        if not self.current_scope.define(symbol):
            raise ValueError(f"Symbol '{name}' already defined in current scope")
        
        if kind == SymbolKind.STRUCT:
            self.structs[name] = symbol
        elif kind == SymbolKind.FUNCTION:
            self.functions[name] = symbol
            
        return symbol
    
    def resolve(self, name: str) -> Optional[Symbol]:
        return self.current_scope.resolve(name)
    
    def resolve_function(self, name: str) -> Optional[Symbol]:
        return self.functions.get(name)
    
    def resolve_struct(self, name: str) -> Optional[Symbol]:
        return self.structs.get(name)