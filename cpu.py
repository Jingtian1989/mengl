__author__ = 'ZhangJingtian'
import ast
class OpCode(object):
    """OpCode class

    The supported opcode.

    """
    ANDR    = "andr"
    ANDI    = "andi"
    ORR     = "orr"
    ORI     = "ori"
    XORR    = "xorr"
    XORI    = "xori"
    ADDSR   = "addsr"
    ADDSI   = "addsi"
    ADDUR   = "addur"
    ADDUI   = "addui"
    SUBSR   = "subsr"
    SUBUR   = "subur"
    MULSR   = "mulsr"
    MULSI   = "mulsi"
    MULUR   = "mulur"
    MULUI   = "mului"
    DIVSR   = "divsr"
    DIVSI   = "divsi"
    DIVUR   = "divur"
    DIVUI   = "divui"
    SHRLR   = "shrlr"
    SHRLI   = "shrli"
    SHLLR   = "shllr"
    SHLLI   = "shlli"
    BE      = "be"
    BNE     = "bne"
    BSGT    = "bsgt"
    BUGT    = "bugt"
    JMP     = "jmp"
    CALL    = "call"
    LDW     = "ldw"
    STW     = "stw"
    HALT    = "halt"