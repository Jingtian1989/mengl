__author__ = 'ZhangJingtian'
import ty
import il
import sym
import lexer
import errors

class Node(object):
    """ Node class

    The top class of ast node.

    """
    def __init__(self):
        super(Node, self).__init__()
        self.lexline = lexer.Lexer.line

    def _type_error(self, expected, encountered):
        """ Print Type Error Message

        Prints a type error message with details about the expected type an
        the type that was encountered.

        Arguments:
            encountered : A string containing the type encountered.
        """
        msg = 'Expected %s type, encounted %s' % (expected, encountered)
        print('Error: "%s", line %d' % (msg, self.lexline))
        return

    def emit_label(self, label, frame):
        """ Emit the label

        Emits the label to the current line of frame.

        Arguments:
            label: The label containing the label number.
            ar: The function frame.
        """
        frame.emit_label(label)
        return

    def emit(self, code, frame):
        """Emit the code

        Emits the IL code to frame.

        Arguments:
            code: A three address code.
            ar: The function table.
        """
        frame.emit_code(code)

class Expression(Node):
    def __init__(self, token, expr_type):
        super(Expression, self).__init__()
        self._op    = token
        self._type  = expr_type

    def gen(self, frame):
        """ Generate Expression's Node

        Generate a node represent the expression.

        Arguments:
            ar: The function table.

        """
        return self

    def reduce(self, frame):
        """ Reduce Expression's Value

        Generate a node containing the expression's value.

        Arguments:
            ar: The function table.
        """
        return self

    def jumping(self, true_label, false_label, frame):
        """ Generate Expression's Jumping Code

        Arguments:
            true_label: The true branch.
            false_label: The false branch.
        """
        const = Constant(lexer.Num(0), ty.Type.Int)
        self.emitjumps(Rel(lexer.Token('>'), self.reduce(frame), const), true_label, false_label, frame)

    def emitjumps(self, con, t, f, frame):
        """ Emit Jumping Code

        Emit the jumping code to three address code table.

        """
        if t != 0 and f != 0:
            self.emit(il.IfTrue(con, t), frame)
            self.emit(il.Goto(f), frame)
        elif t != 0:
            self.emit(il.IfTrue(con, t), frame)
        elif f != 0:
            self.emit(il.IfFalse(con, f), frame)

    def get_type(self):
        return self._type

    def __str__(self):
        return str(self._op)

class Symbol(Expression):
    """ Symbol class

    The base class of symbols that have to been stored in identifier table.

    """
    def __init__(self, token, sym_type):
        super(Symbol, self).__init__(token, sym_type)

    def get_offset(self):
        """Get Offset

        Gets the symbol's offset within the it's id table.

        """
        return self._offset

    def set_offset(self, offset):
        self._offset = offset

class Identifier(Symbol):
    """ Identifier class

    Represent the identifier declared in program scope.

    """
    def __init__(self, token, id_type):
        super(Identifier, self).__init__(token, id_type)

class Constant(Symbol):
    """ Constant class

    Represent the constant used in the program scope.

    """
    def __init__(self, token, id_type):
        super(Constant, self).__init__(token, id_type)

class Temporary(Symbol):
    """ Temporary class

    Represent the temporary generated through the parses.

    """
    def __init__(self, num, temp_type):
        super(Temporary, self).__init__(lexer.Word.TEMP, temp_type)
        self._num = num
    def __str__(self):
        return "t" + str(self._num)

class Funcall(Expression):
    """ Funcall class

    Represent the function call node.

    """
    def __init__(self, id_expr, args):
        super(Funcall, self).__init__(lexer.Word("call", lexer.Tag.FUNCTION), None)
        self._id_expr = id_expr
        self._args  = args
        self._type  = self.check(id_expr.get_type())

    def check(self, t):
        ret = t
        if type(t) is ty.Pointer:
            ret = t.get_ref_type()
        if type(ret) is ty.Function:
            return ret.get_ret_type()
        self._type_error("pointer or function", str(t))

    def reduce(self, frame):
        func_call = self.gen(frame)
        for arg in func_call.get_args():
            self.emit(il.Param(param=arg), frame)
        args_count = len(func_call.get_args())
        const = Constant(lexer.Num(args_count), ty.Type.Int)
        self.emit(il.Call(call=func_call.get_id_expr(), n=const), frame)
        if func_call.get_type() is ty.Type.Void:
            return None
        temp = frame.alloc_temp(func_call.get_type())
        self.emit(il.LoadRet(temp), frame)
        return temp

    def get_args(self):
        return self._args

    def get_id_expr(self):
        return self._id_expr

    def gen(self, frame):
        args = []
        for arg in self._args:
            t = arg.reduce(frame)
            args.append(t)
        return Funcall(self.get_id_expr().reduce(frame), args)

