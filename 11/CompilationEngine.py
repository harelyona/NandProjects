"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from pandas.compat.numpy.function import validate_resampler_func, validate_argsort_kind

from SymbolTable import SymbolTable
from JackTokenizer import JackTokenizer
from VMWriter import VMWriter


OP = {'+':"ADD", '-':"SUB", '&':"AND", '|':"OR", '<':"LT", '>':"GT", '=':"EQ"}
UNARYOP = {'-':"NEG", '~':"NOT", '^':"SHIFTLEFT", '#':"SHIFTRIGHT"}
KEYWORD_CONSTANTS_SEGMENTS_AND_IDX = {'true':("CONST", 0), 'false':("CONST", -1), 'null':(), 'this':("POINTER", 0)}
UNARY_OPT = ['-', '~']
KEYWORD_CONSTANTS = ['true', 'false', 'null', 'this']

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
        self.counter = 0
        self.class_symbol_table = SymbolTable()
        self.subroutine_symbol_table = SymbolTable()
        self.class_name = ""
        self.writer = VMWriter(output_stream)

    def _label_generator(self, label_name: str) -> str:
        self.counter += 1
        return label_name + str(self.counter)

    def compile_class(self) -> None:
        # Write class className { classVarDec* subroutineDec* }
        self.input_stream.advance()
        self.class_name = self._get_identifier()
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() in ["STATIC", "FIELD"]:
            self.compile_class_var_dec()
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() in ["CONSTRUCTOR", "FUNCTION", "METHOD"]:
            self.compile_subroutine()
        self.input_stream.advance()

    def compile_class_var_dec(self) -> None:
        # Write static/field type variableName(, variableName)*;
        var_kind = self._get_keyword()
        var_type = self._get_type()
        var_name = self._get_identifier()
        self.class_symbol_table.define(var_name, var_type, var_kind)
        # Write the rest of the variables
        while self.input_stream.symbol() == ',':
            self.input_stream.advance()
            name = self._get_identifier()
            self.class_symbol_table.define(name, var_type, var_kind)

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Write subroutine_keyword type subroutineName(parameterList){subroutine_body}
        self.subroutine_symbol_table.start_subroutine()
        subroutine_type = self._get_keyword()
        self.input_stream.advance()
        name = self._get_identifier()
        #(parameterList)
        if subroutine_type == "METHOD":
            self.subroutine_symbol_table.define("this", self.class_name, "ARG")
        self.input_stream.advance() # Skip the opening (
        self._write_parameter_list()
        self.input_stream.advance() # Skip the closing )
        self.input_stream.advance() # Skip the opening {
        # SubroutineBody: {varDec* statements}
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword().lower() == "var":
            self.compile_var_dec()
        number_of_locals = self.subroutine_symbol_table.var_count("VAR")
        self.writer.write_function(f"{self.class_name}.{name}", number_of_locals)

        if subroutine_type == "constructor":
            # Set allocated memory segment for the newly created object
            number_of_field_variables = self.class_symbol_table.var_count("FIELD")
            self.writer.write_push("CONST",number_of_field_variables)
            self.writer.write_call("Memory.alloc",1)
            self.writer.write_pop("POINTER",0)

        elif subroutine_type == "method":
            # Set the pointer to this object
            self.writer.write_push("ARG",0)
            self.writer.write_pop("POINTER",0)
        self.compile_statements()
        self.input_stream.advance() # Skip the closing }

    # def compile_parameter_list(self) -> None:
    #     """Compiles a (possibly empty) parameter list, not including the
    #     enclosing "()".
    #     """
    #     self.output_stream.write("<parameterList>\n")
    #     # If not parameters
    #     if self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ")":
    #         return
    #     # write type var_name
    #     self._write_type()
    #     self._get_identifier()
    #
    #     # Write the rest of the parameters
    #     while self.input_stream.symbol() == ",":
    #         self._write_type()
    #         self._get_identifier()
    #     self.output_stream.write("</parameterList>\n")
    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # VarDec: 'var' type varName (',' varName)* ';'
        var = self._get_keyword()
        if var != "var":
            raise ValueError("Expected 'var' keyword")
        var_type = self._get_type()
        var_name = self._get_identifier()
        self.subroutine_symbol_table.define(var_name, var_type, "VAR")

        # Write the rest of the variables
        while self.input_stream.symbol() == ',':
            self.input_stream.advance()
            self._get_identifier()
            self.subroutine_symbol_table.define(var_name, var_type, "VAR")
        self.input_stream.advance() # Skip closing ;

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
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

    def compile_do(self) -> None:
        """Compiles a do statement."""
        do = self._get_keyword()
        if do != "do":
            raise ValueError("Expected 'do' keyword")
        # subroutine call
        self.compile_expression()
        self.writer.write_pop("TEMP", 0)
        self.input_stream.advance()# skip semicolon



    def compile_let(self) -> None:
        """Compiles a let statement."""
        # letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        let = self._get_keyword()
        if let != "let":
            raise ValueError("Expected 'let' keyword")

        identifier = self._get_identifier()
        self._push_variable(identifier)
        # If the next symbol is [ then it's an array assignment,
        if self.input_stream.symbol() == "[":
            self.input_stream.advance()
            self.compile_expression()
            self.input_stream.advance()
            self.writer.write_arithmetic("ADD")
        self.input_stream.advance() # Skip =
        # Save the second expression in a temp variable
        self.compile_expression()
        self.writer.write_pop("TEMP", 0)

        # Pop the second expression into the correct place
        self.writer.write_pop("POINTER", 1)
        self.writer.write_push("TEMP", 0)
        self.writer.write_pop("THAT", 0)
        self.input_stream.advance() # Skip semicolon

    def compile_while(self) -> None:
        """Compiles a while statement."""
        start_loop = self._label_generator("WhileStart")
        end_loop = self._label_generator("WhileEnd")
        # Write while (expression) {statements}
        self.input_stream.advance() # Skip 'while'
        self.input_stream.advance() # Skip (

        # Start of the loop
        self.writer.write_label(start_loop)
        self.compile_expression()
        self.input_stream.advance() # Skip )
        self.writer.write_arithmetic("NEG")
        self.writer.write_if(end_loop)
        self.input_stream.advance() # Skip {
        self.compile_statements()
        self.input_stream.advance() # Skip }
        self.writer.write_goto(start_loop)
        # End of the loop

        self.writer.write_goto(end_loop)
    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output_stream.write("<returnStatement>\n")
        self._get_keyword()
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
        # ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
        false_label = self._label_generator("FALSE")
        if_keyword = self._get_keyword()
        if if_keyword != "if":
            raise ValueError("Expected 'if' keyword")
        self.input_stream.advance() # Skip (
        self.compile_expression()
        self.input_stream.advance() # Skip )
        self.writer.write_arithmetic("NEG")
        self.writer.write_if(false_label)
        self.compile_statements()

        # If else clause is present, compile it
        if self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() == "ELSE":
            # Write else {statements}
            else_clause = self._get_keyword()
            if else_clause != "else":
                raise ValueError("Expected 'else' keyword")
            self.writer.write_label(false_label)
            self.input_stream.advance() # Skip {
            self.compile_statements()
            self.input_stream.advance() # Skip }
        else:
            self.writer.write_label(false_label)


    def compile_expression(self) -> None:
        """Compiles an expression."""
        # expression: term (op term)*
        self.compile_term()
        while self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() in OP:
            op = OP[self._get_symbol()] # TODO chack if * and / are need to be Math.
            self.input_stream.advance() # Skip the operator
            self.compile_term()
            self.writer.write_arithmetic(op)


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
        token_type = self.input_stream.token_type()

        if token_type == "INT_CONST":
            self.writer.write_push("CONST", self.input_stream.int_val())
            self.input_stream.advance()

        elif token_type == "STRING_CONST":
            self._create_string(self.input_stream.string_val())

        elif token_type == "KEYWORD" and self.input_stream.keyword() in KEYWORD_CONSTANTS:
            if self.input_stream.keyword() in ["false", "null"]:
                self.writer.write_push("CONST", 0)
            elif self.input_stream.keyword() == "true":
                self.writer.write_push("CONST", 0)
                self.writer.write_arithmetic("NEG")
            elif self.input_stream.keyword() == "this":
                self.writer.write_push("POINTER", 0)

        elif token_type == "SYMBOL":
            if self.input_stream.symbol() in UNARY_OPT:
                unary_op = UNARYOP[self._get_symbol()]
                self.compile_term()
                self.writer.write_arithmetic(unary_op)
            elif self.input_stream.symbol() == "(":
                self.input_stream.advance() # Skip (
                self.compile_expression()
                self.input_stream.advance() # Skip )
            else:
                raise ValueError(f"Unexpected symbol: {self.input_stream.symbol()}")

        elif token_type == "IDENTIFIER":
            self.input_stream.advance()
            if self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() in ["(", ".", '[']:
                # If an array entry
                if self.input_stream.symbol() == "[":
                    self.input_stream.backward()
                    self._get_identifier()
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
                self._get_identifier()
        else:
            self.input_stream.backward()


    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output_stream.write("<expressionList>\n")
        if not(self.input_stream.token_type() == "SYMBOL" and self.input_stream.keyword() == ")"):
            self.compile_expression()
            while self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ",":
                self._write_symbol()
                self.compile_expression()
        self.output_stream.write("</expressionList>\n")


    def _get_keyword(self):
        keyword = self.input_stream.keyword().lower()
        self.input_stream.advance()
        return keyword

    def _get_identifier(self):
        identifier = self.input_stream.identifier()
        self.input_stream.advance()
        return identifier

    def _get_symbol(self):
        symbol = self.input_stream.symbol()
        self.input_stream.advance()
        return symbol

    def _write_type(self):
        if self.input_stream.token_type() == "IDENTIFIER":
            identifier = self.input_stream.identifier()
            self.output_stream.write(IDENTIFIER.format(identifier))
        if self.input_stream.token_type() == "KEYWORD":
            keyword = self.input_stream.keyword().lower()
            self.output_stream.write(KEYWORD.format(keyword))
        self.input_stream.advance()

    def _get_type(self):
        var_type = None
        if self.input_stream.token_type() == "IDENTIFIER":
            var_type = self.input_stream.identifier()
        if self.input_stream.token_type() == "KEYWORD":
            var_type = self.input_stream.keyword().lower()
        self.input_stream.advance()
        return var_type
    def _write_parameter_list(self):
        # parameterList: (type varName) (',' type varName)* or empty
        if not (self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ")"):
            type = self._get_type()
            name = self._get_identifier()
            self.subroutine_symbol_table.define(name, type, "ARG")
            while self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ",":
                self.input_stream.advance()
                type = self._get_type()
                name = self._get_identifier()
                self.subroutine_symbol_table.define(name, type, "ARG")


    def _write_subroutine_call(self):
        """Writes a subroutine call: subroutineName(...) or (className|varName).subroutineName(...)."""
        # First identifier: could be a class name, var name, or subroutine name
        self._get_identifier()

        # If next token is '.', it's a method or function in another class
        if self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ".":
            self._write_symbol()  # Write '.'
            self._get_identifier()  # subroutine name after the dot

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

    def _get_segment(self, var_name: str) -> str:
        var_kind = self.subroutine_symbol_table.kind_of(var_name)
        if var_kind == "STATIC":
            segment = "STATIC"
        elif var_kind == "FIELD":
            segment = "THIS"
        elif var_kind == "ARG":
            segment = "ARG"
        elif var_kind == "VAR":
            segment = "LOCAL"
        else:
            raise ValueError(f"Invalid variable kind: {var_kind}")
        return segment

    def _push_variable(self, var_name: str) -> None:
        segment = self._get_segment(var_name)
        index = self.subroutine_symbol_table.index_of(var_name)
        self.writer.write_push(segment, index)

    def _create_string(self, string: str) -> None:
        self.writer.write_push("CONST", len(string))
        self.writer.write_call("String.new", 1)
        for char in string:
            self.writer.write_push("CONST", ord(char))
            self.writer.write_call("String.appendChar", 2)