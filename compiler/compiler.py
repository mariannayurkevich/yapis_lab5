import sys
from antlr4 import *
from antlr.ImgLangLexer import ImgLangLexer
from antlr.ImgLangParser import ImgLangParser
from antlr.ImgLangVisitor import ImgLangVisitor

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
        self.locals_count = 0
        self.arg_count = 0
        self.local_definitions = [] 

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def reset_for_method(self):
        self.scopes = [{}]
        self.locals_count = 0
        self.arg_count = 0
        self.local_definitions = []

    def define_arg(self, name, var_type, is_ref=False):
        idx = self.arg_count
        self.arg_count += 1
        cil_type = self.map_type(var_type)
        if is_ref: cil_type += "&"
        self.scopes[-1][name] = {"index": idx, "type": cil_type, "kind": "arg", "is_ref": is_ref}
        return idx, cil_type

    def define_local(self, name, var_type):
        idx = self.locals_count
        self.locals_count += 1
        cil_type = self.map_type(var_type)
        self.scopes[-1][name] = {"index": idx, "type": cil_type, "kind": "loc", "is_ref": False}
        self.local_definitions.append(f"{cil_type} V_{idx}")
        return idx

    def resolve(self, name):
        for scope in reversed(self.scopes):
            if name in scope: return scope[name]
        return None

    def map_type(self, var_type):
        if var_type == "image": return "class [System.Drawing]System.Drawing.Bitmap"
        if var_type in ["color", "pixel"]: return "valuetype [System.Drawing]System.Drawing.Color"
        if var_type == "string": return "string"
        if var_type == "float": return "float64"
        if var_type == "bool": return "bool"
        return "int32"

class PrePassVisitor(ImgLangVisitor):
    def __init__(self):
        self.signatures = {} 

    def visitFunctionDecl(self, ctx):
        func_name = ctx.ID().getText()
        ret_type = "void"
        
        full_text = ctx.getText()
        if "int res" in full_text or "res =" in full_text or "res=" in full_text:
            ret_type = "int32"

        arg_types = []
        arg_kinds = [] 

        if ctx.parameterList():
            for param in ctx.parameterList().parameter():
                p_kind = "result" if param.getChild(0).getText() == "result" else "value"
                p_type = param.type_().getText()
                cil_type = self.map_type(p_type)
                if p_kind == "result": cil_type += "&"
                arg_types.append(cil_type)
                arg_kinds.append(p_kind)

        self.signatures[func_name] = {
            "ret": ret_type,
            "args": arg_types,
            "kinds": arg_kinds
        }

    def map_type(self, var_type):
        if var_type == "image": return "class [System.Drawing]System.Drawing.Bitmap"
        if var_type in ["color", "pixel"]: return "valuetype [System.Drawing]System.Drawing.Color"
        if var_type == "string": return "string"
        if var_type == "float": return "float64"
        if var_type == "bool": return "bool"
        return "int32"

