from enum import Enum
from typing import Dict, Set, Optional

class TypeCompatibility(Enum):
    EXACT = 1
    IMPLICIT = 2
    EXPLICIT = 3
    NONE = 4

class TypeSystem:
    def __init__(self):
        self.numeric_types = {"int", "float"}
        self.image_types = {"image", "color", "pixel"}
        self.builtin_types = self.numeric_types | self.image_types | {"bool", "string"}
        
        self.implicit_conversions = {
            ("int", "float"): True,
            ("int", "bool"): False,
        }
        
        self.explicit_conversions = {
            ("int", "float"): True,
            ("float", "int"): True,
            ("color", "pixel"): True,
            ("pixel", "color"): True,
        }
        
        self.operation_table = {
            # Арифметика
            "+": {("int", "int"): "int", ("float", "float"): "float", ("int", "float"): "float", ("string", "string"): "string"},
            "-": {("int", "int"): "int", ("float", "float"): "float", ("int", "float"): "float"},
            "*": {("int", "int"): "int", ("float", "float"): "float", ("int", "float"): "float"},
            "/": {("int", "int"): "int", ("float", "float"): "float", ("int", "float"): "float"},
            "**": {("int", "int"): "int", ("float", "float"): "float"},
            
            # Сравнение (результат всегда bool)
            "==": {("int", "int"): "bool", ("float", "float"): "bool", ("bool", "bool"): "bool", ("string", "string"): "bool"},
            "!=": {("int", "int"): "bool", ("float", "float"): "bool", ("bool", "bool"): "bool", ("string", "string"): "bool"},
            ">":  {("int", "int"): "bool", ("float", "float"): "bool"},
            "<":  {("int", "int"): "bool", ("float", "float"): "bool"},
            ">=": {("int", "int"): "bool", ("float", "float"): "bool"},
            "<=": {("int", "int"): "bool", ("float", "float"): "bool"},
            
            # Логика
            "&&": {("bool", "bool"): "bool"},
            "||": {("bool", "bool"): "bool"},
        }
    
    def check_compatibility(self, from_type: str, to_type: str) -> TypeCompatibility:
        if from_type == to_type:
            return TypeCompatibility.EXACT
        
        if (from_type, to_type) in self.implicit_conversions:
            return TypeCompatibility.IMPLICIT
        
        if (from_type, to_type) in self.explicit_conversions:
            return TypeCompatibility.EXPLICIT
        
        return TypeCompatibility.NONE
    
    def get_operation_result_type(self, op: str, left_type: str, right_type: str) -> Optional[str]:
        return self.operation_table.get(op, {}).get((left_type, right_type))