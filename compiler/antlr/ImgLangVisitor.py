# Generated from ImgLang.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .ImgLangParser import ImgLangParser
else:
    from ImgLangParser import ImgLangParser

# This class defines a complete generic visitor for a parse tree produced by ImgLangParser.

class ImgLangVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ImgLangParser#program.
    def visitProgram(self, ctx:ImgLangParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#structDecl.
    def visitStructDecl(self, ctx:ImgLangParser.StructDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#memberDecl.
    def visitMemberDecl(self, ctx:ImgLangParser.MemberDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#accessModifier.
    def visitAccessModifier(self, ctx:ImgLangParser.AccessModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#fieldDecl.
    def visitFieldDecl(self, ctx:ImgLangParser.FieldDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#methodDecl.
    def visitMethodDecl(self, ctx:ImgLangParser.MethodDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#functionDecl.
    def visitFunctionDecl(self, ctx:ImgLangParser.FunctionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#parameterList.
    def visitParameterList(self, ctx:ImgLangParser.ParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#parameter.
    def visitParameter(self, ctx:ImgLangParser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#type.
    def visitType(self, ctx:ImgLangParser.TypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#BraceBlock.
    def visitBraceBlock(self, ctx:ImgLangParser.BraceBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#BeginEndBlock.
    def visitBeginEndBlock(self, ctx:ImgLangParser.BeginEndBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#statement.
    def visitStatement(self, ctx:ImgLangParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#returnStatement.
    def visitReturnStatement(self, ctx:ImgLangParser.ReturnStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#superCall.
    def visitSuperCall(self, ctx:ImgLangParser.SuperCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#whileLoop.
    def visitWhileLoop(self, ctx:ImgLangParser.WhileLoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#doUntilLoop.
    def visitDoUntilLoop(self, ctx:ImgLangParser.DoUntilLoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#variableDecl.
    def visitVariableDecl(self, ctx:ImgLangParser.VariableDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#variableList.
    def visitVariableList(self, ctx:ImgLangParser.VariableListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#variableEntry.
    def visitVariableEntry(self, ctx:ImgLangParser.VariableEntryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#SingleAssign.
    def visitSingleAssign(self, ctx:ImgLangParser.SingleAssignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#MultiAssign.
    def visitMultiAssign(self, ctx:ImgLangParser.MultiAssignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#StructFieldAssign.
    def visitStructFieldAssign(self, ctx:ImgLangParser.StructFieldAssignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#ThisFieldAssign.
    def visitThisFieldAssign(self, ctx:ImgLangParser.ThisFieldAssignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#idList.
    def visitIdList(self, ctx:ImgLangParser.IdListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#exprList.
    def visitExprList(self, ctx:ImgLangParser.ExprListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#forLoop.
    def visitForLoop(self, ctx:ImgLangParser.ForLoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#forInit.
    def visitForInit(self, ctx:ImgLangParser.ForInitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#forCondition.
    def visitForCondition(self, ctx:ImgLangParser.ForConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#forUpdate.
    def visitForUpdate(self, ctx:ImgLangParser.ForUpdateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#ifStatement.
    def visitIfStatement(self, ctx:ImgLangParser.IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#expression.
    def visitExpression(self, ctx:ImgLangParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#logicalOr.
    def visitLogicalOr(self, ctx:ImgLangParser.LogicalOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#logicalAnd.
    def visitLogicalAnd(self, ctx:ImgLangParser.LogicalAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#equality.
    def visitEquality(self, ctx:ImgLangParser.EqualityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#comparison.
    def visitComparison(self, ctx:ImgLangParser.ComparisonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#addition.
    def visitAddition(self, ctx:ImgLangParser.AdditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#multiplication.
    def visitMultiplication(self, ctx:ImgLangParser.MultiplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#power.
    def visitPower(self, ctx:ImgLangParser.PowerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#unary.
    def visitUnary(self, ctx:ImgLangParser.UnaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#MethodCallPrimary.
    def visitMethodCallPrimary(self, ctx:ImgLangParser.MethodCallPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#ConstructorPrimary.
    def visitConstructorPrimary(self, ctx:ImgLangParser.ConstructorPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#SuperConstructorCall.
    def visitSuperConstructorCall(self, ctx:ImgLangParser.SuperConstructorCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#LiteralPrimary.
    def visitLiteralPrimary(self, ctx:ImgLangParser.LiteralPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#FunctionCallPrimary.
    def visitFunctionCallPrimary(self, ctx:ImgLangParser.FunctionCallPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#IdPrimary.
    def visitIdPrimary(self, ctx:ImgLangParser.IdPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#CastPrimary.
    def visitCastPrimary(self, ctx:ImgLangParser.CastPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#ThisPrimary.
    def visitThisPrimary(self, ctx:ImgLangParser.ThisPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#SuperPrimary.
    def visitSuperPrimary(self, ctx:ImgLangParser.SuperPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#MemberAccessPrimary.
    def visitMemberAccessPrimary(self, ctx:ImgLangParser.MemberAccessPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#ParenPrimary.
    def visitParenPrimary(self, ctx:ImgLangParser.ParenPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#literal.
    def visitLiteral(self, ctx:ImgLangParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#NormalCall.
    def visitNormalCall(self, ctx:ImgLangParser.NormalCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#funcName.
    def visitFuncName(self, ctx:ImgLangParser.FuncNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#argumentList.
    def visitArgumentList(self, ctx:ImgLangParser.ArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ImgLangParser#builtInFunction.
    def visitBuiltInFunction(self, ctx:ImgLangParser.BuiltInFunctionContext):
        return self.visitChildren(ctx)



del ImgLangParser