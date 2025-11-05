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

// Pseudo code:
// Initialize index i = 0
// initialize a variable min and max with the first variable of the array
// Initialize the adress of min and max
// Loop for the length of the array and compare between min and max and update them accordingly and save their adresses.


// Initialization:
// i=0
@i 
M=0

// D=arr[0]
@R14
A=M
D=M

// max = arr[0]
@max
M=D
// min = arr[0]
@min
M=D

// max_address = address of first element
@R14
D=M
@max_address
M=D
// min_address = address of first element
@min_address
M=D


(LOOP)
    // Check if we reached the end if the array. If yes then perform a swap.
    @i
    D=M 
    @R15
    D=D-M
    @SWAP
    D;JGE

    // Get the current array value
    @R14
    D=M 
    @i 
    A=D+M

    // D = arr[i]
    D=M
    @max
    D=D-M
    @CHECKMIN
    D;JLE

    // if the arr[i] <= skip update max otherwise update max:
    // max = arr[i]
    @R14
    D=M 
    @i 
    D=D+M
    @max_address
    M=D
    A=D
    // D = arr[i]
    D=M
    @max
    M=D

(CHECKMIN)
    // Get the current array value
    @R14
    D=M 
    @i 
    A=D+M
    
    // D = arr[i]
    D=M
    @min
    D=D-M
    @INCREMENT
    D;JGE

    // if the arr[i] >= skip update mmin otherwise update min:
    // min = arr[i]
    @R14
    D=M 
    @i 
    D=D+M
    @min_address
    M=D
    A=D
    // D = arr[i]
    D=M
    @min
    M=D

(INCREMENT)
    // i++
    @i
    M=M+1
    @LOOP
    0;JMP

(SWAP)
    // Swap between the min and max value in the array

    // Go to address of min value and update it with max value
    @max
    D=M 
    @min_address
    A=M 
    M=D

    // Go to address of max value and update it with min value
    @min
    D=M 
    @max_address
    A=M 
    M=D

(END)
    @END
    0;JMP

