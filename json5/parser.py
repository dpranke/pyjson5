# pylint: disable=line-too-long

from builtins import str, chr

class Parser(object):
    def __init__(self, msg, fname, starting_rule='grammar'):
        self.msg = str(msg)
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
        prefix = u'%s:%d' % (self.fname, lineno)
        if type(self.err) == type(''):
            return u'%s %s' % (prefix, self.err)
        exps = list(self.errset)
        if len(exps) > 1:
            return u'%s Unexpected "%s" at column %d' % (
                prefix, self.msg[self.errpos], colno)
        if self.errpos == 0 and len(self.msg) == 0:
            return u'input must not be empty'
        return u'%s Expecting a "%s" at column %d, got a "%s"' % (
                prefix, exps[0], colno, self.msg[self.errpos])

    def _err_offsets(self):
        lineno = 1
        colno = 1
        i = 0
        begpos = 0
        while i < self.errpos:
            if self.msg[i] == u'\n':
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
        self._value_()
        if not self.err:
            self._set('v', self.val)
        if self.err:
            self._pop('grammar')
            return
        self._sp_()
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
            self._expect(u' ')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._eol_()
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._comment_()
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._expect(u'\t')
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._expect(u'\x0b')
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._expect(u'\x0c')
        choice_5()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_6():
            self._expect(u'\xa0')
        choice_6()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_7():
            self._expect(u'\ufeff')
        choice_7()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_8():
            self._push('ws_8')
            self._anything_()
            if not self.err:
                self._set('x', self.val)
            if self.err:
                self._pop('ws_8')
                return
            v = self._is_unicat(self._get('x'), u'Zs')
            if v:
                self.val = v
                self.err = None
            else:
                self.err = "pred check failed"
                self.val = None
            if self.err:
                self._pop('ws_8')
                return
            self.val = self._get('x')
            self.err = None
            self._pop('ws_8')
        choice_8()

    def _eol_(self):
        p = self.pos
        def choice_0():
            self._expect(u'\r')
            if self.err:
                return
            self._expect(u'\n')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect(u'\r')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect(u'\n')
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._expect(u'\u2028')
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._expect(u'\u2029')
        choice_4()

    def _comment_(self):
        p = self.pos
        def choice_0():
            self._expect(u'//')
            if self.err:
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    p = self.pos
                    self._eol_()
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
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect(u'/*')
            if self.err:
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    p = self.pos
                    self._expect(u'*/')
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
            self._expect(u'*/')
        choice_1()

    def _value_(self):
        p = self.pos
        def choice_0():
            self._expect(u'null')
            if self.err:
                return
            self.val = u'None'
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect(u'true')
            if self.err:
                return
            self.val = u'True'
            self.err = None
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect(u'false')
            if self.err:
                return
            self.val = u'False'
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
            self.val = [u'object', self._get('v')]
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
            self.val = [u'array', self._get('v')]
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
            self.val = [u'string', self._get('v')]
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
            self.val = [u'number', self._get('v')]
            self.err = None
            self._pop('value_6')
        choice_6()

    def _object_(self):
        p = self.pos
        def choice_0():
            self._push('object_0')
            self._expect(u'{')
            if self.err:
                self._pop('object_0')
                return
            self._sp_()
            self._member_list_()
            if not self.err:
                self._set('v', self.val)
            if self.err:
                self._pop('object_0')
                return
            self._sp_()
            self._expect(u'}')
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
            self._expect(u'{')
            if self.err:
                return
            self._sp_()
            self._expect(u'}')
            if self.err:
                return
            self.val = []
            self.err = None
        choice_1()

    def _array_(self):
        p = self.pos
        def choice_0():
            self._push('array_0')
            self._expect(u'[')
            if self.err:
                self._pop('array_0')
                return
            self._sp_()
            self._element_list_()
            if not self.err:
                self._set('v', self.val)
            if self.err:
                self._pop('array_0')
                return
            self._sp_()
            self._expect(u']')
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
            self._expect(u'[')
            if self.err:
                return
            self._sp_()
            self._expect(u']')
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
            vs = []
            while not self.err:
                p = self.pos
                self._sqchar_()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('cs', self.val)
            if self.err:
                self._pop('string_0')
                return
            self._squote_()
            if self.err:
                self._pop('string_0')
                return
            self.val = self._join(u'', self._get('cs'))
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
            vs = []
            while not self.err:
                p = self.pos
                self._dqchar_()
                if not self.err:
                    vs.append(self.val)
                else:
                    self.pos = p
            self.val = vs
            self.err = None
            if not self.err:
                self._set('cs', self.val)
            if self.err:
                self._pop('string_1')
                return
            self._dquote_()
            if self.err:
                self._pop('string_1')
                return
            self.val = self._join(u'', self._get('cs'))
            self.err = None
            self._pop('string_1')
        choice_1()

    def _sqchar_(self):
        p = self.pos
        def choice_0():
            self._push('sqchar_0')
            self._bslash_()
            if self.err:
                self._pop('sqchar_0')
                return
            self._esc_char_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('sqchar_0')
                return
            self.val = self._get('c')
            self.err = None
            self._pop('sqchar_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._bslash_()
            if self.err:
                return
            self._eol_()
            if self.err:
                return
            self.val = u''
            self.err = None
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._push('sqchar_2')
            p = self.pos
            self._bslash_()
            self.pos = p
            if not self.err:
                self.err = "not"
                self.val = None
                self._pop('sqchar_2')
                return
            self.err = None
            if self.err:
                self._pop('sqchar_2')
                return
            p = self.pos
            self._squote_()
            self.pos = p
            if not self.err:
                self.err = "not"
                self.val = None
                self._pop('sqchar_2')
                return
            self.err = None
            if self.err:
                self._pop('sqchar_2')
                return
            p = self.pos
            self._eol_()
            self.pos = p
            if not self.err:
                self.err = "not"
                self.val = None
                self._pop('sqchar_2')
                return
            self.err = None
            if self.err:
                self._pop('sqchar_2')
                return
            self._anything_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('sqchar_2')
                return
            self.val = self._get('c')
            self.err = None
            self._pop('sqchar_2')
        choice_2()

    def _dqchar_(self):
        p = self.pos
        def choice_0():
            self._push('dqchar_0')
            self._bslash_()
            if self.err:
                self._pop('dqchar_0')
                return
            self._esc_char_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('dqchar_0')
                return
            self.val = self._get('c')
            self.err = None
            self._pop('dqchar_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._bslash_()
            if self.err:
                return
            self._eol_()
            if self.err:
                return
            self.val = u''
            self.err = None
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._push('dqchar_2')
            p = self.pos
            self._bslash_()
            self.pos = p
            if not self.err:
                self.err = "not"
                self.val = None
                self._pop('dqchar_2')
                return
            self.err = None
            if self.err:
                self._pop('dqchar_2')
                return
            p = self.pos
            self._dquote_()
            self.pos = p
            if not self.err:
                self.err = "not"
                self.val = None
                self._pop('dqchar_2')
                return
            self.err = None
            if self.err:
                self._pop('dqchar_2')
                return
            p = self.pos
            self._eol_()
            self.pos = p
            if not self.err:
                self.err = "not"
                self.val = None
                self._pop('dqchar_2')
                return
            self.err = None
            if self.err:
                self._pop('dqchar_2')
                return
            self._anything_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('dqchar_2')
                return
            self.val = self._get('c')
            self.err = None
            self._pop('dqchar_2')
        choice_2()

    def _bslash_(self):
        self._expect(u'\\')

    def _squote_(self):
        self._expect(u"'")

    def _dquote_(self):
        self._expect(u'"')

    def _esc_char_(self):
        p = self.pos
        def choice_0():
            self._expect(u'b')
            if self.err:
                return
            self.val = u'\x08'
            self.err = None
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._expect(u'f')
            if self.err:
                return
            self.val = u'\x0c'
            self.err = None
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._expect(u'n')
            if self.err:
                return
            self.val = u'\n'
            self.err = None
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._expect(u'r')
            if self.err:
                return
            self.val = u'\r'
            self.err = None
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._expect(u't')
            if self.err:
                return
            self.val = u'\t'
            self.err = None
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._expect(u'v')
            if self.err:
                return
            self.val = u'\x0b'
            self.err = None
        choice_5()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_6():
            self._squote_()
            if self.err:
                return
            self.val = u"'"
            self.err = None
        choice_6()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_7():
            self._dquote_()
            if self.err:
                return
            self.val = u'"'
            self.err = None
        choice_7()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_8():
            self._bslash_()
            if self.err:
                return
            self.val = u'\\'
            self.err = None
        choice_8()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_9():
            self._push('esc_char_9')
            self._hex_esc_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('esc_char_9')
                return
            self.val = self._get('c')
            self.err = None
            self._pop('esc_char_9')
        choice_9()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_10():
            self._push('esc_char_10')
            self._unicode_esc_()
            if not self.err:
                self._set('c', self.val)
            if self.err:
                self._pop('esc_char_10')
                return
            self.val = self._get('c')
            self.err = None
            self._pop('esc_char_10')
        choice_10()

    def _hex_esc_(self):
        self._push('hex_esc')
        self._expect(u'x')
        if self.err:
            self._pop('hex_esc')
            return
        self._hex_()
        if not self.err:
            self._set('h1', self.val)
        if self.err:
            self._pop('hex_esc')
            return
        self._hex_()
        if not self.err:
            self._set('h2', self.val)
        if self.err:
            self._pop('hex_esc')
            return
        self.val = self._xtou(self._get('h1') + self._get('h2'))
        self.err = None
        self._pop('hex_esc')

    def _unicode_esc_(self):
        self._push('unicode_esc')
        self._expect(u'u')
        if self.err:
            self._pop('unicode_esc')
            return
        self._hex_()
        if not self.err:
            self._set('a', self.val)
        if self.err:
            self._pop('unicode_esc')
            return
        self._hex_()
        if not self.err:
            self._set('b', self.val)
        if self.err:
            self._pop('unicode_esc')
            return
        self._hex_()
        if not self.err:
            self._set('c', self.val)
        if self.err:
            self._pop('unicode_esc')
            return
        self._hex_()
        if not self.err:
            self._set('d', self.val)
        if self.err:
            self._pop('unicode_esc')
            return
        self.val = self._xtou(self._get('a') + self._get('b') + self._get('c') + self._get('d'))
        self.err = None
        self._pop('unicode_esc')

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
            self._expect(u',')
            if self.err:
                self._pop('element_list_0')
                return
            self._sp_()
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
            self._expect(u',')
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
            self._expect(u',')
            if self.err:
                self._pop('member_list_0')
                return
            self._sp_()
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
            self._expect(u',')
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
            self._expect(u':')
            if self.err:
                self._pop('member_0')
                return
            self._sp_()
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
            self._expect(u':')
            if self.err:
                self._pop('member_1')
                return
            self._sp_()
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
        self.val = self._join(u'', [self._get('hd')] + self._get('tl'))
        self.err = None
        self._pop('ident')

    def _id_start_(self):
        p = self.pos
        def choice_0():
            self._ascii_id_start_()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._other_id_start_()
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._bslash_()
            if self.err:
                return
            self._unicode_esc_()
        choice_2()

    def _ascii_id_start_(self):
        p = self.pos
        def choice_0():
            i = u'a'
            j = u'z'
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
            j = u'Z'
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
            self._expect(u'$')
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._expect(u'_')
        choice_3()

    def _other_id_start_(self):
        p = self.pos
        def choice_0():
            self._push('other_id_start_0')
            self._anything_()
            if not self.err:
                self._set('x', self.val)
            if self.err:
                self._pop('other_id_start_0')
                return
            v = self._is_unicat(self._get('x'), u'Ll')
            if v:
                self.val = v
                self.err = None
            else:
                self.err = "pred check failed"
                self.val = None
            if self.err:
                self._pop('other_id_start_0')
                return
            self.val = self._get('x')
            self.err = None
            self._pop('other_id_start_0')
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._push('other_id_start_1')
            self._anything_()
            if not self.err:
                self._set('x', self.val)
            if self.err:
                self._pop('other_id_start_1')
                return
            v = self._is_unicat(self._get('x'), u'Lm')
            if v:
                self.val = v
                self.err = None
            else:
                self.err = "pred check failed"
                self.val = None
            if self.err:
                self._pop('other_id_start_1')
                return
            self.val = self._get('x')
            self.err = None
            self._pop('other_id_start_1')
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._push('other_id_start_2')
            self._anything_()
            if not self.err:
                self._set('x', self.val)
            if self.err:
                self._pop('other_id_start_2')
                return
            v = self._is_unicat(self._get('x'), u'Lo')
            if v:
                self.val = v
                self.err = None
            else:
                self.err = "pred check failed"
                self.val = None
            if self.err:
                self._pop('other_id_start_2')
                return
            self.val = self._get('x')
            self.err = None
            self._pop('other_id_start_2')
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._push('other_id_start_3')
            self._anything_()
            if not self.err:
                self._set('x', self.val)
            if self.err:
                self._pop('other_id_start_3')
                return
            v = self._is_unicat(self._get('x'), u'Lt')
            if v:
                self.val = v
                self.err = None
            else:
                self.err = "pred check failed"
                self.val = None
            if self.err:
                self._pop('other_id_start_3')
                return
            self.val = self._get('x')
            self.err = None
            self._pop('other_id_start_3')
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._push('other_id_start_4')
            self._anything_()
            if not self.err:
                self._set('x', self.val)
            if self.err:
                self._pop('other_id_start_4')
                return
            v = self._is_unicat(self._get('x'), u'Lu')
            if v:
                self.val = v
                self.err = None
            else:
                self.err = "pred check failed"
                self.val = None
            if self.err:
                self._pop('other_id_start_4')
                return
            self.val = self._get('x')
            self.err = None
            self._pop('other_id_start_4')
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._push('other_id_start_5')
            self._anything_()
            if not self.err:
                self._set('x', self.val)
            if self.err:
                self._pop('other_id_start_5')
                return
            v = self._is_unicat(self._get('x'), u'Nl')
            if v:
                self.val = v
                self.err = None
            else:
                self.err = "pred check failed"
                self.val = None
            if self.err:
                self._pop('other_id_start_5')
                return
            self.val = self._get('x')
            self.err = None
            self._pop('other_id_start_5')
        choice_5()

    def _id_continue_(self):
        p = self.pos
        def choice_0():
            self._ascii_id_start_()
        choice_0()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_1():
            self._digit_()
        choice_1()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_2():
            self._other_id_start_()
        choice_2()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_3():
            self._push('id_continue_3')
            self._anything_()
            if not self.err:
                self._set('x', self.val)
            if self.err:
                self._pop('id_continue_3')
                return
            v = self._is_unicat(self._get('x'), u'Mn')
            if v:
                self.val = v
                self.err = None
            else:
                self.err = "pred check failed"
                self.val = None
            if self.err:
                self._pop('id_continue_3')
                return
            self.val = self._get('x')
            self.err = None
            self._pop('id_continue_3')
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._push('id_continue_4')
            self._anything_()
            if not self.err:
                self._set('x', self.val)
            if self.err:
                self._pop('id_continue_4')
                return
            v = self._is_unicat(self._get('x'), u'Mc')
            if v:
                self.val = v
                self.err = None
            else:
                self.err = "pred check failed"
                self.val = None
            if self.err:
                self._pop('id_continue_4')
                return
            self.val = self._get('x')
            self.err = None
            self._pop('id_continue_4')
        choice_4()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_5():
            self._push('id_continue_5')
            self._anything_()
            if not self.err:
                self._set('x', self.val)
            if self.err:
                self._pop('id_continue_5')
                return
            v = self._is_unicat(self._get('x'), u'Nd')
            if v:
                self.val = v
                self.err = None
            else:
                self.err = "pred check failed"
                self.val = None
            if self.err:
                self._pop('id_continue_5')
                return
            self.val = self._get('x')
            self.err = None
            self._pop('id_continue_5')
        choice_5()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_6():
            self._push('id_continue_6')
            self._anything_()
            if not self.err:
                self._set('x', self.val)
            if self.err:
                self._pop('id_continue_6')
                return
            v = self._is_unicat(self._get('x'), u'Pc')
            if v:
                self.val = v
                self.err = None
            else:
                self.err = "pred check failed"
                self.val = None
            if self.err:
                self._pop('id_continue_6')
                return
            self.val = self._get('x')
            self.err = None
            self._pop('id_continue_6')
        choice_6()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_7():
            self._bslash_()
            if self.err:
                return
            self._unicode_esc_()
        choice_7()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_8():
            self._expect(u'\u200c')
        choice_8()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_9():
            self._expect(u'\u200d')
        choice_9()

    def _num_literal_(self):
        p = self.pos
        def choice_0():
            self._push('num_literal_0')
            self._expect(u'-')
            if self.err:
                self._pop('num_literal_0')
                return
            self._num_literal_()
            if not self.err:
                self._set('n', self.val)
            if self.err:
                self._pop('num_literal_0')
                return
            self.val = u'-' + self._get('n')
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
            self._expect(u'+')
            if self.err:
                self.val = []
                self.err = None
                self.pos = p
            else:
                self.val = [self.val]
            self._dec_literal_()
            if not self.err:
                self._set('d', self.val)
            if self.err:
                self._pop('num_literal_1')
                return
            p = self.pos
            self._id_start_()
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
            self._expect(u'Infinity')
        choice_3()
        if not self.err:
            return

        self.err = False
        self.pos = p
        def choice_4():
            self._expect(u'NaN')
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
            self._expect(u'0')
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
            self.val = u'0'
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
                self._set('d', self.val)
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
            self.val = self._get('d') + self._join(u'', self._get('ds'))
            self.err = None
            self._pop('dec_int_lit_1')
        choice_1()

    def _digit_(self):
        i = u'0'
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
                self._expect(u'0x')
            choice_0()
            if not self.err:
                return

            self.err = False
            self.pos = p
            def choice_1():
                self._expect(u'0X')
            choice_1()
        group()
        if self.err:
            self._pop('hex_literal')
            return
        vs = []
        self._hex_()
        if self.err:
            self._pop('hex_literal')
            return
        vs.append(self.val)
        while not self.err:
            p = self.pos
            self._hex_()
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
        self.val = u'0x' + self._join(u'', self._get('hs'))
        self.err = None
        self._pop('hex_literal')

    def _hex_(self):
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
        self._expect(u'.')
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
        self.val = u'.' + self._join(u'', self._get('ds'))
        self.err = None
        self._pop('frac')

    def _exp_(self):
        p = self.pos
        def choice_0():
            self._push('exp_0')
            def group():
                p = self.pos
                def choice_0():
                    self._expect(u'e')
                choice_0()
                if not self.err:
                    return

                self.err = False
                self.pos = p
                def choice_1():
                    self._expect(u'E')
                choice_1()
            group()
            if self.err:
                self._pop('exp_0')
                return
            def group():
                p = self.pos
                def choice_0():
                    self._expect(u'+')
                choice_0()
                if not self.err:
                    return

                self.err = False
                self.pos = p
                def choice_1():
                    self._expect(u'-')
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
            self.val = u'e' + self._get('s') + self._join(u'', self._get('ds'))
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
                    self._expect(u'e')
                choice_0()
                if not self.err:
                    return

                self.err = False
                self.pos = p
                def choice_1():
                    self._expect(u'E')
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
            self.val = u'e' + self._join(u'', self._get('ds'))
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
            self.err = u'anything'

    def _end_(self):
        if self.pos == self.end:
            self.val = None
            self.err = None
        else:
            self.val = None
            self.err = u'the end'
        return

    def _is_unicat(self, var, cat):
        import unicodedata
        return unicodedata.category(var) == cat

    def _join(self, s, vs):
        return s.join(vs)

    def _xtou(self, s):
        return chr(int(s, base=16))
