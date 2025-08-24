"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    # Token type constants
    KEYWORD = "keyword"
    SYMBOL = "symbol"
    IDENTIFIER = "identifier" 
    INT_CONST = "integerConstant"
    STRING_CONST = "stringConstant"

    # Define keywords
    KEYWORDS = {
        'class', 'constructor', 'function', 'method', 'field', 'static',
        'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
        'this', 'let', 'do', 'if', 'else', 'while', 'return'
    }

    # Define symbols
    SYMBOLS = {
        '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/',
        '&', '|', '<', '>', '=', '~', '^', '#'
    }

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_stream.read().splitlines()
        self.input_text = self._remove_comments(input_stream.read())
        self.tokens = self._tokenize()
        self.current_token = None
        self.current_token_idx = -1

    def _remove_comments(self, text: str) -> str:
        # Store string literals temporarily
        strings = []
        def store_string(match):
            strings.append(match.group(0))
            return f"__STRING_{len(strings)-1}__"
        
        # Replace string literals with placeholders
        text = re.sub(r'"[^"]*"', store_string, text)
        
        # Remove /* ... */ comments
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        
        # Remove // comments
        text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
        
        # Restore string literals
        def restore_string(match):
            index = int(match.group(1))
            return strings[index]
        
        text = re.sub(r'__STRING_(\d+)__', restore_string, text)
        
        return text
    
    def _tokenize(self)->list:
        tokens = []
        i = 0
        text = self.input_text
        while(i<len(text)):
            char = text[i]

            # If whitespace continue:
            if char.isspace():
                i+=1
                continue

            # Check if char is a symbol:
            if char in JackTokenizer.SYMBOLS:
                tokens.append((self.SYMBOL,char))
                i+=1
                continue

            # Handle Keywords and identifiers:
            if char.isalpha() or char == '_':
                identifier = ''
                while i < len(text) and (text[i].isdigit() or text[i].isalpha() or text[i] == '_'):
                    identifier+=text[i]
                    i+=1
                if identifier in JackTokenizer.KEYWORDS:
                    tokens.append((self.KEYWORD,identifier))
                else:
                    tokens.append((self.IDENTIFIER,identifier))
                continue

            # Handle numbers
            if char.isdigit():
                num = ''
                while i < len(text) and text[i].isdigit():
                    num += text[i]
                    i += 1
                if 0 <= int(num) <= 32767:
                    tokens.append((self.INT_CONST, int(num)))
                    continue

            # Handle string constants
            if char == '"':
                string = ''
                i += 1  # Skip opening quote
                while i < len(text):
                    if text[i] == '\\' and i + 1 < len(text) and text[i + 1] == '"':
                        # Handle escaped quote
                        string += '"'
                        i += 2  # Skip both the backslash and quote
                    elif text[i] == '"':
                        # Found unescaped closing quote
                        break
                    elif text[i] != '\n':
                        string += text[i]
                        i += 1
                    else:
                        i += 1
                        
                if i < len(text):  # Found closing quote
                    tokens.append((self.STRING_CONST, string))
                    i += 1  # Skip closing quote
                continue

            i+=1

        return tokens

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        if self.current_token_idx < len(self.tokens) - 1:
            return True
        else:
            return False

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # Your code goes here!
        if self.has_more_tokens():
            self.current_token_idx+=1
            self.current_token = self.tokens[self.current_token_idx]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        if self.current_token:
            return self.current_token[0]
        else:
            raise ValueError("The current token is empty")

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        if self.token_type() == self.KEYWORD:
            return self.current_token[1]
        else:
            raise ValueError("The current token is not a keyword.")

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        # Your code goes here!
        if self.token_type() == self.SYMBOL:
            return self.current_token[1]
        else:
            raise ValueError("The current token is not a symbol.")

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        # Your code goes here!
        if self.token_type() == self.IDENTIFIER:
            return self.current_token[1]
        else:
            raise ValueError("The current token is not an identifier.")

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        # Your code goes here!
        if self.token_type() == self.INT_CONST:
            return self.current_token[1]
        else:
            raise ValueError("The current token is not an constant integer.")

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        # Your code goes here!
        if self.token_type() == self.STRING_CONST:
            return self.current_token[1]
        else:
            raise ValueError("The current token is not an constant string.")
