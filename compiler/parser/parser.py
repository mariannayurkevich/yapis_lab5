from antlr4 import ParserRuleContext
from antlr4.error.ErrorListener import ErrorListener
from antlr.ImgLangParser import ImgLangParser
from errors.base import SourceLocation, SyntaxError
from .ast_builder import ASTBuilder

class ParserErrorListener(ErrorListener):
    """Слушатель ошибок для парсера"""
    def __init__(self):
        super().__init__()
        self.errors = []
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(SyntaxError(
            message=msg,
            location=SourceLocation(line=line, column=column + 1),
            severity="error"
        ))

class ImgParser:
    """Обёртка над ANTLR парсером"""
    
    def __init__(self, token_stream):
        self.antlr_parser = ImgLangParser(token_stream)
        
        self.error_listener = ParserErrorListener()
        self.antlr_parser.removeErrorListeners()
        self.antlr_parser.addErrorListener(self.error_listener)
        
        self.ast_builder = ASTBuilder()
    
    def parse(self):
        """Парсит поток токенов и возвращает AST"""
        try:
            parse_tree = self.antlr_parser.program()
            
            print(f"Parse tree: {parse_tree}")
            print(f"Parse errors: {self.error_listener.errors}")
            
            if self.error_listener.errors:
                return None, self.error_listener.errors
            
            ast = self.ast_builder.visit(parse_tree) if parse_tree else None
            return ast, []
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            
            error = SyntaxError(
                message=f"Parser error: {str(e)}",
                location=None,
                severity="error"
            )
            return None, [error]