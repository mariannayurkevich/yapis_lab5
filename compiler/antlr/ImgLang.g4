grammar ImgLang;

// ==========================================
// ОСНОВНАЯ СТРУКТУРА ПРОГРАММЫ
// ==========================================

// Программа состоит из набора объявлений функций, структур или свободных операторов
program: (functionDecl | structDecl | statement)* EOF;

// Объявление структуры (класса). Поддерживает наследование (extends)
structDecl:
    'struct' ID ('extends' ID)? '{'
        (memberDecl)*
    '}' ';'?
    ;

// Элемент структуры: поле или метод с модификатором доступа
memberDecl:
    accessModifier (fieldDecl | methodDecl)
    ;

// Модификаторы доступа в стиле ООП
accessModifier: 'public' | 'protected' | 'private';

// Объявление поля структуры (например: public int x;)
fieldDecl: type ID ';' ;

// Объявление метода внутри структуры. Может быть виртуальным или переопределенным
methodDecl:
    ('virtual' | 'override')? 'proc' ID
    '(' parameterList? ')' ('->' type)? block
    ;

// Глобальная функция (вне структуры)
functionDecl:
    'proc' ID '(' parameterList? ')' ('->' type)? block
    ;

// Список параметров через запятую
parameterList:
    parameter (',' parameter)*
    ;

// Параметр может передаваться по значению (value) или как результат (result - аналог ref/out)
parameter:
    ('value' | 'result')? type ID
    ;

// Типы данных: встроенные примитивы, типы для работы с графикой или пользовательские ID (структуры)
type:
    'image' | 'int' | 'float' | 'color' | 'pixel' | 'bool' | 'string' | ID
    ;

// Блок кода может быть либо в фигурных скобках {}, либо в стиле Pascal (begin...end)
block:
    '{' statement* '}'          # BraceBlock
    | BEGIN statement* END      # BeginEndBlock
    ;

// ==========================================
// ОПЕРАТОРЫ (STATEMENTS)
// ==========================================

statement:
    variableDecl           // Объявление переменной
    | assignment           // Присваивание
    | forLoop              // Цикл for
    | whileLoop            // Цикл while
    | doUntilLoop          // Цикл do-until
    | ifStatement          // Условие if-then-else
    | functionCall ';'     // Вызов функции как отдельная строка
    | expression ';'       // Любое выражение
    | returnStatement      // Возврат из функции
    | superCall ';'        // Вызов конструктора/метода родителя
    ;

returnStatement: 'return' expression? ';' ;

superCall: 'super' '(' argumentList? ')' ;

whileLoop:
    WHILE '(' expression ')' block
    ;

// Цикл "выполнять пока условие ложно" (аналог do-while с инверсией)
doUntilLoop:
    DO block UNTIL '(' expression ')' ';'? ;

// Объявление переменных: тип имя = значение, имя2...
variableDecl:
    type variableList ';'
    ;

variableList:
    variableEntry (',' variableEntry)* ;

variableEntry:
    ID ('=' expression)?;

// Различные виды присваивания
assignment:
    ID '=' expression ';'                        # SingleAssign       // Обычное: x = 5;
    | idList '=' exprList ';'                    # MultiAssign        // Множественное: x, y = 1, 2;
    | expression '.' ID '=' expression ';'       # StructFieldAssign  // Полю структуры: obj.x = 5;
    | 'this' '.' ID '=' expression ';'           # ThisFieldAssign    // Через this: this.x = 5;
    ;

idList:
    ID (',' ID)* ;

exprList:
    expression (',' expression)* ;

forLoop:
    'for' '(' forInit ';' forCondition ';' forUpdate ')' block
    ;

forInit:
    type ID '=' expression
    | ID '=' expression
    ;

forCondition:
    expression
    ;

forUpdate:
    ID '=' expression
    ;

ifStatement
    : IF '(' expression ')' (THEN)? block (ELSE block)? ';'?
    ;

// ==========================================
// ВЫРАЖЕНИЯ И ПРИОРИТЕТ ОПЕРАТОРОВ (от низшего к высшему)
// ==========================================

expression:
    logicalOr
    ;

logicalOr:
    logicalAnd (OR logicalAnd)*
    ;

logicalAnd:
    equality (AND equality)*
    ;

equality:
    comparison (('==' | '!=') comparison)*
    ;

comparison:
    addition (('<' | '>' | '<=' | '>=') addition)*
    ;

addition:
    multiplication (('+' | '-') multiplication)*
    ;

