"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.output_stream = output_stream
        self.file_name = None
        self.label_counter = 0
        self.function_name = ""

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
        self.file_name = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        self.output_stream.write("//" + command + "\n")
        self.label_counter += 1
        pop_last_to_D = "@SP\nAM=M-1\nD=M\n"
        go_one_element_back = "A=A-1\n"
        update_to_true = "@SP\nA=M-1\nM=-1\n"
        update_to_false = "@SP\nA=M-1\nM=0\n"
        push_D = "@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        if command == "add":
            self.output_stream.write(f"{pop_last_to_D}{go_one_element_back}M=M+D\n")
            return
        if command == "sub":
            self.output_stream.write(f"{pop_last_to_D}{go_one_element_back}M=M-D\n")
            return

        if command == "neg":
            self.output_stream.write("@SP\nA=M-1\nM=-M\n")
            return
        true_label = f"TRUE{self.label_counter}"
        continue_label = f"CONTINUE{self.label_counter}"
        jump_to_end = f"@CONTINUE{self.label_counter}\n0;JMP\n"

        if command in ["eq", "gt", "lt"]:
            normal_case_label = "NORMAL_CASE" + str(self.label_counter)
            y_positive_label = "y_POSITIVE" + str(self.label_counter)
            y_negative_label = "y_NEGATIVE" + str(self.label_counter)
            insert_y_to_D = "@SP\nA=M-1\nD=M\n"
            condition = {"eq": "D;JEQ", "gt": "D;JGT", "lt": "D;JLT"}[command]
            if command in ("gt", "lt"):
                # For gt and lt, check bit overflow

                # Check the sign of the first number
                self.output_stream.write(f"{insert_y_to_D}\n@{y_positive_label}\n"
                                         f"D;JGT\n@{y_negative_label}\nD;JLT\n"
                                         f"@{normal_case_label}\n0;JMP\n")
                # Check the sign of the second number
                self.output_stream.write(f"({y_positive_label})\n")
                self._y_positive(command, normal_case_label)
                self.output_stream.write(f"({y_negative_label})\n")
                self._y_negative(command, normal_case_label)

            # Normal case
            self.output_stream.write(f"({normal_case_label})\n{pop_last_to_D}{go_one_element_back}D=M-D\n"
                                     f"@{true_label}\n{condition}\n{update_to_false}"
                                     f"{jump_to_end}({true_label})\n"
                                     f"{update_to_true}({continue_label})\n")
            return
        if command == "not":
            self.output_stream.write(f"{pop_last_to_D}D=-D\nD=D-1\n{push_D}")
            return
        compute = {"and": "M=D&M\n", "or": "M=D|M\n"}[command]
        self.output_stream.write(f"{pop_last_to_D}{go_one_element_back}{compute}\n")


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
        move_to_segment = {"argument": f"@ARG\nD=M\n@{index}\nA=D+A\n",
            "local": f"@LCL\nD=M\n@{index}\nA=D+A\n",
            "static": f"@{self.file_name}.{index}\n",
            "constant": f"@{index}\n",
            "this": f"@THIS\nD=M\n@{index}\nA=D+A\n",
            "that": f"@THAT\nD=M\n@{index}\nA=D+A\n",
            "pointer": f"@{3 + index}\n",
            "temp": f"@{5 + index}\n"}
        self.output_stream.write("//" + command[2:].lower() + " " + segment + " " + str(index) + "\n")
        if command == "C_PUSH":
            self.output_stream.write(move_to_segment[segment])
            if segment == "constant":
                self.output_stream.write(f"D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            else:
                self.output_stream.write("D=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            return
        self.output_stream.write(move_to_segment[segment])
        self.output_stream.write("D=A\n@temp\nM=D\n")
        self.output_stream.write("@SP\nAM=M-1\nD=M\n@temp\nA=M\nM=D\n")


    def _y_positive(self, command, normal_case_label):
        insert_x_into_D = "@SP\nA=M-1\nA=A-1\nD=M\n"
        push_false = "A=M-1\nM=0\n"
        push_true = "A=M-1\nM=-1\n"
        negative_positive_label = "NEGATIVE_POSITIVE" + str(self.label_counter)
        self.output_stream.write(f"{insert_x_into_D}"
                                 f"@{negative_positive_label}\nD;JLT\n@{normal_case_label}\n0;JMP\n")
        self.output_stream.write(f"({negative_positive_label})\n@SP\nM=M-1\n")
        if command == "gt":
            self.output_stream.write(push_false)
        if command == "lt":
            self.output_stream.write(push_true)
        self.output_stream.write(f"@CONTINUE{self.label_counter}\n0;JMP\n")


    def _y_negative(self, command, normal_case_label):
        insert_x_into_D = "@SP\nA=M-1\nA=A-1\nD=M\n"
        push_false = "@SP\nA=M-1\nM=0\n"
        push_true = "@SP\nA=M-1\nM=-1\n"
        positive_negative_label = "POSITIVE_NEGATIVE" + str(self.label_counter)

        self.output_stream.write(f"{insert_x_into_D}"
                                 f"@{positive_negative_label}\nD;JGT\n@{normal_case_label}\n0;JMP\n")
        self.output_stream.write(f"({positive_negative_label})\n@SP\nM=M-1\n")
        if command == "gt":
            self.output_stream.write(push_true)
        if command == "lt":
            self.output_stream.write(push_false)
        self.output_stream.write(f"@CONTINUE{self.label_counter}\n0;JMP\n")

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
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        self.output_stream.write(f"// write label {label}\n")
        self.output_stream.write(f"({self.file_name}.{self.function_name}${label})\n")

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.
        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        self.output_stream.write("// write goto " + label + "\n")
        self.output_stream.write(f"@{self.file_name}.{self.function_name}${label}\n")
        self.output_stream.write("0;JMP\n")
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pop = "@SP\nAM=M-1\nD=M\n"
        goto_label = f"{self.file_name}.{self.function_name}${label}\n"
        self.output_stream.write("// write if-goto " + label + "\n")
        self.output_stream.write(f"{pop}@{goto_label}\nD;JNE\n")
    
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
        pass
    
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
        pass
    
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
        pass

