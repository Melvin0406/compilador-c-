# The lexer will receive a text and it will separate it into tokens. Each word, variable and symbol will be a token.
# Params: text (str): The program in C++
# Returns: list: A list of tokens
def lexer(fileString):
    tokens = []

    i = 0
    while i < len(fileString):
        char = fileString[i]

        # Skip whitespace
        if char.isspace():
            i += 1
            continue

        # Check for keywords and identifiers
        if  char.isalpha() or char == '_':
            start = i
            while i < len(fileString) and (fileString[i].isalnum() or fileString[i] == '_'):
                i += 1
            tokens.append(fileString[start:i])
            continue

        # Check for numbers
        if char.isdigit():
            start = i
            while i < len(fileString) and fileString[i].isdigit():
                i += 1
            tokens.append(fileString[start:i])
            continue

        # Check for multi-character operators first
        if fileString[i:i+2] in ['::', '<<', '>>', '<=', '>=', '==', '!=']:
            tokens.append(fileString[i:i+2])
            i += 2
            continue

        # Then check for single-character symbols
        if char in ['+', '-', '*', '/', '=', '(', ')', '{', '}', ';', ',', ':', '!', '<', '>', '&', '|', '^', '~', '?']:
            tokens.append(char)
            i += 1
            continue

        # Handle string literals
        if char == '"':
            start = i
            i += 1
            while i < len(fileString) and fileString[i] != '"':
                i += 1
            i += 1  # include closing "
            tokens.append(fileString[start:i])
            continue


        # If we reach here, it's an unknown character
        print(f"Unknown character: {char}")
        i += 1
    return tokens

