"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class Code:
    """Translates Hack assembly language mnemonics into binary codes."""
    
    @staticmethod
    def dest(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a dest mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        d1 = '1' if 'A' in mnemonic else '0'
        d2 = '1' if 'D' in mnemonic else '0'
        d3 = '1' if 'M' in mnemonic else '0'
        return d1 + d2 + d3


    @staticmethod
    def comp(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a comp mnemonic string.

        Returns:
            str: the binary code of the given mnemonic.
        """
        a_bit = "1" if "M" in mnemonic else "0"
        if "A" in mnemonic:
            mnemonic = mnemonic.replace("A", "M")
        prefix = '101' if ">>" in mnemonic or "<<" in mnemonic else '111'

        comp_map = {
            "0": "101010", "1": "111111", "-1": "111010", "D": "001100", "M": "110000",
            "!D": "001101", "!M": "110001", "-D": "001111", "-M": "110011", "D+1": "011111",
            "M+1": "110111", "D-1": "001110", "M-1": "110010", "D+M": "000010", "D-M": "010011",
            "M-D": "000111", "D&M": "000000", "D|M": "010101",
            "M<<": "100000", "D<<": "110000", "M>>": "000000", "D>>": "010000"
        }
        return prefix + a_bit + comp_map[mnemonic]

    @staticmethod
    def jump(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a jump mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        if not mnemonic:
            return "000"
        if mnemonic == "JGT":
            return "001"
        if mnemonic == "JEQ":
            return "010"
        if mnemonic == "JGE":
            return "011"
        if mnemonic == "JLT":
            return "100"
        if mnemonic == "JNE":
            return "101"
        if mnemonic == "JLE":
            return "110"
        if mnemonic == "JMP":
            return "111"

# c = Code()
# assert c.comp('0') == "1110101010"
# assert c.comp('1') == "1110111111"
# assert c.comp('-1') == "1110111010"
# assert c.comp('D') == "1110001100"
# assert c.comp('M') == "1111110000"
# assert c.comp('A') == "1110110000"
# assert c.comp('!D') == "1110001101"
# assert c.comp('!M') == "1111110001"
# assert c.comp('-D') == "1110001111"
# assert c.comp('-M') == "1111110011"
# assert c.comp('D+1') == "1110011111"
# assert c.comp('M+1') == "1111110111"
# assert c.comp('D-1') == "1110001110"
# assert c.comp('M-1') == "1111110010"
# assert c.comp('D+M') == "1111000010"
# assert c.comp('D-M') == "1111010011"
# assert c.comp('M-D') == "1111000111"
# assert c.comp('D&M') == "1111000000"
# assert c.comp('D|M') == "1111010101"
# assert c.comp('D|A') == "1110010101"
# assert c.comp("A<<") == "1010100000"
# assert c.comp("D<<") == "1010110000"
# assert c.comp("M<<") == "1011100000"
#
# assert c.comp('M<<') == "1011100000"


