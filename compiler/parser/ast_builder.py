from antlr.ImgLangVisitor import ImgLangVisitor
from antlr.ImgLangParser import ImgLangParser
from .ast import *

class ASTBuilder(ImgLangVisitor):
    def _get_source_info(self, ctx):
        if ctx and hasattr(ctx, 'start') and ctx.start:
            stop = ctx.stop if ctx.stop else ctx.start
            return SourceLocation(
                line=ctx.start.line,
                column=ctx.start.column + 1,
                end_line=stop.line,
                end_column=stop.column + 1
            )
        return None

    def visitStatement(self, ctx: ImgLangParser.StatementContext):
        if ctx.functionCall() or ctx.expression():
            expr_ctx = ctx.functionCall() if ctx.functionCall() else ctx.expression()
            expr = expr_ctx.accept(self)
            if expr:
                return ExpressionStatement(expr=expr, source_info=self._get_source_info(ctx))
        
        for child in ctx.children:
            if hasattr(child, 'accept'):
                res = child.accept(self)
                if isinstance(res, Statement):
                    return res
        return None
    
    def visitFunctionDecl(self, ctx: ImgLangParser.FunctionDeclContext):
        name = ctx.ID().getText()
        params = ctx.parameterList().accept(self) if ctx.parameterList() else []
        
        if ctx.type_():
            ret_type = self._map_type(ctx.type_().getText())
        else:
            body_text = ctx.block().getText()
            if "res" in body_text:
                ret_type = Type(kind=TypeKind.INT)
            else:
                ret_type = Type(kind=TypeKind.VOID)
            
        body = ctx.block().accept(self)
        return FunctionDecl(name=name, params=params, return_type=ret_type, body=body)
    
    def visitDoUntilLoop(self, ctx: ImgLangParser.DoUntilLoopContext):
        body = ctx.block().accept(self)
        condition = ctx.expression().accept(self)
        return DoUntilLoop(body=body, condition=condition, source_info=self._get_source_info(ctx))
    
    def visitParameterList(self, ctx: ImgLangParser.ParameterListContext):
        return [p.accept(self) for p in ctx.parameter()]

    def visitParameter(self, ctx: ImgLangParser.ParameterContext):
        kind = "value"
        if ctx.getChildCount() > 2:
            kind = ctx.getChild(0).getText()
        
        type_str = ctx.type_().getText()
        param_type = self._map_type(type_str)
        name = ctx.ID().getText()
        
        return Parameter(
            param_type=param_type,
            name=name,
            kind=kind,
            source_info=self._get_source_info(ctx)
        )
    
    def visitForLoop(self, ctx: ImgLangParser.ForLoopContext):
        init = ctx.forInit().accept(self) if ctx.forInit() else None
        cond = ctx.forCondition().accept(self) if ctx.forCondition() else None
        update = ctx.forUpdate().accept(self) if ctx.forUpdate() else None
        body = ctx.block().accept(self)
        
        return ForLoop(
            init=init, 
            condition=cond, 
            update=update, 
            body=body, 
            source_info=self._get_source_info(ctx)
        )

    def visitForInit(self, ctx: ImgLangParser.ForInitContext):
        if ctx.type_():
            var_type = self._map_type(ctx.type_().getText())
            entry = VariableEntry(name=ctx.ID().getText(), initializer=ctx.expression().accept(self))
            return VariableDecl(var_type=var_type, variables=[entry], source_info=self._get_source_info(ctx))
        else:
            target = VariableExpr(name=ctx.ID().getText(), source_info=self._get_source_info(ctx))
            return Assignment(target=target, value=ctx.expression().accept(self), source_info=self._get_source_info(ctx))

    def visitForUpdate(self, ctx: ImgLangParser.ForUpdateContext):
        target = VariableExpr(name=ctx.ID().getText(), source_info=self._get_source_info(ctx))
        return Assignment(target=target, value=ctx.expression().accept(self), source_info=self._get_source_info(ctx))
    
    def visitVariableDecl(self, ctx: ImgLangParser.VariableDeclContext):
        var_type = self._map_type(ctx.type_().getText())
        variables = []
        for entry_ctx in ctx.variableList().variableEntry():
            entry = entry_ctx.accept(self)
            if entry:
                variables.append(entry)
        return VariableDecl(var_type=var_type, variables=variables, source_info=self._get_source_info(ctx))

    def visitVariableEntry(self, ctx: ImgLangParser.VariableEntryContext):
        name = ctx.ID().getText()
        initializer = None
        if ctx.expression():
            initializer = ctx.expression().accept(self)
        return VariableEntry(name=name, initializer=initializer)

    def visitBraceBlock(self, ctx: ImgLangParser.BraceBlockContext):
        statements = []
        for s in ctx.statement():
            res = s.accept(self)
            if res: statements.append(res)
        return Block(statements=statements, source_info=self._get_source_info(ctx))

    def visitBeginEndBlock(self, ctx: ImgLangParser.BeginEndBlockContext):
        statements = []
        for s in ctx.statement():
            res = s.accept(self)
            if res: statements.append(res)
        return Block(statements=statements, source_info=self._get_source_info(ctx))

    def visitLiteralPrimary(self, ctx: ImgLangParser.LiteralPrimaryContext):
        return ctx.literal().accept(self)

    def visitIdPrimary(self, ctx: ImgLangParser.IdPrimaryContext):
        return VariableExpr(name=ctx.ID().getText(), source_info=self._get_source_info(ctx))

    def visitParenPrimary(self, ctx: ImgLangParser.ParenPrimaryContext):
        return ctx.expression().accept(self)

    def visitCastPrimary(self, ctx: ImgLangParser.CastPrimaryContext):
        target_type = self._map_type(ctx.type_().getText())
        expr = ctx.expression().accept(self)
        return CastExpr(target_type=target_type, expr=expr, source_info=self._get_source_info(ctx))

    def visitFunctionCallPrimary(self, ctx: ImgLangParser.FunctionCallPrimaryContext):
        return ctx.functionCall().accept(self)

    def visitMemberAccessPrimary(self, ctx: ImgLangParser.MemberAccessPrimaryContext):
        obj = ctx.primary().accept(self)
        member = ctx.ID().getText()
        return MemberAccessExpr(obj=obj, member=member, source_info=self._get_source_info(ctx))

    def visitConstructorPrimary(self, ctx: ImgLangParser.ConstructorPrimaryContext):
        struct_name = ctx.ID().getText()
        args = []
        if ctx.argumentList():
            for arg_ctx in ctx.argumentList().expression():
                args.append(arg_ctx.accept(self))
        return ConstructorExpr(struct_name=struct_name, args=args, source_info=self._get_source_info(ctx))

    def visitUnary(self, ctx: ImgLangParser.UnaryContext):
        if ctx.primary():
            return ctx.primary().accept(self)
        
        op = ctx.getChild(0).getText()
        expr_ctx = ctx.unary()
        if expr_ctx:
            expr = expr_ctx.accept(self)
            return UnaryExpr(op=op, expr=expr, source_info=self._get_source_info(ctx))
        return None

    def visitPower(self, ctx: ImgLangParser.PowerContext):
        if not ctx.unary(0): return None
        left = ctx.unary(0).accept(self)
        for i in range(1, len(ctx.unary())):
            right = ctx.unary(i).accept(self)
            left = BinaryExpr(left=left, op='**', right=right, source_info=self._get_source_info(ctx))
        return left

    def visitMultiplication(self, ctx: ImgLangParser.MultiplicationContext):
        if not ctx.power(0): return None
        left = ctx.power(0).accept(self)
        for i in range(1, len(ctx.power())):
            op = ctx.getChild(i * 2 - 1).getText()
            right = ctx.power(i).accept(self)
            left = BinaryExpr(left=left, op=op, right=right, source_info=self._get_source_info(ctx))
        return left

    def visitAddition(self, ctx):
        if len(ctx.multiplication()) == 1:
            return ctx.multiplication(0).accept(self)
        
        left = ctx.multiplication(0).accept(self)
        for i in range(1, len(ctx.multiplication())):
            op = ctx.getChild(i * 2 - 1).getText()
            right = ctx.multiplication(i).accept(self)
            left = BinaryExpr(left=left, op=op, right=right, source_info=self._get_source_info(ctx))
        return left
    
    def visitAssignment(self, ctx: ImgLangParser.AssignmentContext):
        if ctx.StructFieldAssign():
            return self.visitStructFieldAssign(ctx.StructFieldAssign())
        elif ctx.ThisFieldAssign():
            return self.visitThisFieldAssign(ctx.ThisFieldAssign())
        elif ctx.SingleAssign():
            return self.visitSingleAssign(ctx.SingleAssign())
        elif ctx.MultiAssign():
            return self.visitMultiAssign(ctx.MultiAssign())

    def visitSingleAssign(self, ctx: ImgLangParser.SingleAssignContext):
        target = VariableExpr(name=ctx.ID().getText(), source_info=self._get_source_info(ctx))
        value_ctx = ctx.expression()
        if value_ctx:
            value = value_ctx.accept(self)
            return Assignment(target=target, value=value, source_info=self._get_source_info(ctx))
        return None

    def visitProgram(self, ctx: ImgLangParser.ProgramContext):
        declarations = []
        statements = []
        if ctx.children:
            for child in ctx.children:
                if hasattr(child, 'accept'):
                    res = child.accept(self)
                    if isinstance(res, Declaration): declarations.append(res)
                    elif isinstance(res, Statement): statements.append(res)
        return Program(declarations=declarations, statements=statements, source_info=self._get_source_info(ctx))
    
    def visitIfStatement(self, ctx: ImgLangParser.IfStatementContext):
        condition = ctx.expression().accept(self)
        then_block = ctx.block(0).accept(self)
        else_block = ctx.block(1).accept(self) if len(ctx.block()) > 1 else None
        return IfStatement(
            condition=condition, 
            then_block=then_block, 
            else_block=else_block, 
            source_info=self._get_source_info(ctx)
        )

    def visitWhileLoop(self, ctx: ImgLangParser.WhileLoopContext):
        condition = ctx.expression().accept(self)
        body = ctx.block().accept(self)
        return WhileLoop(condition=condition, body=body, source_info=self._get_source_info(ctx))

    def visitReturnStatement(self, ctx: ImgLangParser.ReturnStatementContext):
        value = ctx.expression().accept(self) if ctx.expression() else None
        return ReturnStatement(value=value, source_info=self._get_source_info(ctx))
    
    def visitComparison(self, ctx: ImgLangParser.ComparisonContext):
        if len(ctx.addition()) == 1:
            return ctx.addition(0).accept(self)
        
        left = ctx.addition(0).accept(self)
        for i in range(1, len(ctx.addition())):
            op = ctx.getChild(i * 2 - 1).getText()
            right = ctx.addition(i).accept(self)
            left = BinaryExpr(left=left, op=op, right=right, source_info=self._get_source_info(ctx))
        return left
    
    def visitEquality(self, ctx: ImgLangParser.EqualityContext):
        if len(ctx.comparison()) == 1:
            return ctx.comparison(0).accept(self)
        
        left = ctx.comparison(0).accept(self)
        for i in range(1, len(ctx.comparison())):
            op = ctx.getChild(i * 2 - 1).getText()
            right = ctx.comparison(i).accept(self)
            left = BinaryExpr(left=left, op=op, right=right, source_info=self._get_source_info(ctx))
        return left

    def visitLogicalAnd(self, ctx: ImgLangParser.LogicalAndContext):
        if len(ctx.equality()) == 1:
            return ctx.equality(0).accept(self)
        
        left = ctx.equality(0).accept(self)
        for i in range(1, len(ctx.equality())):
            right = ctx.equality(i).accept(self)
            left = BinaryExpr(left=left, op='&&', right=right, source_info=self._get_source_info(ctx))
        return left

    def visitLogicalOr(self, ctx: ImgLangParser.LogicalOrContext):
        if len(ctx.logicalAnd()) == 1:
            return ctx.logicalAnd(0).accept(self)
        
        left = ctx.logicalAnd(0).accept(self)
        for i in range(1, len(ctx.logicalAnd())):
            right = ctx.logicalAnd(i).accept(self)
            left = BinaryExpr(left=left, op='||', right=right, source_info=self._get_source_info(ctx))
        return left

    def visitLiteral(self, ctx: ImgLangParser.LiteralContext):
        if ctx.INT():
            return LiteralExpr(value=int(ctx.INT().getText()), type=Type(kind=TypeKind.INT), source_info=self._get_source_info(ctx))
        if ctx.FLOAT():
            return LiteralExpr(value=float(ctx.FLOAT().getText()), type=Type(kind=TypeKind.FLOAT), source_info=self._get_source_info(ctx))
        if ctx.STRING():
            return LiteralExpr(value=ctx.STRING().getText()[1:-1], type=Type(kind=TypeKind.STRING), source_info=self._get_source_info(ctx))
        if ctx.TRUE() or ctx.FALSE():
            return LiteralExpr(value=(ctx.TRUE() is not None), type=Type(kind=TypeKind.BOOL), source_info=self._get_source_info(ctx))
        return None
    
    def visitNormalCall(self, ctx: ImgLangParser.NormalCallContext):
        func_name = ctx.funcName().getText()
        args = [arg.accept(self) for arg in (ctx.argumentList().expression() if ctx.argumentList() else [])]
        
        return CallExpr(
            func_name=func_name,
            args=args,
            receiver=None,
            source_info=self._get_source_info(ctx)
        )
    
    def visitStructDecl(self, ctx: ImgLangParser.StructDeclContext):
        name = ctx.ID(0).getText()
        parent = None
        
        if ctx.EXTENDS() and len(ctx.ID()) > 1:
            parent = ctx.ID(1).getText()
        
        members = []
        for member in ctx.memberDecl():
            member_node = member.accept(self)
            if member_node:
                members.append(member_node)
        
        return StructDecl(
            name=name,
            parent=parent,
            members=members,
            access_modifier=AccessModifier.PUBLIC,
            source_info=self._get_source_info(ctx)
        )

    def visitMemberDecl(self, ctx: ImgLangParser.MemberDeclContext):
        access = ctx.accessModifier().accept(self)
        
        if ctx.fieldDecl():
            decl = ctx.fieldDecl().accept(self)
        elif ctx.methodDecl():
            decl = ctx.methodDecl().accept(self)
        else:
            return None
        
        return MemberDecl(
            access=access,
            decl=decl,
            source_info=self._get_source_info(ctx)
        )

    def visitAccessModifier(self, ctx: ImgLangParser.AccessModifierContext):
        text = ctx.getText().upper()
        return AccessModifier(text)

    def visitFieldDecl(self, ctx: ImgLangParser.FieldDeclContext):
        field_type = self._map_type(ctx.type_().getText())
        name = ctx.ID().getText()
        return FieldDecl(
            field_type=field_type,
            name=name,
            source_info=self._get_source_info(ctx)
        )

    def visitMethodDecl(self, ctx: ImgLangParser.MethodDeclContext):
        name = ctx.ID().getText()
        params = ctx.parameterList().accept(self) if ctx.parameterList() else []
        return_type = self._map_type(ctx.type_().getText()) if ctx.type_() else Type(kind=TypeKind.VOID)
        body = ctx.block().accept(self)
        
        modifiers = []
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            if hasattr(child, 'getText'):
                text = child.getText()
                if text in ['virtual', 'override']:
                    modifiers.append(text)
        
        return MethodDecl(
            name=name,
            params=params,
            return_type=return_type,
            body=body,
            modifiers=modifiers,
            source_info=self._get_source_info(ctx)
        )

    def visitSuperCall(self, ctx: ImgLangParser.SuperCallContext):
        """Обработка вызова super() (теперь используем SuperConstructorCall)"""
        return self.visitSuperConstructorCall(ctx)
    
    def visitSuperPrimary(self, ctx: ImgLangParser.SuperPrimaryContext):
        """Обработка 'super' в выражениях (например, super.validate())"""
        return VariableExpr(
            name='super',
            source_info=self._get_source_info(ctx)
        )
    
    def visitSuperConstructorCall(self, ctx: ImgLangParser.SuperConstructorCallContext):
        """Обработка вызова конструктора родительского класса: super(...)"""
        args = []
        if ctx.argumentList():
            for arg_ctx in ctx.argumentList().expression():
                args.append(arg_ctx.accept(self))
        
        return CallExpr(
            func_name='super',
            args=args,
            source_info=self._get_source_info(ctx)
        )

    def visitThisPrimary(self, ctx: ImgLangParser.ThisPrimaryContext):
        return VariableExpr(
            name='this',
            source_info=self._get_source_info(ctx)
        )

    def visitStructFieldAssign(self, ctx: ImgLangParser.StructFieldAssignContext):
        obj = ctx.expression(0).accept(self)
        member = ctx.ID().getText()
        value = ctx.expression(1).accept(self)
        
        target = MemberAccessExpr(
            obj=obj,
            member=member,
            source_info=self._get_source_info(ctx)
        )
        
        return Assignment(
            target=target,
            value=value,
            source_info=self._get_source_info(ctx)
        )

    def visitThisFieldAssign(self, ctx: ImgLangParser.ThisFieldAssignContext):
        target = MemberAccessExpr(
            obj=VariableExpr(name='this', source_info=self._get_source_info(ctx)),
            member=ctx.ID().getText(),
            source_info=self._get_source_info(ctx)
        )
        
        value = ctx.expression().accept(self)
        return self.visitStructFieldAssign(ctx)

    def visitMethodCallPrimary(self, ctx: ImgLangParser.MethodCallPrimaryContext):
        obj = ctx.primary().accept(self)
        method_name = ctx.ID().getText()
        args = [arg.accept(self) for arg in (ctx.argumentList().expression() if ctx.argumentList() else [])]
        
        return CallExpr(
            func_name=method_name,
            args=args,
            receiver=obj,
            source_info=self._get_source_info(ctx)
        )

    def _map_type(self, type_str: str) -> Type:
        type_map = {
            'int': TypeKind.INT, 'float': TypeKind.FLOAT, 'bool': TypeKind.BOOL,
            'image': TypeKind.IMAGE, 'color': TypeKind.COLOR, 'pixel': TypeKind.PIXEL,
            'string': TypeKind.STRING, 'void': TypeKind.VOID,
        }
        kind = type_map.get(type_str, TypeKind.STRUCT)
        return Type(kind=kind, struct_name=type_str if kind == TypeKind.STRUCT else None)