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

# Recursive descent parser based on the CFG
# Params: tokens (list): The list of tokens from the lexer
# Returns: Prints a success or error message
def parser(tokens):
    index = 0
    # Updated KEYWORDS list
    KEYWORDS = [
        'int', 'main', 'std', 'cout', 'cin', 'endl', 'return',
        'float', 'char', 'string', 'if', 'else', 'while'
    ]
    RELATIONAL_OPERATORS = ['==', '!=', '<', '<=', '>', '>=']
    ARITHMETIC_OPERATORS = ['+', '-', '*', '/']

    def current_token():
        return tokens[index] if index < len(tokens) else None

    def match(expected_type_or_value):
        nonlocal index
        tok = current_token()
        if tok is None:
            return False

        if expected_type_or_value == 'IDENTIFIER':
            # Lexer provides a string. Parser checks if it looks like an identifier and isn't a keyword.
            if isinstance(tok, str) and tok.isidentifier() and tok not in KEYWORDS:
                index += 1
                return True
            return False
        elif expected_type_or_value == 'NUMBER':
            # Lexer provides a string. Parser checks if it looks like a number.
            if isinstance(tok, str):
                # Handle simple integers and basic decimals like "123", "123.45"
                import re
                if re.fullmatch(r'[0-9]+(\.[0-9]+)?', tok):
                    index += 1
                    return True
            return False
        elif expected_type_or_value == 'STRING_LITERAL':
            # Lexer provides a string. Parser checks if it's quoted.
            if isinstance(tok, str) and tok.startswith('"') and tok.endswith('"'):
                index += 1
                return True
            return False
        # For specific keywords or symbols (terminals in CFG)
        elif tok == expected_type_or_value:
            index += 1
            return True
        return False

    def expect(expected_type_or_value):
        token_at_error = current_token()
        if not match(expected_type_or_value):
            error_message = f"Expected '{expected_type_or_value}', but got '{token_at_error}'"
            raise SyntaxError(f"{error_message} (at token index {index})")

    # --- Grammar Rule Parsing Functions ---

    def parse_program():
        expect('int')
        expect('main')
        expect('(')
        expect(')')
        expect('{')
        parse_statement_list()
        expect('}')
        if current_token() is not None:
            raise SyntaxError(f"Unexpected token '{current_token()}' after end of program.")
        print("✅ Program is syntactically correct!")

    def parse_statement_list():
        # <StatementList> → <Statement> <StatementList> | ε
        while current_token() is not None and current_token() != '}':
            parse_statement()
        # Epsilon case is handled by the loop condition: if no statement starts, it does nothing.

    def parse_statement():
        nonlocal index
        tok = current_token()
        if tok is None: 
            raise SyntaxError("Unexpected end of input while expecting a statement.")

        if tok == 'std': 
            if index + 2 < len(tokens): 
                if tokens[index + 2] == 'cout':
                    parse_cout_statement()
                elif tokens[index + 2] == 'cin':
                    parse_cin_statement()
                else:
                    raise SyntaxError(f"Expected 'cout' or 'cin' after 'std::', got '{tokens[index+2]}'")
            else:
                raise SyntaxError("Incomplete 'std::' statement.")
        elif tok == 'return':
            parse_return_statement()
        elif tok in ['int', 'float', 'char', 'string']: 
            parse_variable_statement()
        elif tok == 'if':
            parse_if_statement()
        elif tok == 'while':
            parse_while_statement()
        elif match('IDENTIFIER'): 
            index -=1
            if index + 1 < len(tokens) and tokens[index+1] == '=':
                 parse_assignment_statement()
            else:
                 raise SyntaxError(f"Identifier '{current_token()}' initiated a statement but was not followed by '=' for assignment, or is not part of another valid statement structure here.")
        else:
            raise SyntaxError(f"Unexpected token '{tok}' at start of a statement.")

    def parse_variable_statement():
        # <VariableStatement> → <Type> <IDENTIFIER> ';'
        #                    | <Type> <IDENTIFIER> '=' <ComplexExpression> ';'
        parse_type()
        expect('IDENTIFIER')
        if current_token() == '=':
            match('=')
            parse_complex_expression()
            expect(';')
        elif current_token() == ';':
            match(';')
        else:
            raise SyntaxError(f"Expected '=' or ';' after identifier in variable declaration, got '{current_token()}'")

    def parse_assignment_statement():
        # <AssignmentStatement> → <IDENTIFIER> '=' <ComplexExpression> ';'
        expect('IDENTIFIER')
        expect('=')
        parse_complex_expression()
        expect(';')

    def parse_expression():
        # <Expression> → <NUMBER> | <IDENTIFIER>
        if not (match('NUMBER') or match('IDENTIFIER')):
            raise SyntaxError(f"Expected NUMBER or IDENTIFIER for expression, got '{current_token()}'")

    def parse_complex_expression():
        # <ComplexExpression> → <Expression> <ExpressionChain>
        parse_expression()
        parse_expression_chain()

    def parse_expression_chain():
        # <ExpressionChain> → <Operator> <Expression> <ExpressionChain> | ε
        if current_token() in ARITHMETIC_OPERATORS:
            parse_operator()
            parse_expression()
            parse_expression_chain()
        # Epsilon case: do nothing

    def parse_operator():
        # <Operator> → '+' | '-' | '*' | '/'
        op = current_token()
        if op in ARITHMETIC_OPERATORS:
            match(op)
        else:
            raise SyntaxError(f"Expected arithmetic operator (+, -, *, /), got '{op}'")

    def parse_type():
        # <Type> → 'int' | 'float' | 'char' | 'string'
        tok = current_token()
        if tok in ['int', 'float', 'char', 'string']:
            match(tok)
        else:
            raise SyntaxError(f"Expected type (int, float, char, string), got '{tok}'")

    def parse_cout_statement():
        # <CoutStatement> → 'std' '::' 'cout' '<<' <CoutItem> <CoutTail> ';'
        expect('std')
        expect('::')
        expect('cout')
        expect('<<')
        parse_cout_item()
        parse_cout_tail()
        expect(';')

    def parse_cout_tail():
        # <CoutTail> → '<<' <CoutItem> <CoutTail> | ε
        if current_token() == '<<':
            match('<<')
            parse_cout_item()
            parse_cout_tail()
        # Epsilon case: do nothing

    def parse_cout_item():
        # <CoutItem> → <STRING_LITERAL> | <NUMBER> | <IDENTIFIER> | 'std' '::' 'endl'
        if current_token() == 'std' and index + 2 < len(tokens) and \
           tokens[index+1] == '::' and tokens[index+2] == 'endl':
            match('std')
            match('::')
            match('endl')
        elif not (match('STRING_LITERAL') or match('NUMBER') or match('IDENTIFIER')):
            raise SyntaxError(f"Invalid cout item. Expected STRING_LITERAL, NUMBER, IDENTIFIER or 'std::endl', got '{current_token()}'")

    def parse_return_statement():
        # <ReturnStatement> → 'return' <NUMBER> ';'
        expect('return')
        expect('NUMBER')
        expect(';')

    def parse_cin_statement():
        # <CinStatement> → 'std' '::' 'cin' '>>' <CinItem> <CinTail> ';'
        expect('std')
        expect('::')
        expect('cin')
        expect('>>')
        parse_cin_item()
        parse_cin_tail()
        expect(';')

    def parse_cin_tail():
        # <CinTail> → '>>' <CinItem> <CinTail> | ε
        if current_token() == '>>':
            match('>>')
            parse_cin_item()
            parse_cin_tail()
        # Epsilon case: do nothing

    def parse_cin_item():
        # <CinItem> → <IDENTIFIER>
        expect('IDENTIFIER')

    def parse_if_statement():
        # <IfStatement> → 'if' '(' <Condition> ')' '{' <StatementList> '}' <ElseClause>
        expect('if')
        expect('(')
        parse_condition()
        expect(')')
        expect('{')
        parse_statement_list()
        expect('}')
        parse_else_clause()

    def parse_else_clause():
        # <ElseClause> → 'else' '{' <StatementList> '}' | 'else' <IfStatement> | ε
        if current_token() == 'else':
            match('else')
            if current_token() == 'if': # else if
                parse_if_statement()
            elif current_token() == '{': # else { ... }
                expect('{')
                parse_statement_list()
                expect('}')
            else:
                raise SyntaxError(f"Expected '{{' or 'if' after 'else', got '{current_token()}'")
        # Epsilon case: do nothing if no 'else' is found

    def parse_while_statement():
        # <WhileStatement> → 'while' '(' <Condition> ')' '{' <StatementList> '}'
        expect('while')
        expect('(')
        parse_condition()
        expect(')')
        expect('{')
        parse_statement_list()
        expect('}')

    def parse_condition():
        # <Condition> → <ComplexExpression> <RelationalOperator> <ComplexExpression>
        parse_complex_expression()
        parse_relational_operator()
        parse_complex_expression()

    def parse_relational_operator():
        # <RelationalOperator> → '==' | '!=' | '<' | '<=' | '>' | '>='
        op = current_token()
        if op in RELATIONAL_OPERATORS:
            match(op)
        else:
            raise SyntaxError(f"Expected relational operator, got '{op}'")

    try:
        if not tokens:
            raise SyntaxError("Cannot parse an empty list of tokens.")
        parse_program()
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")
    except IndexError:
        print(f"🚨 Parser Error: Unexpected end of input or index out of bounds near token {index}. Grammar might expect more tokens.")
    except Exception as e:
        print(f"🚨 An unexpected error occurred during parsing: {e} (at token index {index})")


with open("cpp_file.cpp", "r") as file:
    fileString = file.read()

tokens = lexer(fileString)
print(tokens)
parser(tokens)