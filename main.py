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
        if char.isalpha() or char == '_':
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

        # Check for symbols
        if char in ['+', '-', '*', '/', '=', '(', ')', '{', '}', ';', ',', ':', '!', '<', '>', '&', '|', '^', '~', '?', '"']:
            tokens.append(char)
            i += 1
            continue

        # If we reach here, it's an unknown character
        print(f"Unknown character: {char}")
        i += 1
    return tokens

# Recursive descent parser
# Params: tokens (list): The list of tokens to parse
# Returns: If the tokens are valid, it returns that the tokens are valid, otherwise it returns an error message
def parser(tokens):
    print(tokens)

with open("cpp_file.cpp", "r") as file:
    fileString = file.read()

tokens = lexer(fileString)
parser(tokens)