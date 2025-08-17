"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


from JackTokenizer import JackTokenizer

IDENTIFIER = "<identifier> {} </identifier>\n"
KEYWORD = "<keyword> {} </keyword>\n"
SYMBOL = "<symbol> {} </symbol>\n"
OP = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
KEYWORD_CONSTANTS = ['true', 'false', 'null', 'this']
UNARY_OPT = ['-', '~']

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.input_stream = input_stream
        self.output_stream = output_stream

    def compile_class(self) -> None:
        # Write class classname{
        self.output_stream.write("<class>\n")
        self._write_keyword()
        self._write_identifier()
        self._write_symbol()
        # Write class variables and subroutines
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() in ["STATIC", "FIELD"]:
            self.compile_class_var_dec()
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() in ["CONSTRUCTOR", "FUNCTION", "METHOD"]:
            self.compile_subroutine()

        # Write closing }
        self._write_symbol()
        self.output_stream.write("</class>\n")

    def compile_class_var_dec(self) -> None:
        # Write static/field type variableName
        self.output_stream.write("<classVarDec>\n")
        self._write_keyword()
        self._write_type()
        self._write_identifier()

        # Write the rest of the variables
        while self.input_stream.symbol() == ',':
            self._write_symbol()
            self._write_identifier()

        # Write ;
        self._write_symbol()
        self.output_stream.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.output_stream.write("<subroutineDec>\n")
        # Write subroutine_keyword type subroutineName(parameterList)
        self._write_keyword()
        self._write_type()
        self._write_identifier()
        self._write_symbol()
        self._write_parameter_list()
        self._write_symbol()
        self._write_subroutine_body()
        self.output_stream.write("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.output_stream.write("<parameterList>\n")
        # If not parameters
        if self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ")":
            return
        # write type var_name
        self._write_type()
        self._write_identifier()

        # Write the rest of the parameters
        while self.input_stream.symbol() == ",":
            self._write_type()
            self._write_identifier()
        self.output_stream.write("</parameterList>\n")
    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output_stream.write("<varDec>\n")
        self._write_keyword()
        self._write_type()
        self._write_identifier()

        # Write the rest of the variables
        while self.input_stream.symbol() == ',':
            self._write_symbol()
            self._write_identifier()

        self._write_symbol() # Write the closing ;
        self.output_stream.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.output_stream.write("<statements>\n")
        while self.input_stream.keyword() in ["LET", "IF", "WHILE", "DO", "RETURN"]:
            if self.input_stream.keyword() == "LET":
                self.compile_let()
            elif self.input_stream.keyword() == "IF":
                self.compile_if()
            elif self.input_stream.keyword() == "WHILE":
                self.compile_while()
            elif self.input_stream.keyword() == "DO":
                self.compile_do()
            elif self.input_stream.keyword() == "RETURN":
                self.compile_return()
        self.output_stream.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output_stream.write("<doStatement>\n")
        self._write_keyword()  # Write the do keyword
        self._write_subroutine_call()
        self._write_symbol()  # Write the semicolon
        self.output_stream.write("</doStatement>\n")



    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output_stream.write("<letStatement>\n")
        self._write_keyword()
        self._write_identifier()
        # If the next symbol is [ then it's an array assignment,
        if self.input_stream.symbol() == "[":
            # Write [expression]
            self._write_symbol()
            self.compile_expression()
            self._write_symbol()
        self._write_symbol() # Write =
        self.compile_expression()
        self._write_symbol() # Write the semicolon
        self.output_stream.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output_stream.write("<whileStatement>\n")
        self._write_keyword()
        # Write (expression){statements}
        self._write_expressions_and_statements()
        self.output_stream.write("</whileStatement>\n")
    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output_stream.write("<returnStatement>\n")
        self._write_keyword()
        # If the next token is a semicolon, return without an expression
        if self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ";":
            self._write_symbol()
        else:
            # Write expression
            self.compile_expression()
            self._write_symbol()
        self.output_stream.write("</returnStatement>\n")


    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.output_stream.write("<ifStatement>\n")
        self._write_keyword()
        self._write_expressions_and_statements()
        # If else clause is present, compile it
        if self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() == "ELSE":
            # Write else {statements}
            self._write_keyword()
            self._write_symbol()
            self.compile_statements()
            self._write_symbol()
        self.output_stream.write("</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.output_stream.write("<expression>\n")
        self.compile_term()
        while self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
            self._write_symbol()
            self.compile_term()
        self.output_stream.write("</expression>\n")


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
        #self.output_stream.write("starting term\n")
        self.output_stream.write("<term>\n")
        if self.input_stream.current_token_idx >= 96:
            pass
        token_type = self.input_stream.token_type()
        if token_type == "INT_CONST":
            self._write_integer_constant()
        elif token_type == "STRING_CONST":
            self._write_string_constant()
        elif token_type == "KEYWORD":
            self._write_keyword()
        elif token_type == "SYMBOL":
            if self.input_stream.symbol() in UNARY_OPT:
                self._write_symbol()
                self.compile_term()
            elif self.input_stream.symbol() == "(":
                self._write_symbol()
                self.compile_expression()
                self._write_symbol()


        elif token_type == "IDENTIFIER":
            self.input_stream.advance()
            if self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() in ["(", ".", '[']:
                # If an array entry
                if self.input_stream.symbol() == "[":
                    self.input_stream.backward()
                    self._write_identifier()
                    self._write_symbol()
                    self.compile_expression()
                    self._write_symbol()
                # If a subroutine call
                else:
                    self.input_stream.backward()
                    self._write_subroutine_call()
            else:
                # If a variable
                self.input_stream.backward()
                self._write_identifier()
        else:
            self.input_stream.backward()
        self.output_stream.write("</term>\n")
        #self.output_stream.write("ending term\n")

    def _write_string_constant(self):
        self.output_stream.write("<stringConstant> {} </stringConstant>\n".format(self.input_stream.string_val()))
        self.input_stream.advance()

    def _write_integer_constant(self):
        self.output_stream.write("<integerConstant> {} </integerConstant>\n".format(self.input_stream.int_val()))
        self.input_stream.advance()

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output_stream.write("<expressionList>\n")
        if not(self.input_stream.token_type() == "SYMBOL" and self.input_stream.keyword() == ")"):
            self.compile_expression()
            while self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ",":
                self._write_symbol()
                self.compile_expression()
        self.output_stream.write("</expressionList>\n")


    def _write_keyword(self):
        keyword = self.input_stream.keyword().lower()
        self.output_stream.write(KEYWORD.format(keyword))
        self.input_stream.advance()

    def _write_identifier(self):
        identifier = self.input_stream.identifier()
        self.output_stream.write(IDENTIFIER.format(identifier))
        self.input_stream.advance()

    def _write_symbol(self):
        symbol = self.input_stream.symbol()
        if symbol == "<":
            self.output_stream.write(SYMBOL.format("&lt;"))
        elif symbol == ">":
            self.output_stream.write(SYMBOL.format("&gt;"))
        elif symbol == "&":
            self.output_stream.write(SYMBOL.format("&amp;"))
        elif symbol == '"':
            self.output_stream.write(SYMBOL.format("&quot;"))
        else:
            self.output_stream.write(SYMBOL.format(symbol))
        self.input_stream.advance()

    def _write_type(self):
        if self.input_stream.token_type() == "IDENTIFIER":
            identifier = self.input_stream.identifier()
            self.output_stream.write(IDENTIFIER.format(identifier))
        if self.input_stream.token_type() == "KEYWORD":
            keyword = self.input_stream.keyword().lower()
            self.output_stream.write(KEYWORD.format(keyword))
        self.input_stream.advance()

    def _write_parameter_list(self):
        self.output_stream.write("<parameterList>\n")
        if not (self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ")"):
            self._write_type()
            self._write_identifier()
            while self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ",":
                self._write_symbol()
                self._write_type()
                self._write_identifier()
        self.output_stream.write("</parameterList>\n")


    def _write_subroutine_body(self):
        self.output_stream.write("<subroutineBody>\n")
        self._write_symbol() # Write opening {
        # Write variable declarations
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword().lower() == "var":
            self.compile_var_dec()
        # Write statements
        self.compile_statements()
        self._write_symbol()# Write closing }
        self.output_stream.write("</subroutineBody>\n")

    def _write_subroutine_call(self):
        """Writes a subroutine call: subroutineName(...) or (className|varName).subroutineName(...)."""
        # First identifier: could be a class name, var name, or subroutine name
        self._write_identifier()

        # If next token is '.', it's a method or function in another class
        if self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ".":
            self._write_symbol()  # Write '.'
            self._write_identifier()  # subroutine name after the dot

        # Now we must see '('
        self._write_symbol()  # Write '('
        self.compile_expression_list()
        self._write_symbol()  # Write ')'

    def _write_expressions_and_statements(self):
        # Write (expression)
        self._write_symbol()
        self.compile_expression()
        self._write_symbol()
        # Write {statements}
        self._write_symbol()
        self.compile_statements()
        self._write_symbol()
