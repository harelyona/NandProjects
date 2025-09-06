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


OP = {'+':"ADD", '-':"SUB", '&':"AND", '|':"OR", '<':"LT", '>':"GT", '=':"EQ", '*':"Math.multiply", '/':"Math.divide"}
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
        self.symbol_table = SymbolTable()
        self.class_name = ""
        self.writer = VMWriter(output_stream)

    def _label_generator(self, label_name: str) -> str:
        self.counter += 1
        return label_name + str(self.counter)

    def compile_class(self) -> None:
        # Write class className { classVarDec* subroutineDec* }
        self.input_stream.advance() # Skip 'class' keyword
        self.class_name = self._get_identifier()
        self.input_stream.advance() # Skip the opening {
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
        self.symbol_table.define(var_name, var_type, var_kind)
        # Write the rest of the variables
        while self.input_stream.symbol() == ',':
            self.input_stream.advance()
            name = self._get_identifier()
            self.symbol_table.define(name, var_type, var_kind)

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Write subroutine_keyword return_type subroutineName(parameterList){subroutine_body}
        self.symbol_table.start_subroutine()
        subroutine_type = self._get_keyword()
        return_type = self._get_type()
        name = self._get_identifier()
        #(parameterList)
        if subroutine_type == "method":
            self.symbol_table.define("this", self.class_name, "ARG")
        self.input_stream.advance() # Skip the opening (
        self._write_parameter_list("define")
        self.input_stream.advance() # Skip the closing )
        self.input_stream.advance() # Skip the opening {
        # SubroutineBody: {varDec* statements}
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword().lower() == "var":
            self.compile_var_dec()

        number_of_locals = self.symbol_table.var_count("VAR")
        self.writer.write_function(f"{self.class_name}.{name}", number_of_locals)
        self.compile_statements()

        if subroutine_type == "constructor":
            # Set allocated memory segment for the newly created object
            number_of_field_variables = self.symbol_table.var_count("FIELD")
            self.writer.write_push("CONST",number_of_field_variables)
            self.writer.write_call("Memory.alloc",1)
            self.writer.write_pop("POINTER",0)

        elif subroutine_type == "method":
            # Set the pointer to this object
            self.writer.write_push("ARG",0)
            self.writer.write_pop("POINTER",0)

        # self.input_stream.advance() # Skip the opening {
        # self.compile_parameter_list()
        # self.input_stream.advance() # Skip the closing )
        # self.input_stream.advance() # Skip the opening {
        # self.compile_statements()
        # self.input_stream.advance() # Skip the closing }



    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        # If not parameters
        if self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ")":
            return
        # write type var_name
        parameter_name = self._get_identifier()
        parameter_type = self._get_type()
        self.symbol_table.define(parameter_name, parameter_type, "ARG")
        # Write the rest of the parameters
        while self.input_stream.symbol() == ",":
            parameter_name = self._get_identifier()
            parameter_type = self._get_type()
            self.symbol_table.define(parameter_name, parameter_type, "ARG")
    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # VarDec: 'var' type varName (',' varName)* ';'
        var = self._get_keyword()
        if var != "var":
            raise ValueError("Expected 'var' keyword")
        var_type = self._get_type()
        var_name = self._get_identifier()
        self.symbol_table.define(var_name, var_type, "VAR")

        # Write the rest of the variables
        while self.input_stream.symbol() == ',':
            self.input_stream.advance()
            var_name = self._get_identifier()
            self.symbol_table.define(var_name, var_type, "VAR")
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
        #letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        let = self._get_keyword()
        if let != "let":
            raise ValueError(f"Expected 'let' keyword got {self.input_stream.get_current_token()}")

        var_name = self._get_identifier()
        is_array = False

        # Handle array assignment
        if self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == "[":
            is_array = True
            self.input_stream.advance()  # Skip [
            self._push_variable(var_name)  # push base address
            self.compile_expression()  # push index
            self.input_stream.advance()  # Skip ]
            self.writer.write_arithmetic("ADD")

        self.input_stream.advance()  # Skip '='
        self.compile_expression()  # Compile RHS

        if is_array:
            # For arrays: pop RHS into temp, pop address into pointer, then assign
            self.writer.write_pop("TEMP", 0)
            self.writer.write_pop("POINTER", 1)
            self.writer.write_push("TEMP", 0)
            self.writer.write_pop("THAT", 0)
        else:
            # For normal vars
            segment = self._get_segment(var_name)
            index = self.symbol_table.index_of(var_name)
            self.writer.write_pop(segment, index)

        if self.input_stream.token_type() != "SYMBOL" or self.input_stream.symbol() != ";":
            raise ValueError(f"Expected ';' at the end of let statement got {self.input_stream.get_current_token()}")
        self.input_stream.advance()  # Skip ;

    def compile_while(self) -> None:
        """Compiles a while statement."""
        start_loop = self._label_generator("WhileStart")
        end_loop = self._label_generator("WhileEnd")
        # Write while (expression) {statements}
        if self.input_stream.token_type() != "KEYWORD" or self._get_keyword() != "while":
            raise ValueError(f"Expected 'while' keyword got {self.input_stream.get_current_token()}")
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
        return_keyword = self._get_keyword()
        if return_keyword != "return":
            raise ValueError("Expected 'return' keyword")
        # If the next token is not a semicolon, push expression
        if not (self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ";"):
            self.compile_expression()
        self.writer.write_return()


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
            self.input_stream.advance()

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
            identifier = self._get_identifier()
            if self.input_stream.token_type() == "SYMBOL":
                # If an array entry
                if self.input_stream.symbol() == "[":
                    self.input_stream.backward()
                    name = self._get_identifier()
                    self._push_variable(name)
                    self.input_stream.advance() # Skip [
                    self.compile_expression()
                    self.input_stream.advance() # Skip ]
                    self.writer.write_arithmetic("ADD")
                    self.writer.write_pop("POINTER", 1)
                    self.writer.write_push("THAT", 0)
                # If a method call
                if self.input_stream.symbol() == ".":
                    if self.symbol_table.type_of(identifier):
                        # It's a method call on an object
                        self.input_stream.backward()
                        self._write_subroutine_call("method")
                    else:
                        # It's a function call on a class
                        self.input_stream.backward()
                        self._write_subroutine_call("class function")
                # If a function call on this class
                if self.input_stream.symbol() == "(":
                    self.input_stream.backward()
                    self._write_subroutine_call("local function")


            else:
                # If a variable
                self.input_stream.backward()
                var = self._get_identifier()
                self._push_variable(var)
        else:
            self.input_stream.backward()


    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions.
        return the number of expressions in the list."""
        expression_count = 0
        while not (self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ")"):
            self.compile_expression()
            expression_count += 1
            if self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ",":
                self.input_stream.advance()
            else:
                break
        return expression_count


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


    def _get_type(self):
        var_type = None
        if self.input_stream.token_type() == "IDENTIFIER":
            var_type = self.input_stream.identifier()
        if self.input_stream.token_type() == "KEYWORD":
            var_type = self.input_stream.keyword().lower()
        self.input_stream.advance()
        return var_type
    def _write_parameter_list(self, mode):
        # type varName (',' type varName)* or empty
        while not (self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ")"):
            type = self._get_type()
            name = self._get_identifier()
            if mode == "define":
                self.symbol_table.define(name, type, "ARG")
            if mode == "push":
                self._push_variable(name)
            if self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ",":
                self.input_stream.advance()
            else:
                break


    def _write_subroutine_call(self, subroutine_type: str):
        """Writes a subroutine call: subroutineName(...) or (className|varName).subroutineName(...)."""
        # First identifier: could be a class name, var name, or subroutine name
        number_of_args = 0
        class_name = None
        subroutine_name = None
        if subroutine_type == "method":
            class_name = self._get_identifier()
            self.input_stream.advance()  # Skip '.'
            subroutine_name = self._get_identifier()  # subroutine name after the dot
            self._push_variable(class_name)
            number_of_args += 1

        elif subroutine_type == "class function":
            class_name = self._get_identifier()
            self.input_stream.advance()  # Skip '.'
            subroutine_name = self._get_identifier()

        elif subroutine_type == "local function":
            class_name = self.class_name
            subroutine_name = self._get_identifier()
            self._push_variable(class_name)
            number_of_args += 1

        self.input_stream.advance()  # Skip '('
        number_of_args += self.compile_expression_list()
        if self.input_stream.token_type() == "SYMBOL" and self._get_symbol() != ")":
            raise Exception(f"Expected ')' at the end of subroutine call got {self.input_stream.get_current_token()}")
        self.writer.write_call(f"{class_name}.{subroutine_name}", number_of_args)




    def _get_segment(self, var_name: str) -> str:
        var_kind = self.symbol_table.kind_of(var_name)
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
        if self.symbol_table.kind_of(var_name) is None:
            raise ValueError(f"Variable {var_name} not found in symbol table.")
        segment = self._get_segment(var_name)
        index = self.symbol_table.index_of(var_name)
        self.writer.write_push(segment, index)

    def _create_string(self, string: str) -> None:
        self.writer.write_push("CONST", len(string))
        self.writer.write_call("String.new", 1)
        for char in string:
            self.writer.write_push("CONST", ord(char))
            self.writer.write_call("String.appendChar", 2)
