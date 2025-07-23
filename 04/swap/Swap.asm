// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.
// Put your code here.

// Initialize parameters
@R14
D = M

@MaxVal
M = D
@MinVal
M = D
@idx
M = D

A = D

(MainLoop)
// Check end of array
    @R14
    D = M
    @R15
    D = D + M
    @idx
    D = D - M
    @Swap
    D;JEQ

    // Check if current value is max
    @MaxVal
    A = M
    D = M
    @idx
    A = M
    D = D - M
    @UpdateMax
    D;JLT

    // Check if current value is min
    @MinVal
    A = M
    D = M
    @idx
    A = M
    D = D - M
    @UpdateMin
    D;JGT

    // Increment index
    @idx
    M = M + 1

    @MainLoop
    0;JMP

(UpdateMax)
    @idx
    D = M
    @MaxVal
    M = D
    @MainLoop
    0;JMP

(UpdateMin)
    @idx
    D = M
    @MinVal
    M = D
    @MainLoop
    0;JMP

(Swap)
    // Save Min val in temp
    @MinVal
    A = M
    D = M
    @temp
    M = D

    // Save Max val in Min
    @MaxVal
    A = M
    D = M
    @MinVal
    A = M
    M = D

    // Save temp in Max
    @temp
    D = M
    @MaxVal
    A = M
    M = D
(END)
