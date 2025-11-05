// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// This program illustrates low-level handling of the screen and keyboard
// devices, as follows.
//
// The program runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.
// 
// Assumptions:
// Your program may blacken and clear the screen's pixels in any spatial/visual
// Order, as long as pressing a key continuously for long enough results in a
// fully blackened screen, and not pressing any key for long enough results in a
// fully cleared screen.
//
// Test Scripts:
// For completeness of testing, test the Fill program both interactively and
// automatically.
// 
// The supplied FillAutomatic.tst script, along with the supplied compare file
// FillAutomatic.cmp, are designed to test the Fill program automatically, as 
// described by the test script documentation.
//
// The supplied Fill.tst script, which comes with no compare file, is designed
// to do two things:
// - Load the Fill.hack program
// - Remind you to select 'no animation', and then test the program
//   interactively by pressing and releasing some keyboard keys

// Put your code here.

// High level pseudocode:
// while(true)
//{
//  if(keyboard != 0)
//  {
//      draw screen black by asigning every register -1 
//  }
// else
// {
//      draw screen white by asigning every register 0
// }
//}


//  addr = SCREEN
// n = 256
// i = 0
// LOOP:
//    if i > n goto END
//    RAM[addr] = -1 // 1111111111111111
//    advances to the next row
//    addr = addr + 32
//    i = i + 1
//    goto LOOP 
// END:
//     goto END



//Initialize code:
@8192
D=A
@n
M=D // n = 8192

(LOOP)
    @SCREEN
    D=A
    @addr
    M=D // addr = screen address
    @i
    M=0 // i = 0
    @KBD
    D=M // D = key value
    @WHITE
    D;JEQ // If key is not pressed jump to white else continue to black

(BLACK)
    @n
    D=M
    @i
    D=D-M // D = n - i
    @LOOP
    D;JLE // Jump to loop if n<=i

    @addr
    A=M // Access the address using the value stored in addr
    M=-1 // Set all pixels in this register black

    @i
    M=M+1 // i++
    @addr
    M=M+1 // addr++

    @BLACK
    0;JMP

(WHITE)
    @n
    D=M
    @i
    D=D-M // D = n - i
    @LOOP
    D;JLE // Jump to loop if n<=i

    @addr
    A=M // Access the address using the value stored in addr
    M=0 // Set all pixels in this register white

    @i
    M=M+1 // i++
    @addr
    M=M+1 // addr++
    
    @WHITE
    0;JMP


