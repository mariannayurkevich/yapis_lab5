# Generated from ImgLang.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .ImgLangParser import ImgLangParser
else:
    from ImgLangParser import ImgLangParser

# This class defines a complete listener for a parse tree produced by ImgLangParser.
class ImgLangListener(ParseTreeListener):

    # Enter a parse tree produced by ImgLangParser#program.
    def enterProgram(self, ctx:ImgLangParser.ProgramContext):
        pass

    # Exit a parse tree produced by ImgLangParser#program.
    def exitProgram(self, ctx:ImgLangParser.ProgramContext):
        pass


    # Enter a parse tree produced by ImgLangParser#structDecl.
    def enterStructDecl(self, ctx:ImgLangParser.StructDeclContext):
        pass

    # Exit a parse tree produced by ImgLangParser#structDecl.
    def exitStructDecl(self, ctx:ImgLangParser.StructDeclContext):
        pass


    # Enter a parse tree produced by ImgLangParser#memberDecl.
    def enterMemberDecl(self, ctx:ImgLangParser.MemberDeclContext):
        pass

    # Exit a parse tree produced by ImgLangParser#memberDecl.
    def exitMemberDecl(self, ctx:ImgLangParser.MemberDeclContext):
        pass


    # Enter a parse tree produced by ImgLangParser#accessModifier.
    def enterAccessModifier(self, ctx:ImgLangParser.AccessModifierContext):
        pass

    # Exit a parse tree produced by ImgLangParser#accessModifier.
    def exitAccessModifier(self, ctx:ImgLangParser.AccessModifierContext):
        pass


    # Enter a parse tree produced by ImgLangParser#fieldDecl.
    def enterFieldDecl(self, ctx:ImgLangParser.FieldDeclContext):
        pass

    # Exit a parse tree produced by ImgLangParser#fieldDecl.
    def exitFieldDecl(self, ctx:ImgLangParser.FieldDeclContext):
        pass


    # Enter a parse tree produced by ImgLangParser#methodDecl.
    def enterMethodDecl(self, ctx:ImgLangParser.MethodDeclContext):
        pass

    # Exit a parse tree produced by ImgLangParser#methodDecl.
    def exitMethodDecl(self, ctx:ImgLangParser.MethodDeclContext):
        pass


    # Enter a parse tree produced by ImgLangParser#functionDecl.
    def enterFunctionDecl(self, ctx:ImgLangParser.FunctionDeclContext):
        pass

    # Exit a parse tree produced by ImgLangParser#functionDecl.
    def exitFunctionDecl(self, ctx:ImgLangParser.FunctionDeclContext):
        pass


    # Enter a parse tree produced by ImgLangParser#parameterList.
    def enterParameterList(self, ctx:ImgLangParser.ParameterListContext):
        pass

    # Exit a parse tree produced by ImgLangParser#parameterList.
    def exitParameterList(self, ctx:ImgLangParser.ParameterListContext):
        pass


    # Enter a parse tree produced by ImgLangParser#parameter.
    def enterParameter(self, ctx:ImgLangParser.ParameterContext):
        pass

    # Exit a parse tree produced by ImgLangParser#parameter.
    def exitParameter(self, ctx:ImgLangParser.ParameterContext):
        pass


    # Enter a parse tree produced by ImgLangParser#type.
    def enterType(self, ctx:ImgLangParser.TypeContext):
        pass

    # Exit a parse tree produced by ImgLangParser#type.
    def exitType(self, ctx:ImgLangParser.TypeContext):
        pass


    # Enter a parse tree produced by ImgLangParser#BraceBlock.
    def enterBraceBlock(self, ctx:ImgLangParser.BraceBlockContext):
        pass

    # Exit a parse tree produced by ImgLangParser#BraceBlock.
    def exitBraceBlock(self, ctx:ImgLangParser.BraceBlockContext):
        pass


    # Enter a parse tree produced by ImgLangParser#BeginEndBlock.
    def enterBeginEndBlock(self, ctx:ImgLangParser.BeginEndBlockContext):
        pass

    # Exit a parse tree produced by ImgLangParser#BeginEndBlock.
    def exitBeginEndBlock(self, ctx:ImgLangParser.BeginEndBlockContext):
        pass


    # Enter a parse tree produced by ImgLangParser#statement.
    def enterStatement(self, ctx:ImgLangParser.StatementContext):
        pass

    # Exit a parse tree produced by ImgLangParser#statement.
    def exitStatement(self, ctx:ImgLangParser.StatementContext):
        pass


    # Enter a parse tree produced by ImgLangParser#returnStatement.
    def enterReturnStatement(self, ctx:ImgLangParser.ReturnStatementContext):
        pass

    # Exit a parse tree produced by ImgLangParser#returnStatement.
    def exitReturnStatement(self, ctx:ImgLangParser.ReturnStatementContext):
        pass


    # Enter a parse tree produced by ImgLangParser#superCall.
    def enterSuperCall(self, ctx:ImgLangParser.SuperCallContext):
        pass

    # Exit a parse tree produced by ImgLangParser#superCall.
    def exitSuperCall(self, ctx:ImgLangParser.SuperCallContext):
        pass


    # Enter a parse tree produced by ImgLangParser#whileLoop.
    def enterWhileLoop(self, ctx:ImgLangParser.WhileLoopContext):
        pass

    # Exit a parse tree produced by ImgLangParser#whileLoop.
    def exitWhileLoop(self, ctx:ImgLangParser.WhileLoopContext):
        pass


    # Enter a parse tree produced by ImgLangParser#doUntilLoop.
    def enterDoUntilLoop(self, ctx:ImgLangParser.DoUntilLoopContext):
        pass

    # Exit a parse tree produced by ImgLangParser#doUntilLoop.
    def exitDoUntilLoop(self, ctx:ImgLangParser.DoUntilLoopContext):
        pass


    # Enter a parse tree produced by ImgLangParser#variableDecl.
    def enterVariableDecl(self, ctx:ImgLangParser.VariableDeclContext):
        pass

    # Exit a parse tree produced by ImgLangParser#variableDecl.
    def exitVariableDecl(self, ctx:ImgLangParser.VariableDeclContext):
        pass


    # Enter a parse tree produced by ImgLangParser#variableList.
    def enterVariableList(self, ctx:ImgLangParser.VariableListContext):
        pass

    # Exit a parse tree produced by ImgLangParser#variableList.
    def exitVariableList(self, ctx:ImgLangParser.VariableListContext):
        pass


    # Enter a parse tree produced by ImgLangParser#variableEntry.
    def enterVariableEntry(self, ctx:ImgLangParser.VariableEntryContext):
        pass

    # Exit a parse tree produced by ImgLangParser#variableEntry.
    def exitVariableEntry(self, ctx:ImgLangParser.VariableEntryContext):
        pass


    # Enter a parse tree produced by ImgLangParser#SingleAssign.
    def enterSingleAssign(self, ctx:ImgLangParser.SingleAssignContext):
        pass

    # Exit a parse tree produced by ImgLangParser#SingleAssign.
    def exitSingleAssign(self, ctx:ImgLangParser.SingleAssignContext):
        pass


    # Enter a parse tree produced by ImgLangParser#MultiAssign.
    def enterMultiAssign(self, ctx:ImgLangParser.MultiAssignContext):
        pass

    # Exit a parse tree produced by ImgLangParser#MultiAssign.
    def exitMultiAssign(self, ctx:ImgLangParser.MultiAssignContext):
        pass


    # Enter a parse tree produced by ImgLangParser#StructFieldAssign.
    def enterStructFieldAssign(self, ctx:ImgLangParser.StructFieldAssignContext):
        pass

    # Exit a parse tree produced by ImgLangParser#StructFieldAssign.
    def exitStructFieldAssign(self, ctx:ImgLangParser.StructFieldAssignContext):
        pass


    # Enter a parse tree produced by ImgLangParser#ThisFieldAssign.
    def enterThisFieldAssign(self, ctx:ImgLangParser.ThisFieldAssignContext):
        pass

    # Exit a parse tree produced by ImgLangParser#ThisFieldAssign.
    def exitThisFieldAssign(self, ctx:ImgLangParser.ThisFieldAssignContext):
        pass


    # Enter a parse tree produced by ImgLangParser#idList.
    def enterIdList(self, ctx:ImgLangParser.IdListContext):
        pass

    # Exit a parse tree produced by ImgLangParser#idList.
    def exitIdList(self, ctx:ImgLangParser.IdListContext):
        pass


    # Enter a parse tree produced by ImgLangParser#exprList.
    def enterExprList(self, ctx:ImgLangParser.ExprListContext):
        pass

    # Exit a parse tree produced by ImgLangParser#exprList.
    def exitExprList(self, ctx:ImgLangParser.ExprListContext):
        pass


    # Enter a parse tree produced by ImgLangParser#forLoop.
    def enterForLoop(self, ctx:ImgLangParser.ForLoopContext):
        pass

    # Exit a parse tree produced by ImgLangParser#forLoop.
    def exitForLoop(self, ctx:ImgLangParser.ForLoopContext):
        pass


    # Enter a parse tree produced by ImgLangParser#forInit.
    def enterForInit(self, ctx:ImgLangParser.ForInitContext):
        pass

    # Exit a parse tree produced by ImgLangParser#forInit.
    def exitForInit(self, ctx:ImgLangParser.ForInitContext):
        pass


    # Enter a parse tree produced by ImgLangParser#forCondition.
    def enterForCondition(self, ctx:ImgLangParser.ForConditionContext):
        pass

    # Exit a parse tree produced by ImgLangParser#forCondition.
    def exitForCondition(self, ctx:ImgLangParser.ForConditionContext):
        pass


    # Enter a parse tree produced by ImgLangParser#forUpdate.
    def enterForUpdate(self, ctx:ImgLangParser.ForUpdateContext):
        pass

    # Exit a parse tree produced by ImgLangParser#forUpdate.
    def exitForUpdate(self, ctx:ImgLangParser.ForUpdateContext):
        pass


    # Enter a parse tree produced by ImgLangParser#ifStatement.
    def enterIfStatement(self, ctx:ImgLangParser.IfStatementContext):
        pass

    # Exit a parse tree produced by ImgLangParser#ifStatement.
    def exitIfStatement(self, ctx:ImgLangParser.IfStatementContext):
        pass


    # Enter a parse tree produced by ImgLangParser#expression.
    def enterExpression(self, ctx:ImgLangParser.ExpressionContext):
        pass

    # Exit a parse tree produced by ImgLangParser#expression.
    def exitExpression(self, ctx:ImgLangParser.ExpressionContext):
        pass


    # Enter a parse tree produced by ImgLangParser#logicalOr.
    def enterLogicalOr(self, ctx:ImgLangParser.LogicalOrContext):
        pass

    # Exit a parse tree produced by ImgLangParser#logicalOr.
    def exitLogicalOr(self, ctx:ImgLangParser.LogicalOrContext):
        pass


    # Enter a parse tree produced by ImgLangParser#logicalAnd.
    def enterLogicalAnd(self, ctx:ImgLangParser.LogicalAndContext):
        pass

    # Exit a parse tree produced by ImgLangParser#logicalAnd.
    def exitLogicalAnd(self, ctx:ImgLangParser.LogicalAndContext):
        pass


    # Enter a parse tree produced by ImgLangParser#equality.
    def enterEquality(self, ctx:ImgLangParser.EqualityContext):
        pass

    # Exit a parse tree produced by ImgLangParser#equality.
    def exitEquality(self, ctx:ImgLangParser.EqualityContext):
        pass


    # Enter a parse tree produced by ImgLangParser#comparison.
    def enterComparison(self, ctx:ImgLangParser.ComparisonContext):
        pass

    # Exit a parse tree produced by ImgLangParser#comparison.
    def exitComparison(self, ctx:ImgLangParser.ComparisonContext):
        pass


    # Enter a parse tree produced by ImgLangParser#addition.
    def enterAddition(self, ctx:ImgLangParser.AdditionContext):
        pass

    # Exit a parse tree produced by ImgLangParser#addition.
    def exitAddition(self, ctx:ImgLangParser.AdditionContext):
        pass


    # Enter a parse tree produced by ImgLangParser#multiplication.
    def enterMultiplication(self, ctx:ImgLangParser.MultiplicationContext):
        pass

    # Exit a parse tree produced by ImgLangParser#multiplication.
    def exitMultiplication(self, ctx:ImgLangParser.MultiplicationContext):
        pass


    # Enter a parse tree produced by ImgLangParser#power.
    def enterPower(self, ctx:ImgLangParser.PowerContext):
        pass

    # Exit a parse tree produced by ImgLangParser#power.
    def exitPower(self, ctx:ImgLangParser.PowerContext):
        pass


    # Enter a parse tree produced by ImgLangParser#unary.
    def enterUnary(self, ctx:ImgLangParser.UnaryContext):
        pass

    # Exit a parse tree produced by ImgLangParser#unary.
    def exitUnary(self, ctx:ImgLangParser.UnaryContext):
        pass


    # Enter a parse tree produced by ImgLangParser#MethodCallPrimary.
    def enterMethodCallPrimary(self, ctx:ImgLangParser.MethodCallPrimaryContext):
        pass

    # Exit a parse tree produced by ImgLangParser#MethodCallPrimary.
    def exitMethodCallPrimary(self, ctx:ImgLangParser.MethodCallPrimaryContext):
        pass


    # Enter a parse tree produced by ImgLangParser#ConstructorPrimary.
    def enterConstructorPrimary(self, ctx:ImgLangParser.ConstructorPrimaryContext):
        pass

    # Exit a parse tree produced by ImgLangParser#ConstructorPrimary.
    def exitConstructorPrimary(self, ctx:ImgLangParser.ConstructorPrimaryContext):
        pass


    # Enter a parse tree produced by ImgLangParser#SuperConstructorCall.
    def enterSuperConstructorCall(self, ctx:ImgLangParser.SuperConstructorCallContext):
        pass

    # Exit a parse tree produced by ImgLangParser#SuperConstructorCall.
    def exitSuperConstructorCall(self, ctx:ImgLangParser.SuperConstructorCallContext):
        pass


    # Enter a parse tree produced by ImgLangParser#LiteralPrimary.
    def enterLiteralPrimary(self, ctx:ImgLangParser.LiteralPrimaryContext):
        pass

    # Exit a parse tree produced by ImgLangParser#LiteralPrimary.
    def exitLiteralPrimary(self, ctx:ImgLangParser.LiteralPrimaryContext):
        pass


    # Enter a parse tree produced by ImgLangParser#FunctionCallPrimary.
    def enterFunctionCallPrimary(self, ctx:ImgLangParser.FunctionCallPrimaryContext):
        pass

    # Exit a parse tree produced by ImgLangParser#FunctionCallPrimary.
    def exitFunctionCallPrimary(self, ctx:ImgLangParser.FunctionCallPrimaryContext):
        pass


    # Enter a parse tree produced by ImgLangParser#IdPrimary.
    def enterIdPrimary(self, ctx:ImgLangParser.IdPrimaryContext):
        pass

    # Exit a parse tree produced by ImgLangParser#IdPrimary.
    def exitIdPrimary(self, ctx:ImgLangParser.IdPrimaryContext):
        pass


    # Enter a parse tree produced by ImgLangParser#CastPrimary.
    def enterCastPrimary(self, ctx:ImgLangParser.CastPrimaryContext):
        pass

    # Exit a parse tree produced by ImgLangParser#CastPrimary.
    def exitCastPrimary(self, ctx:ImgLangParser.CastPrimaryContext):
        pass


    # Enter a parse tree produced by ImgLangParser#ThisPrimary.
    def enterThisPrimary(self, ctx:ImgLangParser.ThisPrimaryContext):
        pass

    # Exit a parse tree produced by ImgLangParser#ThisPrimary.
    def exitThisPrimary(self, ctx:ImgLangParser.ThisPrimaryContext):
        pass


    # Enter a parse tree produced by ImgLangParser#SuperPrimary.
    def enterSuperPrimary(self, ctx:ImgLangParser.SuperPrimaryContext):
        pass

    # Exit a parse tree produced by ImgLangParser#SuperPrimary.
    def exitSuperPrimary(self, ctx:ImgLangParser.SuperPrimaryContext):
        pass


    # Enter a parse tree produced by ImgLangParser#MemberAccessPrimary.
    def enterMemberAccessPrimary(self, ctx:ImgLangParser.MemberAccessPrimaryContext):
        pass

    # Exit a parse tree produced by ImgLangParser#MemberAccessPrimary.
    def exitMemberAccessPrimary(self, ctx:ImgLangParser.MemberAccessPrimaryContext):
        pass


    # Enter a parse tree produced by ImgLangParser#ParenPrimary.
    def enterParenPrimary(self, ctx:ImgLangParser.ParenPrimaryContext):
        pass

    # Exit a parse tree produced by ImgLangParser#ParenPrimary.
    def exitParenPrimary(self, ctx:ImgLangParser.ParenPrimaryContext):
        pass


    # Enter a parse tree produced by ImgLangParser#literal.
    def enterLiteral(self, ctx:ImgLangParser.LiteralContext):
        pass

    # Exit a parse tree produced by ImgLangParser#literal.
    def exitLiteral(self, ctx:ImgLangParser.LiteralContext):
        pass


    # Enter a parse tree produced by ImgLangParser#NormalCall.
    def enterNormalCall(self, ctx:ImgLangParser.NormalCallContext):
        pass

    # Exit a parse tree produced by ImgLangParser#NormalCall.
    def exitNormalCall(self, ctx:ImgLangParser.NormalCallContext):
        pass


    # Enter a parse tree produced by ImgLangParser#funcName.
    def enterFuncName(self, ctx:ImgLangParser.FuncNameContext):
        pass

    # Exit a parse tree produced by ImgLangParser#funcName.
    def exitFuncName(self, ctx:ImgLangParser.FuncNameContext):
        pass


    # Enter a parse tree produced by ImgLangParser#argumentList.
    def enterArgumentList(self, ctx:ImgLangParser.ArgumentListContext):
        pass

    # Exit a parse tree produced by ImgLangParser#argumentList.
    def exitArgumentList(self, ctx:ImgLangParser.ArgumentListContext):
        pass


    # Enter a parse tree produced by ImgLangParser#builtInFunction.
    def enterBuiltInFunction(self, ctx:ImgLangParser.BuiltInFunctionContext):
        pass

    # Exit a parse tree produced by ImgLangParser#builtInFunction.
    def exitBuiltInFunction(self, ctx:ImgLangParser.BuiltInFunctionContext):
        pass



del ImgLangParser