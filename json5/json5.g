grammar      = ws value:v ws end                    -> v,

ws           = (' ' | '\t' | comment | eol)*,

eol          = '\r\n' | '\r' | '\n',

comment      = '//' (~(eol|end) anything)* (end|eol)
             | '/*' (~'*/' anything)* '*/',

value        = 'null'                               -> 'None'
             | 'true'                               -> 'True'
             | 'false'                              -> 'False'
             | object:v                             -> ['object', v]
             | array:v                              -> ['array', v]
             | string:v                             -> ['string', v]
             | num_literal:v                        -> ['number', v],

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

member       = string:k ws ':' ws value:v           -> [k, v]
             | ident:k ws ':' ws value:v            -> [k, v],

ident        = ident_start:hd (letter|digit)*:tl    -> ''.join([hd] + tl),

ident_start  = (letter|'$'|'_'):i                   -> i,

num_literal  = dec_literal:d ~(ident_start|digit)   -> d
             | hex_literal,
             
dec_literal  = dec_int_lit:d frac:f exp:e           -> d + '.' + f + e
             | dec_int_lit:d frac:f                 -> d + '.' + f
             | dec_int_lit:d exp:e                  -> d + e
             | dec_int_lit:d                        -> d
             | frac:f exp:e                         -> f + e
             | frac:f                               -> f,

dec_int_lit  = '0' ~digit                           -> '0'
             | nonzerodigit:n digit*:ds             -> n + ''.join(ds),

nonzerodigit = ('1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'|'9'),

hex_literal  = ('0x'|'0X') hex_digit:h1 hex_digit:h2  -> '0x' + h1 + h2
             | ('0x'|'0X') hex_digit:h                -> '0x' + h,


hex_digit    = ('a'|'b'|'c'|'d'|'e'|'f'|
                'A'|'B'|'C'|'D'|'E'|'F'|
                digit),

frac         = '.' digit*:ds                        -> ''.join(ds),

exp          = ('e'|'E') ('+'|'-'):s digit*:ds      -> 'e' + s + ''.join(ds)
             | ('e'|'E') digit*:ds                  -> 'e' + ''.join(ds),
