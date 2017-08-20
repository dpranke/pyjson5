grammar      = sp value:v sp end                      -> v

sp           = ws*

ws           = ' ' | '\t' | eol | comment

eol          = '\r\n' | '\r' | '\n'

comment      = '//' (~(eol | end) anything)* (end |   eol)
             | '/*' (~'*/' anything)* '*/'

value        = 'null'                                 -> 'None'
             | 'true'                                 -> 'True'
             | 'false'                                -> 'False'
             | object:v                               -> ['object', v]
             | array:v                                -> ['array', v]
             | string:v                               -> ['string', v]
             | num_literal:v                          -> ['number', v]

object       = '{' sp member_list:v sp '}'            -> v
             | '{' sp '}'                             -> []

array        = '[' sp element_list:v sp ']'           -> v
             | '[' sp ']'                             -> []

string       = squote sqchars:s squote                -> s
             | dquote dqchars:s dquote                -> s

sqchars      = (~(squote | eol) sqchar)*:cs           -> ''.join(cs)

sqchar       = bslash squote                          -> '\x5C\x27'
             | bslash '\n'                            -> '\n'
             | bslash '\r\n'                          -> '\r\n'
             | bslash '\r'                            -> '\r'
             | bslash bslash                          -> '\x5C\x5C'
             | anything

dqchars      = (~(dquote | eol) dqchar)*:cs           -> ''.join(cs)

dqchar       = bslash dquote                          -> '\x5C\x22'
             | bslash '\n'                            -> '\n'
             | bslash '\r\n'                          -> '\r\n'
             | bslash '\r'                            -> '\r'
             | bslash bslash                          -> '\x5C\x5C'
             | anything

bslash       = '\x5C'

squote       = '\x27'

dquote       = '\x22'

element_list = value:v sp ',' sp element_list:vs      -> [v] + vs
             | value:v sp ','                         -> [v]
             | value:v                                -> [v]
 
member_list  = member:m sp ',' sp member_list:ms      -> [m] + ms
             | member:m sp ','                        -> [m]
             | member:m                               -> [m]

member       = string:k sp ':' sp value:v             -> [k, v]
             | ident:k sp ':' sp value:v              -> [k, v]

ident        = id_start:hd id_continue*:tl            -> ''.join([hd] + tl)

id_start     = letter | '$' | '_' 
id_continue  = id_start | digit

num_literal  = '-' num_literal:n                      -> '-' + n
             | '+'? dec_literal:d ~(id_start | digit) -> d
             | hex_literal
             | 'Infinity'
             | 'NaN'
             
dec_literal  = dec_int_lit:d frac:f exp:e             -> d + f + e
             | dec_int_lit:d frac:f                   -> d + f
             | dec_int_lit:d exp:e                    -> d + e
             | dec_int_lit:d                          -> d
             | frac:f exp:e                           -> f + e
             | frac:f                                 -> f

dec_int_lit  = '0' ~digit                             -> '0'
             | nonzerodigit:n digit*:ds               -> n + ''.join(ds)

nonzerodigit = '1'..'9'

hex_literal  = ('0x' | '0X') hex_digit+:hs            -> '0x' + ''.join(hs)

hex_digit    = 'a'..'f' | 'A'..'F' | digit

frac         = '.' digit*:ds                        -> '.' + ''.join(ds)

exp          = ('e' | 'E') ('+' | '-'):s digit*:ds  -> 'e' + s + ''.join(ds)
             | ('e' | 'E') digit*:ds                -> 'e' + ''.join(ds)
