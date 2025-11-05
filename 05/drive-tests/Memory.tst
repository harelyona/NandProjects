// This file is part of the materials accompanying the book
// "The Elements of Computing Systems" by Nisan and Schocken, 
// MIT Press 2004. Book site: http://www.idc.ac.il/tecs
// File name: projects/05/Memory.tst.   Version: beta 1.4.

load Memory.hdl,
output-file Memory.out,
compare-to Memory.cmp,
output-list in%D1.6.1 load%B2.1.2 address%D2.5.2 out%D1.6.1;

echo "Before you run this script, select the 'Screen' option from the 'View' menu";

set in 0,
set load 0,
set address 0,
tick,
output;
tock,
output;

set load 1,
tick,
output;
tock,
output;

set in 4444,
set load 0,
tick,
output;
tock,
output;

set load 1,
set address 4444,
tick,
output;
tock,
output;

set load 0,
set address 0,
tick,
output;
tock,
output;

set in 13131,
set address 13131,
tick,
output;
tock,
output;

set load 1,
tick,
output;
tock,
output;

set load 0,
tick,
output;
tock,
output;

set address 4444,
eval,
output;

set in 16383,
tick,
output;
tock,
output;

set load 1,
set address 16383,
tick,
output;
tock,
output;

set load 0,
tick,
output;
tock,
output;

set address 13131,
eval,
output;

set address 16383,
eval,
output;


clear-echo,
output;

set load 1,
set in -1,
set address 20431,
tick,
tock,
output,

set address 20559,
tick,
tock,
output,

set load 0,
set address 24576,
eval,
clear-echo,
output;
