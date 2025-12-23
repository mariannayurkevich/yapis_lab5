from typing import List, Dict, Optional, Any
from codegen.cil_emitter import CILEmitter, CILVariable
from codegen.cil_runtime import RuntimeCodeGenerator
from codegen.cil_types import CILTypeSystem
from parser.ast import *
from semantic.symbols import SymbolTable, SymbolKind
from errors.semantic import SemanticError

class CILGenerator:
    """Главный генератор CIL кода из AST"""
    
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.emitter = CILEmitter()
        self.current_scope = None
        self.current_method = None
        self.label_counter = 0
        
        self.variable_map: Dict[str, CILVariable] = {}
        self.method_map: Dict[str, Dict] = {}
        
    def generate(self, program: Program) -> str:
        self._collect_function_info(program)
        
        for decl in program.declarations:
            if isinstance(decl, StructDecl):
                struct_sym = self.symbol_table.resolve_struct(decl.name)
                fields_for_emitter = []
                for field_name, field_sym in struct_sym.fields.items():
                    cil_type, _ = CILTypeSystem.map_type(field_sym.type)
                    fields_for_emitter.append((cil_type, field_name))
                self.emitter.register_struct(decl.name, fields_for_emitter)

        for decl in program.declarations:
            if isinstance(decl, FunctionDecl) and not isinstance(decl, MethodDecl):
                self._generate_function(decl)
            elif isinstance(decl, StructDecl):
                for member in decl.members:
                    if isinstance(member.decl, MethodDecl):
                        method = member.decl
                        orig_name = method.name

                        has_this = any(p.name == "this" for p in method.params)
                        if not has_this:
                            this_param = Parameter(
                                name="this", 
                                param_type=Type(kind=TypeKind.STRUCT, struct_name=decl.name),
                                source_info=None
                            )
                            method.params.insert(0, this_param)
                        
                        self._generate_function(method, owner_struct=decl.name)
                        
                        method.name = orig_name

        self._generate_entry_point(program)
        return self.emitter.generate_code()
    
    def _collect_function_info(self, program: Program):
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl) and not isinstance(decl, MethodDecl):
                self.method_map[decl.name] = {
                    'return_type': decl.return_type,
                    'params': decl.params,
                    'is_struct_method': False
                }
            elif isinstance(decl, StructDecl):
                for member in decl.members:
                    if isinstance(member.decl, MethodDecl):
                        method = member.decl
                        full_name = f"{decl.name}::{method.name}"
                        self.method_map[full_name] = {
                            'return_type': method.return_type,
                            'params': method.params,
                            'is_struct_method': True,
                            'struct_name': decl.name
                        }
        
    def _generate_entry_point(self, program: Program):
        """Генерирует точку входа Main"""
        self.emitter.begin_method("Main", Type(TypeKind.VOID))
        
        for stmt in program.statements:
            self._generate_statement(stmt)
        
        self.emitter.return_instruction()
        self.emitter.end_method()
    
    def _generate_function(self, func: FunctionDecl, owner_struct: str = None):
        old_variable_map = self.variable_map.copy()
        
        is_virtual = "virtual" in func.modifiers or "override" in func.modifiers
        is_static = (owner_struct is None)
        
        self.emitter.begin_method(
            func.name, 
            func.return_type, 
            is_static=is_static, 
            owner_class=owner_struct,
            is_virtual=is_virtual
        )
        
        self.variable_map = {}
        arg_idx = 0 if is_static else 1

        for param in func.params:
            is_this = (param.name == "this")
            is_result = (param.kind == "result")
            
            if not is_this:
                self.emitter.add_parameter(param.param_type, param.name, is_result)
            
            var_index = self.emitter.declare_local(param.name, param.param_type, is_result)
            
            if is_this:
                self.emitter.load_argument(0)
            else:
                self.emitter.load_argument(arg_idx)
                arg_idx += 1
                
            self.emitter.store_local(var_index)
            cil_type, _ = CILTypeSystem.map_type(param.param_type, is_result)
            self.variable_map[param.name] = CILVariable(param.name, cil_type, "", var_index, is_reference=is_result)

        self._generate_block(func.body)
        
        if func.return_type.kind == TypeKind.VOID:
            self.emitter.return_instruction()
        elif not self._has_return_statement(func.body):
            self._generate_default_return(func.return_type)

        self.emitter.end_method()
        self.variable_map = old_variable_map
        
    def _has_return_statement(self, block: Block) -> bool:
        """Проверяет, есть ли в блоке оператор return"""
        for stmt in block.statements:
            if isinstance(stmt, ReturnStatement):
                return True
            if isinstance(stmt, IfStatement):
                if self._has_return_statement(stmt.then_block):
                    return True
                if stmt.else_block and self._has_return_statement(stmt.else_block):
                    return True
            elif isinstance(stmt, (WhileLoop, ForLoop)):
                if self._has_return_statement(stmt.body):
                    return True
        return False
    
    def _generate_default_return(self, return_type: Type):
        res_var = self.variable_map.get("res")
        
        if res_var:
            self.emitter.load_local(res_var.index)
            self.emitter.return_instruction(has_value=True)
        else:
            if return_type.kind == TypeKind.INT:
                self.emitter.load_constant(0, TypeKind.INT)
            elif return_type.kind == TypeKind.FLOAT:
                self.emitter.load_constant(0.0, TypeKind.FLOAT)
            elif return_type.kind == TypeKind.BOOL:
                self.emitter.load_constant(False, TypeKind.BOOL)
            elif return_type.kind == TypeKind.STRING:
                self.emitter.load_constant("", TypeKind.STRING)
            
            has_val = return_type.kind != TypeKind.VOID
            self.emitter.return_instruction(has_value=has_val)
    
    def _generate_block(self, block: Block):
        """Генерирует код для блока"""
        for stmt in block.statements:
            self._generate_statement(stmt)
    
    def _generate_statement(self, stmt: Statement):
        """Генерирует код для оператора"""
        if isinstance(stmt, VariableDecl):
            self._generate_variable_declaration(stmt)
        elif isinstance(stmt, Assignment):
            self._generate_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            self._generate_if_statement(stmt)
        elif isinstance(stmt, WhileLoop):
            self._generate_while_loop(stmt)
        elif isinstance(stmt, ForLoop):
            self._generate_for_loop(stmt)
        elif isinstance(stmt, DoUntilLoop):
            self._generate_do_until_loop(stmt)
        elif isinstance(stmt, ReturnStatement):
            self._generate_return_statement(stmt)
        elif isinstance(stmt, ExpressionStatement):
            self._generate_expression(stmt.expr)
            if stmt.expr.type and stmt.expr.type.kind != TypeKind.VOID:
                self.emitter.emit("pop", "discard expression value")
        else:
            raise NotImplementedError(f"Unsupported statement type: {type(stmt)}")
    
    def _generate_variable_declaration(self, decl: VariableDecl):
        for var_entry in decl.variables:
            var_index = self.emitter.declare_local(var_entry.name, decl.var_type)
            
            cil_type, net_type = CILTypeSystem.map_type(decl.var_type)
            var = CILVariable(var_entry.name, cil_type, net_type, var_index)
            self.variable_map[var_entry.name] = var

            if var_entry.initializer:
                self._generate_expression(var_entry.initializer)
                self.emitter.store_local(var_index)
            else:
                if decl.var_type.kind == TypeKind.STRUCT or decl.var_type.kind == TypeKind.IMAGE:
                    self.emitter.load_null()
                    self.emitter.store_local(var_index)
    
    def _generate_assignment(self, assign: Assignment):
        if isinstance(assign.target, MemberAccessExpr):
            obj_expr = assign.target.obj
            struct_name = None
            
            if obj_expr.type and obj_expr.type.struct_name:
                struct_name = obj_expr.type.struct_name
            
            if not struct_name and isinstance(obj_expr, VariableExpr):
                var_info = self.variable_map.get(obj_expr.name)
                if var_info:
                    struct_name = var_info.cil_type.replace("class Program/", "").replace("&", "")

            if not struct_name:
                raise ValueError(f"Could not determine struct type for assignment to {assign.target.member}")

            self._generate_expression(obj_expr)
            self._generate_expression(assign.value)
            
            struct_sym = self.symbol_table.resolve_struct(struct_name)
            field_sym = struct_sym.fields[assign.target.member]
            field_cil_type, _ = CILTypeSystem.map_type(field_sym.type)
            
            self.emitter.emit(f"stfld {field_cil_type} Program/{struct_name}::{assign.target.member}")
            return

        var = None
        if isinstance(assign.target, VariableExpr):
            var = self.variable_map.get(assign.target.name)

        if var and var.is_reference:
            self.emitter.load_argument(var.index)

        self._generate_expression(assign.value)
        
        if var:
            if var.is_reference:
                self.emitter.store_indirect(var.cil_type)
            else:
                self.emitter.store_local(var.index)
    
    def _generate_if_statement(self, stmt: IfStatement):
        """Генерирует код для if-else"""
        else_label = self.emitter.new_label("else")
        end_label = self.emitter.new_label("endif")
        
        self._generate_expression(stmt.condition)
        
        self.emitter.branch_if_false(else_label)
        
        self._generate_block(stmt.then_block)
        self.emitter.unconditional_branch(end_label)
        
        self.emitter.emit_label(else_label)
        if stmt.else_block:
            self._generate_block(stmt.else_block)
        
        self.emitter.emit_label(end_label)
    
    def _generate_while_loop(self, stmt: WhileLoop):
        """Генерирует код для while цикла"""
        start_label = self.emitter.new_label("while_start")
        end_label = self.emitter.new_label("while_end")
        
        self.emitter.emit_label(start_label)
        
        self._generate_expression(stmt.condition)
        self.emitter.branch_if_false(end_label)
        
        self._generate_block(stmt.body)
        self.emitter.unconditional_branch(start_label)
        
        self.emitter.emit_label(end_label)
    
    def _generate_for_loop(self, stmt: ForLoop):
        """Генерирует код for цикла"""
        start_label = self.emitter.new_label("for_start")
        end_label = self.emitter.new_label("for_end")
        
        if stmt.init:
            self._generate_variable_declaration(stmt.init)
        
        self.emitter.emit_label(start_label)
        
        if stmt.condition:
            self._generate_expression(stmt.condition)
            self.emitter.branch_if_false(end_label)
        
        self._generate_block(stmt.body)
        
        if stmt.update:
            self._generate_assignment(stmt.update)
        
        self.emitter.unconditional_branch(start_label)
        self.emitter.emit_label(end_label)
    
    def _generate_return_statement(self, stmt: ReturnStatement):
        """Генерирует код для return"""
        if stmt.value:
            self._generate_expression(stmt.value)
            self.emitter.return_instruction(has_value=True)
        else:
            self.emitter.return_instruction()
    
    def _generate_expression(self, expr: Expression) -> Optional[str]:
        """Генерирует код для выражения, возвращает тип результата"""
        if isinstance(expr, LiteralExpr):
            return self._generate_literal(expr)
        elif isinstance(expr, VariableExpr):
            return self._generate_variable_access(expr)
        elif isinstance(expr, BinaryExpr):
            return self._generate_binary_expression(expr)
        elif isinstance(expr, UnaryExpr):
            return self._generate_unary_expression(expr)
        elif isinstance(expr, CallExpr):
            return self._generate_function_call(expr)
        elif isinstance(expr, MemberAccessExpr):
            return self._generate_member_access(expr)
        elif isinstance(expr, ConstructorExpr):
            return self._generate_constructor(expr)
        elif isinstance(expr, DoUntilLoop):
            return self._generate_do_until_loop(expr)
        elif isinstance(expr, CastExpr):
            return self._generate_cast_expression(expr)
        else:
            raise NotImplementedError(f"Unsupported expression type: {type(expr)}")
        
    def _generate_cast_expression(self, expr: CastExpr) -> str:
        """Генерирует код для явного приведения типов"""
        self._generate_expression(expr.expr)
        
        target_kind = expr.target_type.kind
        
        if target_kind == TypeKind.INT:
            self.emitter.emit("conv.i4", "explicit cast to int32")
        elif target_kind == TypeKind.FLOAT:
            self.emitter.emit("conv.r8", "explicit cast to float64")
        elif target_kind == TypeKind.BOOL:
            self.emitter.emit("conv.i4", "cast to bool")
            
        return CILTypeSystem.map_type(expr.target_type)[0]
    
    def _generate_literal(self, expr: LiteralExpr) -> str:
        """Генерирует код для литерала"""
        self.emitter.load_constant(expr.value, expr.type.kind)
        return CILTypeSystem.map_type(expr.type)[0]
    
    def _generate_variable_access(self, expr: VariableExpr) -> str:
        """Генерирует код для доступа к переменной"""
        var = self.variable_map.get(expr.name)
        if not var:
            symbol = self.symbol_table.resolve(expr.name)
            if symbol:
                pass
            raise ValueError(f"Undefined variable: {expr.name}")
        
        if var.is_reference:
            self.emitter.load_argument(var.index)
            self.emitter.load_indirect(var.cil_type)
        else:
            self.emitter.load_local(var.index)
        
        return var.cil_type
    
    def _generate_do_until_loop(self, stmt: DoUntilLoop):
        """Генерирует код do-until цикла"""
        start_label = self.emitter.new_label("do_start")
        
        self.emitter.emit_label(start_label)
        
        self._generate_block(stmt.body)
        
        self._generate_expression(stmt.condition)
        
        self.emitter.branch_if_false(start_label)
    
    def _generate_binary_expression(self, expr: BinaryExpr) -> str:
        left_kind = expr.left.type.kind if expr.left.type else TypeKind.INT
        right_kind = expr.right.type.kind if expr.right.type else TypeKind.INT
        
        is_float_op = (left_kind == TypeKind.FLOAT or right_kind == TypeKind.FLOAT)

        self._generate_expression(expr.left)
        if is_float_op and left_kind == TypeKind.INT:
            self.emitter.emit("conv.r8", "promote left to float")

        self._generate_expression(expr.right)
        if is_float_op and right_kind == TypeKind.INT:
            self.emitter.emit("conv.r8", "promote right to float")

        if expr.op in ['==', '!=', '>', '<', '>=', '<=']:
            self.emitter.comparison_operation(expr.op)
            return "bool"
        elif expr.op in ['&&', '||']:
            instr = "and" if expr.op == '&&' else "or"
            self.emitter.emit(instr)
            return "bool"
        else:
            self.emitter.arithmetic_operation(expr.op, left_kind, right_kind)
            return "float64" if is_float_op else "int32"
    
    def _generate_unary_expression(self, expr: UnaryExpr) -> str:
        """Генерирует код для унарного выражения"""
        expr_type = self._generate_expression(expr.expr)
        
        if expr.op == '-':
            self.emitter.load_constant(0, TypeKind.INT)
            if expr.expr.type and CILTypeSystem.is_floating_point(expr.expr.type.kind):
                self.emitter.convert_to_float(TypeKind.INT)
                self.emitter.emit("sub", "unary minus")
            else:
                self.emitter.emit("sub", "unary minus")
        elif expr.op == '!':
            self.emitter.load_constant(1, TypeKind.INT)
            self.emitter.emit("xor", "logical not")
        
        return expr_type
    
    def _generate_function_call(self, expr: CallExpr) -> str:
        if expr.func_name in RuntimeCodeGenerator.BUILTIN_FUNCTIONS:
            if expr.func_name == "write":
                for arg in expr.args:
                    arg_type = self._generate_expression(arg)
                    RuntimeCodeGenerator.generate_builtin_call(self.emitter, "write", [arg_type])
                return "void"
            arg_types = [self._generate_expression(arg) for arg in expr.args]
            return RuntimeCodeGenerator.generate_builtin_call(self.emitter, expr.func_name, arg_types)

        target_name = expr.func_name
        if expr.receiver and expr.receiver.type and expr.receiver.type.struct_name:
            target_name = f"{expr.receiver.type.struct_name}::{expr.func_name}"

        func_info = self.method_map.get(target_name)
        if not func_info:
            func_info = self.method_map.get(expr.func_name)

        if not func_info:
            raise ValueError(f"Undefined function: {target_name}")


        is_instance = func_info.get('is_struct_method', False)

        if is_instance:
            if expr.receiver:
                self._generate_expression(expr.receiver)
            else:
                this_var = self.variable_map.get("this")
                self.emitter.load_local(this_var.index)

        sig_params = []
        for i, p in enumerate(func_info['params']):
            if p.name == "this":
                continue
                
            arg_idx = func_info['params'].index(p)
            if is_instance: arg_idx -= 1
            
            arg_expr = expr.args[arg_idx]

            if p.kind == "result":
                if isinstance(arg_expr, VariableExpr):
                    var_info = self.variable_map.get(arg_expr.name)
                    if var_info:
                        if var_info.is_local:
                            self.emitter.load_local_address(var_info.index)
                        else:
                            self.emitter.load_argument_address(var_info.index)
                    else:
                        raise ValueError(f"Variable {arg_expr.name} not found for result parameter")
                else:
                    raise ValueError("Only variables can be passed to 'result' parameters")
            else:
                self._generate_expression(arg_expr)
            
            cil_t, _ = CILTypeSystem.map_type(p.param_type, p.kind == "result")
            sig_params.append(cil_t)

        ret_type = CILTypeSystem.map_type(func_info['return_type'])[0]
        params_sig = ", ".join(sig_params)
        
        if is_instance:
            struct_name = func_info['struct_name']
            self.emitter.emit(f"callvirt instance {ret_type} Program/{struct_name}::{expr.func_name}({params_sig})")
        else:
            self.emitter.emit(f"call {ret_type} Program::{expr.func_name}({params_sig})")

        return ret_type
        
    def _generate_member_access(self, expr: MemberAccessExpr) -> str:
        obj_type_str = self._generate_expression(expr.obj)
        
        if expr.obj.type and expr.obj.type.kind in [TypeKind.COLOR, TypeKind.PIXEL]:
            temp_idx = self.emitter.declare_local("tmp_col_access", expr.obj.type)
            self.emitter.store_local(temp_idx)
            self.emitter.load_local_address(temp_idx)
            
            member = expr.member.lower()
            if member == 'r': self.emitter.emit("call instance uint8 [System.Drawing]System.Drawing.Color::get_R()")
            elif member == 'g': self.emitter.emit("call instance uint8 [System.Drawing]System.Drawing.Color::get_G()")
            elif member == 'b': self.emitter.emit("call instance uint8 [System.Drawing]System.Drawing.Color::get_B()")
            self.emitter.emit("conv.i4")
            return "int32"
        
        if expr.obj.type and expr.obj.type.kind == TypeKind.STRUCT:
            struct_name = expr.obj.type.struct_name
            struct_sym = self.symbol_table.resolve_struct(struct_name)
            
            if struct_sym and expr.member in struct_sym.fields:
                field_sym = struct_sym.fields[expr.member]
                field_cil_type, _ = CILTypeSystem.map_type(field_sym.type)
                
                self.emitter.emit(f"ldfld {field_cil_type} Program/{struct_name}::{expr.member}")
                return field_cil_type
            else:
                self.emitter.emit(f"ldfld int32 Program/{struct_name}::{expr.member}")
                return "int32"

        return "int32"
    
    def _generate_constructor(self, expr: ConstructorExpr) -> str:
        struct_name = expr.struct_name
        
        self.emitter.emit(f"newobj instance void Program/{struct_name}::.ctor()")
        
        self.emitter.emit("dup")
        
        target_full_name = f"{struct_name}::{struct_name}"
        func_info = self.method_map.get(target_full_name)
        
        if func_info:
            for i, arg in enumerate(expr.args):
                param_info = func_info['params'][i + 1]
                if param_info.kind == "result":
                    var = self.variable_map.get(arg.name)
                    if var.is_local: self.emitter.load_local_address(var.index)
                    else: self.emitter.load_argument_address(var.index)
                else:
                    self._generate_expression(arg)
            
            params_cil = []
            for p in func_info['params']:
                if p.name != "this":
                    cil_t, _ = CILTypeSystem.map_type(p.param_type, p.kind == "result")
                    params_cil.append(cil_t)
            
            sig = ", ".join(params_cil)
            
            self.emitter.emit(f"call instance void Program/{struct_name}::{struct_name}({sig})")
        else:
            self.emitter.emit("pop")
            
        return f"class Program/{struct_name}"