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
# Returns: If the tokens are valid, it returns that the tokens are valid, otherwise it returns an error message
def parser(tokens):
    index = 0

    def current():
        return tokens[index] if index < len(tokens) else None

    def match(expected):
        nonlocal index
        if current() == expected:
            index += 1
            return True
        return False

    def expect(expected):
        if not match(expected):
            raise SyntaxError(f"Expected '{expected}', got '{current()}'")

    def parse_program():
        expect('int')
        expect('main')
        expect('(')
        expect(')')
        expect('{')
        parse_statement_list()
        expect('}')
        print("✅ Program is syntactically correct!")

    def parse_statement_list():
        while current() in ['std', 'return']:
            parse_statement()

    def parse_statement():
        if current() == 'std':
            parse_cout_statement()
        elif current() == 'return':
            parse_return_statement()
        else:
            raise SyntaxError(f"Unexpected statement start: {current()}")

    def parse_cout_statement():
        expect('std')
        expect('::')
        expect('cout')
        expect('<<')
        parse_cout_item()
        parse_cout_tail()
        expect(';')

    def parse_cout_item():
        if current() is None:
            raise SyntaxError("Expected cout item but got end of input")
        token = current()

        # Caso especial: std::endl
        if token == 'std' and tokens[index + 1] == '::' and tokens[index + 2] == 'endl':
            match('std')
            match('::')
            match('endl')
        elif token.startswith('"') and token.endswith('"'):
            match(token)
        elif token.isidentifier() or token.isdigit():
            match(token)
        else:
            raise SyntaxError(f"Invalid cout item: {token}")


    def parse_cout_tail():
        while current() == '<<':
            match('<<')
            parse_cout_item()

    def parse_return_statement():
        expect('return')
        if current() and current().isdigit():
            match(current())
        else:
            raise SyntaxError(f"Expected number after return, got {current()}")
        expect(';')

    # Start parsing
    try:
        parse_program()
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")


with open("cpp_file.cpp", "r") as file:
    fileString = file.read()

tokens = lexer(fileString)
print(tokens)
parser(tokens)