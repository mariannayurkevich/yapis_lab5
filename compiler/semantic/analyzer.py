from typing import List, Optional
from errors.semantic import *
from errors.base import SourceLocation, InternalCompilerError
from parser.ast import *
from semantic.symbols import SymbolTable, SymbolKind, Symbol
from semantic.types import TypeSystem, TypeCompatibility

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.type_system = TypeSystem()
        self.errors: List[SemanticError] = []
        self.current_struct: Optional[Symbol] = None
        self.current_method: Optional[Symbol] = None
        self.return_type_stack: List[Type] = []
        
        self._register_builtins()

    def _add_error(self, error: SemanticError):
        """Регистрирует семантическую ошибку в списке"""
        self.errors.append(error)

    def _is_subtype(self, sub_type: Type, super_type: Type) -> bool:
        """Проверяет, является ли sub_type производным от super_type"""
        if sub_type.kind != TypeKind.STRUCT or super_type.kind != TypeKind.STRUCT:
            return False
            
        if sub_type.struct_name == super_type.struct_name:
            return True
            
        current_name = sub_type.struct_name
        while current_name:
            struct_sym = self.symbol_table.resolve_struct(current_name)
            if not struct_sym or not struct_sym.parent:
                break
            
            if struct_sym.parent == super_type.struct_name:
                return True
            current_name = struct_sym.parent
            
        return False

    def _register_builtins(self):
        """Добавляет стандартные функции в глобальную таблицу символов"""
        
        builtins = [
            ("load_image", [TypeKind.STRING], TypeKind.IMAGE),
            ("save_image", [TypeKind.IMAGE, TypeKind.STRING], TypeKind.VOID),
            ("create_image", [TypeKind.INT, TypeKind.INT], TypeKind.IMAGE),
            ("get_width", [TypeKind.IMAGE], TypeKind.INT),
            ("get_height", [TypeKind.IMAGE], TypeKind.INT),
            ("get_pixel", [TypeKind.IMAGE, TypeKind.INT, TypeKind.INT], TypeKind.PIXEL),
            ("set_pixel", [TypeKind.IMAGE, TypeKind.INT, TypeKind.INT, TypeKind.PIXEL], TypeKind.VOID),
            ("to_color", [TypeKind.INT, TypeKind.INT, TypeKind.INT], TypeKind.COLOR),
            ("clamp", [TypeKind.INT, TypeKind.INT, TypeKind.INT], TypeKind.INT),
            ("read_int", [], TypeKind.INT),
            ("read_float", [], TypeKind.FLOAT),
            ("write", None, TypeKind.VOID),
        ]

        for name, arg_kinds, ret_kind in builtins:
            func_symbol = self.symbol_table.define_symbol(
                name,
                SymbolKind.FUNCTION,
                Type(kind=ret_kind),
                None
            )
            
            if arg_kinds is not None:
                func_symbol.params = [
                    Symbol(f"p{i}", SymbolKind.PARAMETER, Type(kind=k), 0)
                    for i, k in enumerate(arg_kinds)
                ]
            else:
                func_symbol.params = None
    
    def analyze(self, program: Program) -> List[SemanticError]:
        self.errors = []
        try:
            self._collect_declarations(program)
            
            self._check_program(program)
            
        except Exception as e:
            self.errors.append(SemanticError(f"Internal error: {str(e)}", SourceLocation(1,1)))
        
        return self.errors
    
    def _collect_declarations(self, program: Program):
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self._collect_function(decl)
            elif isinstance(decl, StructDecl):
                self._collect_struct(decl)
    
    def _collect_function(self, func: FunctionDecl):
        func_symbol = self.symbol_table.define_symbol(
            func.name,
            SymbolKind.FUNCTION,
            func.return_type,
            func.source_info
        )
        
        func_symbol.params = []
        for param in func.params:
            param_symbol = Symbol(
                param.name,
                SymbolKind.PARAMETER,
                param.param_type,
                self.symbol_table.current_scope.level + 1
            )
            func_symbol.params.append(param_symbol)
        
        func_symbol.return_type = func.return_type
        func_symbol.is_virtual = "virtual" in func.modifiers
        func_symbol.is_override = "override" in func.modifiers
    
    def _collect_struct(self, struct: StructDecl):
        struct_symbol = self.symbol_table.define_symbol(
            struct.name,
            SymbolKind.STRUCT,
            Type(TypeKind.STRUCT, struct.name),
            struct.source_info
        )
        
        struct_symbol.parent = struct.parent
        struct_symbol.access = struct.access_modifier
        
        self.symbol_table.enter_scope()
        self.current_struct = struct_symbol
        
        for member in struct.members:
            if isinstance(member.decl, FieldDecl):
                self._collect_field(member.decl, member.access)
            elif isinstance(member.decl, MethodDecl):
                self._collect_method(member.decl, member.access)
        
        self.symbol_table.exit_scope()
        self.current_struct = None
    
    def _collect_field(self, field: FieldDecl, access: AccessModifier):
        field_symbol = self.symbol_table.define_symbol(
            field.name,
            SymbolKind.FIELD,
            field.field_type,
            field.source_info
        )
        field_symbol.access_modifier = access
        self.current_struct.fields[field.name] = field_symbol
    
    def _collect_method(self, method: MethodDecl, access: AccessModifier):
        method_symbol = self.symbol_table.define_symbol(
            method.name,
            SymbolKind.METHOD,
            method.return_type,
            method.source_info
        )
        method_symbol.access_modifier = access
        method_symbol.is_virtual = "virtual" in method.modifiers
        method_symbol.is_override = "override" in method.modifiers
        self.current_struct.methods[method.name] = method_symbol
    
    def _check_program(self, program: Program):
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self._check_function(decl)
            elif isinstance(decl, StructDecl):
                self._check_struct(decl)
        
        for stmt in program.statements:
            self._check_statement(stmt)
    
    def _check_function(self, func: FunctionDecl):
        self.symbol_table.enter_scope()
        self.return_type_stack.append(func.return_type)
        
        for param in func.params:
            self.symbol_table.define_symbol(
                param.name,
                SymbolKind.PARAMETER,
                param.param_type,
                param.source_info if hasattr(param, 'source_info') else None
            )
        
        self._check_block(func.body)
        
        if func.return_type.kind != TypeKind.VOID:
            pass
        
        self.return_type_stack.pop()
        self.symbol_table.exit_scope()
    
    def _check_struct(self, struct: StructDecl):
        if struct.parent:
            parent_symbol = self.symbol_table.resolve_struct(struct.parent)
            if not parent_symbol:
                self._add_error(UndefinedSymbolError(
                    struct.parent,
                    SourceLocation(struct.source_info.line, struct.source_info.column)
                ))
        
        self.symbol_table.enter_scope()
        self.current_struct = self.symbol_table.resolve_struct(struct.name)
        
        for member in struct.members:
            if isinstance(member.decl, MethodDecl):
                self._check_method(member.decl, member.access)
        
        self.symbol_table.exit_scope()
        self.current_struct = None
    
    def _check_method(self, method: MethodDecl, access: AccessModifier):
        self.symbol_table.enter_scope()
        self.return_type_stack.append(method.return_type)

        if self.current_struct:
            self.symbol_table.define_symbol(
                name="this",
                kind=SymbolKind.VARIABLE,
                symbol_type=Type(kind=TypeKind.STRUCT, struct_name=self.current_struct.name),
                source_info=method.source_info
            )
        for param in method.params:
            self.symbol_table.define_symbol(param.name, SymbolKind.PARAMETER, param.param_type, None)

        self._check_block(method.body)
        self.return_type_stack.pop()
        self.symbol_table.exit_scope()
    
    def _check_block(self, block: Block):
        self.symbol_table.enter_scope()
        
        for stmt in block.statements:
            self._check_statement(stmt)
        
        self.symbol_table.exit_scope()
    
    def _check_statement(self, stmt: Statement):
        if stmt is None: return

        if isinstance(stmt, VariableDecl):
            self._check_variable_decl(stmt)
        elif isinstance(stmt, Assignment):
            self._check_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            self._check_if_statement(stmt)
        elif isinstance(stmt, WhileLoop):
            self._check_while_loop(stmt)
        elif isinstance(stmt, ForLoop):
            self._check_for_loop(stmt)
        elif isinstance(stmt, ReturnStatement):
            self._check_return_statement(stmt)
        elif isinstance(stmt, ExpressionStatement):
            self._check_expression(stmt.expr)
        elif isinstance(stmt, DoUntilLoop):
            self._check_do_until_loop(stmt)
        elif isinstance(stmt, Block):
            self._check_block(stmt)
    
    def _check_do_until_loop(self, stmt: DoUntilLoop):
        self._check_block(stmt.body)
        cond_type = self._check_expression(stmt.condition)
        if cond_type and cond_type.kind != TypeKind.BOOL:
            self._add_error(TypeMismatchError("bool", str(cond_type), self._get_loc(stmt.condition)))

    def _check_variable_decl(self, decl: VariableDecl):
        for var_entry in decl.variables:
            if self.symbol_table.current_scope.resolve_local(var_entry.name):
                self._add_error(RedeclarationError(
                    var_entry.name,
                    SourceLocation(decl.source_info.line, decl.source_info.column)
                ))
                continue
            
            self.symbol_table.define_symbol(
                name=var_entry.name,
                kind=SymbolKind.VARIABLE,
                symbol_type=decl.var_type,
                source_info=decl.source_info
            )
            
            if var_entry.initializer:
                init_type = self._check_expression(var_entry.initializer)
                if init_type:
                    self._check_type_compatibility(decl.var_type, init_type, var_entry.initializer)
    
    def _check_assignment(self, assign: Assignment):
        if isinstance(assign.target, VariableExpr):
            var_symbol = self.symbol_table.resolve(assign.target.name)
            if not var_symbol:
                self._add_error(UndefinedSymbolError(
                    assign.target.name,
                    SourceLocation(assign.source_info.line, assign.source_info.column)
                ))
                return
            
            target_type = var_symbol.type
        else:
            target_type = None
        
        value_type = self._check_expression(assign.value)
        if target_type and value_type:
            self._check_type_compatibility(target_type, value_type, assign.value)
    
    def _check_if_statement(self, stmt: IfStatement):
        cond_type = self._check_expression(stmt.condition)
        if cond_type and cond_type.kind != TypeKind.BOOL:
            self._add_error(TypeMismatchError(
                "bool",
                str(cond_type),
                SourceLocation(stmt.condition.source_info.line, stmt.condition.source_info.column)
            ))
        
        self._check_block(stmt.then_block)
        if stmt.else_block:
            self._check_block(stmt.else_block)
    
    def _check_while_loop(self, stmt: WhileLoop):
        cond_type = self._check_expression(stmt.condition)
        if cond_type and cond_type.kind != TypeKind.BOOL:
            self._add_error(TypeMismatchError(
                "bool",
                str(cond_type),
                SourceLocation(stmt.condition.source_info.line, stmt.condition.source_info.column)
            ))
        
        self._check_block(stmt.body)
    
    def _check_for_loop(self, stmt: ForLoop):
        self.symbol_table.enter_scope()
        
        if stmt.init:
            self._check_variable_decl(stmt.init)
        
        if stmt.condition:
            cond_type = self._check_expression(stmt.condition)
            if cond_type and cond_type.kind != TypeKind.BOOL:
                self._add_error(TypeMismatchError(
                    "bool",
                    str(cond_type),
                    SourceLocation(stmt.condition.source_info.line, stmt.condition.source_info.column)
                ))
        
        if stmt.update:
            self._check_assignment(stmt.update)
        
        self._check_block(stmt.body)
        
        self.symbol_table.exit_scope()
    
    def _check_return_statement(self, stmt: ReturnStatement):
        if not self.return_type_stack:
            self._add_error(SemanticError(
                "Return statement outside of function",
                SourceLocation(stmt.source_info.line, stmt.source_info.column)
            ))
            return
        
        expected_type = self.return_type_stack[-1]
        
        if stmt.value:
            actual_type = self._check_expression(stmt.value)
            if actual_type:
                self._check_type_compatibility(expected_type, actual_type, stmt.value)
        else:
            if expected_type.kind != TypeKind.VOID:
                self._add_error(InvalidReturnError(
                    str(expected_type),
                    "void",
                    SourceLocation(stmt.source_info.line, stmt.source_info.column)
                ))
    
    def _check_expression(self, expr: Expression) -> Optional[Type]:
        """
        Полная проверка выражений с установкой типов в узлы AST.
        Возвращает объект Type или None в случае ошибки.
        """
        if expr is None:
            return None

        if isinstance(expr, LiteralExpr):
            return expr.type

        if isinstance(expr, VariableExpr):
            symbol = self.symbol_table.resolve(expr.name)
            if symbol:
                expr.type = symbol.type 
                return symbol.type
            
            expr.type = symbol.type
            return expr.type

        elif isinstance(expr, BinaryExpr):
            left_type = self._check_expression(expr.left)
            right_type = self._check_expression(expr.right)
            
            if left_type and right_type:
                res_kind_str = self.type_system.get_operation_result_type(
                    expr.op, str(left_type), str(right_type)
                )
                
                if res_kind_str:
                    kind = TypeKind(res_kind_str)
                    expr.type = Type(kind=kind)
                    return expr.type
                else:
                    self._add_error(InvalidOperationError(
                        expr.op, f"{left_type} and {right_type}",
                        SourceLocation(expr.source_info.line, expr.source_info.column)
                    ))
            return None

        elif isinstance(expr, CallExpr):
            target_func = None
            
            if expr.receiver:
                receiver_type = self._check_expression(expr.receiver)
                
                if not receiver_type:
                    return None
                
                if receiver_type.kind != TypeKind.STRUCT:
                    self._add_error(SemanticError(f"Cannot call method on type {receiver_type}", self._get_loc(expr)))
                    return None
                
                struct_sym = self.symbol_table.resolve_struct(receiver_type.struct_name)
                if not struct_sym or expr.func_name not in struct_sym.methods:
                    self._add_error(UndefinedSymbolError(f"Method '{expr.func_name}' in struct '{receiver_type.struct_name}'", self._get_loc(expr)))
                    return None
                
                target_func = struct_sym.methods[expr.func_name]
            
            else:
                target_func = self.symbol_table.resolve_function(expr.func_name)
                
                if not target_func and self.current_struct:
                    if expr.func_name in self.current_struct.methods:
                        target_func = self.current_struct.methods[expr.func_name]
            
            if not target_func:
                self._add_error(UndefinedSymbolError(expr.func_name, self._get_loc(expr)))
                return None

            if target_func.params is None:
                for arg in expr.args:
                    self._check_expression(arg)
            else:
                for i, arg in enumerate(expr.args):
                    arg_type = self._check_expression(arg)
                    if i < len(target_func.params):
                        expected = target_func.params[i].type
                        if arg_type:
                            self._check_type_compatibility(expected, arg_type, arg)

            expr.type = target_func.type
            return expr.type

        elif isinstance(expr, CastExpr):
            actual_type = self._check_expression(expr.expr)
            expr.type = expr.target_type
            return expr.type

        elif isinstance(expr, UnaryExpr):
            inner_type = self._check_expression(expr.expr)
            if inner_type:
                if expr.op == '!' and inner_type.kind != TypeKind.BOOL:
                    self._add_error(TypeMismatchError("bool", str(inner_type), 
                        SourceLocation(expr.source_info.line, expr.source_info.column)))
                expr.type = inner_type
                return expr.type
            return None

        elif isinstance(expr, MemberAccessExpr):
            obj_type = self._check_expression(expr.obj)
            expr.obj.type = obj_type 
            
            if obj_type and obj_type.kind == TypeKind.STRUCT:
                struct_sym = self.symbol_table.resolve_struct(obj_type.struct_name)
                if struct_sym:
                    if expr.member in struct_sym.fields:
                        expr.type = struct_sym.fields[expr.member].type
                        return expr.type
                    if expr.member in struct_symbol.methods:
                        expr.type = struct_symbol.methods[expr.member].type
                        return expr.type

        elif isinstance(expr, ConstructorExpr):
            struct_symbol = self.symbol_table.resolve_struct(expr.struct_name)
            if not struct_symbol:
                self._add_error(UndefinedSymbolError(expr.struct_name, 
                    SourceLocation(expr.source_info.line, expr.source_info.column)))
                return None
            expr.type = Type(kind=TypeKind.STRUCT, struct_name=expr.struct_name)
            return expr.type

        return None
    
    def _get_loc(self, node: ASTNode) -> SourceLocation:
        if node.source_info:
            return SourceLocation(
                line=node.source_info.line, 
                column=node.source_info.column
            )
        return SourceLocation(0, 0)

    def _check_type_compatibility(self, expected: Type, actual: Type, context: ASTNode):
        compatibility = self.type_system.check_compatibility(str(expected), str(actual))
        
        if compatibility != TypeCompatibility.NONE:
            return

        if expected.kind == TypeKind.STRUCT and actual.kind == TypeKind.STRUCT:
            if self._is_subtype(actual, expected):
                return

        self._add_error(TypeMismatchError(
            str(expected),
            str(actual),
            SourceLocation(context.source_info.line, context.source_info.column)
        ))