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
@NOT_EQUAL1
D;JNE
// Handle the equal case by setting -1 (true)
@SP
A=M-1
M=-1
(NOT_EQUAL1)
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
@Y_NEGATIVE2
D;JLT
@R14
M=D
@SP
A=M-1
D=M
@X_NEGATIVE_Y_POSITIVE2
D;JLT
// Handle the case where both are positive or zero:
@R14
D=D-M
@R15
M=-1
@END_BOOL2
D;JLT
@R15
M=0
@END_BOOL2
0;JMP
(X_NEGATIVE_Y_POSITIVE2)
@R15
M=-1
@END_BOOL2
0;JMP
(Y_NEGATIVE2)
@R14
M=D
@SP
A=M-1
D=M
@X_AND_Y_NEGATIVE2
D;JLT
// Handle the case where x>=0 and y<0:
@R15
M=0
@END_BOOL2
0;JMP
(X_AND_Y_NEGATIVE2)
// Handle the case where both negative:
@R14
D=D-M
@R15
M=-1
@END_BOOL2
D;JLT
@R15
M=0
@END_BOOL2
0;JMP
(END_BOOL2)
@R15
D=M
@SP
A=M-1
M=D
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
@Y_NEGATIVE3
D;JLT
@R14
M=D
@SP
A=M-1
D=M
@X_NEGATIVE_Y_POSITIVE3
D;JLT
// Handle the case where both are positive or zero:
@R14
D=D-M
@R15
M=-1
@END_BOOL3
D;JGT
@R15
M=0
@END_BOOL3
0;JMP
(X_NEGATIVE_Y_POSITIVE3)
@R15
M=0
@END_BOOL3
0;JMP
(Y_NEGATIVE3)
@R14
M=D
@SP
A=M-1
D=M
@X_AND_Y_NEGATIVE3
D;JLT
// Handle the case where x>=0 and y<0:
@R15
M=-1
@END_BOOL3
0;JMP
(X_AND_Y_NEGATIVE3)
// Handle the case where both negative:
@R14
D=D-M
@R15
M=-1
@END_BOOL3
D;JGT
@R15
M=0
@END_BOOL3
0;JMP
(END_BOOL3)
@R15
D=M
@SP
A=M-1
M=D
// C_PUSH constant 56:
@56
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
