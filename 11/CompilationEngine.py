"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    segment_map = {
        "STATIC": "STATIC",
        "FIELD": "THIS",    # field variables are accessed through THIS
        "VAR": "LOCAL",     # local variables are in the LOCAL segment
        "ARG": "ARG"       # arguments are in the ARG segment
    }

    def __init__(self, input_stream: JackTokenizer, output_stream:typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.writer = VMWriter(output_stream)
        self.symbol_table = SymbolTable()
        
        # For generating unique labels
        self.label_counter = 0
        # Track current class and subroutine names
        self.class_name = ""

    def get_unique_label(self, prefix: str) -> str:
        """Generate a unique label with given prefix."""
        self.label_counter += 1
        return f"{prefix}_{self.label_counter}"

    def compile_class(self) -> None:
        """Compiles a complete class."""
        
        # class
        self.tokenizer.advance()
        
        # className
        self.class_name = self.tokenizer.identifier()
        self.tokenizer.advance()
        
        
        # {
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
        self.tokenizer.advance()
        
    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # static or field
        kind = self.tokenizer.keyword()
        self.tokenizer.advance()

        # type 
        type = (self.tokenizer.keyword() if self.tokenizer.token_type() == JackTokenizer.KEYWORD 
                   else self.tokenizer.identifier())
        self.tokenizer.advance()

        # varName
        name = self.tokenizer.identifier()
        self.tokenizer.advance()

        # Add the variables to the symbol table
        self.symbol_table.define(name,type,kind.upper())
        
        # (',' varName)*
        while self.tokenizer.token_type() == JackTokenizer.SYMBOL and \
              self.tokenizer.symbol() == ",":
            self.tokenizer.advance()
            name = self.tokenizer.identifier()
            self.tokenizer.advance()

            # Add the variables to the symbol table
            self.symbol_table.define(name,type,kind.upper())

        # ;
        self.tokenizer.advance()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.symbol_table.start_subroutine()

        # constructor or method or function
        subroutine_type = self.tokenizer.keyword()
        self.tokenizer.advance()

        # type or void
        self.tokenizer.advance()

        # subroutineName
        subroutine_name = self.tokenizer.identifier()
        self.tokenizer.advance()

        if subroutine_type == "method":
            # Add the object to the symbol table
            self.symbol_table.define("this", self.class_name, "ARG")

        # (
        self.tokenizer.advance()

        # parameters list
        self.compile_parameter_list()

        # )        
        self.tokenizer.advance()

        # {
        self.tokenizer.advance()

        # compile var dec
        n_locals = 0
        while self.tokenizer.token_type() == JackTokenizer.KEYWORD and self.tokenizer.keyword() == "var":
            n_locals += self.compile_var_dec()

        # Write function declaration
        self.writer.write_function(
            f"{self.class_name}.{subroutine_name}", n_locals)

        # Constructor:
        if subroutine_type == "constructor":
            n_fields = self.symbol_table.var_count("FIELD")
            self.writer.write_push("CONST",n_fields)
            self.writer.write_call("Memory.alloc",1)
            self.writer.write_pop("POINTER",0)

        elif subroutine_type == "method":
            # method
            self.writer.write_push("ARG",0)
            self.writer.write_pop("POINTER",0)

        # compile statements
        self.compile_statements()

        # }
        self.tokenizer.advance()        

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # ((type varName), (',' type varName)*)?
        if not (self.tokenizer.token_type() == JackTokenizer.SYMBOL and \
                self.tokenizer.symbol() == ")"):
            
            # type
            type = (self.tokenizer.keyword() if self.tokenizer.token_type() == JackTokenizer.KEYWORD 
                   else self.tokenizer.identifier())
            self.tokenizer.advance()

            # varName
            name = self.tokenizer.identifier()
            self.tokenizer.advance()

            # Add the argument to the symbol table:
            self.symbol_table.define(name,type,"ARG")

            # (',' type varName)*
            while self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == ",":
                # , 
                self.tokenizer.advance()

                # type
                type = (self.tokenizer.keyword() if self.tokenizer.token_type() == JackTokenizer.KEYWORD 
                   else self.tokenizer.identifier())
                self.tokenizer.advance()

                # varName
                name = self.tokenizer.identifier()
                self.tokenizer.advance()

                # Add the argument to the symbol table:
                self.symbol_table.define(name,type,"ARG")

    def compile_var_dec(self) -> int:
        """Compiles a var declaration."""
        n_vars = 1

        # var 
        self.tokenizer.advance()

        # type 
        type = (self.tokenizer.keyword() if self.tokenizer.token_type() == JackTokenizer.KEYWORD 
                   else self.tokenizer.identifier())
        
        self.tokenizer.advance()

        # varName 
        name = self.tokenizer.identifier()
        self.tokenizer.advance()

        # Add the argument to the symbol table:
        self.symbol_table.define(name,type,"VAR")

        # (',' varName)*
        while self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == ',':
            # ,
            self.tokenizer.advance()

            # varName 
            name = self.tokenizer.identifier()
            self.tokenizer.advance()

            # Add the argument to the symbol table:
            self.symbol_table.define(name,type,"VAR")

            n_vars += 1

        # ;
        self.tokenizer.advance()
        return n_vars

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
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

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # do
        self.tokenizer.advance()

        # subroutine call
        self.compile_expression()

        self.writer.write_pop("TEMP",0)

        # ;
        self.tokenizer.advance()

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # let 
        self.tokenizer.advance()

        # varName 
        varName = self.tokenizer.identifier()
        self.tokenizer.advance()

        # Compile arrays.
        # ('[' expression ']')?
        if self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == '[':
            # [ 
            self.tokenizer.advance()

            # push arr
            index = self.symbol_table.index_of(varName)
            segment = self.symbol_table.kind_of(varName)
            vm_segment = CompilationEngine.segment_map[segment]
            self.writer.write_push(vm_segment,index)

            # compile expression1
            self.compile_expression()

            # add
            self.writer.write_arithmetic("ADD")

            # ] 
            self.tokenizer.advance()

            # = 
            self.tokenizer.advance()

            # compile expression2 
            self.compile_expression()

            # save the expression2 value in temp
            self.writer.write_pop("TEMP",0)

            # Pop pointer 1
            self.writer.write_pop("POINTER",1)

            # Push temp 0
            self.writer.write_push("TEMP",0)

            # Pop that 0
            self.writer.write_pop("THAT",0)

            # ;
            self.tokenizer.advance()

        else:
            # =
            self.tokenizer.advance()

            # expression 
            self.compile_expression()

            # ;
            self.tokenizer.advance()

            # Pop the expression return value to the mapping of varName:
            segment = self.symbol_table.kind_of(varName) 
            index = self.symbol_table.index_of(varName)
            vm_segment = CompilationEngine.segment_map[segment]
            self.writer.write_pop(vm_segment,index)

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # loop labels
        loop_label = self.get_unique_label("WHILE")
        end_label = self.get_unique_label("WHILE_END")

        # while
        self.tokenizer.advance()

        # Write loop label  
        self.writer.write_label(loop_label)

        # (
        self.tokenizer.advance()

        # expression
        self.compile_expression()

        self.writer.write_arithmetic("NOT")
        self.writer.write_if(end_label)

        # )
        self.tokenizer.advance()

        # {
        self.tokenizer.advance()

        # statements
        self.compile_statements()

        # }
        self.tokenizer.advance()

        self.writer.write_goto(loop_label)

        self.writer.write_label(end_label)

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # return
        self.tokenizer.advance()

        # expression?
        if not (self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == ';'):
            # expression
            self.compile_expression()
        else:
            # Push 0 for void functions
            self.writer.write_push("CONST", 0)

        # ;
        self.tokenizer.advance()

        self.writer.write_return()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        else_label = self.get_unique_label("IF_ELSE")
        end_label = self.get_unique_label("IF_END")

        # if
        self.tokenizer.advance()

        # (
        self.tokenizer.advance()

        # expression
        self.compile_expression()

        self.writer.write_arithmetic("NOT")
        self.writer.write_if(else_label)

        # )
        self.tokenizer.advance()

        # {
        self.tokenizer.advance()

        # statements
        self.compile_statements()

        # }
        self.tokenizer.advance()
        
        # Go to end table and skip the else segment
        self.writer.write_goto(end_label)

        # Else label 
        self.writer.write_label(else_label)

        # (else '{' statements '}')?
        if self.tokenizer.token_type() == JackTokenizer.KEYWORD and self.tokenizer.keyword() == "else":
            # else            
            self.tokenizer.advance()

            # {
            self.tokenizer.advance()

            # statements
            self.compile_statements()

            # }
            self.tokenizer.advance()

        # End label
        self.writer.write_label(end_label)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # term
        self.compile_term()

        binary_op = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MULT',
            '/': 'DIV',
            '&': 'AND',
            '|': 'OR',
            '<': 'LT',
            '>': 'GT',
            '=': 'EQ'
        }

        while  self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() in binary_op:
            jack_op = self.tokenizer.symbol()

            # binary op
            self.tokenizer.advance()

            # term
            self.compile_term()

            if jack_op == '*':
                self.writer.write_call("Math.multiply",2)
            elif jack_op == '/':
                self.writer.write_call("Math.divide",2)
            else:
                vm_op = binary_op[jack_op]
                self.writer.write_arithmetic(vm_op)

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
        # integerConstant
        if self.tokenizer.token_type() == JackTokenizer.INT_CONST:
            num = self.tokenizer.int_val()
            self.writer.write_push("CONST",num)
            self.tokenizer.advance()

        # stringConstant
        elif self.tokenizer.token_type() == JackTokenizer.STRING_CONST:
            string = self.tokenizer.string_val()
            str_len = len(string)

            # Push string length in the stack
            self.writer.write_push("CONST",str_len)

            # call the String new constructor
            self.writer.write_call("String.new",1)

            # Loop for at char:
            for char in string:
                self.writer.write_push("CONST",ord(char))
                self.writer.write_call("String.appendChar",2)

            self.tokenizer.advance()

        # keywordConstant
        elif self.tokenizer.token_type() == JackTokenizer.KEYWORD and \
             self.tokenizer.keyword() in ["true", "false", "null", "this"]:
            
            keyword_const = self.tokenizer.keyword()
            if keyword_const in ["false","null"]:
                self.writer.write_push("CONST",0)
            elif keyword_const == "true":
                self.writer.write_push("CONST",1)
                self.writer.write_arithmetic("NEG")
            elif keyword_const == "this":
                self.writer.write_push('POINTER',0)
            
            self.tokenizer.advance()
        # ( expression )
        elif self.tokenizer.token_type() == JackTokenizer.SYMBOL and \
             self.tokenizer.symbol() == "(":
            # (
            self.tokenizer.advance()
            # expression
            self.compile_expression()
            # )
            self.tokenizer.advance()
        # unary op
        elif self.tokenizer.token_type() == JackTokenizer.SYMBOL and \
             self.tokenizer.symbol() in ['-','~','^','#']:
            # unary op
            op = self.tokenizer.symbol()
            self.tokenizer.advance()
            # term
            self.compile_term()
            if op == "^":
                self.writer.write_arithmetic("SHIFTLEFT")
            elif op == "#":
                self.writer.write_arithmetic("SHIFTRIGHT")
            elif op == "-":
                self.writer.write_arithmetic("NEG")
            elif op == "~":
                self.writer.write_arithmetic("NOT")
        
        # identifier
        elif self.tokenizer.token_type() == JackTokenizer.IDENTIFIER:
            # varName or subroutineName
            name = self.tokenizer.identifier()
            self.tokenizer.advance()
            
            if self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == "[":
                # varName[expression]
                if self.tokenizer.symbol() == "[":
                    # [
                    self.tokenizer.advance()

                    # Push variable to stack
                    segment = self.symbol_table.kind_of(name)
                    index = self.symbol_table.index_of(name)
                    vm_segment = CompilationEngine.segment_map[segment]
                    self.writer.write_push(vm_segment,index)

                    # expression
                    self.compile_expression()

                     # add
                    self.writer.write_arithmetic("ADD")

                    # ]
                    self.tokenizer.advance()

                    # We compile array logic:
                    self.writer.write_pop("POINTER",1)
                    self.writer.write_push("THAT",0)

            # subroutineCall 
            elif self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() in ["(", "."]:
                    n_args = 0
                    if self.tokenizer.symbol() == ".":
                        # .
                        self.tokenizer.advance()
                        type = self.symbol_table.type_of(name)
                        subroutine_name = self.tokenizer.identifier()

                        # subroutineName
                        self.tokenizer.advance()

                        if type:
                            # We have method call on object name

                            # We push the object in the stack
                            index = self.symbol_table.index_of(name)
                            segment = self.symbol_table.kind_of(name)
                            vm_segment = CompilationEngine.segment_map[segment]
                            self.writer.write_push(vm_segment,index)

                            n_args = 1
                            # varName.subroutineName
                            function_name = f"{type}.{subroutine_name}"

                        else:
                            # We have a function call: className.subroutineName
                            function_name = f"{name}.{subroutine_name}"

                    else:
                        # call the method on this
                        self.writer.write_push("POINTER",0)
                        n_args = 1
                        function_name = f"{self.class_name}.{name}"

                    # (
                    self.tokenizer.advance()
                    # Expression list
                    n_args += self.compile_expression_list()
                    # )
                    self.tokenizer.advance()
                    
                    # call the function:
                    self.writer.write_call(function_name,n_args)
                    
            else:
                # Variable
                segment = self.symbol_table.kind_of(name)
                index = self.symbol_table.index_of(name)
                vm_segment = CompilationEngine.segment_map[segment]
                self.writer.write_push(vm_segment, index)

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        n_args = 0
        # (expression (',' expression)* )?
        if not(self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == ')'):
            n_args += 1
            # expression
            self.compile_expression()
            # (',' expression)*
            while self.tokenizer.token_type() == JackTokenizer.SYMBOL and self.tokenizer.symbol() == ',':
                # ,
                self.tokenizer.advance()

                # expression
                self.compile_expression()

                n_args += 1

        return n_args