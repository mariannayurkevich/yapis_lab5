from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from codegen.cil_types import CILTypeSystem
from parser.ast import Type, TypeKind

@dataclass
class CILVariable:
    """Информация о переменной CIL"""
    name: str
    cil_type: str
    net_type: str
    index: int
    is_local: bool = True
    is_reference: bool = False
    initialized: bool = False

@dataclass
class CILMethod:
    name: str
    return_type: str
    parameters: List[Tuple[str, str]]
    is_static: bool = True
    is_public: bool = True
    is_virtual: bool = False
    owner_class: str = None
    max_stack: int = 50
    locals: List[CILVariable] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict) 

class CILEmitter:
    """Низкоуровневый генератор инструкций CIL"""
    
    def __init__(self):
        self.current_method: Optional[CILMethod] = None
        self.methods: List[CILMethod] = []
        self.class_name: str = "Program"
        
        self.assembly_refs: List[str] = []
        
        self.struct_definitions: Dict[str, List[Tuple[str, str]]] = {}
        
        self._label_counter: int = 0
        self._local_counter: int = 0
        
        self.add_assembly_ref("mscorlib", 
                             "B7 7A 5C 56 19 34 E0 89", 
                             "4:0:0:0")
        self.add_assembly_ref("System.Drawing",
                             "B0 3F 5F 7F 11 D5 0A 3A",
                             "4:0:0:0")
        self.add_assembly_ref("ImgLangRuntime", "", "")
    
    def add_assembly_ref(self, name: str, public_key_token: str, version: str):
        """Добавляет ссылку на сборку"""
        ref = f'.assembly extern {name} {{\n'
        if public_key_token:
            ref += f'  .publickeytoken = ( {public_key_token} )\n'
        if version:
            ref += f'  .ver {version}\n'
        ref += '}'
        self.assembly_refs.append(ref)
    
    def begin_method(self, name: str, return_type: Type, is_static: bool = True, 
                     owner_class: str = None, is_virtual: bool = False):
        self.current_method = CILMethod(
            name=name,
            return_type=CILTypeSystem.map_type(return_type)[0],
            parameters=[],
            is_static=is_static,
            is_public=True,
            is_virtual=is_virtual,
            owner_class=owner_class
        )
        self._local_counter = 0
        self._label_counter = 0
    
    def end_method(self):
        """Завершает генерацию метода"""
        if self.current_method:
            self.methods.append(self.current_method)
            self.current_method = None
    
    def add_parameter(self, param_type: Type, name: str, is_ref: bool = False):
        """Добавляет параметр к текущему методу"""
        if not self.current_method:
            return
        
        cil_type, _ = CILTypeSystem.map_type(param_type, is_ref)
        self.current_method.parameters.append((cil_type, name))

    def register_struct(self, name: str, fields: List[Tuple[str, str]]):
        self.struct_definitions[name] = fields
    
    def declare_local(self, name: str, var_type: Type, is_ref: bool = False) -> int:
        """Объявляет локальную переменную и возвращает её индекс"""
        if not self.current_method:
            return -1
        
        cil_type, net_type = CILTypeSystem.map_type(var_type, is_ref)
        var = CILVariable(
            name=name,
            cil_type=cil_type,
            net_type=net_type,
            index=self._local_counter,
            is_local=True,
            is_reference=is_ref
        )
        
        self.current_method.locals.append(var)
        self._local_counter += 1
        return var.index
    
    def emit(self, instruction: str, comment: str = ""):
        """Добавляет инструкцию CIL"""
        if not self.current_method:
            return
        
        if comment:
            instruction = f"{instruction} // {comment}"
        self.current_method.instructions.append(instruction)
    
    def emit_label(self, label: str):
        """Добавляет метку"""
        if not self.current_method:
            return
        
        self.current_method.instructions.append(f"{label}:")
        self.current_method.labels[label] = label
    
    def new_label(self, prefix: str = "L") -> str:
        """Создаёт новую уникальную метку"""
        self._label_counter += 1
        return f"{prefix}_{self._label_counter}"
    
    def load_constant(self, value: Any, value_type: TypeKind):
        """Загружает константу на стек"""
        if value_type == TypeKind.INT:
            if value == 0:
                self.emit("ldc.i4.0", f"load {value}")
            elif value == 1:
                self.emit("ldc.i4.1", f"load {value}")
            elif value == 2:
                self.emit("ldc.i4.2", f"load {value}")
            elif value == 3:
                self.emit("ldc.i4.3", f"load {value}")
            elif value == 4:
                self.emit("ldc.i4.4", f"load {value}")
            elif value == 5:
                self.emit("ldc.i4.5", f"load {value}")
            elif value == 6:
                self.emit("ldc.i4.6", f"load {value}")
            elif value == 7:
                self.emit("ldc.i4.7", f"load {value}")
            elif value == 8:
                self.emit("ldc.i4.8", f"load {value}")
            elif -128 <= value <= 127:
                self.emit(f"ldc.i4.s {value}", f"load {value}")
            else:
                self.emit(f"ldc.i4 {value}", f"load {value}")
        
        elif value_type == TypeKind.FLOAT:
            float_val = float(value)
            self.emit(f"ldc.r8 {float_val}", f"load {value}")
        
        elif value_type == TypeKind.BOOL:
            if value:
                self.emit("ldc.i4.1", "load true")
            else:
                self.emit("ldc.i4.0", "load false")
        
        elif value_type == TypeKind.STRING:
            self.emit(f'ldstr "{value}"', f'load "{value}"')
    
    def load_argument(self, index: int):
        if index <= 3:
            instruction = f"ldarg.{index}"
        else:
            instruction = f"ldarg.s {index}"
        self.emit(instruction, f"load arg {index}")
    
    def load_local(self, index: int):
        """Загружает локальную переменную на стек"""
        instruction = CILTypeSystem.get_ldloc_instruction(index)
        self.emit(instruction, f"load local {index}")
    
    def load_local_address(self, index: int):
        """Загружает адрес локальной переменной на стек"""
        self.emit(f"ldloca {index}", f"load address of local {index}")
    
    def load_argument_address(self, index: int):
        """Загружает адрес аргумента на стек"""
        self.emit(f"ldarga {index}", f"load address of arg {index}")
    
    def store_local(self, index: int):
        if index <= 3:
            instruction = f"stloc.{index}"
        else:
            instruction = f"stloc.s {index}"
        self.emit(instruction, f"store to local {index}")
    
    def store_indirect(self, cil_type: str):
        """Сохраняет значение по адресу (для ref параметров)"""
        if "class" in cil_type or "Bitmap" in cil_type:
            self.emit("stind.ref", "store indirect (ref)")
        elif "int32" in cil_type:
            self.emit("stind.i4", "store indirect (int32)")
        elif "float64" in cil_type:
            self.emit("stind.r8", "store indirect (float64)")
        elif "bool" in cil_type:
            self.emit("stind.i1", "store indirect (bool)")
        else:
            self.emit(f"stobj {cil_type.replace('&', '')}", f"store indirect ({cil_type})")
    
    def load_indirect(self, cil_type: str):
        """Загружает значение по адресу (для ref параметров)"""
        if "class" in cil_type or "Bitmap" in cil_type:
            self.emit("ldind.ref", "load indirect (ref)")
        elif "int32" in cil_type:
            self.emit("ldind.i4", "load indirect (int32)")
        elif "float64" in cil_type:
            self.emit("ldind.r8", "load indirect (float64)")
        elif "bool" in cil_type:
            self.emit("ldind.i1", "load indirect (bool)")
        else:
            self.emit(f"ldobj {cil_type.replace('&', '')}", f"load indirect ({cil_type})")
    
    def arithmetic_operation(self, operator: str, left_kind: TypeKind, right_kind: TypeKind):
        """Генерирует арифметическую операцию без дублирования"""
        instruction = CILTypeSystem.get_arithmetic_instruction(operator)
        if instruction:
            self.emit(instruction, f"arithmetic {operator}")


    def comparison_operation(self, operator: str):
        """Генерирует операцию сравнения"""
        instruction = CILTypeSystem.get_comparison_instruction(operator)
        
        if callable(instruction):
            for instr in instruction():
                self.emit(instr)
        else:
            self.emit(instruction, f"compare {operator}")
    
    def convert_to_float(self, type_kind: TypeKind):
        """Конвертирует значение на стеке в float64 если нужно"""
        if CILTypeSystem.is_integer(type_kind):
            self.emit("conv.r8", "convert int to float")
    
    def convert_to_int(self, type_kind: TypeKind):
        """Конвертирует значение на стеке в int32 если нужно"""
        if CILTypeSystem.is_floating_point(type_kind):
            self.emit("conv.i4", "convert float to int")
    
    def call_method(self, method_name: str, return_type: str, 
                    class_name: str = None, is_instance: bool = False):
        """Генерирует вызов метода"""
        if class_name:
            if is_instance:
                self.emit(f"call instance {return_type} {class_name}::{method_name}()", 
                         f"call instance method {method_name}")
            else:
                self.emit(f"call {return_type} {class_name}::{method_name}()", 
                         f"call static method {method_name}")
        else:
            self.emit(f"call {return_type} {method_name}()", 
                     f"call method {method_name}")
    
    def new_object(self, class_name: str):
        """Создаёт новый объект"""
        self.emit(f"newobj instance void {class_name}::.ctor()", 
                 f"new {class_name}")
    
    def return_instruction(self, has_value: bool = False):
        """Генерирует инструкцию возврата"""
        if has_value:
            self.emit("ret", "return with value")
        else:
            self.emit("ret", "return")
    
    def branch_if_false(self, label: str):
        """Переход если false (0)"""
        self.emit(f"brfalse {label}", f"branch if false to {label}")
    
    def branch_if_true(self, label: str):
        """Переход если true (не 0)"""
        self.emit(f"brtrue {label}", f"branch if true to {label}")
    
    def unconditional_branch(self, label: str):
        """Безусловный переход"""
        self.emit(f"br {label}", f"branch to {label}")
    
    def generate_code(self) -> str:
        code_lines = []
        code_lines.extend(self.assembly_refs)
        code_lines.append('.assembly Program {}')
        code_lines.append(f'.class public auto ansi beforefieldinit {self.class_name} extends [mscorlib]System.Object {{')
        code_lines.append('  .method public hidebysig specialname rtspecialname instance void .ctor() cil managed { ldarg.0; call instance void [mscorlib]System.Object::.ctor(); ret }')

        for struct_name, fields in self.struct_definitions.items():
            code_lines.append(f'  .class nested public auto ansi beforefieldinit {struct_name} extends [mscorlib]System.Object {{')
            for f_type, f_name in fields:
                code_lines.append(f'    .field public {f_type} {f_name}')
            code_lines.append('    .method public hidebysig specialname rtspecialname instance void .ctor() cil managed { ldarg.0; call instance void [mscorlib]System.Object::.ctor(); ret }')
            
            struct_methods = [m for m in self.methods if m.owner_class == struct_name]
            for m in struct_methods:
                self._emit_method_body(code_lines, m, indent="    ")
            code_lines.append('  }')

        global_methods = [m for m in self.methods if m.owner_class is None]
        for m in global_methods:
            self._emit_method_body(code_lines, m, indent="  ")
        
        code_lines.append('}')
        return '\n'.join(code_lines)
    
    def _emit_method_body(self, code_lines, method, indent):
        params_str = ', '.join([p[0] for p in method.parameters])
        static_str = "static" if method.is_static else "instance"
        virt_str = "virtual hidebysig" if method.is_virtual else ""
        
        code_lines.append(f'{indent}.method public {virt_str} {static_str} {method.return_type} {method.name}({params_str}) cil managed {{')
        if method.name == "Main":
            code_lines.append(f'{indent}  .entrypoint')
        code_lines.append(f'{indent}  .maxstack {method.max_stack}')
        if method.locals:
            locals_str = ', '.join([f'{var.cil_type} V_{var.index}' for var in method.locals])
            code_lines.append(f'{indent}  .locals init ({locals_str})')
        for instr in method.instructions:
            code_lines.append(f'{indent}  {instr}')
        code_lines.append(f'{indent}}}')
    
    def _write_method_body(self, code_lines, method, is_nested=False):
        params_str = ', '.join([p[0] for p in method.parameters])
        visibility = "public"
        
        virt = "virtual hidebysig" if method.is_virtual else ""
        call_conv = "instance" if not method.is_static else ""
        
        indent = "    " if is_nested else "  "
        code_lines.append(f'{indent}.method {visibility} {virt} {call_conv} {method.return_type} {method.name}({params_str}) cil managed {{')
        
        if method.name == "Main":
            code_lines.append(f'{indent}  .entrypoint')
        
        code_lines.append(f'{indent}  .maxstack {method.max_stack}')
        if method.locals:
            locals_str = ', '.join([f'{var.cil_type} V_{var.index}' for var in method.locals])
            code_lines.append(f'{indent}  .locals init ({locals_str})')
        
        for instr in method.instructions:
            code_lines.append(f'{indent}  {instr}')
        code_lines.append(f'{indent}}}')
    
    def load_null(self):
        """Загружает null на стек для ссылочных типов"""
        self.emit("ldnull")