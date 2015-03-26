from compiled_parser_base import CompiledParserBase


class Parser(CompiledParserBase):

    def _grammar_(self):
        """ sp value sp end """
        self._sp_()
        if self.err:
            return
        self._value_()
        if self.err:
            return
        self._sp_()
        if self.err:
            return
        self._end_()

    def _sp_(self):
        """ ws* """
        vs = []
        while not self.err:
            self._ws_()
            if not self.err:
                vs.append(self.val)
        self.val = vs
        self.err = None

    def _ws_(self):
        """ ' '|'\t'|comment|eol """
        p = self.pos
        def choice_0():
            self._expect(' ')
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._expect('\t')
        choice_1()
        if not self.err:
            return

        self.pos = p
        def choice_2():
            self._comment_()
        choice_2()
        if not self.err:
            return

        self.pos = p
        def choice_3():
            self._eol_()
        choice_3()

    def _eol_(self):
        """ '\r\n'|'\r'|'\n' """
        p = self.pos
        def choice_0():
            self._expect('\r\n')
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._expect('\r')
        choice_1()
        if not self.err:
            return

        self.pos = p
        def choice_2():
            self._expect('\n')
        choice_2()

    def _comment_(self):
        """ '//' ~eol* eol|'/*' ~('*/')* '*/' """
        p = self.pos
        def choice_0():
            self._expect('//')
            if self.err:
                return
            vs = []
            while not self.err:
                p = self.pos
                self._eol_()
                self.pos = p
                if not self.err:
                     self.err = "not"
                     self.val = None
                     return
                self.err = None
                if not self.err:
                    vs.append(self.val)
            self.val = vs
            self.err = None
            if self.err:
                return
            self._eol_()
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._expect('/*')
            if self.err:
                return
            vs = []
            while not self.err:
                p = self.pos
                def group():
                    self._expect('*/')
                group()
                self.pos = p
                if not self.err:
                     self.err = "not"
                     self.val = None
                     return
                self.err = None
                if not self.err:
                    vs.append(self.val)
            self.val = vs
            self.err = None
            if self.err:
                return
            self._expect('*/')
        choice_1()

    def _value_(self):
        """ 'null'|'true'|'false'|object|array|string|number """
        p = self.pos
        def choice_0():
            self._expect('null')
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._expect('true')
        choice_1()
        if not self.err:
            return

        self.pos = p
        def choice_2():
            self._expect('false')
        choice_2()
        if not self.err:
            return

        self.pos = p
        def choice_3():
            self._object_()
        choice_3()
        if not self.err:
            return

        self.pos = p
        def choice_4():
            self._array_()
        choice_4()
        if not self.err:
            return

        self.pos = p
        def choice_5():
            self._string_()
        choice_5()
        if not self.err:
            return

        self.pos = p
        def choice_6():
            self._number_()
        choice_6()

    def _object_(self):
        """ '{' ws member_list ws '}'|'{' ws '}' """
        p = self.pos
        def choice_0():
            self._expect('{')
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._member_list_()
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect('}')
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._expect('{')
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect('}')
        choice_1()

    def _array_(self):
        """ '[' ws element_list ws ']'|'[' ws ']' """
        p = self.pos
        def choice_0():
            self._expect('[')
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._element_list_()
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect(']')
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._expect('[')
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect(']')
        choice_1()

    def _string_(self):
        """ squote (~squote qchar*)* squote|dquote (~dquote qchar*)* dquote """
        p = self.pos
        def choice_0():
            self._squote_()
            if self.err:
                return
            vs = []
            while not self.err:
                def group():
                    p = self.pos
                    self._squote_()
                    self.pos = p
                    if not self.err:
                         self.err = "not"
                         self.val = None
                         return
                    self.err = None
                    if self.err:
                        return
                    vs = []
                    while not self.err:
                        self._qchar_()
                        if not self.err:
                            vs.append(self.val)
                    self.val = vs
                    self.err = None
                group()
                if not self.err:
                    vs.append(self.val)
            self.val = vs
            self.err = None
            if self.err:
                return
            self._squote_()
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._dquote_()
            if self.err:
                return
            vs = []
            while not self.err:
                def group():
                    p = self.pos
                    self._dquote_()
                    self.pos = p
                    if not self.err:
                         self.err = "not"
                         self.val = None
                         return
                    self.err = None
                    if self.err:
                        return
                    vs = []
                    while not self.err:
                        self._qchar_()
                        if not self.err:
                            vs.append(self.val)
                    self.val = vs
                    self.err = None
                group()
                if not self.err:
                    vs.append(self.val)
            self.val = vs
            self.err = None
            if self.err:
                return
            self._dquote_()
        choice_1()

    def _squote_(self):
        """ '\'' """
        self._expect('\'')

    def _dquote_(self):
        """ '"' """
        self._expect('"')

    def _qchar_(self):
        """ '\\\''|'\\"'|anything """
        p = self.pos
        def choice_0():
            self._expect('\\\'')
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._expect('\\"')
        choice_1()
        if not self.err:
            return

        self.pos = p
        def choice_2():
            self._anything_()
        choice_2()

    def _element_list_(self):
        """ value ws ',' ws element_list|value ws ','|value """
        p = self.pos
        def choice_0():
            self._value_()
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect(',')
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._element_list_()
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._value_()
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect(',')
        choice_1()
        if not self.err:
            return

        self.pos = p
        def choice_2():
            self._value_()
        choice_2()

    def _member_list_(self):
        """ member ws ',' ws member_list|member ws ','|member """
        p = self.pos
        def choice_0():
            self._member_()
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect(',')
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._member_list_()
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._member_()
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect(',')
        choice_1()
        if not self.err:
            return

        self.pos = p
        def choice_2():
            self._member_()
        choice_2()

    def _member_(self):
        """ string ws ':' value|ident ws ':' value """
        p = self.pos
        def choice_0():
            self._string_()
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect(':')
            if self.err:
                return
            self._value_()
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._ident_()
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect(':')
            if self.err:
                return
            self._value_()
        choice_1()

    def _ident_(self):
        """ (letter|'$'|'_') (letter|digit)* """
        def group():
            p = self.pos
            def choice_0():
                self._letter_()
            choice_0()
            if not self.err:
                return

            self.pos = p
            def choice_1():
                self._expect('$')
            choice_1()
            if not self.err:
                return

            self.pos = p
            def choice_2():
                self._expect('_')
            choice_2()
        group()
        if self.err:
            return
        vs = []
        while not self.err:
            def group():
                p = self.pos
                def choice_0():
                    self._letter_()
                choice_0()
                if not self.err:
                    return

                self.pos = p
                def choice_1():
                    self._digit_()
                choice_1()
            group()
            if not self.err:
                vs.append(self.val)
        self.val = vs
        self.err = None

    def _number_(self):
        """ digit digit* """
        self._digit_()
        if self.err:
            return
        vs = []
        while not self.err:
            self._digit_()
            if not self.err:
                vs.append(self.val)
        self.val = vs
        self.err = None
