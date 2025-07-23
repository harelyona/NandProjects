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

(MainLoop)
    @KBD
    D = M
    @BlackScreen
    D;JNE
    @WhiteScreen
    0;JMP

(BlackScreen)
    @SCREEN
    D = A
    @i
    M = D

(BlackLoop)
    @KBD
    D = A
    @i
    D = M - D
    @MainLoop
    D;JEQ
    @i
    A = M
    M = -1
    @i
    M = M + 1
    @KBD
    D = M
    @BlackLoop
    D;JNE
    @MainLoop
    0;JMP

(WhiteScreen)
    @SCREEN
    D = A
    @i
    M = D

(WhiteLoop)
    @KBD
    D = A
    @i
    D = M - D
    @MainLoop
    D;JEQ
    @i
    A = M
    M = 0
    @i
    M = M + 1
    @KBD
    D = M
    @MainLoop
    D;JNE
    @WhiteLoop
    0;JMP