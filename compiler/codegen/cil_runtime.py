from typing import List, Tuple
from codegen.cil_emitter import CILEmitter
from parser.ast import Type, TypeKind

class RuntimeCodeGenerator:
    """Генератор вызовов runtime функций"""
    
    RUNTIME_CLASS = "[ImgLangRuntime]Runtime"
    
    BUILTIN_FUNCTIONS = {
        "load_image": {
            "return_type": "class [System.Drawing]System.Drawing.Bitmap",
            "params": ["string"],
            "method": "LoadImage"
        },
        "save_image": {
            "return_type": "void",
            "params": ["class [System.Drawing]System.Drawing.Bitmap", "string"],
            "method": "SaveImage"
        },
        "create_image": {
            "return_type": "class [System.Drawing]System.Drawing.Bitmap",
            "params": ["int32", "int32"],
            "method": "CreateImage"
        },
        
        "get_width": {
            "return_type": "int32",
            "params": ["class [System.Drawing]System.Drawing.Bitmap"],
            "method": "GetWidth"
        },
        "get_height": {
            "return_type": "int32",
            "params": ["class [System.Drawing]System.Drawing.Bitmap"],
            "method": "GetHeight"
        },
        "get_pixel": {
            "return_type": "valuetype [System.Drawing]System.Drawing.Color",
            "params": ["class [System.Drawing]System.Drawing.Bitmap", "int32", "int32"],
            "method": "GetPixel"
        },
        "set_pixel": {
            "return_type": "void",
            "params": [
                "class [System.Drawing]System.Drawing.Bitmap", 
                "int32", 
                "int32", 
                "valuetype [System.Drawing]System.Drawing.Color"
            ],
            "method": "SetPixel"
        },
        
        "to_color": {
            "return_type": "valuetype [System.Drawing]System.Drawing.Color",
            "params": ["int32", "int32", "int32"],
            "method": "ToColor"
        },
        
        "clamp": {
            "return_type": "int32",
            "params": ["int32", "int32", "int32"],
            "method": "Clamp"
        },
        
        "write": {
            "return_type": "void",
            "params": [],
            "method": "Write"
        },
        "read_int": {
            "return_type": "int32",
            "params": [],
            "method": "ReadInt"
        },
        "read_float": {
            "return_type": "float64",
            "params": [],
            "method": "ReadFloat"
        },
    }
    
    @classmethod
    def generate_builtin_call(cls, emitter: CILEmitter, func_name: str, 
                            arg_types: List[str] = None):
        """Генерирует вызов встроенной функции"""
        
        if func_name == "write":
            return cls._generate_write_call(emitter, arg_types)
        
        func_info = cls.BUILTIN_FUNCTIONS.get(func_name)
        if not func_info:
            raise ValueError(f"Unknown builtin function: {func_name}")
        
        params_str = ', '.join(func_info["params"])
        method_call = f'call {func_info["return_type"]} {cls.RUNTIME_CLASS}::{func_info["method"]}({params_str})'
        emitter.emit(method_call, f"call {func_name}")
        
        return func_info["return_type"]
    
    @classmethod
    def _generate_write_call(cls, emitter: CILEmitter, arg_types: List[str]):
        if not arg_types:
            return "void"
        
        for arg_type in arg_types:
            if arg_type == "int32":
                emitter.emit(f"call void {cls.RUNTIME_CLASS}::Write(int32)")
            elif arg_type == "float64":
                emitter.emit(f"call void {cls.RUNTIME_CLASS}::Write(float64)")
            elif arg_type == "string":
                emitter.emit(f"call void {cls.RUNTIME_CLASS}::Write(string)")
            elif arg_type == "bool":
                emitter.emit(f"call void {cls.RUNTIME_CLASS}::Write(bool)")
            else:
                emitter.emit(f"call void {cls.RUNTIME_CLASS}::Write(object)")
        
        return "void"
    
    @classmethod
    def generate_color_access(cls, emitter: CILEmitter, member: str):
        """Генерирует доступ к компонентам цвета"""
        
        if member.lower() == 'r':
            emitter.emit("call instance uint8 [System.Drawing]System.Drawing.Color::get_R()", "get R")
            emitter.emit("conv.i4", "convert byte to int")
        elif member.lower() == 'g':
            emitter.emit("call instance uint8 [System.Drawing]System.Drawing.Color::get_G()", "get G")
            emitter.emit("conv.i4", "convert byte to int")
        elif member.lower() == 'b':
            emitter.emit("call instance uint8 [System.Drawing]System.Drawing.Color::get_B()", "get B")
            emitter.emit("conv.i4", "convert byte to int")
        else:
            raise ValueError(f"Unknown color member: {member}")