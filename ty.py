__author__ = 'ZhangJingtian'
import sym
import lexer

class Type(lexer.Word):
    def __init__(self, s, tag, w, a):
        super(Type , self).__init__(s, tag)
        self.width = w
        self.align = a

    @classmethod
    def numeric(cls, ty):
        if (ty is Type.Int) or (ty is Type.UnsignedInt) or (type(ty) is Pointer) \
            or (ty is Type.Null) or (type(ty) is Function):
            return True
        return False


    @classmethod
    def max(cls, ty1, ty2):
        if (not cls.numeric(ty1)) or (not cls.numeric(ty2)):
            return None
        elif ty1 is Type.UnsignedInt or ty2 is Type.UnsignedInt:
            return Type.UnsignedInt
        elif ty1 is Type.Int or ty2 is Type.Int:
            return Type.Int
        return None

    @classmethod
    def isbasic(cls, tok):
        if tok.tag == lexer.Tag.INT or tok.tag == lexer.Tag.UNSIGNED \
            or tok.tag == lexer.Tag.VOID:
            return True
        return False

    def isvoid(self, tok):
        if tok.tag == lexer.Tag.VOID:
            return True
        return False

    @classmethod
    def isstruct(cls, tok):
        if tok.tag == lexer.Tag.STRUCT:
            return True
        return False

    @classmethod
    def isfunction(cls, tok):
        if tok.tag == lexer.Tag.FUNCTION:
            return True
        return False

    @classmethod
    def isarray(cls, tok):
        if tok.tag == lexer.Tag.ARRAY:
            return True
        return False

    @classmethod
    def ispointer(cls, tok):
        if tok.tag == lexer.Tag.POINTER:
            return True
        return False

    def get_width(self):
        return self.width

    def get_align(self):
        return self.align

class Array(Type):
    def __init__(self, size, of_type):
        super(Array, self).__init__("ARRAY", lexer.Tag.ARRAY, size * of_type.get_width(), of_type.get_align())
        self._size    = size
        self._of_type = of_type

    def get_of_type(self):
        return self._of_type

class Struct(Type):
    def __init__(self, token):
        super(Struct, self).__init__("STRUCT", lexer.Tag.STRUCT, 0, 0)
        self._ids = sym.IdentifierTable()
        self._token  = token
        self._used   = 0

    def get_identifier_table(self):
        return self._ids

    def init_struct_field(self, id_obj):
        id_type = id_obj.get_type()
        id_obj.set_offset(self._used)
        self._used = self._used + id_type.get_width()

    def __str__(self):
        return str(self._token)

class Pointer(Type):
    def __init__(self, ty):
        super(Pointer, self).__init__("POINTER",lexer.Tag.POINTER, 4, 4)
        self._ref_type = ty

    def get_ref_type(self):
        return self._ref_type

class Function(Type):
    def __init__(self):
        super(Function, self).__init__("FUNCTION", lexer.Tag.FUNCTION, 4, 4)
        self._ids     = sym.IdentifierTable()
        self._ret_type= None
        self._proto   = None
        self._stmt    = None

    def init(self, proto, rettype):
        self._ret_type   = rettype
        self._proto      = proto

    def get_identifier_table(self):
        return self._ids

    def get_ret_type(self):
        return self._ret_type

    def get_protos(self):
        return self._proto

    def set_statement(self, func_stmt):
        self._stmt = func_stmt

    def get_statement(self):
        return self._stmt

Type.Int            =   Type("int",             lexer.Tag.INT,      4, 4)
Type.UnsignedInt    =   Type("unsigned int",    lexer.Tag.INT,      4, 4)
Type.Void           =   Type("",                lexer.Tag.VOID,     0, 0)
Type.VoidPointer    =   Type("T*",              lexer.Tag.POINTER,  4, 4)
Type.Null           =   Type("null",            lexer.Tag.NULL,     0, 0)


