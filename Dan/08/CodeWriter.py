"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

STORE_ADDRESS = "R13" 
TEMP = "R14"
BOOL = "R15"


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    # Class attributes
    call_counter = 0
    bool_num = 0

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.output_stream = output_stream
        self.filename = ""
        # Counter for how many boolean comparison there where and to differentitate between the labels. 

        # The function name of this instance:
        self.func_name = ''

        self.variableTypeDict = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT"}

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.filename = filename

    def __non_bool_arithmetic_command(self,command:str) -> None:
        """
        The method writes to the output file the following non bolean commands in hack assembly: add,sub,and,or.
        """
        # Dictionary of commands:
        commands = {"add":"+","sub":"-","and":"&","or":"|"}
        current_command = commands[command]
        self.output_stream.write("@SP\n")
        self.output_stream.write("AM=M-1\n")  # SP--, A = SP
        self.output_stream.write("D=M\n")    # D = RAM[SP]
        self.output_stream.write("A=A-1\n")  # A = SP-1
        self.output_stream.write(f"M=M{current_command}D\n")  # RAM[SP-1] = D (operation) RAM[SP]

    def __write_equal_command(self) ->None:
        """
        This method writes assembly code for the equal command:
        """
        # First subtract between the two numbers in the stack
        self.output_stream.write("@SP\n")
        self.output_stream.write("AM=M-1\n")  # SP--, A = SP
        self.output_stream.write("D=M\n")     # D = RAM[SP] 
        self.output_stream.write("A=A-1\n")   # A = SP-1 
        self.output_stream.write("D=M-D\n")   # D = RAM[SP-1] - D

        # Set the default answer to be false 
        self.output_stream.write("M=0\n")  # Set false

        # If boolean comparison is true then 
        self.output_stream.write(f"@NOT_EQUAL{CodeWriter.bool_num}\n")
        self.output_stream.write(f"D;JNE\n")  # Jump if not equal
        self.output_stream.write("// Handle the equal case by setting -1 (true)\n")
        # Access RAM[SP-1]:
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M-1\n")  # Access SP-1 again
        self.output_stream.write("M=-1\n")  # Set true (-1)

        # Label for false comparison case.
        self.output_stream.write(f"(NOT_EQUAL{CodeWriter.bool_num})\n")

    def __bool_comparison_command(self, command: str) -> None:
        """
        The method writes to the output file the following boolean comparison commands in Hack assembly: eq, gt, lt.
        Handles overflow during subtraction and ensures comparison is valid.
        """
        # increment number of boolean comparisons.
        CodeWriter.bool_num += 1
        if command == "eq":
            self.__write_equal_command()
        # Else we need to handle the gt and lt case:
        else:
            # Check if y is negative:
            self.output_stream.write("@SP\n")
            self.output_stream.write("AM=M-1\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write(f"@Y_NEGATIVE{CodeWriter.bool_num}\n")
            self.output_stream.write(f"D;JLT\n") # Jump if y<0
            # y>=0:
            # Store y in temp for later use:
            self.output_stream.write(f"@{TEMP}\n")
            self.output_stream.write("M=D\n")
            
            # Check if x is negative:
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write(f"@X_NEGATIVE_Y_POSITIVE{CodeWriter.bool_num}\n")
            self.output_stream.write(f"D;JLT\n") # Jump if x<0

            # x>=0 and y>=0:
            self.output_stream.write("// Handle the case where both are positive or zero:\n")
            self.output_stream.write(f"@{TEMP}\n")
            self.output_stream.write(f"D=D-M\n")

            self.output_stream.write(f"@{BOOL}\n")
            self.output_stream.write("M=-1\n")
            
            self.output_stream.write(f"@END_BOOL{CodeWriter.bool_num}\n")
            if command == "gt":
                self.output_stream.write("D;JGT\n")
            elif command == "lt":
                self.output_stream.write("D;JLT\n")

            # If no jump where performed then the answer is false:
            self.output_stream.write(f"@{BOOL}\n")
            self.output_stream.write("M=0\n")
            self.output_stream.write(f"@END_BOOL{CodeWriter.bool_num}\n")
            self.output_stream.write("0;JMP\n")
            
            # X<0 and y>=0
            self.output_stream.write(f"(X_NEGATIVE_Y_POSITIVE{CodeWriter.bool_num})\n")
            self.output_stream.write(f"@{BOOL}\n")
            # if x is negative and y is positive it's trivial to know which one is greater or lesser.
            if command == "gt":
                self.output_stream.write("M=0\n")
            elif command == "lt":
                self.output_stream.write("M=-1\n")

            self.output_stream.write(f"@END_BOOL{CodeWriter.bool_num}\n")
            self.output_stream.write("0;JMP\n")

            # y<0:
            self.output_stream.write(f"(Y_NEGATIVE{CodeWriter.bool_num})\n")
            # Store y in temp for later use:
            self.output_stream.write(f"@{TEMP}\n")
            self.output_stream.write("M=D\n")
            # Check if x is negative:
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write(f"@X_AND_Y_NEGATIVE{CodeWriter.bool_num}\n")
            self.output_stream.write(f"D;JLT\n") # Jump if x<0

            # x>=0 and y<0
            self.output_stream.write("// Handle the case where x>=0 and y<0:\n")
            self.output_stream.write(f"@{BOOL}\n")
            # if x is positive and y is negative it's trivial to know which one is greater or lesser.
            if command == "gt":
                self.output_stream.write("M=-1\n")
            elif command == "lt":
                self.output_stream.write("M=0\n")

            self.output_stream.write(f"@END_BOOL{CodeWriter.bool_num}\n")
            self.output_stream.write("0;JMP\n")

            # x<0 and y<0:
            self.output_stream.write(f"(X_AND_Y_NEGATIVE{CodeWriter.bool_num})\n")
            self.output_stream.write("// Handle the case where both negative:\n")
            self.output_stream.write(f"@{TEMP}\n")
            self.output_stream.write(f"D=D-M\n")

            self.output_stream.write(f"@{BOOL}\n")
            self.output_stream.write("M=-1\n")
            
            self.output_stream.write(f"@END_BOOL{CodeWriter.bool_num}\n")
            if command == "gt":
                self.output_stream.write("D;JGT\n")
            elif command == "lt":
                self.output_stream.write("D;JLT\n")

            # If no jump where performed then the answer is false:
            self.output_stream.write(f"@{BOOL}\n")
            self.output_stream.write("M=0\n")
            self.output_stream.write(f"@END_BOOL{CodeWriter.bool_num}\n")
            self.output_stream.write("0;JMP\n")

            # Save the answer in bool in the stack:
            self.output_stream.write(f"(END_BOOL{CodeWriter.bool_num})\n")
            self.output_stream.write(f"@{BOOL}\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("M=D\n")

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        # Write in assembly commands the intended command we want to excecute:
        self.output_stream.write(f"// {command}\n")

        if command in ("add","sub","and","or"):
            self.__non_bool_arithmetic_command(command)

        elif command == "neg":
            #RAM[SP-1]= - RAM[SP-1]
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("M=-M\n")

        elif command in ("eq","gt","lt"):
            self.__bool_comparison_command(command)

        elif command == "not":
            self.output_stream.write("@SP\n") 
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("M=!M\n") # RAM[SP-1] = NOT RAM[SP-1]

        elif command == "shiftleft":
            self.output_stream.write("@SP\n") 
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("M=M<<\n") # RAM[SP-1] = << RAM[SP-1]

        elif command == "shiftright":
            self.output_stream.write("@SP\n") 
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("M=M>>\n") # RAM[SP-1] = >> RAM[SP-1]


    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.

        # This line writes the comment for debugging later.
        self.output_stream.write(f"// {command} {segment} {index}:\n")

        if command not in ("C_PUSH","C_POP"):
            raise ValueError("The given command is invalid should be push or pop.")
        
        if segment not in ("constant","argument","local","static","this","that","pointer","temp"):
            raise ValueError("The given segment is invalid should be: constant,argument,local,static,this,that,pointer or temp.")

        if segment == "constant" and command == "C_POP":
            raise ValueError("Cannot pop to the constant segment.")

        # This part checks which memory to access before push to stack:
        if segment == "constant":
            # Push constant directly onto the stack
            self.output_stream.write(f"@{index}\n")
            self.output_stream.write("D=A\n")
        else:
            # Calculate the address or retrieve its value
            if segment in self.variableTypeDict:
                # Local, argument, this, that
                base_address = self.variableTypeDict[segment]
                self.output_stream.write(f"@{base_address}\n")
                self.output_stream.write("D=M\n")
                self.output_stream.write(f"@{index}\n")
                self.output_stream.write("A=D+A\n")
            elif segment == "temp":
                if index < 0 or index > 7:
                    raise ValueError("Index out of range for temp segment.")
                self.output_stream.write(f"@{5 + index}\n")
            elif segment == "pointer":
                if index not in (0, 1):
                    raise ValueError("Invalid index for pointer segment.")
                self.output_stream.write(f"@{'THIS' if index == 0 else 'THAT'}\n")
            elif segment == "static":
                self.output_stream.write(f"@{self.filename}.{index}\n")

            # Put in D register the variable:
            if command == "C_PUSH":
                self.output_stream.write("D=M\n")
            elif command == "C_POP":
                self.output_stream.write("D=A\n")

        if command == "C_PUSH":
            # RAM[SP] = D
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M\n")
            self.output_stream.write("M=D\n")
            # SP++
            self.output_stream.write("@SP\n")
            self.output_stream.write("M=M+1\n")
            
        elif command == "C_POP":
            # Store target address in R13
            self.output_stream.write(f"@{STORE_ADDRESS}\n")
            self.output_stream.write("M=D\n")
            # SP-- and retrieve top value
            self.output_stream.write("@SP\n")
            self.output_stream.write("AM=M-1\n")
            self.output_stream.write("D=M\n")
            # RAM[R13] = D
            self.output_stream.write(f"@{STORE_ADDRESS}\n")
            self.output_stream.write("A=M\n")
            self.output_stream.write("M=D\n")

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        self.output_stream.write(f"// label {label}:\n")
        self.output_stream.write(f"({self.func_name}${label})\n")
        
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        self.output_stream.write(f"// goto {label}:\n")

        self.output_stream.write(f"@{self.func_name}${label}\n")
        self.output_stream.write("0;JMP\n")
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!

        # Pop value from stack:
        self.output_stream.write(f"// if goto {label}:\n")

        self.output_stream.write("@SP\n")
        self.output_stream.write("AM=M-1\n")
        self.output_stream.write("D=M\n")
        
        # Go to label if the poped value is not zero:
        self.output_stream.write(f"@{self.func_name}${label}\n")
        self.output_stream.write("D;JNE\n")
    
    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self.output_stream.write(f"// funciton {function_name}:\n")

        self.func_name = function_name
        self.output_stream.write(f"({function_name})\n")
        
        for i in range(n_vars):
            self.write_push_pop("C_PUSH", "constant", 0)
    
    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        self.output_stream.write(f"// call {function_name}:\n")
        self.call_counter += 1
        self.output_stream.write(f"@{self.func_name}$ret.{self.call_counter}\n")
        self.output_stream.write("D=A\n")

        # Push the address of the label above to the global stack
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("M=D\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M+1\n")

        # Pushes lcl, arg, this, that to the global stack
        for dest in ["LCL", "ARG", "THIS", "THAT"]:
            self.output_stream.write(f"@{dest}\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M\n")
            self.output_stream.write("M=D\n")
            self.output_stream.write("@SP\n")
            self.output_stream.write("M=M+1\n")

        # ARG = SP-5-n_args. 
        self.output_stream.write(f"@{n_args+5}\n")
        self.output_stream.write("D=A\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("D=M-D\n")
        self.output_stream.write("@ARG\n")
        self.output_stream.write("M=D\n")

        # LCL=SP.
        self.output_stream.write("@SP\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@LCL\n")
        self.output_stream.write("M=D\n")

        # goto function_name
        self.output_stream.write(f"@{function_name}\n")
        self.output_stream.write("0;JMP\n")

        # return_address label
        self.output_stream.write(f"({self.func_name}$ret.{self.call_counter})\n")
    
    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        # frame = LCL
        self.output_stream.write(f"// return {self.func_name}:\n")

        self.output_stream.write("@LCL\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write(f"@{TEMP}\n")
        self.output_stream.write("M=D\n")

        #return_address = *(frame-5)
        self.output_stream.write(f"@{TEMP}\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@5\n")
        self.output_stream.write("A=D-A\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write(f"@{STORE_ADDRESS}\n")
        self.output_stream.write("M=D\n")

        # ARG = pop(). The last value in the stack of the callee is the return value.
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@ARG\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("M=D\n")

        # SP = ARG + 1
        self.output_stream.write("@ARG\n")
        self.output_stream.write("D=M+1\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=D\n")

        #return directories to what they were before the function was
        for i,dest in enumerate(["THAT", "THIS", "ARG", "LCL"]):
            self.output_stream.write(f"@{TEMP}\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write(f"@{i+1}\n")
            self.output_stream.write("A=D-A\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write(f"@{dest}\n")
            self.output_stream.write("M=D\n")

        #return to given address
        self.output_stream.write(f"@{STORE_ADDRESS}\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("0;JMP\n")
