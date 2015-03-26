from compiled_parser_base import CompiledParserBase


class Parser(CompiledParserBase):

    def _grammar_(self):
        """ sp value:v sp end -> v """
        self._sp_()
        if self.err:
            return
        self._value_()
        if not self.err:
            v_v = self.val
        if self.err:
            return
        self._sp_()
        if self.err:
            return
        self._end_()
        if self.err:
            return
        self.val = v_v
        self.err = None

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
        """ 'null' -> 'None'|'true' -> 'True'|'false' -> 'False'|object:v -> ['object', v]|array:v -> ['array', v]|string:v -> ['string', v]|number:v -> ['number', v] """
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

        self.pos = p
        def choice_3():
            self._object_()
            if not self.err:
                v_v = self.val
            if self.err:
                return
            self.val = ['object', v_v]
            self.err = None
        choice_3()
        if not self.err:
            return

        self.pos = p
        def choice_4():
            self._array_()
            if not self.err:
                v_v = self.val
            if self.err:
                return
            self.val = ['array', v_v]
            self.err = None
        choice_4()
        if not self.err:
            return

        self.pos = p
        def choice_5():
            self._string_()
            if not self.err:
                v_v = self.val
            if self.err:
                return
            self.val = ['string', v_v]
            self.err = None
        choice_5()
        if not self.err:
            return

        self.pos = p
        def choice_6():
            self._number_()
            if not self.err:
                v_v = self.val
            if self.err:
                return
            self.val = ['number', v_v]
            self.err = None
        choice_6()

    def _object_(self):
        """ '{' ws member_list:v ws '}' -> v|'{' ws '}' -> [] """
        p = self.pos
        def choice_0():
            self._expect('{')
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._member_list_()
            if not self.err:
                v_v = self.val
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect('}')
            if self.err:
                return
            self.val = v_v
            self.err = None
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
            if self.err:
                return
            self.val = []
            self.err = None
        choice_1()

    def _array_(self):
        """ '[' ws element_list:v ws ']' -> v|'[' ws ']' -> [] """
        p = self.pos
        def choice_0():
            self._expect('[')
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._element_list_()
            if not self.err:
                v_v = self.val
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect(']')
            if self.err:
                return
            self.val = v_v
            self.err = None
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
            if self.err:
                return
            self.val = []
            self.err = None
        choice_1()

    def _string_(self):
        """ squote (~squote qchar)*:qs squote -> ''.join(qs)|dquote (~dquote qchar)*:qs dquote -> ''.join(qs) """
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
                    self._qchar_()
                group()
                if not self.err:
                    vs.append(self.val)
            self.val = vs
            self.err = None
            if not self.err:
                v_qs = self.val
            if self.err:
                return
            self._squote_()
            if self.err:
                return
            self.val = ''.join(v_qs)
            self.err = None
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
                    self._qchar_()
                group()
                if not self.err:
                    vs.append(self.val)
            self.val = vs
            self.err = None
            if not self.err:
                v_qs = self.val
            if self.err:
                return
            self._dquote_()
            if self.err:
                return
            self.val = ''.join(v_qs)
            self.err = None
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
        """ value:v ws ',' ws element_list:vs -> [v] + vs|value:v ws ',' -> [v]|value:v -> [v] """
        p = self.pos
        def choice_0():
            self._value_()
            if not self.err:
                v_v = self.val
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
            if not self.err:
                v_vs = self.val
            if self.err:
                return
            self.val = [v_v] + v_vs
            self.err = None
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._value_()
            if not self.err:
                v_v = self.val
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect(',')
            if self.err:
                return
            self.val = [v_v]
            self.err = None
        choice_1()
        if not self.err:
            return

        self.pos = p
        def choice_2():
            self._value_()
            if not self.err:
                v_v = self.val
            if self.err:
                return
            self.val = [v_v]
            self.err = None
        choice_2()

    def _member_list_(self):
        """ member:m ws ',' ws member_list:ms -> [m] + ms|member:m ws ',' -> [m]|member:m -> [m] """
        p = self.pos
        def choice_0():
            self._member_()
            if not self.err:
                v_m = self.val
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
            if not self.err:
                v_ms = self.val
            if self.err:
                return
            self.val = [v_m] + v_ms
            self.err = None
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._member_()
            if not self.err:
                v_m = self.val
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect(',')
            if self.err:
                return
            self.val = [v_m]
            self.err = None
        choice_1()
        if not self.err:
            return

        self.pos = p
        def choice_2():
            self._member_()
            if not self.err:
                v_m = self.val
            if self.err:
                return
            self.val = [v_m]
            self.err = None
        choice_2()

    def _member_(self):
        """ string:k ws ':' value:v -> [k, v]|ident:k ws ':' value:v -> [k, v] """
        p = self.pos
        def choice_0():
            self._string_()
            if not self.err:
                v_k = self.val
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect(':')
            if self.err:
                return
            self._value_()
            if not self.err:
                v_v = self.val
            if self.err:
                return
            self.val = [v_k, v_v]
            self.err = None
        choice_0()
        if not self.err:
            return

        self.pos = p
        def choice_1():
            self._ident_()
            if not self.err:
                v_k = self.val
            if self.err:
                return
            self._ws_()
            if self.err:
                return
            self._expect(':')
            if self.err:
                return
            self._value_()
            if not self.err:
                v_v = self.val
            if self.err:
                return
            self.val = [v_k, v_v]
            self.err = None
        choice_1()

    def _ident_(self):
        """ (letter|'$'|'_'):hd (letter|digit)*:tl -> ''.join([hd] + tl) """
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
        if not self.err:
            v_hd = self.val
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
        if not self.err:
            v_tl = self.val
        if self.err:
            return
        self.val = ''.join([v_hd] + v_tl)
        self.err = None

    def _number_(self):
        """ digit:hd digit*:tl -> ''.join([hd] + tl) """
        self._digit_()
        if not self.err:
            v_hd = self.val
        if self.err:
            return
        vs = []
        while not self.err:
            self._digit_()
            if not self.err:
                vs.append(self.val)
        self.val = vs
        self.err = None
        if not self.err:
            v_tl = self.val
        if self.err:
            return
        self.val = ''.join([v_hd] + v_tl)
        self.err = None
