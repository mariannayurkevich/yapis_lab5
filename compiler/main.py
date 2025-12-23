import sys
import os
import subprocess
from pathlib import Path

from lexer.lexer import ImgLexer
from parser.parser import ImgParser
from semantic.analyzer import SemanticAnalyzer
from codegen.cil_generator import CILGenerator
from errors.formatter import ErrorFormatter

def compile_program(source_file: str, output_file: str = None) -> bool:
    
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        print("🔍 Лексический анализ...")
        
        lexer = ImgLexer(source_code)
        tokens, lex_errors = lexer.tokenize()
        
        if lex_errors:
            print("❌ Лексические ошибки:")
            formatter = ErrorFormatter(source_code)
            print(formatter.format_all(lex_errors))
            return False
        
        print("✅ Лексический анализ завершён")
        print(f"   Найдено токенов: {len(tokens)}")
        
        print("🔍 Синтаксический анализ...")
        parser = ImgParser(lexer.get_token_stream())
        ast, parse_errors = parser.parse()
        
        if parse_errors:
            print("❌ Синтаксические ошибки:")
            formatter = ErrorFormatter(source_code)
            print(formatter.format_all(parse_errors))
            return False
        
        if ast is None:
            print("❌ Не удалось построить AST")
            return False
        
        print("✅ Синтаксический анализ завершён")
        print("🔍 Семантический анализ...")
        
        analyzer = SemanticAnalyzer()
        semantic_errors = analyzer.analyze(ast)
        
        if semantic_errors:
            print("❌ Семантические ошибки:")
            formatter = ErrorFormatter(source_code)
            print(formatter.format_all(semantic_errors))
            return False
        
        print("✅ Семантический анализ завершён")
        print("⚡ Генерация CIL кода...")
        
        generator = CILGenerator(analyzer.symbol_table)
        cil_code = generator.generate(ast)
        
        if output_file:
            il_file = output_file.replace('.exe', '.il')
            exe_file = output_file
        else:
            base_name = Path(source_file).stem
            il_file = f"{base_name}.il"
            exe_file = f"{base_name}.exe"
        
        with open(il_file, 'w', encoding='utf-8') as f:
            f.write(cil_code)
        print(f"✓ Сгенерирован IL файл: {il_file}")
        
        print("⚡ Компиляция в .exe...")
        
        try:
            result = subprocess.run([
                'ilasm',
                il_file,
                f'/output={exe_file}',
                '/quiet'
            ], capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print(f"✅ Успешно скомпилировано: {exe_file}")
                
                try:
                    os.remove(f"{Path(il_file).stem}.pdb")
                except:
                    pass
                
                return True
            else:
                print("❌ Ошибка компиляции IL:")
                print(result.stdout)
                print(result.stderr)
                print(f"IL файл сохранён: {il_file}")
                return False
                
        except FileNotFoundError:
            print("❌ Не найден ilasm. Убедитесь, что .NET Framework SDK установлен")
            print(f"IL файл сохранён: {il_file}")
            return False
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        sys.exit(1)

    success = compile_program(input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()