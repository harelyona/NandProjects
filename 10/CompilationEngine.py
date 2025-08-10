"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer

IDENTIFIER = "<identifier>{}</identifier>\n"
KEYWORD = "<keyword>{}</keyword>\n"
SYMBOL = "<symbol>{}</symbol>\n"

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
        self.compile_class_var_dec()
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
        self._write_parameter_list()
        self._write_subroutine_body()
        self.output_stream.write("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
        pass

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        pass

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        pass

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        pass

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        pass

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        pass

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        pass

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!
        pass

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
        # Your code goes here!
        pass

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        pass

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
        self._write_symbol() # Write the opening (
        first_parameter = True
        while not (self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ")"):
            # Write comma if not the first parameter
            if not first_parameter:
                self._write_symbol()
            self._write_type()
            self._write_identifier()
            first_parameter = False
        self._write_symbol() # Write the closing )

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