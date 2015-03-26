grammar      = sp value:v sp end                    -> v,

sp           = ws*,

ws           = ' ' | '\t' | comment | eol,

eol          = '\r\n' | '\r' | '\n',

comment      = '//' ~eol* eol
             | '/*' ~('*/')* '*/',

value        = 'null'                               -> 'None'
             | 'true'                               -> 'True'
             | 'false'                              -> 'False'
             | object:v                             -> ['object', v]
             | array:v                              -> ['array', v]
             | string:v                             -> ['string', v]
             | number:v                             -> ['number', v],

object       = '{' ws member_list:v ws '}'          -> v
             | '{' ws '}'                           -> [],

array        = '[' ws element_list:v ws ']'         -> v
             | '[' ws ']'                           -> [],

string       = squote (~squote qchar)*:qs squote    -> ''.join(qs)
             | dquote (~dquote qchar)*:qs dquote    -> ''.join(qs),

squote       = '\'',

dquote       = '"',

qchar        = '\\\''
             | '\\"'
             | anything,

element_list = value:v ws ',' ws element_list:vs    -> [v] + vs
             | value:v ws ','                       -> [v]
             | value:v                              -> [v],

member_list  = member:m ws ',' ws member_list:ms    -> [m] + ms
             | member:m ws ','                      -> [m]
             | member:m                             -> [m],

member       = string:k ws ':' value:v              -> [k, v]
             | ident:k ws ':' value:v               -> [k, v],

ident        = (letter|'$'|'_'):hd (letter|digit)*:tl -> ''.join([hd] + tl),

number       = digit:hd digit*:tl                     -> ''.join([hd] + tl),
