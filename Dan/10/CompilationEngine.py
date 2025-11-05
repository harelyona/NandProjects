"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: JackTokenizer, output_stream:typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.output = output_stream

        # For knowing how many indents to make:
        self.indent_level = 0

    # Function for writing a line:
    def write_to_file(self, content: str) -> None:
        self.output.write("  " * self.indent_level + content + "\n")

    def write_terminal(self) -> None:
        token_type = self.tokenizer.token_type()
        if token_type == JackTokenizer.SYMBOL:
            content = self.tokenizer.symbol()
        elif token_type == JackTokenizer.KEYWORD:
            content = self.tokenizer.keyword()
        elif token_type == JackTokenizer.IDENTIFIER:
            content = self.tokenizer.identifier()
        elif token_type == JackTokenizer.INT_CONST:
            content = str(self.tokenizer.int_val())
        elif token_type == JackTokenizer.STRING_CONST:
            content = self.tokenizer.string_val()
        else:
            raise ValueError("The token isn't legal.")

        self.write_to_file(f"<{token_type}> {content} </{token_type}>")

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.write_to_file("<class>")
        self.indent_level += 1
        
        # class
        self.write_terminal()
        self.tokenizer.advance()
        
        # className
        self.write_terminal()
        self.tokenizer.advance()
        
        # {
        self.write_terminal()
        self.tokenizer.advance()
        
        # classVarDec*
        while self.tokenizer.token_type() == JackTokenizer.KEYWORD and \
              self.tokenizer.keyword() in ["static", "field"]:
            self.compile_class_var_dec()
            
        # subroutineDec*
        while self.tokenizer.token_type() == JackTokenizer.KEYWORD and \
              self.tokenizer.keyword() in ["constructor", "function", "method"]:
            self.compile_subroutine()
            
        # }
        self.write_terminal()
        
        self.indent_level -= 1
        self.write_to_file("</class>")
        

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.write_to_file("<classVarDec>")
        self.indent_level += 1 

        # static or field
        self.write_terminal()
        self.tokenizer.advance()

        # type 
        self.write_terminal()
        self.tokenizer.advance()

        # varName
        self.write_terminal()
        self.tokenizer.advance()
        
        # (',' varName)*
        while self.tokenizer.token_type() == JackTokenizer.SYMBOL and \
              self.tokenizer.symbol() == ",":
            self.write_terminal()
            self.tokenizer.advance()
            self.write_terminal()
            self.tokenizer.advance()

        # ;
        self.write_terminal()
        self.tokenizer.advance()

        self.indent_level -= 1
        self.write_to_file("</classVarDec>")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.write_to_file("<subroutineDec>")
        self.indent_level += 1

        # constructor or method or function
        self.write_terminal()
        self.tokenizer.advance()

        # type or void
        self.write_terminal()
        self.tokenizer.advance()

        # subroutineName
        self.write_terminal()
        self.tokenizer.advance()

        # (
        self.write_terminal()
        self.tokenizer.advance()

        # parameters list
        self.compile_parameter_list()

        # )
        self.write_terminal()
        self.tokenizer.advance()

        # start subroutinebody
        self.write_to_file("<subroutineBody>")
        self.indent_level += 1

        # {
        self.write_terminal()
        self.tokenizer.advance()

        # compile var dec
        while self.tokenizer.token_type() == JackTokenizer.KEYWORD and self.tokenizer.keyword() == "var":
            self.compile_var_dec()

        # compile statements
        self.compile_statements()

        # }
        self.write_terminal()
        self.tokenizer.advance()
        
        # end subroutinebody
        self.indent_level -= 1
        self.write_to_file("</subroutineBody>")

        self.indent_level -= 1
        self.write_to_file("</subroutineDec>")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.write_to_file("<parameterList>")
        self.indent_level += 1

        # ((type varName), (',' type varName)*)?
        if not (self.tokenizer.token_type() == JackTokenizer.SYMBOL and \
                self.tokenizer.symbol() == ")"):
            
            # type
            self.write_terminal()
            self.tokenizer.advance()

            # varName
            self.write_terminal()
            self.tokenizer.advance()

            # (',' type varName)*
            while self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == ",":
                # , 
                self.write_terminal()
                self.tokenizer.advance()

                # type
                self.write_terminal()
                self.tokenizer.advance()

                # varName
                self.write_terminal()
                self.tokenizer.advance()

        self.indent_level -= 1
        self.write_to_file("</parameterList>")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.write_to_file("<varDec>")
        self.indent_level += 1

        # var 
        self.write_terminal()
        self.tokenizer.advance()

        # type 
        self.write_terminal()
        self.tokenizer.advance()

        # varName 
        self.write_terminal()
        self.tokenizer.advance()

        # (',' varName)*
        while self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == ',':
            # ,
            self.write_terminal()
            self.tokenizer.advance()

            # varName 
            self.write_terminal()
            self.tokenizer.advance()

        # ;
        self.write_terminal()
        self.tokenizer.advance()

        self.indent_level -= 1
        self.write_to_file("</varDec>")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.write_to_file("<statements>")
        self.indent_level += 1

        while not (self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == '}'):
            keyword = self.tokenizer.keyword()
            if keyword == "let":
                self.compile_let()
            elif keyword == "if":
                self.compile_if()
            elif keyword == "while":
                self.compile_while()
            elif keyword == "do":
                self.compile_do()
            elif keyword == "return":
                self.compile_return()
            else:
                break
                                               
        self.indent_level -= 1
        self.write_to_file("</statements>")
        

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.write_to_file("<doStatement>")
        self.indent_level += 1

        # do
        self.write_terminal()
        self.tokenizer.advance()

        # subroutine call
        self.compile_subroutine_call()

        # ;
        self.write_terminal()
        self.tokenizer.advance()

        self.indent_level -= 1
        self.write_to_file("</doStatement>")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.write_to_file("<letStatement>")
        self.indent_level += 1

        # let 
        self.write_terminal()
        self.tokenizer.advance()

        # varName 
        self.write_terminal()
        self.tokenizer.advance()

        # ('[' expression ']')?
        if self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == '[':
            # [ 
            self.write_terminal()
            self.tokenizer.advance()

            # expression
            self.compile_expression()

            # ] 
            self.write_terminal()
            self.tokenizer.advance()
        
        # =
        self.write_terminal()
        self.tokenizer.advance()

        # expression 
        self.compile_expression()

        # ;
        self.write_terminal()
        self.tokenizer.advance()


        self.indent_level -= 1
        self.write_to_file("</letStatement>")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.write_to_file("<whileStatement>")
        self.indent_level += 1

        # while
        self.write_terminal()
        self.tokenizer.advance()

        # (
        self.write_terminal()
        self.tokenizer.advance()

        # expression
        self.compile_expression()

        # )
        self.write_terminal()
        self.tokenizer.advance()

        # {
        self.write_terminal()
        self.tokenizer.advance()

        # statements
        self.compile_statements()

        # }
        self.write_terminal()
        self.tokenizer.advance()


        self.indent_level -= 1
        self.write_to_file("</whileStatement>")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.write_to_file("<returnStatement>")
        self.indent_level += 1

        # return
        self.write_terminal()
        self.tokenizer.advance()

        # expression?
        if not (self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == ';'):
            # expression
            self.compile_expression()

        # ;
        self.write_terminal()
        self.tokenizer.advance()

        self.indent_level -= 1
        self.write_to_file("</returnStatement>")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.write_to_file("<ifStatement>")
        self.indent_level += 1

        # if
        self.write_terminal()
        self.tokenizer.advance()

        # (
        self.write_terminal()
        self.tokenizer.advance()

        # expression
        self.compile_expression()

        # )
        self.write_terminal()
        self.tokenizer.advance()

        # {
        self.write_terminal()
        self.tokenizer.advance()

        # statements
        self.compile_statements()

        # }
        self.write_terminal()
        self.tokenizer.advance()

        # (else '{' statements '}')?
        if self.tokenizer.token_type() == JackTokenizer.KEYWORD and self.tokenizer.keyword() == "else":
            # else
            self.write_terminal()
            self.tokenizer.advance()

            # {
            self.write_terminal()
            self.tokenizer.advance()

            # statements
            self.compile_statements()

            # }
            self.write_terminal()
            self.tokenizer.advance()


        self.indent_level -= 1
        self.write_to_file("</ifStatement>")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.write_to_file("<expression>")
        self.indent_level += 1

        # term
        self.compile_term()

        binary_op = ['+','-','*','/','&amp;','|','&lt;','&gt;','=']

        while  self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() in binary_op:
            # binary op
            self.write_terminal()
            self.tokenizer.advance()

            # term
            self.compile_term()

        self.indent_level -= 1
        self.write_to_file("</expression>")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.write_to_file("<term>")
        self.indent_level += 1

        # integerConstant
        if self.tokenizer.token_type() == JackTokenizer.INT_CONST:
            self.write_terminal()
            self.tokenizer.advance()
        # stringConstant
        elif self.tokenizer.token_type() == JackTokenizer.STRING_CONST:
            self.write_terminal()
            self.tokenizer.advance()
        # keywordConstant
        elif self.tokenizer.token_type() == JackTokenizer.KEYWORD and \
             self.tokenizer.keyword() in ["true", "false", "null", "this"]:
            self.write_terminal()
            self.tokenizer.advance()
        # ( expression )
        elif self.tokenizer.token_type() == JackTokenizer.SYMBOL and \
             self.tokenizer.symbol() == "(":
            # (
            self.write_terminal()
            self.tokenizer.advance()
            # expression
            self.compile_expression()
            # )
            self.write_terminal()
            self.tokenizer.advance()
        # unary op
        elif self.tokenizer.token_type() == JackTokenizer.SYMBOL and \
             self.tokenizer.symbol() in {'-','~','^','#'}:
            # unary op
            self.write_terminal()
            self.tokenizer.advance()
            # expression
            self.compile_term()
        
        # identifier
        elif self.tokenizer.token_type() == JackTokenizer.IDENTIFIER:
            # varName or subroutineName
            self.write_terminal()
            self.tokenizer.advance()
            
            if self.tokenizer.token_type() == JackTokenizer.SYMBOL:

                # varName[expression]
                if self.tokenizer.symbol() == "[":
                    # [
                    self.write_terminal()
                    self.tokenizer.advance()
                    # expression
                    self.compile_expression()
                    # ]
                    self.write_terminal()
                    self.tokenizer.advance()
                # subroutineCall 
                elif self.tokenizer.symbol() in {"(", "."}:
                    if self.tokenizer.symbol() == ".":
                        # .
                        self.write_terminal()
                        self.tokenizer.advance()
                        # subroutineName
                        self.write_terminal()
                        self.tokenizer.advance()
                    # (
                    self.write_terminal()
                    self.tokenizer.advance()
                    # expression list
                    self.compile_expression_list()
                    # )
                    self.write_terminal()
                    self.tokenizer.advance()

        self.indent_level -= 1
        self.write_to_file("</term>")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.write_to_file("<expressionList>")
        self.indent_level += 1

        # (expression (',' expression)* )?
        if not(self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == ')'):
            
            # expression
            self.compile_expression()

            # (',' expression)*
            while self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == ',':
                # ,
                self.write_terminal()
                self.tokenizer.advance()

                # expression
                self.compile_expression()

        self.indent_level -= 1
        self.write_to_file("</expressionList>")

    def compile_subroutine_call(self):
        # subroutineName
        self.write_terminal()
        self.tokenizer.advance()
        
        if self.tokenizer.symbol() == ".":
            self.write_terminal()
            self.tokenizer.advance()
            
            self.write_terminal()
            self.tokenizer.advance()
        
        # (
        self.write_terminal()
        self.tokenizer.advance()
        
        # expressionList
        self.compile_expression_list()
        
        # )
        self.write_terminal()
        self.tokenizer.advance()