__author__ = 'ZhangJingtian'

class Tag(object):
    AND     =   256
    ARRAY   =   257
    BREAK   =   258
    CHAR    =   259
    CONTINUE=   260
    CAST    =   261
    DO      =   262
    EQ      =   263
    ELSE    =   264
    FUNCTION=   265
    GE      =   266
    ID      =   267
    IF      =   268
    INT     =   270
    INDEX   =   271

    LS      =   272
    LE      =   273
    NUM     =   275
    NULL    =   276
    NE      =   277
    OR      =   278
    OF      =   279
    POINTER =   280
    PTR     =   281
    RETURN  =   282
    RS      =   283
    SIZEOF  =   285
    STRUCT  =   286
    TEMP    =   287
    TO      =   288
    VOID    =   289
    UNSIGNED=   290
    WHILE   =   291

class Token(object):
    def __init__(self, tag):
        super(Token, self).__init__()
        self.tag = tag

    def get_tag(self):
        return self.tag

    def __str__(self):
        return str(self.tag)

class Word(Token):
    def __init__(self, lexeme, tag):
        super(Word, self).__init__(tag)
        self.lexeme = lexeme

    def __str__(self):
        return str(self.lexeme)

class Num(Token):
    def __init__(self, v):
        super(Num, self).__init__(Tag.NUM)
        self.value = v

    def __str__(self):
        return str(self.value)

class Char(Token):
    def __init__(self, c):
        super(Char).__init__(Tag.CHAR)
        self.value = c

    def __str__(self):
        return str(self.value)


Word.AND    =   Word("&&",      Tag.AND)
Word.OR     =   Word("||",      Tag.OR)
Word.EQ     =   Word("==",      Tag.EQ)
Word.NE     =   Word("!=",      Tag.NE)
Word.LE     =   Word("<=",      Tag.LE)
Word.GE     =   Word(">=",      Tag.GE)
Word.RS     =   Word(">>",      Tag.RS)
Word.LS     =   Word("<<",      Tag.LS)
Word.PTR    =   Word("->",      Tag.PTR)
Word.TEMP   =   Word("t",       Tag.TEMP)


class Lexer(object):
    line = 1
    def __init__(self, text):
        super(Lexer, self).__init__()
        self.peek   = ' '
        self.words  = {}
        self.text   = text
        self.cursor = 0

        self.reserve(Word("array",      Tag.ARRAY))
        self.reserve(Word("break",      Tag.BREAK))
        self.reserve(Word("continue",   Tag.CONTINUE))
        self.reserve(Word("cast",       Tag.CAST))
        self.reserve(Word("do",         Tag.DO))
        self.reserve(Word("else",       Tag.ELSE))
        self.reserve(Word("function",   Tag.FUNCTION))
        self.reserve(Word("if",         Tag.IF))
        self.reserve(Word("int",        Tag.INT))
        self.reserve(Word("null",       Tag.NULL))
        self.reserve(Word("of",         Tag.OF))
        self.reserve(Word("pointer",    Tag.POINTER))
        self.reserve(Word("return",     Tag.RETURN))
        self.reserve(Word("struct",     Tag.STRUCT))
        self.reserve(Word("sizeof",     Tag.SIZEOF))
        self.reserve(Word("to",         Tag.TO))
        self.reserve(Word("unsigned",   Tag.UNSIGNED))
        self.reserve(Word("void",       Tag.VOID))
        self.reserve(Word("while",      Tag.WHILE))

    def reserve(self, word):
        self.words[word.lexeme] = word

    def isdigit(self, v):
        if (v is not None) and v >= '0' and v <= '9':
            return True
        else:
            return False

    def isletter(self, v):
        if (v is not None) and ((v >='a' and v <= 'z') or (v >= 'A' and v <= 'Z')):
            return True
        else:
            return False

    def isletterOrdigitOrline(self, v):
        return self.isletter(v) or self.isdigit(v) or v == '_'

    def __readchar(self):
        if self.cursor < len(self.text):
            self.peek = self.text[self.cursor]
            self.cursor = self.cursor + 1
        else:
            self.peek = None

    def __readcharc(self, c):
        self.__readchar()
        if self.peek != c:
            return False
        self.peek = ' '
        return True

    def __esc(self):
        v = ""
        v += self.peek
        self.__readchar()
        v += self.peek
        return v

    def error(self, s):
        raise Exception("lexer error at line %d, %s."%(Lexer.line, s))

    def scan(self):
        while self.peek == ' ' or self.peek == '\t' or self.peek == '\n':
            if self.peek == '\n':
                Lexer.line = Lexer.line + 1
            self.__readchar()

        if self.peek == '&':
            if self.__readcharc('&'):
                return Word.AND
            else:
                return Token('&')
        elif self.peek == '|':
            if self.__readcharc('|'):
                return  Word.OR
            else:
                return Token('|')
        elif self.peek == '=':
            if self.__readcharc('='):
                return Word.EQ
            else:
                return Token('=')
        elif self.peek == '!':
            if self.__readcharc('='):
                return Word.NE
            else:
                return Token('!')
        elif self.peek == '<':
            if self.__readcharc('='):
                return Word.LE
            elif self.peek == '<':
                self.__readchar()
                return Word.LS
            else:
                return Token('<')
        elif self.peek == '>':
            if self.__readcharc('='):
                return Word.GE
            elif self.peek == '>':
                self.__readchar()
                return Word.RS
            else:
                return Token('>')

        elif self.peek == '-':
            if self.__readcharc('>'):
                return Word.PTR
            else:
                return Token('-')

        if self.peek == '\'':
            v = self.__readchar()
            if not self.__readcharc('\''):
                self.error("single quota")
            return Char(v)


        if self.isdigit(self.peek):
            v = 0
            while self.isdigit(self.peek):
                v = 10*v + int(self.peek)
                self.__readchar()
            return Num(v)

        if self.isletter(self.peek):
            s = ""
            while self.isletterOrdigitOrline(self.peek):
                s += self.peek
                self.__readchar()
            if self.words.get(s) is not None:
                return self.words.get(s)
            w = Word(s, Tag.ID)
            self.words[s] = w
            return w

        tok = Token(self.peek)
        self.peek = ' '
        return tok

