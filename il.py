__author__ = 'ZhangJingtian'
import ast

class Tacode(object):
    ASSIGN = 1
    IFFALSE= 2
    IFTRUE = 3
    GOTO   = 4
    PARAM  = 5
    CALL   = 6
    LDRET  = 7
    STRET  = 8
    RETURN = 9
    def __init__(self, op=None, arg1=None, arg2=None, arg3=None):
        self.op   = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def get_opcode(self):
        return self.op

class Assign(Tacode):
    def __init__(self, dst, src):
        super(Assign, self).__init__(op=Tacode.ASSIGN, arg1=dst, arg2=src)
    def __str__(self):
        return str(self.arg1) + " " + "=" + " " + str(self.arg2)

class IfFalse(Tacode):
    def __init__(self, rel, dst):
        super(IfFalse, self).__init__(op=Tacode.IFFALSE, arg1=rel, arg2=dst)

    def __str__(self):
        return "iffalse" + " " + str(self.arg1) + " " + "goto" + " " + str(self.arg2)

class IfTrue(Tacode):
    def __init__(self, rel, dst):
        super(IfTrue, self).__init__(op=Tacode.IFTRUE, arg1=rel, arg2=dst)

    def __str__(self):
        return "iftrue" + " " + str(self.arg1) + " " + "goto" + " " + str(self.arg2)

class Goto(Tacode):
    def __init__(self, dst):
        super(Goto, self).__init__(op=Tacode.GOTO, arg1=dst)

    def __str__(self):
        return "goto" + " " + str(self.arg1)

class Param(Tacode):
    def __init__(self, param):
        super(Param, self).__init__(op=Tacode.PARAM, arg1=param)

    def __str__(self):
        return "param" + " " + str(self.arg1)

class Call(Tacode):
    def __init__(self, call, n):
        super(Call, self).__init__(op=Tacode.CALL, arg1=call, arg2=n)

    def __str__(self):
        return "call" + " " + str(self.arg1) + "," + " " + str(self.arg2)

class LoadRet(Tacode):
    def __init__(self, temp):
        super(LoadRet, self).__init__(op=Tacode.LDRET, arg1=temp)

    def __str__(self):
        return "loadret" + " " + str(self.arg1)

class StoreRet(Tacode):
    def __init__(self, ret):
        super(StoreRet, self).__init__(op=Tacode.STRET, arg1=ret)

    def __str__(self):
        return "saveret" + " " + str(self.arg1)

class Ret(Tacode):
    def __init__(self):
        super(Ret, self).__init__(op=Tacode.RETURN)

    def __str__(self):
        return "ret"

class Label(object):
    def __init__(self, num):
        super(Label, self).__init__()
        self.num = num

    def set_code(self, code):
        self.code = code

    def __str__(self):
        return "l" + str(self.num)

class LabelSet(object):
    def __init__(self):
        self.labels = list()

    def append(self, label):
        self.labels.append(label)

    def get_labels(self):
        return self.labels

    def __str__(self):
        s = ""
        for label in self.labels:
            s = s + str(label) + ":"
        return s

    def __len__(self):
        return len(self.labels)

class Line(object):
    def __init__(self, code=None):
        self.code   = code
        self.labels = LabelSet()

    def __str__(self):
        return str(self.labels) + " " + str(self.code)

    def get_code(self):
        return self.code

    def get_label_set(self):
        return self.labels

class Frame(object):
    def __init__(self, id_obj):
        super(Frame, self).__init__()
        self._id_obj    = id_obj
        self._label     = 0
        self._used      = 4
        self._local_used= 0
        self._param_used= 0
        self._temps     = []
        self._locals    = []
        self._table     = []
        self._line      = Line()
        self._start     = self.new_label()
        self._end       = self.new_label()


    def get_frame_id(self):
        return self._id_obj

    def get_frame_start(self):
        return self._start

    def get_frame_end(self):
        return self._end

    def get_tacode_table(self):
        return self._table

    def get_local_size(self):
        return self._local_used

    def get_param_size(self):
        return self._param_used

    def align_offset(self, curr_offset, align):
        return(curr_offset + (align - 1))&(~(align-1))

    def alloc_local(self, id_obj, is_param=False):
        id_type     = id_obj.get_type()
        id_align    = id_type.get_align()
        id_width    = id_type.get_width()
        if is_param:
            offset = self.align_offset(self._param_used, id_align)
            self._param_used = offset + id_width
            #skip oldfp pointer
            offset = -offset -4
        else:
            offset = self.align_offset(self._local_used, id_align)
            self._local_used = offset + id_width
            #skip oldfp pointer & return address pointer
            offset = offset + 8
        id_obj.set_offset(offset)

    def alloc_temp(self, temp_type):
        num = len(self._temps)
        temp = ast.Temporary(num, temp_type)
        self._temps.append(temp)
        return temp

    def new_label(self):
        l = Label(self._label)
        self._label = self._label + 1
        return l

    def emit_code(self, code):
        self._line.code = code
        self._table.append(self._line)
        self._line = Line()

    def emit_label(self, label):
        self._line.labels.append(label)

    def emit_end(self):
        self.emit_label(self.get_frame_end())
        self.emit_code(Ret())
