# lexer/lexer.py
from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from antlr.ImgLangLexer import ImgLangLexer
from errors.base import SourceLocation, SyntaxError

class LexerErrorListener(ErrorListener):
    """Слушатель ошибок для лексера"""
    def __init__(self):
        super().__init__()
        self.errors = []
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(SyntaxError(
            message=msg,
            location=SourceLocation(line=line, column=column + 1),
            severity="error"
        ))

class ImgLexer:
    """Обёртка над ANTLR лексером"""
    
    def __init__(self, source_code: str):
        self.input_stream = InputStream(source_code)
        self.antlr_lexer = ImgLangLexer(self.input_stream)
        self.token_stream = CommonTokenStream(self.antlr_lexer)
        
        self.error_listener = LexerErrorListener()
        self.antlr_lexer.removeErrorListeners()
        self.antlr_lexer.addErrorListener(self.error_listener)
    
    def tokenize(self):
        """Токенизирует исходный код"""
        self.token_stream.fill()
        tokens = self.token_stream.tokens
        errors = self.error_listener.errors
        return tokens, errors
    
    def get_token_stream(self):
        """Возвращает поток токенов"""
        return self.token_stream