class Operation(Expression):
    """ Operation class

    The base class of operations.

    """
    def __init__(self, token, op_type):
        super(Operation, self).__init__(token, op_type)

    def get_op(self):
        return str(self._op)

    def reduce(self, frame):
        op   = self.gen(frame)
        temp = frame.alloc_temp(op.get_type())
        self.emit(il.Assign(temp, op), frame)
        return temp

class Binary(Operation):
    """ Binary class

    Represent binary operations.

    """
    def __init__(self, token, expr1, expr2):
        super(Binary, self).__init__(token, None)
        self._expr1  = expr1
        self._expr2  = expr2
        self._type   = ty.Type.max(expr1.get_type(), expr2.get_type())
        if self._type is None:
            self._type_error('numeric', str(expr1.get_type()))

    def gen(self, frame):
        return Binary(self._op, self._expr1.reduce(frame), self._expr2.reduce(frame))

    def __str__(self):
        return str(self._expr1) + " " + str(self._op) + " " + str(self._expr2)

class Unary(Operation):
    """ Unary class

    Represent unary operations.

    """
    def __init__(self, token, expr):
        super(Unary, self).__init__(token, None)
        self._expr = expr
        if token.tag == '&':
            self.type = ty.Type.UnsignedInt
        elif token.tag == '-':
            self.type = ty.Type.Int
        else:
            self.type = self._expr.get_type().get_ref_type()

    def gen(self, frame):
        return Unary(self._op, self._expr.reduce(frame))

    def __str__(self):
        return str(self._op) + str(self._expr)

class Cast(Operation):
    """ Cast class

    """
    def __init__(self, expr, ty):
        super(Operation, self).__init__(lexer.Word("cast to", lexer.Tag.CAST), ty)
        self._expr = expr

class Access(Operation):
    """ Access class

    Represent the array, pointer and struct access.

    """
    def __init__(self, token, id_type, access_id, offset):
        super(Access, self).__init__(token, id_type)
        self._access_id = access_id
        self._offset = offset

    def get_offset(self):
        """ Get offset

        Gets the offset of identifier.

        """
        return self._offset

    def get_access_id(self):
        return self._access_id

    def gen(self, frame):
        return Access(self._op, self.get_type(), self.get_access_id().reduce(frame), self.get_offset().reduce(frame))

    def __str__(self):
        return str(self._access_id) + " offset " + str(self._offset)

class Logical(Expression):
    """ Logical class

    The base class of logical operations.

    """
    def __init__(self, token, expr1, expr2):
        super(Logical, self).__init__(token ,None)
        self._expr1 = expr1
        self._expr2 = expr2
        self._type = self.check(expr1.get_type(), expr2.get_type())

    def check(self, ty1, ty2):
        if ty.Type.numeric(ty1) and ty.Type.numeric(ty2):
            return ty.Type.Int
        self._type_error('numeric', str(ty1))

    def gen(self, frame):
        f = frame.new_label()
        t = frame.new_label()
        temp = frame.alloc_temp(ty.Type.Int)
        self.jumping(0, f, frame)
        const = Constant(lexer.Num(1), ty.Type.Int)
        self.emit(il.Assign(temp, const), frame)
        self.emit(il.Goto(t), frame)
        self.emit_label(f, frame)
        const = Constant(lexer.Num(0), ty.Type.Int)
        self.emit(il.Assign(temp, const), frame)
        self.emit_label(t, frame)
        return temp

    def __str__(self):
        return str(self._expr1) + " " + str(self._op) + " " + str(self._expr2)


class And(Logical):
    """And class

    Represent the '&&' operation

    """
    def __init__(self, token, expr1, expr2):
        super(And, self).__init__(token, expr1, expr2)

    def jumping(self, t, f, frame):
        label = f
        if label == 0:
            label = frame.new_label()
        self._expr1.jumping(0, label, frame)
        self._expr2.jumping(t, f, frame)
        if f == 0:
            self.emit_label(label, frame)

class Or(Logical):
    """ Or class

    Represent the '||' operation

    """

    def __init__(self, token, expr1, expr2):
        super(Or, self).__init__(token, expr1, expr2)

    def jumping(self, t, f, frame):
        label = t
        if label == 0:
            label = frame.new_label()
        self._expr1.jumping(label, 0, frame)
        self._expr2.jumping(t, f, frame)
        if t != 0:
            self.emit_label(label, frame)

class Rel(Logical):
    """ Rel class

    The base class of relative operations.

    """

    def __init__(self, token ,expr1, expr2):
        super(Rel, self).__init__(token, expr1, expr2)

    def jumping(self, t, f, frame):
        t1 = self._expr1.reduce(frame)
        t2 = self._expr2.reduce(frame)
        self.emitjumps(Rel(self._op, t1, t2), t, f, frame)

class Statement(Node):
    """ Statement class

    The base class of statements.

    """
    def __init__(self, expr=None):
        super(Statement, self).__init__()
        self._after = None
        self._expr  = expr

    #
    def gen(self, t, f, frame):
        pass