multiplication:
    power (('*' | '/' | '%') power)*
    ;

// Операция возведения в степень (2 ** 3)
power:
    unary ('**' unary)*
    ;

// Унарные операции: отрицание (-x) или логическое НЕ (!true)
unary:
    primary
    | ('-' | '!') unary
    ;

// Базовые элементы выражений
primary:
    literal                                  # LiteralPrimary         // Числа, строки, булевы значения
    | ID                                     # IdPrimary              // Имя переменной
    | 'this'                                 # ThisPrimary            // Ссылка на себя
    | 'super'                                # SuperPrimary           // Ссылка на родителя
    | '(' expression ')'                     # ParenPrimary           // Выражение в скобках
    | '(' type ')' expression                # CastPrimary            // Явное приведение типов: (int)x
    | functionCall                           # FunctionCallPrimary    // Вызов функции
    | 'new' ID '(' argumentList? ')'         # ConstructorPrimary     // Создание объекта: new MyStruct()
    | primary '.' ID                         # MemberAccessPrimary    // Доступ к полю: obj.field
    | primary '.' ID '(' argumentList? ')'   # MethodCallPrimary      // Вызов метода: obj.method()
    | 'super' '(' argumentList? ')'          # SuperConstructorCall   // Вызов конструктора родителя
    ;

literal:
    INT
    | FLOAT
    | STRING
    | TRUE
    | FALSE
    ;

functionCall:
    funcName '(' argumentList? ')'                     # NormalCall
    ;

funcName: 
    ID 
    | builtInFunction
    ;

argumentList:
    expression (',' expression)*
    ;

// Встроенные функции языка для обработки изображений и ввода-вывода
builtInFunction:
    LOAD_IMAGE | SAVE_IMAGE | CREATE_IMAGE |
    GET_WIDTH | GET_HEIGHT | GET_PIXEL | SET_PIXEL |
    TO_COLOR | CLAMP | WRITE | READ_INT
    ;

// ==========================================
// ЛЕКСЕР (КЛЮЧЕВЫЕ СЛОВА И ТОКЕНЫ)
// ==========================================

PROC: 'proc';
STRUCT: 'struct';
VALUE: 'value';
RESULT: 'result';
IMAGE: 'image';
INT_TYPE: 'int';
FLOAT_TYPE : 'float' ;
COLOR: 'color';
PIXEL: 'pixel';
BOOL: 'bool';
STRING_TYPE: 'string';
FOR: 'for';
IF: 'if';
ELSE: 'else';
TRUE: 'true';
FALSE: 'false';
THEN: 'then';
BEGIN: 'begin';
END: 'end';
WHILE: 'while';
DO: 'do';
UNTIL: 'until';
PUBLIC: 'public';
PROTECTED: 'protected';
PRIVATE: 'private';
RETURN: 'return';
THIS: 'this';
SUPER: 'super';
VIRTUAL: 'virtual';
OVERRIDE: 'override';
NEW: 'new';
EXTENDS: 'extends';

// Встроенные функции как ключевые слова лексера
LOAD_IMAGE: 'load_image';
SAVE_IMAGE: 'save_image';
CREATE_IMAGE: 'create_image';
GET_WIDTH: 'get_width';
GET_HEIGHT: 'get_height';
GET_PIXEL: 'get_pixel';
SET_PIXEL: 'set_pixel';
TO_COLOR: 'to_color';
CLAMP: 'clamp';
WRITE: 'write';
READ_INT: 'read_int';

// Определение базовых типов (числа, строки, идентификаторы)
INT: [0-9]+;
STRING: '"' ~["\r\n]* '"';
FLOAT : [0-9]+ '.' [0-9]+ ;
ID: [a-zA-Z_][a-zA-Z_0-9]*;

// Пропуски (пробелы, табы, переносы строк) и комментарии
WS: [ \t\r\n]+ -> skip;
LINE_COMMENT: '//' ~[\r\n]* -> skip;
BLOCK_COMMENT: '/*' .*? '*/' -> skip;

// Операторы пунктуации и математики
PLUS: '+';
MINUS: '-';
MUL: '*';
DIV: '/';
MOD: '%';
ASSIGN: '=';
LT: '<';
GT: '>';
LE: '<=';
GE: '>=';
EQ: '==';
NE: '!=';
AND: '&&';
OR : '||';
POW: '**';
NOT: '!';

LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
COMMA: ',';
SEMI: ';';
DOT: '.';
ARROW: '->';