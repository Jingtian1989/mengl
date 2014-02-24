__author__ = 'ZhangJingtian'
import ty
import il
import ast
import sym
import cpu
import lexer
import errors

class Parser(object):
    """Parser class

    """
    def __init__(self, lexer):
        super(Parser, self).__init__()
        self._look           = None
        self._lookahead      = []
        self._lexer          = lexer
        self._ids            = sym.IdentifierTable()
        self._frames         = {}
        self._advance_token()

    def _advance_token(self):
        """Adnvance Tokens

        Populates the current token.

        """
        if len(self._lookahead) > 0:
            self._look = self._lookahead[0]
            del self._lookahead[0]
        else:
            self._look = self._lexer.scan()

    def _accept(self, expected_tag):
        """Accept Token

        Compares the token to an expected tag. If it matches, then
        consume the token.

        Arguments:
            expected_tag: The expected type of the token.
        """
        if self._check(expected_tag):
            self._advance_token()
            return True
        return False

    def _check(self, expected_tag):
        """Check Token

        Peeks at the token to see if the current token matches the given tag.

        Arguments:
            expected_tag: The expected
        """
        return self._look.tag == expected_tag

    def _warning(self, msg, line, prefix='Warning'):
        """Pring Parser Warning Message

        Print a parser warning message with details about the expected token
        and the current token being parsed.

        Arguments:
            msg: The warning message to display.
            line: The line where the warning has occurred.
            prefix: A string value to be print at the start of the warning.
                Overwritten for error messages. (Default: 'Warning')
        """
        print('%s: "%s", line %d' % (prefix, msg, line) )
        return

    def _name_error(self, msg, name):
        """Print Name Error Message

        Prints a name error message with details about the encountered
        identifier which caused the error.

        Arguments:
            msg: The reason for the error.
            name: The name of the identifier where the name error occurred.
        """
        msg = '%s: %s' % (name, msg)
        self._warning(msg, self._lexer.line, prefix='Error')
        return

    def _syntax_error(self, expected):
        """Print Syntax Error Message

        Prints a syntax error message with details about the expected token
        and the current token being parsed. After error printing, an exception
        is raised to be caught and resolved by parent nodes.

        Arguments:
            expected : A string containing the expected token.
        """
        token = self._look

        msg = ('Expected %s, encounted "%s"' %
               (expected, token))
        self._warning(msg, self._lexer.line, prefix='Error')
        raise errors.ParserSyntaxError()

    def _match(self, expected_tag, expected_value=None):
        """ Match Token

        Compares the token to an expected tag.

        Arguments:
            expected_tag: The expected tag of the token.
            expected_value: The expected value of the token.
        """
        if self._look.tag == expected_tag:
            self._advance_token()
        else:
            if expected_value is not None:
                self._syntax_error(expected_value)
            else:
                self._syntax_error(expected_tag)
        return

    def _lookk(self, k):
        """ Look Ahead

        Look ahead k tokens.

        Arguments:
            k: The look ahead count.

        """
        last = k - len(self._lookahead)
        if last > 0:
            for i in range(last):
                self._lookahead.append(self._lexer.scan())
        return self._lookahead[k-1]

    def _parse_program(self):
        """ <program>

        Parses the <program> language structure.

            program ->  struct_declaration_list function_declaration_list struct_definition_list global_variable_declaration
                        function_definition_list
        """
        self._parse_struct_declaration_list()
        self._parse_function_declaration_list()
        self._parse_struct_definition_list()
        self._parse_global_variable_declaration()
        self._parse_function_definition_list()
        return

    def _parse_struct_declaration_list(self):
        """ <struct_declaration_list>

        Parses the <struct_declaration_list> language structure.

            struct_declaration_list -> struct_declaration_list struct_declaration
                                    |   ε
        """
        while self._check(lexer.Tag.STRUCT):
            id_obj = self._parse_struct_declaration()
            try:
                self._ids.add(id_obj)
            except errors.ParserNameError as e:
                self._name_error(str(e), str(id_obj))
        return

    def _parse_struct_declaration(self):
        """ <struct_declaration>

        Parses the <struct_declaration> language structure.

            struct_declaration -> 'struct' 'identifier' ';'
        """
        self._match(lexer.Tag.STRUCT)
        token = self._look
        self._match(lexer.Tag.ID)
        self._match(';')
        id_type = ty.Struct(token)
        id_obj = ast.Identifier(token, id_type)
        id_type.get_identifier_table().init(prev=None, owner_id=id_obj)
        return id_obj

    def _parse_struct_definition_list(self):
        """ <struct_definition_list>

        Parses the <struct_definition> language structure.

            struct_definition_list -> struct_definition_list struct_definition
                                    |   ε
        """
        while self._accept(lexer.Tag.STRUCT):
            token = self._look
            self._match(lexer.Tag.ID)
            id_obj = None
            try:
                id_obj = self._ids.find(str(token))
            except errors.ParserNameError as e:
                self._name_error('struct has not been declared', str(token))
            self._parse_struct_definition(id_obj)
        return


    def _parse_struct_definition(self, id_obj):
        """ <struct_definition>

        Parses the <struct_definition> language structure.

            struct_definition -> 'struct' 'identifier' '{' variable_declaration_list '}' ';'

        """
        self._match('{')
        struct_type = id_obj.get_type()
        va_list = self._parse_variable_declaration_list(struct_type.get_identifier_table())
        for struct_field in va_list:
            struct_type.init_struct_field(struct_field)
        self._match('}')
        self._match(';')
        return

    def _parse_variable_declaration_list(self, env):
        """ <variable_declaration_list>

        Parses the <variable_declaration_list> language structure.

            variable_declaration_list -> variable_declaration_list variable_declaration
                                        |   ε
        """
        la = self._lookk(1)
        va_list = []
        while la != None and la.tag == ':':
            id_obj = self._parse_variable_declaration()
            la = self._lookk(1)
            try:
                env.add(id_obj)
            except errors.ParserNameError as e:
                self._name_error(str(e), str(id_obj))
            va_list.append(id_obj)
        return va_list

    def _parse_variable_declaration(self):
        """ <variable_declaration>

        Parses the <variable_declaration> language structure.

            variable_declaration -> 'identifier' ':' type_specifier ';'

        """
        token = self._look
        self._match(lexer.Tag.ID)
        self._match(':')
        oftype = self._parse_type_specifier()
        self._match(';')
        id = ast.Identifier(token, oftype)
        return id


    def _parse_type_specifiers(self, types):
        """ <type_specifiers>

        Parses the <type_specifiers> language structure.

            type_specifiers -> type_specifiers ',' type_specifier
                            |   type_specifier

        """
        t = self._parse_type_specifier()
        types.append(t)
        if self._check(','):
            types = self._parse_type_specifiers(types)
        return types


    def _parse_type_specifier(self):
        """ <type_specifier>

        Parses the <type_specifier> language structure.

            type_specifier -> basic_specifer
                            |   struct_specifier
                            |   function_specifier
                            |   array_specifier
                            |   pointer_specifier

        """
        if ty.Type.isbasic(self._look):
            return self._parse_basic_specifier()
        elif ty.Type.isstruct(self._look):
            return self._parse_struct_specifier()
        elif ty.Type.isfunction(self._look):
            return self._parse_function_specifier()
        elif ty.Type.isarray(self._look):
            return self._parse_array_specifier()
        elif ty.Type.ispointer(self._look):
            return self._parse_pointer_specifier()


    def _parse_basic_specifier(self):
        """ <basic_specifier>

        Parses the <basic_specifier> language structure.

            basic_specifier -> 'int'
                            |   'unsigned'
                            |   'void'

        """
        if self._accept(lexer.Tag.INT):
            return ty.Type.Int
        elif self._accept(lexer.Tag.VOID):
            return ty.Type.Void
        elif self._accept(lexer.Tag.UNSIGNED):
            self._match(lexer.Tag.INT, 'int')
            return ty.Type.UnsignedInt

    def _parse_struct_specifier(self):
        """ <struct_specifier>

        Parses the <struct_specifier> language structure.

            struct_specifier -> 'struct' 'identifier'

        """

        self._match(lexer.Tag.STRUCT, 'struct')
        token = self._look
        self._match(lexer.Tag.ID, 'identifier')
        id_obj = None
        try:
            id_obj = self._ids.find(str(token))
        except errors.ParserNameError:
            self._name_error('struct has not been declared', str(token))
        return id_obj.get_type()


    def _parse_function_specifier(self):
        """ <function_specifier>

        Parses the <function_specifier> language structure.

            function_specifier -> 'function' '(' type_specifiers ')' basic_specifier

        """

        types = []
        self._match(lexer.Tag.FUNCTION, 'function')
        self._match('(')
        self._parse_type_specifiers(types)
        self._match(')')
        ret_type = self._parse_basic_specifier()
        func_type = ty.Function()
        func_type.init(types, ret_type)
        return func_type

    def _parse_array_specifier(self):
        """ <array_specifier>

        Parses the <array_specifier> language structure.

            array_specifier -> 'array'  '[' num ']' 'of' type_specifier

        """
        self._match(lexer.Tag.ARRAY, 'array')
        self._match('[')
        num = self._look
        self._match(lexer.Tag.NUM, 'constant')
        self._match(']')
        self._match(lexer.Tag.OF, 'of')
        of_type = self._parse_type_specifier()
        array_type = ty.Array(num.value, of_type)
        return array_type

    def _parse_pointer_specifier(self):
        """ <pointer_specifier>

        Parses the <pointer_specifier> language structure.

            pointer_specifier -> 'pointer' 'to' type_specifier

        """
        self._match(lexer.Tag.POINTER, 'pointer')
        self._match(lexer.Tag.TO, 'to')
        ref_type = self._parse_type_specifier()
        pointer_type = ty.Pointer(ref_type)
        return pointer_type

    def _parse_function_declaration_list(self):
        """ <function_declaration_list>

        Parses the <function_declaration_list> language structure.

            function_declaration_list -> function_declaration_list function_declaration
                                        |   ε
        """
        la = self._lookk(2)
        while self._check(lexer.Tag.FUNCTION) and la.tag == '(':
            id_obj = self._parse_function_declaration()
            la = self._lookk(2)
            try:
                self._ids.add(id_obj)
            except errors.ParserNameError as e:
                self._name_error(str(e), str(id_obj))

            id_obj.get_type().get_identifier_table().init(self._ids, id_obj)
            frame = il.Frame(id_obj)
            self._frames[str(id_obj)] = frame
        return

    def _parse_function_declaration(self):
        """ <function_declaration>

        Parses the <function_declaration> language structure.

            function_declaration -> 'function' 'identifer' '(' parameter_list ')' basic_specifier ';'

        """
        self._match(lexer.Tag.FUNCTION, 'function')
        token = self._look
        self._match(lexer.Tag.ID, 'identifier')
        self._match('(')
        func_type  = ty.Function()
        func_proto = self._parse_parameter_list(func_type.get_identifier_table(), [])
        self._match(')')
        ret_type = self._parse_basic_specifier()
        func_type.init(func_proto, ret_type)
        func_id = ast.Identifier(token, func_type)
        self._match(';')
        return func_id

    def _parse_parameter_list(self, env, params):
        """ <parameter_list>

        Parses the <parameter_list> language structure.

            parameter_list -> parameters
                            |   'void'

            parameters -> parameters ',' parameter
                        | parameter

            parameter -> 'identifer' ':' type_specifier

        """
        if self._accept(lexer.Tag.VOID):
            return params
        else:
            params = self._parse_parameters(env, params)

        return params

    def _parse_parameters(self, env, params):
        """ <parameters>

        Parses the <parameters> language structure.

            parameters -> parameters ',' parameter
                        | parameter

        """
        id_obj = self._parse_parameter()
        try:
            env.add(id_obj)
        except errors.ParserNameError as e:
            self._name_error(str(e), str(id_obj))
        params.append(id_obj)
        if self._accept(','):
            params = self._parse_parameters(params, env)
        return params


    def _parse_parameter(self):
        """ <parameter>

        Parses the <parameter> language structure.

            parameter -> 'identifer' ':' type_specifier

        """
        token = self._look
        self._match(lexer.Tag.ID, 'identifier')
        self._match(':')
        param_type = self._parse_type_specifier()
        param_id   = ast.Identifier(token, param_type)
        return param_id

    def _parse_global_variable_declaration(self):
        """ <global_variable_declaration>

        Parses the <global_variable_declaration> language structure.

            global_variable_declaration -> variable_declaration_list variable_declaration
                                        |   ε
        """
        va_list = self._parse_variable_declaration_list(self._ids)
        for id_obj in va_list:
            self.gen_global_variable(id_obj)

    def _parse_function_definition_list(self):
        """ <function_definition_list>

        Parses the <function_definition_list> language structure.

            function_definition_list -> function_defintion_list function_definition
                                    |   ε
        """
        while self._look != None and self._accept(lexer.Tag.FUNCTION):
            token = self._look
            self._match(lexer.Tag.ID, 'identifier')
            id_obj = None
            try:
                id_obj = self._ids.find(str(token))
            except errors.ParserNameError as e:
                self._name_error('function has not been declared', str(token))
            self._parse_function_definition(id_obj)

    def _parse_function_definition(self, func_obj):
        """ <function_definition>

        Parses the <function_definition> language structure.

            function_definition -> 'function' 'identifier' compound_statement ';'

        """
        func_stmt = self._parse_compount_statement(func_obj.get_type().get_identifier_table())
        self._match(';')
        func_obj.get_type().set_statement(func_stmt)

    def _parse_statement_list(self, env):
        """ <statement_list>

        Parses the <statement_list> language structure.

            statment_list -> statement_list statment
                        |   ε
        """
        stmt = self._parse_statement(env)
        if self._check('}'):
            return ast.Sequence(stmt, ast.Statement.Null)
        else:
            return ast.Sequence(stmt, self._parse_statement_list(env))

    def _parse_statement(self, env):
        """ <statement>

        Parses the <statement> language structure.

            statement -> selection_statement
                    |   iteration_statement
                    |   jump_statement
                    |   assign_statement
                    |   expression_statement
                    |   compound_statement

        """

        if self._check(lexer.Tag.IF):
            return self._parse_selection_statement(env)
        elif self._check(lexer.Tag.WHILE) or self._check(lexer.Tag.DO):
            return self._parse_iteration_statement(env)
        elif self._check(lexer.Tag.BREAK) or self._check(lexer.Tag.CONTINUE) \
            or self._check(lexer.Tag.RETURN):
            return self._parse_jump_statement(env)
        elif self._check('{'):
            return self._parse_compount_statement(env)
        elif self._check('@'):
            return self._parse_assign_statement(env)
        else:
            return self._parse_expression_statement(env)

    def _parse_selection_statement(self, env):
        """ <selection_statement>

        Parses the <selection_statement> language structure.

            selection_statement -> 'if' '(' logical_expression ')' statement
                                |   'if' '(' logical_expression ')' 'else' statement

        """
        self._match(lexer.Tag.IF, 'if')
        self._match('(')
        exp = self._parse_logical_expression(env)
        self._match(')')
        stmt1 = self._parse_statement(env)
        if not self._check(lexer.Tag.ELSE):
            return ast.If(exp, stmt1)
        self._match(lexer.Tag.ELSE, 'else')
        stmt2 = self._parse_statement(env)
        return ast.Else(exp, stmt1, stmt2)

    def _parse_iteration_statement(self, env):
        """ <iteration_statement>

        Parses the <iteration_statement> language structure.

            iteration_statement -> 'while' '(' logical_expressoin ')' statement
                                |   'do' statement 'while' '(' logical_expression ')'

        """
        if self._look.tag == lexer.Tag.WHILE:
            while_node = ast.While()
            save_stmt  = ast.Statement.Enclosing
            ast.Statement.Enclosing = while_node
            self._match(lexer.Tag.WHILE, 'whild')
            self._match('(')
            expr = self._parse_logical_expression(env)
            self._match(')')
            stmt = self._parse_statement(env)
            while_node.init(expr, stmt)
            ast.Statement.Enclosing = save_stmt
            return while_node
        else:
            do_node = ast.Do()
            save_stmt = ast.Statement.Enclosing
            ast.Statement.Enclosing = do_node
            self._match(lexer.Tag.DO, 'do')
            stmt = self._parse_statement(env)
            self._match(lexer.Tag.WHILE ,'while')
            self._match('(')
            expr = self._parse_logical_expression(env)
            self._match(')')
            self._match(';')
            do_node.init(expr, stmt)
            ast.Statement.Enclosing = save_stmt
            return do_node

    def _parse_jump_statement(self, env):
        """ <jump_statement>

        Parses the <jump_statement> language structure.

            jump_statement -> 'continue' ';'
                            |   'break' ';'
                            |   'return' ';'
                            |   'return' logical_expression ';'
        """

        if self._accept(lexer.Tag.CONTINUE):
            return ast.Continue()
        elif self._accept(lexer.Tag.BREAK):
            return ast.Break()
        elif self._accept(lexer.Tag.RETURN):
            exp = None
            if not self._check(';'):
                exp = self._parse_logical_expression(env)
            self._match(';')
            return ast.Return(exp)

    def _parse_compount_statement(self, env):
        """ <compound_statement>

        Parses the <compound_statement> language strucutre.

            compound_statement -> '{' variable_declaration_list statement_list '}'

        """
        self._match('{')
        env = env.push_scope()
        id_obj = env.get_owner_id()
        frame = self._frames.get(str(id_obj))
        va_list = self._parse_variable_declaration_list(env)
        for local_obj in va_list:
            frame.alloc_local(local_obj, is_local=True)
        stmt = self._parse_statement_list(env)
        env.pop_scope()
        self._match('}')
        return stmt

    def _parse_assign_statement(self, env):
        """ <assign_statement>

        Parses the <assign_statement> language structure.

            assign_statement -> '@' unary_expression '=' logical_expression ';'

        """

        self._match('@')
        unary = self._parse_unary_expression(env)
        self._match('=')
        logical = self._parse_logical_expression(env)
        self._match(';')
        return ast.Set(unary, logical)

    def _parse_expression_statement(self, env):
        """ <expression_statement>

        Parses the <expression_statement> language structure.

            expression_statement -> logical_expression ';'
                                |   ';'
        """

        stmt = None
        if self._look.tag == ';':
            stmt = ast.Statement.Null
        else:
            exp  = self._parse_logical_expression(env)
            stmt = ast.Statement(exp)
        self._match(';')
        return stmt

    def _parse_logical_expression(self, env):
        """ <logical_expression>

        Parses the <logical_expression> language structure.

            logical_expression -> logical_expression '||' logical_and_expression
                                |   logical_and_expression
        """

        logand = self._parse_logical_and_expression(env)
        while self._look.tag == lexer.Tag.OR:
            tok = self._look
            self._match(lexer.Tag.OR)
            logand = ast.Or(tok, logand, self._parse_logical_expression(env))
        return logand

    def _parse_logical_and_expression(self, env):
        """ <logical_and_expression>

        Parses the <logical_and_expression> language structure.

            logical_and_expression -> logical_and_expression '&&' inclusive_or_expression
                                    |   inclusive_or_expression

        """
        inclor = self._parse_inclusive_or_expression(env)
        while self._look.tag == lexer.Tag.AND:
            tok = self._look
            self._match(lexer.Tag.AND)
            inclor = ast.And(tok, inclor, self._parse_logical_and_expression(env))
        return inclor

    def _parse_inclusive_or_expression(self, env):
        """ <inclusive_or_expression>

        Parses the <inclusive_or_expression> language structure.

            inclusive_or_expression -> inclusive_or_expression '|' exclusive_or_expression
                                    |   exclusive_or_expression

        """
        exclor = self._parse_exclusive_or_expression(env)
        while self._look.tag == '|':
            tok = self._look
            self._match('|')
            exclor = ast.Binary(tok , exclor,self._parse_inclusive_or_expression(env))
        return exclor

    def _parse_exclusive_or_expression(self, env):
        """ <exclusive_or_expression>

        Parses the <exclusive_or_expression> language structure.

            exclusive_or_expression -> exclusive_or_expression '^' and_expression
                                    |   and_expression

        """
        andexp = self._parse_and_expression(env)
        while self._look.tag == '^':
            tok = self._look
            self._match('^')
            andexp = ast.Binary(tok , andexp, self._parse_exclusive_or_expression(env))
        return andexp

    def _parse_and_expression(self, env):
        """ <and_expression>

        Parses the <and_expression> language structure.

            and_expression -> and_expression '&' equality_expression
                                    |   equality_expression

        """
        eqexp = self._parse_equality_expression(env)
        while self._look.tag == '&':
            tok = self._look.tag
            self._match('&')
            eqexp = ast.Binary(tok, eqexp, self._parse_and_expression(env))
        return eqexp

    def _parse_equality_expression(self, env):
        """ <equality_expression>

        Parses the <equality_expression> language structure.

            equality_expression -> equality_expression '==' relational_expression
                                    |   equality_expression '!=' relational_expression
                                    |   relational_expression

        """
        relexp = self._parse_relational_expression(env)
        while self._look.tag == lexer.Tag.EQ or self._look.tag == lexer.Tag.NE:
            tok = self._look
            if self._look.tag == lexer.Tag.EQ:
                self._match(lexer.Tag.EQ)
            else:
                self._match(lexer.Tag.NE)
            relexp = ast.Rel(tok, relexp, self._parse_equality_expression(env))
        return relexp

    def _parse_relational_expression(self, env):
        """ <relational_expression>

        Parses the <relational_expression> language structure.

            relational_expression -> relational_expression '<' shift_expression
                                    |   relational_expression '>' shift_expression
                                    |   relational_expression '>=' shift_expression
                                    |   relational_expression '<=' shift_expression
                                    |   shift_expression

        """
        shexp = self._parse_shift_expression(env)
        while self._look.tag == lexer.Tag.LE or self._look.tag == lexer.Tag.GE \
            or self._look.tag == '>' or self._look.tag == '<':
            tok = self._look
            if self._look.tag == lexer.Tag.LE:
                self._match(lexer.Tag.LE)
            elif self._look.tag == lexer.Tag.GE:
                self._match(lexer.Tag.GE)
            elif self._look.tag == '>':
                self._match('>')
            else:
                self._match('<')
            shexp = ast.Rel(tok , shexp, self._parse_relational_expression(env))
        return shexp

    def _parse_shift_expression(self, env):
        """ <shift_expression>

        Parses the <shift_expression> language structure.

            shift_expression -> shift_expression '<<' additive_expression
                            |   shift_expression '>>' additive_expression
                            |   additive_expression

        """
        addexp = self._parse_additive_expression(env)
        while self._look.tag == lexer.Tag.LS or self._look.tag == lexer.Tag.RS:
            tok = self._look
            if self._look.tag == lexer.Tag.LS:
                self._match(lexer.Tag.LS)
            else:
                self._match(lexer.Tag.RS)
            addexp = ast.Binary(tok , addexp, self._parse_shift_expression(env))
        return addexp

    def _parse_additive_expression(self, env):
        """ <additive_expression>

        Parses the <additive_expression> language structure.

            additive_expression -> additive_expression '+' multiplicative_expression
                            |   additive_expression '-' multiplicative_expression
                            |   multiplicative_expression

        """
        mulexp = self._parse_multiplicative_expression(env)
        while self._look.tag == '+' or self._look.tag == '-':
            tok = self._look
            if self._look.tag == '+':
                self._match('+')
            else:
                self._match('-')
            mulexp = ast.Binary(tok , mulexp, self._parse_additive_expression(env))
        return mulexp

    def _parse_multiplicative_expression(self, env):
        """ <multiplicative_expression>

        Parses the <multiplicative_expression> language structure.

            multiplicative_expression -> multiplicative_expression '*' cast_expression
                                    |   multiplicative_expression '/' cast_expression
                                    |   cast_expression

        """
        castexp = self._parse_cast_expression(env)
        while self._look.tag == '*' or self._look.tag == '/':
            tok = self._look
            if self._look.tag == '*':
                self._match('*')
            else:
                self._match('/')
            castexp = ast.Binary(tok , castexp, self._parse_multiplicative_expression(env))
        return castexp

    def _parse_cast_expression(self, env):
        """ <cast_expression>

        Parses the <cast_expression> language structure.

            cast_expression -> cast_expression 'cast' 'to' type_specifier
                            |   unary_expression

        """
        unary = self._parse_unary_expression(env)
        while self._look.tag == lexer.Tag.CAST:
            self._match(lexer.Tag.CAST)
            self._match(lexer.Tag.TO)
            t = self._parse_type_specifier()
            unary = ast.Cast(unary, t)
        return unary

    def _parse_unary_expression(self, env):
        """ <unary_expression>

        Parses the <unary_expression> language structure.

            unary_expression -> unary_operator unary_expression
                            |   postfix_expression

            unary_operator -> '*'
                        |   '&'
        """
        token = self._look
        if self._accept('*') or self._accept('&') or self._accept('-'):
            return ast.Unary(token, self._parse_unary_expression(env))
        else:
            return self._parse_postfix_expression(env)

    def _parse_postfix_expression(self, env):
        """ <postfix_expression>

        Parses the <postfix_expression> language structure.

            postfix_expression -> postfix_expression '.' 'identifer'
                            |   postfix_expression '->' identifer
                            |   postfix_expression '[' logical_expression ']'
                            |   postfix_expression '(' argument_list ')'
                            |   primary_expression

        """
        exp = self._parse_primary_expression(env)
        while self._look.tag == '.' or self._look.tag == lexer.Tag.PTR \
            or self._look.tag == '[' or self._look.tag == '(':
            if self._look.tag == '.':
                exp = self._parse_struct_offset(exp)
            elif self._look.tag == lexer.Tag.PTR:
                exp = self._parse_ptr_offset(exp)
            elif self._look.tag == '[':
                exp = self._parse_array_offset(exp, env)
            elif self._look.tag == '(':
                exp = self._parse_funcall_expression(exp, env)
        return exp

    def _parse_primary_expression(self, env):
        """ <primary_expression>

        Parses the <primary_expression> language structure.

            primary_expression -> 'constant'
                                |   '(' logical_expression ')'
                                |   'identifier'

        """
        token = self._look
        if self._accept(lexer.Tag.NUM):
            return ast.Constant(token, ty.Type.Int)
        elif self._accept(lexer.Tag.NULL):
            return ast.Constant(lexer.Num(0), ty.Type.Int)
        elif self._accept('('):
            logexp = self._parse_logical_expression(env)
            self._match(')')
            return logexp
        self._match(lexer.Tag.ID, 'identifier')
        id_obj = None
        try:
            id_obj = env.find(str(token))
        except errors.ParserNameError as e:
            self._name_error('identifier has not been declared', str(token))
        return id_obj

    def _parse_struct_offset(self, expr):
        """

        Parses the struct offset.

        """
        self._match('.')
        token = self._look
        self._match(lexer.Tag.ID)
        struct_type = expr.type()
        struct_field = None
        try:
            struct_field = struct_type.get_identifier_table().find(str(token))
        except errors.ParserNameError as e:
            self._name_error('struct has no such field', str(str(token)))
        offset = ast.Constant(lexer.Num(struct_field.get_offset()), ty.Type.Int)
        return ast.Access(lexer.Word('.', lexer.Tag.INDEX), struct_field.get_type(), expr, offset)

    def _parse_ptr_offset(self, expr):
        """
        Parses the pointer offset.

        """
        self._match(lexer.Tag.PTR)
        token = self._look
        self._match(lexer.Tag.ID)
        struct_type = expr.get_type().get_ref_type()
        struct_field = None
        try:
            struct_field = struct_type.get_identifier_table().find(str(token))
        except errors.ParserNameError:
            self._name_error('struct has no such field', str(token))
        offset = ast.Constant(lexer.Num(struct_field.get_offset()), ty.Type.Int)
        return ast.Access(lexer.Word('->', lexer.Tag.INDEX), struct_field.get_type(), expr, offset)

    def _parse_array_offset(self, expr, env):
        """
        Parses the array offset.

        """
        self._match('[')
        num = self._parse_logical_expression(env)
        self._match(']')
        of_type = expr.get_type().get_of_type()
        width = ast.Constant(lexer.Num(of_type.get_width()), ty.Type.Int)
        expr_id = expr
        offset = ast.Binary(lexer.Token('*'), num, width)
        if type(expr) is ast.Access:
            expr_id = expr.get_access_id()
            offset = ast.Binary(lexer.Token('+'), expr.get_offset(), offset)
        return ast.Access(lexer.Word('[]', lexer.Tag.INDEX), of_type, expr_id, offset)

    def _parse_funcall_expression(self, expr, env):
        """ <funcall_expression>

        Parses the <funcall_expression> language structure.

            funcall_expression -> postfix_expression '(' argument_list ')'

        """
        self._match('(')
        func_args = []
        func_args = self._parse_argument_list(env, func_args)
        func_call = ast.Funcall(expr, func_args)
        self._match(')')
        return func_call

    def _parse_argument_list(self, env, args):
        """ <argument_list>

        Parses the <argument_list> language strucutre.

            argument_list -> arguments
                            |   ε

        """
        if self._check(')'):
            return args

        return self._parse_arguments(env, args)

    def _parse_arguments(self, env, args):
        """ <arguments>

        Parses the <arguments> language strucutre.

            arguments -> arguments ',' argument

        """
        expr = self._parse_argument(env)
        args.append(expr)
        if self._accept(','):
            args = self._parse_arguments(env, args)
        return args


    def _parse_argument(self, env):
        """ <argument>

        Parses the <argument> language strucutre.

            argument -> logical_expression

        """
        return self._parse_logical_expression(env)

    def _parse_il_frame(self):
        """ Parse Inter Language Frame

        Walks through the ast and generates the three address code from the input program.

        """
        for frame in self._frames.values():
                frame_type = frame.get_frame_id().get_type()
                statement = frame_type.get_statement()
                statement.gen(frame.get_frame_start(), frame.get_frame_end(), frame)
                frame.emit_end()

    def _generate_runtime(self):
        """ Generate Runtime

        Iterate the tacodes and call the code generate runtine.

        """
        pass


    def parse(self):
        self._parse_program()
        self._parse_il_frame()
        self._generate_runtime()

if __name__ == '__main__':

    text = "" \
        "struct process;" \
        "" \
        "function register_process (p : pointer to struct process) int;" \
        "function main(void) int;" \
        "" \
        "struct process {" \
        "    pid : int;" \
        "    func: pointer to function (pointer to struct process) int;" \
        "    data: pointer to void;" \
        "};" \
        "" \
        "processes : array [10] of pointer to struct process;" \
        "pid : int;" \
        "" \
        "function register_process {" \
        "    @ processes[pid] = p;" \
        "    @ p->pid = pid;" \
        "    return 0;" \
        "};" \
        "" \
        "function main {" \
        "" \
        "   return 0;" \
        "};" \

    parser = Parser(lexer.Lexer(text))
    parser.parse()
    print("ok")

