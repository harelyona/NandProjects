// C_PUSH constant 17:
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 17:
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=0
@UNEQUAL0
D;JNE
@SP
A=M-1
M=-1
(UNEQUAL0)
// C_PUSH constant 17:
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 16:
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=0
@UNEQUAL1
D;JNE
@SP
A=M-1
M=-1
(UNEQUAL1)
// C_PUSH constant 16:
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 17:
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=0
@UNEQUAL2
D;JNE
@SP
A=M-1
M=-1
(UNEQUAL2)
// C_PUSH constant 892:
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 891:
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=0
@GREATEREQUAL3
D;JGE
@SP
A=M-1
M=-1
(GREATEREQUAL3)
// C_PUSH constant 891:
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 892:
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=0
@GREATEREQUAL4
D;JGE
@SP
A=M-1
M=-1
(GREATEREQUAL4)
// C_PUSH constant 891:
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 891:
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=0
@GREATEREQUAL5
D;JGE
@SP
A=M-1
M=-1
(GREATEREQUAL5)
// C_PUSH constant 32767:
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 32766:
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=0
@LESSEQUAL6
D;JLE
@SP
A=M-1
M=-1
(LESSEQUAL6)
// C_PUSH constant 32766:
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 32767:
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=0
@LESSEQUAL7
D;JLE
@SP
A=M-1
M=-1
(LESSEQUAL7)
// C_PUSH constant 32766:
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 32766:
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=0
@LESSEQUAL8
D;JLE
@SP
A=M-1
M=-1
(LESSEQUAL8)
// C_PUSH constant 57:
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 31:
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 53:
@53
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
AM=M-1
D=M
A=A-1
M=M+D
// C_PUSH constant 112:
@112
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
// neg
@SP
A=M-1
M=-M
// and
@SP
AM=M-1
D=M
A=A-1
M=M&D
// C_PUSH constant 82:
@82
D=A
@SP
A=M
M=D
@SP
M=M+1
// or
@SP
AM=M-1
D=M
A=A-1
M=M|D
// not
@SP
A=M-1
M=!M
