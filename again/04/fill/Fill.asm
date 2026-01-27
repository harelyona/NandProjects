@color
M=0

(RestartColoring)
    @SCREEN      // Load Screen base address (16384)
    D=A
    @curPixel
    M=D          // Reset curPixel to start of screen

(MainLoop)
    // --- PART 1: UPDATE COLOR ---
    // Instead of jumping away, we check KBD right here
    @KBD
    D=M          // Read keyboard
    @SetBlack
    D;JNE        // If Key pressed (!=0), goto SetBlack

    // Set White (Default behavior if no jump)
    @color
    M=0
    @DrawPixel   // Jump to drawing (skip the black setting)
    0;JMP

(SetBlack)
    @color
    M=-1         // Set color to -1 (Black)
                 // No jump needed, we fall through to DrawPixel

    // --- PART 2: DRAW PIXEL ---
(DrawPixel)      // We arrive here with 'color' updated
    @color
    D=M          // Load the color (-1 or 0)
    @curPixel
    A=M          // Get the address of the current pixel
    M=D          // Paint the pixel!

    // --- PART 3: ADVANCE & LOOP ---
    @curPixel
    M=M+1        // Move to next pixel

    // Check bounds
    @curPixel
    D=M
    @KBD         // KBD address (24576) is exactly 1 word after Screen ends
    D=A-D        // Calculate (End_Address - Current_Address)

    @RestartColoring
    D;JEQ        // If 0 (reached end), reset to top

    @MainLoop
    0;JMP        // Otherwise, process next pixel