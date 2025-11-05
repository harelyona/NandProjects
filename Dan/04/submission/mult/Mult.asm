// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// Multiplies R0 and R1 and stores the result in R2.
//
// Assumptions:
// - R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.
// - You can assume that you will only receive arguments that satisfy:
//   R0 >= 0, R1 >= 0, and R0*R1 < 32768.
// - Your program does not need to test these conditions.
//
// Requirements:
// - Your program should not change the values stored in R0 and R1.
// - You can implement any multiplication algorithm you want.

// Put your code here.

// High level pseudocode:
// val = RAM[0]
// n = RAM[1]
// sum = 0
// i = 0 
// for(int i = 0; i < n; i++)
//{
// sum = sum + val
//}
// RAM[2] = sum

// Initialize Variables
@R0
D=M 
@val
M=D // val = RAM[0]

@R1
D=M 
@n
M=D // n = RAM[1]

@i
M=0 // i = 0

@R2
M=0 // RAM[2] = 0

@sum
M=0 // sum = 0

(LOOP)
    // Check if reached the final loop iteration
    @n
    D=M
    @i
    D=D-M // D = n - i
    @END
    D;JLE // Jump to end if n - i <= 0 
    
    @val
    D=M
    @sum
    M=D+M // val = val + sum

    // iterate the loop
    @i
    M=M+1 // i++

    @LOOP
    0;JMP // unconditional jmp to repeat this loop again

(END)
    @sum
    D=M // D = sum
    @R2 
    M=D // RAM[2] = sum

(HALT)
    @HALT
    0;JMP // terminate the program with an infinite loop