class Compiler(ImgLangVisitor):
    def __init__(self, signatures):
        self.cil_code = []
        self.symbols = SymbolTable()
        self.signatures = signatures
        self.label_counter = 0
        self.main_buffer = [] 
        self.proc_buffer = [] 
        self.current_buffer = self.main_buffer 
        self.last_type = "void"

    def emit(self, instr):
        self.current_buffer.append("    " + instr)

    def new_label(self):
        self.label_counter += 1
        return f"L_{self.label_counter}"

    def visitProgram(self, ctx):
        headers = []
        headers.append(".assembly extern mscorlib { .publickeytoken = (B7 7A 5C 56 19 34 E0 89 ) .ver 4:0:0:0 }")
        headers.append(".assembly extern System.Drawing { .publickeytoken = (B0 3F 5F 7F 11 D5 0A 3A ) .ver 4:0:0:0 }")
        headers.append(".assembly extern ImgLangRuntime {}")
        headers.append(".assembly Program {}")
        headers.append(".class public auto ansi beforefieldinit Program extends [mscorlib]System.Object {")
        
        self.current_buffer = self.main_buffer
        self.emit(".method public static void Main() cil managed {")
        self.emit(".entrypoint")
        self.emit(".maxstack 50")
        
        for child in ctx.children:
            if isinstance(child, ImgLangParser.FunctionDeclContext):
                saved_buffer = self.current_buffer
                self.current_buffer = self.proc_buffer
                self.visit(child) 
                self.current_buffer = saved_buffer 
            elif isinstance(child, ImgLangParser.StatementContext):
                self.visit(child)
        
        self.current_buffer = self.main_buffer
        self.emit("ret")
        self.emit("}") 
        
        if self.symbols.local_definitions:
            locals_decl = "    .locals init (" + ", ".join(self.symbols.local_definitions) + ")"
            for i, line in enumerate(self.main_buffer):
                if ".maxstack" in line:
                    self.main_buffer.insert(i + 1, locals_decl)
                    break

        final_code = headers + self.proc_buffer + self.main_buffer + ["}"]
        return "\n".join(final_code)

    def visitFunctionDecl(self, ctx):
        func_name = ctx.ID().getText()
        sig = self.signatures.get(func_name, {"ret": "void", "args": []})
        ret_type = sig["ret"]
        
        self.symbols.reset_for_method()
        
        if ctx.parameterList():
            for i, param in enumerate(ctx.parameterList().parameter()):
                p_name = param.ID().getText()
                p_type = param.type_().getText()
                p_is_ref = (sig["kinds"][i] == "result")
                self.symbols.define_arg(p_name, p_type, p_is_ref)
                
        sig_args_str = ", ".join(sig["args"])
        self.emit(f".method public static {ret_type} {func_name}({sig_args_str}) cil managed {{")
        self.emit(".maxstack 50")
        
        self.visit(ctx.block())
        
        if ret_type == "int32":
            info = self.symbols.resolve("res")
            if info: self.emit(f"ldloc {info['index']}")
            else: self.emit("ldc.i4.0")
        
        self.emit("ret")
        self.emit("}")

        if self.symbols.local_definitions:
            locals_decl = "    .locals init (" + ", ".join(self.symbols.local_definitions) + ")"
            for i, line in enumerate(self.proc_buffer):
                decl_str = f"method public static {ret_type} {func_name}"
                if ".maxstack" in line and any(decl_str in prev for prev in self.proc_buffer[max(0, i-2):i]):
                     self.proc_buffer.insert(i + 1, locals_decl)
                     break

    def visitStatement(self, ctx):
        if ctx.variableDecl(): self.visit(ctx.variableDecl())
        elif ctx.assignment(): self.visit(ctx.assignment())
        elif ctx.forLoop(): self.visit(ctx.forLoop())
        elif ctx.whileLoop(): self.visit(ctx.whileLoop())
        elif ctx.doUntilLoop(): self.visit(ctx.doUntilLoop())
        elif ctx.ifStatement(): self.visit(ctx.ifStatement())
        elif ctx.functionCall(): self.visit(ctx.functionCall())
        elif ctx.expression(): self.visit(ctx.expression())

    def visitVariableDecl(self, ctx):
        var_type = ctx.type_().getText()
        for var_entry in ctx.variableList().variableEntry():
            name = var_entry.ID().getText()
            self.symbols.define_local(name, var_type)
            if var_entry.expression():
                self.visit(var_entry.expression())
                info = self.symbols.resolve(name)
                self.emit(f"stloc {info['index']}")

    def visitSingleAssign(self, ctx):
        name = ctx.ID().getText()
        info = self.symbols.resolve(name)
        if info and info['is_ref']:
            self.emit(f"ldarg {info['index']}")
            self.visit(ctx.expression())
            t = info['type'].replace("&", "")
            if "Bitmap" in t or "class" in t: self.emit("stind.ref")
            elif "int32" in t: self.emit("stind.i4")
            elif "float64" in t: self.emit("stind.r8")
            else: self.emit(f"stobj {t}")
        else:
            self.visit(ctx.expression())
            if info:
                if info['kind'] == 'loc': self.emit(f"stloc {info['index']}")
                else: self.emit(f"starg {info['index']}")

    def visitMultiAssign(self, ctx):
        names = [x.getText() for x in ctx.idList().ID()]
        exprs = ctx.exprList().expression()
        for expr in exprs: self.visit(expr)
        for name in reversed(names):
            info = self.symbols.resolve(name)
            if info:
                if info['kind'] == 'loc': self.emit(f"stloc {info['index']}")
                else: self.emit(f"starg {info['index']}")

    def visitIfStatement(self, ctx):
        else_lbl = self.new_label()
        end_lbl = self.new_label()
        self.visit(ctx.expression())
        self.emit(f"brfalse {else_lbl}")
        self.visit(ctx.block(0))
        self.emit(f"br {end_lbl}")
        self.emit(f"{else_lbl}:")
        if len(ctx.block()) > 1: self.visit(ctx.block(1))
        self.emit(f"{end_lbl}:")

    def visitForLoop(self, ctx):
        start_lbl = self.new_label()
        end_lbl = self.new_label()
        self.symbols.enter_scope()
        self.visit(ctx.forInit())
        self.emit(f"{start_lbl}:")
        self.visit(ctx.forCondition())
        self.emit(f"brfalse {end_lbl}")
        self.visit(ctx.block())
        self.visit(ctx.forUpdate())
        self.emit(f"br {start_lbl}")
        self.emit(f"{end_lbl}:")
        self.symbols.exit_scope()
        
    def visitForInit(self, ctx):
        if ctx.type_():
            var_type = ctx.type_().getText()
            name = ctx.ID().getText()
            self.symbols.define_local(name, var_type)
            self.visit(ctx.expression())
            info = self.symbols.resolve(name)
            self.emit(f"stloc {info['index']}")

    def visitForUpdate(self, ctx):
        name = ctx.ID().getText()
        self.visit(ctx.expression())
        info = self.symbols.resolve(name)
        if info: self.emit(f"stloc {info['index']}")

    def visitWhileLoop(self, ctx):
        start_lbl = self.new_label()
        end_lbl = self.new_label()
        self.emit(f"{start_lbl}:")
        self.visit(ctx.expression()) 
        self.emit(f"brfalse {end_lbl}")
        self.visit(ctx.block())
        self.emit(f"br {start_lbl}")
        self.emit(f"{end_lbl}:")

    def visitDoUntilLoop(self, ctx):
        start_lbl = self.new_label()
        self.emit(f"{start_lbl}:")
        self.visit(ctx.block())
        self.visit(ctx.expression())
        self.emit(f"brfalse {start_lbl}")

    def visitIntExpr(self, ctx): 
        self.emit(f"ldc.i4 {ctx.INT().getText()}")
        self.last_type = "int32"
    def visitFloatExpr(self, ctx): 
        self.emit(f"ldc.r8 {ctx.FLOAT().getText()}")
        self.last_type = "float64"
    def visitStringExpr(self, ctx): 
        self.emit(f"ldstr {ctx.STRING().getText()}")
        self.last_type = "string"
    def visitBoolExpr(self, ctx): 
        val = 1 if ctx.getText() == 'true' else 0
        self.emit(f"ldc.i4.{val}")
        self.last_type = "int32"
    def visitTrueExpr(self, ctx): 
        self.emit("ldc.i4.1")
        self.last_type = "int32"
    def visitFalseExpr(self, ctx): 
        self.emit("ldc.i4.0")
        self.last_type = "int32"

    def visitVarExpr(self, ctx):
        name = ctx.ID().getText()
        info = self.symbols.resolve(name)
        if info:
            if info['is_ref']:
                self.emit(f"ldarg {info['index']}")
                t = info['type'].replace("&", "")
                if "Bitmap" in t or "class" in t: self.emit("ldind.ref")
                elif "int32" in t: self.emit("ldind.i4")
                elif "float64" in t: self.emit("ldind.r8")
                else: self.emit(f"ldobj {t}")
            elif info['kind'] == 'loc': self.emit(f"ldloc {info['index']}")
            else: self.emit(f"ldarg {info['index']}")
            
            t_str = info['type']
            if "int32" in t_str: self.last_type = "int32"
            elif "float64" in t_str: self.last_type = "float64"
            elif "string" in t_str: self.last_type = "string"
            else: self.last_type = "object"
        else:
            self.emit("ldc.i4.0")
            self.last_type = "int32"

    def visitMemberAccess(self, ctx):
        self.visit(ctx.expression()) 
        member = ctx.ID().getText()
        tmp_name = f"__tmp_col_access_{self.symbols.locals_count}"
        tmp_idx = self.symbols.define_local(tmp_name, "color")
        self.emit(f"stloc {tmp_idx}")
        self.emit(f"ldloca {tmp_idx}")
        
        if member in ['r', 'R', 'g', 'G', 'b', 'B']:
            if member in ['r', 'R']: self.emit("call instance uint8 [System.Drawing]System.Drawing.Color::get_R()")
            elif member in ['g', 'G']: self.emit("call instance uint8 [System.Drawing]System.Drawing.Color::get_G()")
            elif member in ['b', 'B']: self.emit("call instance uint8 [System.Drawing]System.Drawing.Color::get_B()")
            self.emit("conv.i4") 
            self.last_type = "int32"
        else:
            self.last_type = "object"

    def visitPowerExpr(self, ctx):
        self.visit(ctx.expression(0))
        self.emit("conv.r8")
        self.visit(ctx.expression(1))
        self.emit("conv.r8")
        self.emit("call float64 [mscorlib]System.Math::Pow(float64, float64)")
        self.emit("conv.i4")
        self.last_type = "int32"

    def visitAddSub(self, ctx):
        self.visit(ctx.expression(0))
        self.visit(ctx.expression(1))
        op = ctx.getChild(1).getText()
        if op == '+': self.emit("add")
        elif op == '-': self.emit("sub")
        self.last_type = "int32"
    
    def visitMulDivMod(self, ctx): 
        self.visit(ctx.expression(0))
        self.visit(ctx.expression(1))
        op = ctx.getChild(1).getText()
        if op == '*': self.emit("mul")
        elif op == '/': self.emit("div")
        elif op == '%': self.emit("rem")
        self.last_type = "int32"

    def visitCompare(self, ctx):
        self.visit(ctx.expression(0))
        self.visit(ctx.expression(1))
        op = ctx.getChild(1).getText()
        if op == '>': self.emit("cgt")
        elif op == '<': self.emit("clt")
        elif op == '==': self.emit("ceq")
        elif op == '!=': 
             self.emit("ceq")
             self.emit("ldc.i4.0")
             self.emit("ceq")
        elif op == '<=': 
            self.emit("cgt") 
            self.emit("ldc.i4.0")
            self.emit("ceq")
        elif op == '>=':
            self.emit("clt")
            self.emit("ldc.i4.0")
            self.emit("ceq")
        self.last_type = "int32" 

    def visitAndExpr(self, ctx):
        self.visit(ctx.expression(0))
        self.visit(ctx.expression(1))
        self.emit("and")
        self.last_type = "int32"

    def visitOrExpr(self, ctx):
        self.visit(ctx.expression(0))
        self.visit(ctx.expression(1))
        self.emit("or")
        self.last_type = "int32"

    def visitCastExpr(self, ctx):
        self.visit(ctx.expression())
        target = ctx.type_().getText()
        if target == 'int': 
            self.emit("conv.i4")
            self.last_type = "int32"

    def visitParenExpr(self, ctx):
        self.visit(ctx.expression())

    def visitCallExpr(self, ctx):
        self.visit(ctx.functionCall())

    def visitFunctionCall(self, ctx):
        if ctx.builtInFunction():
            name = ctx.builtInFunction().getText()
            args = ctx.argumentList().expression() if ctx.argumentList() else []
            
            if name == "write":
                for arg in args:
                    self.visit(arg)
                    if self.last_type == "int32": self.emit("call void [ImgLangRuntime]Runtime::Write(int32)")
                    elif self.last_type == "float64": self.emit("call void [ImgLangRuntime]Runtime::Write(float64)")
                    elif self.last_type == "string": self.emit("call void [ImgLangRuntime]Runtime::Write(string)")
                    else: self.emit("call void [ImgLangRuntime]Runtime::Write(object)")
                return

            for arg in args: self.visit(arg)
            
            if name == "load_image":
                self.emit("call class [System.Drawing]System.Drawing.Bitmap [ImgLangRuntime]Runtime::LoadImage(string)")
                self.last_type = "object"
            elif name == "save_image":
                self.emit("call void [ImgLangRuntime]Runtime::SaveImage(class [System.Drawing]System.Drawing.Bitmap, string)")
            elif name == "create_image":
                self.emit("call class [System.Drawing]System.Drawing.Bitmap [ImgLangRuntime]Runtime::CreateImage(int32, int32)")
                self.last_type = "object"
            elif name == "get_width":
                self.emit("call int32 [ImgLangRuntime]Runtime::GetWidth(class [System.Drawing]System.Drawing.Bitmap)")
                self.last_type = "int32"
            elif name == "get_height":
                self.emit("call int32 [ImgLangRuntime]Runtime::GetHeight(class [System.Drawing]System.Drawing.Bitmap)")
                self.last_type = "int32"
            elif name == "get_pixel":
                self.emit("call valuetype [System.Drawing]System.Drawing.Color [ImgLangRuntime]Runtime::GetPixel(class [System.Drawing]System.Drawing.Bitmap, int32, int32)")
                self.last_type = "object"
            elif name == "set_pixel":
                self.emit("call void [ImgLangRuntime]Runtime::SetPixel(class [System.Drawing]System.Drawing.Bitmap, int32, int32, valuetype [System.Drawing]System.Drawing.Color)")
            elif name == "to_color":
                self.emit("call valuetype [System.Drawing]System.Drawing.Color [ImgLangRuntime]Runtime::ToColor(int32, int32, int32)")
                self.last_type = "object"
            elif name == "clamp":
                self.emit("call int32 [ImgLangRuntime]Runtime::Clamp(int32, int32, int32)")
                self.last_type = "int32"
            
        else:
            func_name = ctx.ID().getText()
            if func_name == "read_int":
                self.emit("call int32 [ImgLangRuntime]Runtime::ReadInt()")
                self.last_type = "int32"
                return
            
            elif name == "read_float":
                self.emit("call float64 [ImgLangRuntime]Runtime::ReadFloat()")
                self.last_type = "float64"
                return

            args = ctx.argumentList().expression() if ctx.argumentList() else []
            sig = self.signatures.get(func_name)
            
            for i, arg in enumerate(args):
                if sig and i < len(sig['kinds']) and sig['kinds'][i] == 'result':
                    if isinstance(arg, ImgLangParser.VarExprContext):
                        var_name = arg.ID().getText()
                        info = self.symbols.resolve(var_name)
                        if info:
                            if info['kind'] == 'loc': self.emit(f"ldloca {info['index']}")
                            else: self.emit(f"ldarga {info['index']}")
                    else:
                        print("Error: result param expects variable")
                else:
                    self.visit(arg)
            
            if sig:
                sig_args = ", ".join(sig['args'])
                ret = sig['ret']
                self.emit(f"call {ret} Program::{func_name}({sig_args})")
                self.last_type = "int32" if ret == "int32" else "void"
            else:
                self.emit(f"call void Program::{func_name}()")
                self.last_type = "void"