# pylint: disable=line-too-long

class Parser(object):
    def __init__(self, msg, fname, starting_rule='grammar'):
        self.msg = msg
        self.end = len(msg)
        self.fname = fname
        self.starting_rule = starting_rule
        self.val = None
        self.err = None
        self.pos = 0
        self.errpos = 0
        self.errset = set()
        self.scopes = []

    def parse(self):
        rule_fn = getattr(self, '_' + self.starting_rule + '_', None)
        if not rule_fn:
            return None, 'unknown rule "%s"' % self.starting_rule
        rule_fn()
        if self.err:
            return None, self._err_str()
        return self.val, None

    def _push(self, name):
        self.scopes.append((name, {}))

    def _pop(self, name):
        actual_name, _ = self.scopes.pop()
        assert name == actual_name

    def _get(self, var):
        return self.scopes[-1][1][var]

    def _set(self, var, val):
        self.scopes[-1][1][var] = val

    def _err_str(self):
        lineno, colno, _ = self._err_offsets()
        prefix = '%s:%d' % (self.fname, lineno)
        if isinstance(self.err, basestring):
            return '%s %s' % (prefix, self.err)
        exps = list(self.errset)
        if len(exps) > 1:
            return '%s Unexpected "%s" at column %d' % (
                prefix, self.msg[self.errpos], colno)
        return '%s Expecting a "%s" at column %d, got a "%s"' % (
                prefix, exps[0], colno, self.msg[self.errpos])

    def _err_offsets(self):
        lineno = 1
        colno = 1
        i = 0
        begpos = 0
        while i < self.errpos:
            if self.msg[i] == '\n':
                lineno += 1
                colno = 1
                begpos = i
            else:
                colno += 1
            i += 1
        return lineno, colno, begpos

    def _esc(self, val):
        return str(val)

    def _expect(self, expr):
        p = self.pos
        l = len(expr)
        if (p + l <= self.end) and self.msg[p:p + l] == expr:
            self.pos += l
            self.val = expr
            self.err = False
        else:
            self.val = None
            self.err = True
            if self.pos >= self.errpos:
                if self.pos > self.errpos:
                    self.errset = set()
                self.errset.add(self._esc(expr))
                self.errpos = self.pos
        return

    def _grammar_(self):
        self._push('grammar')
        self._sp_()
        if self.err:
            self._pop('grammar')
            return
        self._value_()
        if not self.err:
            self._set('v', self.val)
        if self.err:
            self._pop('grammar')
            return
        self._sp_()
        if self.err:
            self._pop('grammar')
            return
        self._end_()
        if self.err:
            self._pop('grammar')
            return
        self.val = self._get('v')
        self.err = None
        self._pop('grammar')

    def _sp_(self):
        vs = []
        while not self.err:
            p = self.pos
            self._ws_()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None

    def _ws_(self):
        p = self.pos
        def choice_0():
            self._expect(' ')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('\t')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._eol_()
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._comment_()
        choice_3()

    def _eol_(self):
        p = self.pos
        def choice_0():
            self._expect('\r\n')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('\r')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect('\n')
        choice_2()

    def _comment_(self):
        p = self.pos
        def choice_0():
            self._expect('//')
            if self.err:
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    p = self.pos
                    def group():
                        p = self.pos
                        def choice_0():
                            self._eol_()
                        choice_0()
                        if not self.err:
                            return

                        self.err = False
                        self.pos = p
                        def choice_1():
                            self._end_()
                        choice_1()
                    group()
                    self.pos = p
                    if not self.err:
                        self.err = "not"
                        self.val = None
                        return
                    self.err = None
                    if self.err:
                        return
                    self._anything_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if self.err:
                return
            def group():
                p = self.pos
                def choice_0():
                    self._end_()
                choice_0()
                if not self.err:
                    return

                self.err = False
                self.pos = p
                def choice_1():
                    self._eol_()
                choice_1()
            group()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('/*')
            if self.err:
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    p = self.pos
                    self._expect('*/')
                    self.pos = p
                    if not self.err:
                        self.err = "not"
                        self.val = None
                        return
                    self.err = None
                    if self.err:
                        return
                    self._anything_()
                group()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if self.err:
                return
            self._expect('*/')
        choice_1()

    def _value_(self):
        p = self.pos
        def choice_0():
            self._expect('null')
            if self.err:
                return
            self.val = 'None'
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('true')
            if self.err:
                return
            self.val = 'True'
            self.err = None
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect('false')
            if self.err:
                return
            self.val = 'False'
            self.err = None
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._push('value_3')
            self._object_()
            if not self.err:
                self._set('v', self.val)
            if self.err:
                self._pop('value_3')
                return
            self.val = ['object', self._get('v')]
            self.err = None
            self._pop('value_3')
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._push('value_4')
            self._array_()
            if not self.err:
                self._set('v', self.val)
            if self.err:
                self._pop('value_4')
                return
            self.val = ['array', self._get('v')]
            self.err = None
            self._pop('value_4')
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._push('value_5')
            self._string_()
            if not self.err:
                self._set('v', self.val)
            if self.err:
                self._pop('value_5')
                return
            self.val = ['string', self._get('v')]
            self.err = None
            self._pop('value_5')
        choice_5()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_6():
            self._push('value_6')
            self._num_literal_()
            if not self.err:
                self._set('v', self.val)
            if self.err:
                self._pop('value_6')
                return
            self.val = ['number', self._get('v')]
            self.err = None
            self._pop('value_6')
        choice_6()

    def _object_(self):
        p = self.pos
        def choice_0():
            self._push('object_0')
            self._expect('{')
            if self.err:
                self._pop('object_0')
                return
            self._sp_()
            if self.err:
                self._pop('object_0')
                return
            self._member_list_()
            if not self.err:
                self._set('v', self.val)
            if self.err:
                self._pop('object_0')
                return
            self._sp_()
            if self.err:
                self._pop('object_0')
                return
            self._expect('}')
            if self.err:
                self._pop('object_0')
                return
            self.val = self._get('v')
            self.err = None
            self._pop('object_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('{')
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._expect('}')
            if self.err:
                return
            self.val = []
            self.err = None
        choice_1()

    def _array_(self):
        p = self.pos
        def choice_0():
            self._push('array_0')
            self._expect('[')
            if self.err:
                self._pop('array_0')
                return
            self._sp_()
            if self.err:
                self._pop('array_0')
                return
            self._element_list_()
            if not self.err:
                self._set('v', self.val)
            if self.err:
                self._pop('array_0')
                return
            self._sp_()
            if self.err:
                self._pop('array_0')
                return
            self._expect(']')
            if self.err:
                self._pop('array_0')
                return
            self.val = self._get('v')
            self.err = None
            self._pop('array_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('[')
            if self.err:
                return
            self._sp_()
            if self.err:
                return
            self._expect(']')
            if self.err:
                return
            self.val = []
            self.err = None
        choice_1()

    def _string_(self):
        p = self.pos
        def choice_0():
            self._push('string_0')
            self._squote_()
            if self.err:
                self._pop('string_0')
                return
            self._sqchars_()
            if not self.err:
                self._set('s', self.val)
            if self.err:
                self._pop('string_0')
                return
            self._squote_()
            if self.err:
                self._pop('string_0')
                return
            self.val = self._get('s')
            self.err = None
            self._pop('string_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('string_1')
            self._dquote_()
            if self.err:
                self._pop('string_1')
                return
            self._dqchars_()
            if not self.err:
                self._set('s', self.val)
            if self.err:
                self._pop('string_1')
                return
            self._dquote_()
            if self.err:
                self._pop('string_1')
                return
            self.val = self._get('s')
            self.err = None
            self._pop('string_1')
        choice_1()

    def _sqchars_(self):
        self._push('sqchars')
        vs = []
        while not self.err:
            p = self.pos
            def group():
                p = self.pos
                def group():
                    p = self.pos
                    def choice_0():
                        self._squote_()
                    choice_0()
                    if not self.err:
                        return

                    self.err = False
                    self.pos = p
                    def choice_1():
                        self._eol_()
                    choice_1()
                group()
                self.pos = p
                if not self.err:
                    self.err = "not"
                    self.val = None
                    return
                self.err = None
                if self.err:
                    return
                self._sqchar_()
            group()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('cs', self.val)
        if self.err:
            self._pop('sqchars')
            return
        self.val = ''.join(self._get('cs'))
        self.err = None
        self._pop('sqchars')

    def _sqchar_(self):
        p = self.pos
        def choice_0():
            self._bslash_()
            if self.err:
                return
            self._squote_()
            if self.err:
                return
            self.val = '\x5C\x27'
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._bslash_()
            if self.err:
                return
            self._expect('\n')
            if self.err:
                return
            self.val = '\n'
            self.err = None
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._bslash_()
            if self.err:
                return
            self._expect('\r\n')
            if self.err:
                return
            self.val = '\r\n'
            self.err = None
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._bslash_()
            if self.err:
                return
            self._expect('\r')
            if self.err:
                return
            self.val = '\r'
            self.err = None
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._bslash_()
            if self.err:
                return
            self._bslash_()
            if self.err:
                return
            self.val = '\x5C\x5C'
            self.err = None
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._anything_()
        choice_5()

    def _dqchars_(self):
        self._push('dqchars')
        vs = []
        while not self.err:
            p = self.pos
            def group():
                p = self.pos
                def group():
                    p = self.pos
                    def choice_0():
                        self._dquote_()
                    choice_0()
                    if not self.err:
                        return

                    self.err = False
                    self.pos = p
                    def choice_1():
                        self._eol_()
                    choice_1()
                group()
                self.pos = p
                if not self.err:
                    self.err = "not"
                    self.val = None
                    return
                self.err = None
                if self.err:
                    return
                self._dqchar_()
            group()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('cs', self.val)
        if self.err:
            self._pop('dqchars')
            return
        self.val = ''.join(self._get('cs'))
        self.err = None
        self._pop('dqchars')

    def _dqchar_(self):
        p = self.pos
        def choice_0():
            self._bslash_()
            if self.err:
                return
            self._dquote_()
            if self.err:
                return
            self.val = '\x5C\x22'
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._bslash_()
            if self.err:
                return
            self._expect('\n')
            if self.err:
                return
            self.val = '\n'
            self.err = None
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._bslash_()
            if self.err:
                return
            self._expect('\r\n')
            if self.err:
                return
            self.val = '\r\n'
            self.err = None
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._bslash_()
            if self.err:
                return
            self._expect('\r')
            if self.err:
                return
            self.val = '\r'
            self.err = None
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._bslash_()
            if self.err:
                return
            self._bslash_()
            if self.err:
                return
            self.val = '\x5C\x5C'
            self.err = None
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._anything_()
        choice_5()

    def _bslash_(self):
        self._expect('\x5C')

    def _squote_(self):
        self._expect('\x27')

    def _dquote_(self):
        self._expect('\x22')

    def _element_list_(self):
        p = self.pos
        def choice_0():
            self._push('element_list_0')
            self._value_()
            if not self.err:
                self._set('v', self.val)
            if self.err:
                self._pop('element_list_0')
                return
            self._sp_()
            if self.err:
                self._pop('element_list_0')
                return
            self._expect(',')
            if self.err:
                self._pop('element_list_0')
                return
            self._sp_()
            if self.err:
                self._pop('element_list_0')
                return
            self._element_list_()
            if not self.err:
                self._set('vs', self.val)
            if self.err:
                self._pop('element_list_0')
                return
            self.val = [self._get('v')] + self._get('vs')
            self.err = None
            self._pop('element_list_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('element_list_1')
            self._value_()
            if not self.err:
                self._set('v', self.val)
            if self.err:
                self._pop('element_list_1')
                return
            self._sp_()
            if self.err:
                self._pop('element_list_1')
                return
            self._expect(',')
            if self.err:
                self._pop('element_list_1')
                return
            self.val = [self._get('v')]
            self.err = None
            self._pop('element_list_1')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._push('element_list_2')
            self._value_()
            if not self.err:
                self._set('v', self.val)
            if self.err:
                self._pop('element_list_2')
                return
            self.val = [self._get('v')]
            self.err = None
            self._pop('element_list_2')
        choice_2()

    def _member_list_(self):
        p = self.pos
        def choice_0():
            self._push('member_list_0')
            self._member_()
            if not self.err:
                self._set('m', self.val)
            if self.err:
                self._pop('member_list_0')
                return
            self._sp_()
            if self.err:
                self._pop('member_list_0')
                return
            self._expect(',')
            if self.err:
                self._pop('member_list_0')
                return
            self._sp_()
            if self.err:
                self._pop('member_list_0')
                return
            self._member_list_()
            if not self.err:
                self._set('ms', self.val)
            if self.err:
                self._pop('member_list_0')
                return
            self.val = [self._get('m')] + self._get('ms')
            self.err = None
            self._pop('member_list_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('member_list_1')
            self._member_()
            if not self.err:
                self._set('m', self.val)
            if self.err:
                self._pop('member_list_1')
                return
            self._sp_()
            if self.err:
                self._pop('member_list_1')
                return
            self._expect(',')
            if self.err:
                self._pop('member_list_1')
                return
            self.val = [self._get('m')]
            self.err = None
            self._pop('member_list_1')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._push('member_list_2')
            self._member_()
            if not self.err:
                self._set('m', self.val)
            if self.err:
                self._pop('member_list_2')
                return
            self.val = [self._get('m')]
            self.err = None
            self._pop('member_list_2')
        choice_2()

    def _member_(self):
        p = self.pos
        def choice_0():
            self._push('member_0')
            self._string_()
            if not self.err:
                self._set('k', self.val)
            if self.err:
                self._pop('member_0')
                return
            self._sp_()
            if self.err:
                self._pop('member_0')
                return
            self._expect(':')
            if self.err:
                self._pop('member_0')
                return
            self._sp_()
            if self.err:
                self._pop('member_0')
                return
            self._value_()
            if not self.err:
                self._set('v', self.val)
            if self.err:
                self._pop('member_0')
                return
            self.val = [self._get('k'), self._get('v')]
            self.err = None
            self._pop('member_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('member_1')
            self._ident_()
            if not self.err:
                self._set('k', self.val)
            if self.err:
                self._pop('member_1')
                return
            self._sp_()
            if self.err:
                self._pop('member_1')
                return
            self._expect(':')
            if self.err:
                self._pop('member_1')
                return
            self._sp_()
            if self.err:
                self._pop('member_1')
                return
            self._value_()
            if not self.err:
                self._set('v', self.val)
            if self.err:
                self._pop('member_1')
                return
            self.val = [self._get('k'), self._get('v')]
            self.err = None
            self._pop('member_1')
        choice_1()

    def _ident_(self):
        self._push('ident')
        self._id_start_()
        if not self.err:
            self._set('hd', self.val)
        if self.err:
            self._pop('ident')
            return
        vs = []
        while not self.err:
            p = self.pos
            self._id_continue_()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('tl', self.val)
        if self.err:
            self._pop('ident')
            return
        self.val = ''.join([self._get('hd')] + self._get('tl'))
        self.err = None
        self._pop('ident')

    def _id_start_(self):
        p = self.pos
        def choice_0():
            self._letter_()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect('$')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect('_')
        choice_2()

    def _id_continue_(self):
        p = self.pos
        def choice_0():
            self._id_start_()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._digit_()
        choice_1()

    def _num_literal_(self):
        p = self.pos
        def choice_0():
            self._push('num_literal_0')
            self._expect('-')
            if self.err:
                self._pop('num_literal_0')
                return
            self._num_literal_()
            if not self.err:
                self._set('n', self.val)
            if self.err:
                self._pop('num_literal_0')
                return
            self.val = '-' + self._get('n')
            self.err = None
            self._pop('num_literal_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('num_literal_1')
            p = self.pos
            self._expect('+')
            if self.err:
                self.val = []
                self.err = None
                self.pos = p
            else:
                self.val = [self.val]
            if self.err:
                self._pop('num_literal_1')
                return
            self._dec_literal_()
            if not self.err:
                self._set('d', self.val)
            if self.err:
                self._pop('num_literal_1')
                return
            p = self.pos
            def group():
                p = self.pos
                def choice_0():
                    self._id_start_()
                choice_0()
                if not self.err:
                    return

                self.err = False
                self.pos = p
                def choice_1():
                    self._digit_()
                choice_1()
            group()
            self.pos = p
            if not self.err:
                self.err = "not"
                self.val = None
                self._pop('num_literal_1')
                return
            self.err = None
            if self.err:
                self._pop('num_literal_1')
                return
            self.val = self._get('d')
            self.err = None
            self._pop('num_literal_1')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._hex_literal_()
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._expect('Infinity')
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._expect('NaN')
        choice_4()

    def _dec_literal_(self):
        p = self.pos
        def choice_0():
            self._push('dec_literal_0')
            self._dec_int_lit_()
            if not self.err:
                self._set('d', self.val)
            if self.err:
                self._pop('dec_literal_0')
                return
            self._frac_()
            if not self.err:
                self._set('f', self.val)
            if self.err:
                self._pop('dec_literal_0')
                return
            self._exp_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('dec_literal_0')
                return
            self.val = self._get('d') + self._get('f') + self._get('e')
            self.err = None
            self._pop('dec_literal_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('dec_literal_1')
            self._dec_int_lit_()
            if not self.err:
                self._set('d', self.val)
            if self.err:
                self._pop('dec_literal_1')
                return
            self._frac_()
            if not self.err:
                self._set('f', self.val)
            if self.err:
                self._pop('dec_literal_1')
                return
            self.val = self._get('d') + self._get('f')
            self.err = None
            self._pop('dec_literal_1')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._push('dec_literal_2')
            self._dec_int_lit_()
            if not self.err:
                self._set('d', self.val)
            if self.err:
                self._pop('dec_literal_2')
                return
            self._exp_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('dec_literal_2')
                return
            self.val = self._get('d') + self._get('e')
            self.err = None
            self._pop('dec_literal_2')
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._push('dec_literal_3')
            self._dec_int_lit_()
            if not self.err:
                self._set('d', self.val)
            if self.err:
                self._pop('dec_literal_3')
                return
            self.val = self._get('d')
            self.err = None
            self._pop('dec_literal_3')
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._push('dec_literal_4')
            self._frac_()
            if not self.err:
                self._set('f', self.val)
            if self.err:
                self._pop('dec_literal_4')
                return
            self._exp_()
            if not self.err:
                self._set('e', self.val)
            if self.err:
                self._pop('dec_literal_4')
                return
            self.val = self._get('f') + self._get('e')
            self.err = None
            self._pop('dec_literal_4')
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._push('dec_literal_5')
            self._frac_()
            if not self.err:
                self._set('f', self.val)
            if self.err:
                self._pop('dec_literal_5')
                return
            self.val = self._get('f')
            self.err = None
            self._pop('dec_literal_5')
        choice_5()

    def _dec_int_lit_(self):
        p = self.pos
        def choice_0():
            self._expect('0')
            if self.err:
                return
            p = self.pos
            self._digit_()
            self.pos = p
            if not self.err:
                self.err = "not"
                self.val = None
                return
            self.err = None
            if self.err:
                return
            self.val = '0'
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('dec_int_lit_1')
            self._nonzerodigit_()
            if not self.err:
                self._set('n', self.val)
            if self.err:
                self._pop('dec_int_lit_1')
                return
            vs = []
            while not self.err:
                p = self.pos
                self._digit_()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('ds', self.val)
            if self.err:
                self._pop('dec_int_lit_1')
                return
            self.val = self._get('n') + ''.join(self._get('ds'))
            self.err = None
            self._pop('dec_int_lit_1')
        choice_1()

    def _nonzerodigit_(self):
        i = u'1'
        j = u'9'
        if (self.pos == self.end or
            ord(self.msg[self.pos]) < ord(i) or
            ord(self.msg[self.pos]) > ord(j)):
            self.val = None
            self.err = True
            if self.pos >= self.errpos:
                if self.pos > self.errpos:
                    self.errset = set()
                self.errset.add('something between %s and %s' % (i, j))
                self.errpos = self.pos
        else:
            self.val = self.msg[self.pos]
            self.err = False
            self.pos += 1
        return

    def _hex_literal_(self):
        self._push('hex_literal')
        def group():
            p = self.pos
            def choice_0():
                self._expect('0x')
            choice_0()
            if not self.err:
                return

            self.err = False
            self.pos = p
            def choice_1():
                self._expect('0X')
            choice_1()
        group()
        if self.err:
            self._pop('hex_literal')
            return
        vs = []
        self._hex_digit_()
        if self.err:
            self._pop('hex_literal')
            return
        vs.append(self.val)
        while not self.err:
            p = self.pos
            self._hex_digit_()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('hs', self.val)
        if self.err:
            self._pop('hex_literal')
            return
        self.val = '0x' + ''.join(self._get('hs'))
        self.err = None
        self._pop('hex_literal')

    def _hex_digit_(self):
        p = self.pos
        def choice_0():
            i = u'a'
            j = u'f'
            if (self.pos == self.end or
                ord(self.msg[self.pos]) < ord(i) or
                ord(self.msg[self.pos]) > ord(j)):
                self.val = None
                self.err = True
                if self.pos >= self.errpos:
                    if self.pos > self.errpos:
                        self.errset = set()
                    self.errset.add('something between %s and %s' % (i, j))
                    self.errpos = self.pos
            else:
                self.val = self.msg[self.pos]
                self.err = False
                self.pos += 1
            return
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            i = u'A'
            j = u'F'
            if (self.pos == self.end or
                ord(self.msg[self.pos]) < ord(i) or
                ord(self.msg[self.pos]) > ord(j)):
                self.val = None
                self.err = True
                if self.pos >= self.errpos:
                    if self.pos > self.errpos:
                        self.errset = set()
                    self.errset.add('something between %s and %s' % (i, j))
                    self.errpos = self.pos
            else:
                self.val = self.msg[self.pos]
                self.err = False
                self.pos += 1
            return
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._digit_()
        choice_2()

    def _frac_(self):
        self._push('frac')
        self._expect('.')
        if self.err:
            self._pop('frac')
            return
        vs = []
        while not self.err:
            p = self.pos
            self._digit_()
            if not self.err:
                vs.append(self.val)
            else:
                self.pos = p
        self.val = vs
        self.err = None
        if not self.err:
            self._set('ds', self.val)
        if self.err:
            self._pop('frac')
            return
        self.val = '.' + ''.join(self._get('ds'))
        self.err = None
        self._pop('frac')

    def _exp_(self):
        p = self.pos
        def choice_0():
            self._push('exp_0')
            def group():
                p = self.pos
                def choice_0():
                    self._expect('e')
                choice_0()
                if not self.err:
                    return

                self.err = False
                self.pos = p
                def choice_1():
                    self._expect('E')
                choice_1()
            group()
            if self.err:
                self._pop('exp_0')
                return
            def group():
                p = self.pos
                def choice_0():
                    self._expect('+')
                choice_0()
                if not self.err:
                    return

                self.err = False
                self.pos = p
                def choice_1():
                    self._expect('-')
                choice_1()
            group()
            if not self.err:
                self._set('s', self.val)
            if self.err:
                self._pop('exp_0')
                return
            vs = []
            while not self.err:
                p = self.pos
                self._digit_()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('ds', self.val)
            if self.err:
                self._pop('exp_0')
                return
            self.val = 'e' + self._get('s') + ''.join(self._get('ds'))
            self.err = None
            self._pop('exp_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('exp_1')
            def group():
                p = self.pos
                def choice_0():
                    self._expect('e')
                choice_0()
                if not self.err:
                    return

                self.err = False
                self.pos = p
                def choice_1():
                    self._expect('E')
                choice_1()
            group()
            if self.err:
                self._pop('exp_1')
                return
            vs = []
            while not self.err:
                p = self.pos
                self._digit_()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('ds', self.val)
            if self.err:
                self._pop('exp_1')
                return
            self.val = 'e' + ''.join(self._get('ds'))
            self.err = None
            self._pop('exp_1')
        choice_1()

    def _anything_(self):
        if self.pos < self.end:
            self.val = self.msg[self.pos]
            self.err = None
            self.pos += 1
        else:
            self.val = None
            self.err = "anything"

    def _digit_(self):
        if self.pos < self.end and self.msg[self.pos].isdigit():
            self.val = self.msg[self.pos]
            self.err = None
            self.pos += 1
        else:
            self.val = None
            self.err = "a digit"
        return

    def _end_(self):
        if self.pos == self.end:
            self.val = None
            self.err = None
        else:
            self.val = None
            self.err = "the end"
        return

    def _letter_(self):
        if self.pos < self.end and self.msg[self.pos].isalpha():
            self.val = self.msg[self.pos]
            self.err = None
            self.pos += 1
        else:
            self.val = None
            self.err = "a letter"
        return
