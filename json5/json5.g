grammar      = sp value sp end,

sp           = ws*,

ws           = ' ' | '\t' | comment | eol,

eol          = '\r\n' | '\r' | '\n',

comment      = '//' ~eol* eol
             | '/*' ~('*/')* '*/',

value        = 'null'
             | 'true'
             | 'false'
             | object
             | array
             | string
             | number,

object       = '{' ws member_list ws '}'
             | '{' ws '}',

array        = '[' ws element_list ws ']'
             | '[' ws ']',

string       = squote (~squote qchar*)* squote
             | dquote (~dquote qchar*)* dquote,

squote       = '\'',

dquote       = '"',

qchar        = '\\\''
             | '\\"'
             | anything,

element_list = value ws ',' ws element_list
             | value ws ','
             | value,

member_list  = member ws ',' ws member_list
             | member ws ','
             | member,

member       = string ws ':' value
             | ident ws ':' value,

ident        = (letter | '$' | '_') (letter|digit)*,

number       = digit digit*,

