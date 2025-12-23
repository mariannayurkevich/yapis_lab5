from typing import Dict, Optional, Tuple
from parser.ast import Type, TypeKind

class CILTypeSystem:
    """Сопоставление типов ImgLang с типами CIL/.NET"""
    
    TYPE_MAPPINGS = {
        TypeKind.INT: ("int32", "System.Int32"),
        TypeKind.FLOAT: ("float64", "System.Double"),
        TypeKind.BOOL: ("bool", "System.Boolean"),
        TypeKind.STRING: ("string", "System.String"),
        TypeKind.IMAGE: ("class [System.Drawing]System.Drawing.Bitmap", 
                        "System.Drawing.Bitmap"),
        TypeKind.COLOR: ("valuetype [System.Drawing]System.Drawing.Color", 
                        "System.Drawing.Color"),
        TypeKind.PIXEL: ("valuetype [System.Drawing]System.Drawing.Color", 
                        "System.Drawing.Color"),
        TypeKind.VOID: ("void", "System.Void"),
    }
    
    REF_MODIFIERS = {
        "in": "in",
        "out": "out",
        "ref": "&",
        "result": "&"
    }
    
    @classmethod
    def map_type(cls, img_type: Type, is_ref: bool = False) -> Tuple[str, str]:
        """Преобразует тип ImgLang в CIL тип"""
        if img_type.kind == TypeKind.STRUCT:
            struct_name = img_type.struct_name or "object"
            cil_type = f"class Program/{struct_name}"
            net_type = struct_name
        else:
            cil_type, net_type = cls.TYPE_MAPPINGS[img_type.kind]
        
        if is_ref and img_type.kind != TypeKind.STRING:
            cil_type += "&"
        
        return cil_type, net_type
    
    @classmethod
    def get_ldarg_instruction(cls, index: int) -> str:
        """Возвращает инструкцию загрузки аргумента"""
        if index == 0:
            return "ldarg.0"
        elif index == 1:
            return "ldarg.1"
        elif index == 2:
            return "ldarg.2"
        elif index == 3:
            return "ldarg.3"
        else:
            return f"ldarg {index}"
    
    @classmethod
    def get_ldloc_instruction(cls, index: int) -> str:
        """Возвращает инструкцию загрузки локальной переменной"""
        if index == 0:
            return "ldloc.0"
        elif index == 1:
            return "ldloc.1"
        elif index == 2:
            return "ldloc.2"
        elif index == 3:
            return "ldloc.3"
        else:
            return f"ldloc {index}"
    
    @classmethod
    def get_stloc_instruction(cls, index: int) -> str:
        """Возвращает инструкцию сохранения в локальную переменную"""
        if index == 0:
            return "stloc.0"
        elif index == 1:
            return "stloc.1"
        elif index == 2:
            return "stloc.2"
        elif index == 3:
            return "stloc.3"
        else:
            return f"stloc {index}"
    
    @classmethod
    def get_arithmetic_instruction(cls, operator: str) -> Optional[str]:
        """Возвращает арифметическую инструкцию CIL"""
        instructions = {
            '+': 'add',
            '-': 'sub',
            '*': 'mul',
            '/': 'div',
            '%': 'rem',
            '**': 'call float64 [mscorlib]System.Math::Pow(float64, float64)',
            '&': 'and',
            '|': 'or',
            '^': 'xor',
            '<<': 'shl',
            '>>': 'shr',
            '&&': 'and',
            '||': 'or',
        }
        return instructions.get(operator)
    
    @classmethod
    def get_comparison_instruction(cls, operator: str) -> Optional[str]:
        """Возвращает инструкцию сравнения CIL"""
        instructions = {
            '==': 'ceq',
            '!=': lambda: ['ceq', 'ldc.i4.0', 'ceq'],
            '>': 'cgt',
            '<': 'clt',
            '>=': lambda: ['clt', 'ldc.i4.0', 'ceq'],
            '<=': lambda: ['cgt', 'ldc.i4.0', 'ceq'],
        }
        return instructions.get(operator)
    
    @classmethod
    def is_floating_point(cls, type_kind: TypeKind) -> bool:
        """Проверяет, является ли тип вещественным"""
        return type_kind in [TypeKind.FLOAT]
    
    @classmethod
    def is_integer(cls, type_kind: TypeKind) -> bool:
        """Проверяет, является ли тип целочисленным"""
        return type_kind in [TypeKind.INT, TypeKind.BOOL]