class Eval(Statement):
    """ Eval class

    Represent the expression statement.

    """
    def __init__(self, expr):
        super(Statement, self).__init__(expr)

    def gen(self, t, f, frame):
        self._expr.reduce(frame)

class If(Statement):
    """ If class

    Represent the if statement.

    """
    def __init__(self, expr, stmt):
        super(If, self).__init__()
        self._expr = expr
        self._stmt = stmt
        self.check()

    def gen(self, t, f, frame):
        label = frame.new_label()
        self._expr.jumping(0, f, frame)
        self.emit_label(label, frame)
        self._stmt.gen(label, f, frame)

    def check(self):
        if not ty.Type.numeric(self._expr.get_type()):
            self._type_error('numeric', str(self._expr.get_type()))

class Else(Statement):
    """ Else class

    Represent the if-else statement.

    """

    def __init__(self, expr, stmt1, stmt2):
        super(Else, self).__init__()
        self._expr   = expr
        self._stmt1  = stmt1
        self._stmt2  = stmt2
        self.check()

    def gen(self, t, f, frame):
        label1 = frame.new_label()
        label2 = frame.new_label()
        self._expr.jumping(0, label2, frame)
        self.emit_label(label1, frame)
        self._stmt1.gen(label1, f, frame)
        self.emit(il.Goto(f), frame)
        self.emit_label(label2, frame)
        self._stmt2.gen(label2, f, frame)

    def check(self):
        if not ty.Type.numeric(self._expr.get_type()):
            self._type_error('numeric', str(self._expr.get_type()))

class While(Statement):
    """ While class

    Represent the while statement.

    """
    def __init__(self):
        super(While, self).__init__()
        self._expr = None
        self._stmt = None
    def init(self, expr, stmt):
        self._expr = expr
        self._stmt = stmt
        self.check()


    def gen(self, t, f, frame):
        self._after = f
        self._expr.jumping(0, f, frame)
        label = frame.new_label()
        self.emit_label(label, frame)
        self._stmt.gen(label, f, frame)
        self.emit(il.Goto(t), frame)

    def check(self):
        if not ty.Type.numeric(self._expr.get_type()):
            self._type_error('numeric', str(self._expr.get_type()))

class Do(Statement):
    """ While class

    Represent the do-whild statement.

    """
    def __init__(self):
        super(Do, self).__init__()
        self._expr = None
        self._stmt = None
    def init(self, expr, stmt):
        self._expr = expr
        self._stmt = stmt
        self.check()

    def gen(self, t, f, frame):
        self._after = f
        label = frame.new_label()
        self._stmt.gen(t, label)
        self.emit_label(label, frame)
        self._expr.jumping(t, 0, frame)

    def check(self):
        if ty.Type.numeric(self._expr.get_type()):
            self._type_error('numeric', str(self._expr.get_type()))

class Set(Statement):
    """Set class

    Represent the assign statment.

    """
    def __init__(self, unary, expr):
        super(Set, self).__init__()
        self._unary  = unary
        self._expr   = expr
        self.check()

    def check(self):
        if not (ty.Type.numeric(self._unary.get_type()) and ty.Type.numeric(self._expr.get_type())):
            self._type_error('numeric', str(self._unary.get_type()))

    def gen(self, t, f, frame):
        l = self._unary.gen(frame)
        r = self._expr.reduce(frame)
        self.emit(il.Assign(l, r), frame)

class Break(Statement):
    def __init__(self):
        super(Break, self).__init__()
        self._stmt = Statement.Enclosing

    def gen(self, t, f, ar):
        self.emit(il.Goto(self._stmt.after), ar)

class Continue(Statement):
    def __init__(self):
        super(Continue, self).__init__()
        self._stmt = Statement.Enclosing

    def gen(self, t, f, ar):
        self.emit(il.Goto(self._stmt._after), ar)

class Return(Statement):
    def __init__(self, ret=None):
        super(Return, self).__init__()
        self._ret = ret

    def gen(self, t, f, frame):
        if self._ret is not None:
            ret = self._ret.reduce(frame)
            self.emit(il.StoreRet(ret), frame)
        self.emit(il.Goto(frame.get_frame_end()), frame)

class Sequence(Statement):
    """ Sequence class

    Chains the statement list into a tree form.

    """
    def __init__(self, stmt1, stmt2):
        super(Sequence, self).__init__()
        self._stmt1 = stmt1
        self._stmt2 = stmt2

    def gen(self, t, f, frame):
        if self._stmt1 is Statement.Null:
            self._stmt2.gen(t, f, frame)
        elif self._stmt2 is Statement.Null:
            self._stmt1.gen(t, f, frame)
        else:
            label = frame.new_label()
            self._stmt1.gen(t, label, frame)
            self.emit_label(label, frame)
            self._stmt2.gen(label, f, frame)

Statement.Null      = Statement()
Statement.Enclosing = Statement.Null