# Recursive descent parser
# Params: tokens (list): The list of tokens to parse
# Returns: If the tokens are valid, it prints a success message, otherwise it prints an error message
def parser(tokens):
    index = 0
    KEYWORDS = ['int', 'main', 'std', 'cout', 'cin', 'endl', 'return', 'float', 'char', 'string']

    def current():
        return tokens[index] if index < len(tokens) else None

    def match(expected_type_or_value):
        nonlocal index
        tok = current()
        if tok is None:
            return False

        if expected_type_or_value == 'IDENTIFIER':
            # Un identificador no debe ser una palabra clave y debe cumplir con las reglas de identificador.
            # Asumimos que el lexer ya ha validado la forma del identificador (e.g., empieza con letra o _, seguido de alfanuméricos o _)
            # Aquí solo verificamos que no sea una palabra clave reservada.
            if tok.isidentifier() and tok not in KEYWORDS:
                index += 1
                return True
            return False
        elif expected_type_or_value == 'NUMBER':
            # Asumimos que el lexer ya ha validado que es un número.
            if tok.isdigit(): # Simple check, podría ser más robusto (e.g., para floats si los soportara el lexer como 'NUMBER')
                index += 1
                return True
            return False
        elif expected_type_or_value == 'STRING':
            # Asumimos que el lexer devuelve los strings con sus comillas.
            if tok.startswith('"') and tok.endswith('"'):
                index += 1
                return True
            return False
        # Si es un token literal (palabra clave o símbolo)
        elif tok == expected_type_or_value:
            index += 1
            return True
        return False

    def expect(expected_type_or_value):
        # Guardar el token actual para el mensaje de error, antes de intentar hacer match
        token_before_match = current()
        if not match(expected_type_or_value):
            # Adaptar el mensaje de error si se esperaba un tipo de token
            if expected_type_or_value in ['IDENTIFIER', 'NUMBER', 'STRING']:
                raise SyntaxError(f"Expected {expected_type_or_value}, got '{token_before_match}' at index {index}")
            else:
                raise SyntaxError(f"Expected '{expected_type_or_value}', got '{token_before_match}' at index {index}")

    def parse_program():
        expect('int')
        expect('main')
        expect('(')
        expect(')')
        expect('{')
        parse_statement_list()
        expect('}')
        if current() is not None: # Verificar si hay tokens extra después del '}'
            raise SyntaxError(f"Unexpected token '{current()}' after end of program at index {index}.")
        print("✅ Program is syntactically correct!")

    def parse_statement_list():
        # Un StatementList puede estar vacío (ε) o contener uno o más Statements.
        # El bucle continúa mientras el token actual pueda iniciar un Statement y no sea '}'
        while current() is not None and current() != '}':
            parse_statement()

    def parse_statement():
        tok = current()
        if tok == 'std':
            # Necesitamos mirar hacia adelante para distinguir entre cout y cin
            if index + 2 < len(tokens): # Asegurar que hay suficientes tokens para std::xxx
                if tokens[index+2] == 'cout': # std :: cout
                    parse_cout_statement()
                elif tokens[index+2] == 'cin': # std :: cin
                    parse_cin_statement()
                else:
                    raise SyntaxError(f"Expected 'cout' or 'cin' after 'std::', got '{tokens[index+2]}' at index {index+2}")
            else:
                raise SyntaxError(f"Incomplete 'std::' statement at index {index}")
        elif tok == 'return':
            parse_return_statement()
        elif tok in ['int', 'float', 'char', 'string']: # Inicio de VariableStatement
            parse_variable_statement()
        elif tok is not None and tok.isidentifier() and tok not in KEYWORDS: # Potencial inicio de AssignmentStatement
            # Para ser un AssignmentStatement, debe ser IDENTIFIER = ...
            # Necesitamos mirar adelante para el '='
            if index + 1 < len(tokens) and tokens[index+1] == '=':
                parse_assignment_statement()
            else:
                raise SyntaxError(f"Invalid statement. Identifier '{tok}' not followed by '=' for assignment or not a recognized statement start at index {index}.")
        else:
            # Si StatementList está vacío (ε) y current() es '}', parse_statement_list lo manejará.
            # Si current() no es '}' y no es el inicio de ninguna declaración conocida, es un error.
            raise SyntaxError(f"Unexpected token '{tok}' at start of statement at index {index}")

    def parse_type():
        tok = current()
        if tok in ['int', 'float', 'char', 'string']:
            match(tok) # Consume el token de tipo
        else:
            raise SyntaxError(f"Expected a type (int, float, char, string), got '{tok}' at index {index}")

    def parse_expression():
        if match('NUMBER'):
            pass # El token ya fue consumido por match
        elif match('IDENTIFIER'):
            pass # El token ya fue consumido por match
        else:
            raise SyntaxError(f"Expected NUMBER or IDENTIFIER for expression, got '{current()}' at index {index}")

    def parse_variable_statement():
        parse_type()  # Consume 'int', 'float', 'char', 'string'
        expect('IDENTIFIER') # Consume el nombre de la variable

        if current() == '=':
            match('=') # Consume '='
            parse_expression() # Consume el valor de la inicialización
            expect(';') # Consume ';'
        elif current() == ';':
            match(';') # Consume ';' para declaración sin inicialización
        else:
            raise SyntaxError(f"Expected '=' or ';' after identifier in variable declaration, got '{current()}' at index {index}")

    def parse_assignment_statement():
        expect('IDENTIFIER') # Consume el nombre de la variable a la izquierda del igual
        expect('=')
        parse_expression()
        expect(';')

    def parse_cout_statement():
        expect('std')
        expect('::')
        expect('cout')
        expect('<<')
        parse_cout_item()
        parse_cout_tail()
        expect(';')

    def parse_cout_item():
        # Caso especial: std::endl
        if current() == 'std' and index + 2 < len(tokens) and \
           tokens[index + 1] == '::' and tokens[index + 2] == 'endl':
            match('std')
            match('::')
            match('endl')
        elif match('STRING'):
            pass
        elif match('NUMBER'):
            pass
        elif match('IDENTIFIER'):
            pass
        else:
            if current() is None:
                raise SyntaxError(f"Unexpected end of input when expecting a cout item at index {index}")
            raise SyntaxError(f"Invalid cout item: '{current()}' at index {index}")

    def parse_cout_tail():
        while current() == '<<':
            match('<<')
            parse_cout_item()

    def parse_cin_statement():
        expect('std')
        expect('::')
        expect('cin')
        expect('>>')
        parse_cin_item()
        parse_cin_tail()
        expect(';')

    def parse_cin_item():
        expect('IDENTIFIER') # cin usualmente lee en un identificador (variable)

    def parse_cin_tail():
        while current() == '>>':
            match('>>')
            parse_cin_item()

    def parse_return_statement():
        expect('return')
        expect('NUMBER') # return solo acepta un número según la gramática
        expect(';')

    # Start parsing
    try:
        parse_program()
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
    except Exception as e: # Captura general para otros posibles errores (ej. IndexError)
        print(f"🚨 An unexpected error occurred: {e} (likely an issue with token list or parser logic beyond syntax)")


with open("cpp_file.cpp", "r") as file:
    fileString = file.read()

tokens = lexer(fileString)
print(tokens)
parser(tokens)