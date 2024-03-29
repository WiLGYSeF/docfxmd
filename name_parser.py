from collections import deque


TOKEN_STR = 'str'
TOKEN_DOT = '.'
TOKEN_LPAREN = '('
TOKEN_RPAREN = ')'
TOKEN_LBRACKET = '['
TOKEN_RBRACKET = ']'
TOKEN_LBRACE = '{'
TOKEN_RBRACE = '}'
TOKEN_COMMA = ','
TOKEN_LT = '<'
TOKEN_GT = '>'

def tokenize(string):
    tokens = []
    idx = 0

    while idx < len(string):
        char = string[idx]
        if char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_':
            i = idx
            while i < len(string):
                cur = string[i]
                if cur not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_`':
                    break
                i += 1

            name = string[idx:i]
            idx = i - 1
            tokens.append( (TOKEN_STR, name) )
        elif char == '.':
            tokens.append( (TOKEN_DOT, None) )
        elif char == '(':
            tokens.append( (TOKEN_LPAREN, None) )
        elif char == ')':
            tokens.append( (TOKEN_RPAREN, None) )
        elif char == '[':
            tokens.append( (TOKEN_LBRACKET, None) )
        elif char == ']':
            tokens.append( (TOKEN_RBRACKET, None) )
        elif char == ',':
            tokens.append( (TOKEN_COMMA, None) )
        elif char == '<':
            tokens.append( (TOKEN_LT, None) )
        elif char == '>':
            tokens.append( (TOKEN_GT, None) )
        elif char == '{':
            tokens.append( (TOKEN_LBRACE, None) )
        elif char == '}':
            tokens.append( (TOKEN_RBRACE, None) )
        elif char == ' ':
            pass
        else:
            raise ValueError('cannot parse name: ' + string)
        idx += 1

    return tokens

def tostring(ident, **kwargs):
    include_containers = kwargs.get('include_containers', True)
    prepare_sub_ident = kwargs.get('prepare_sub_ident')

    result = ''

    def tostr_ident(val):
        result = tostring(val, **kwargs)
        if prepare_sub_ident is not None:
            return prepare_sub_ident(result, val)
        return result

    for i in range(len(ident)): #pylint: disable=consider-using-enumerate
        segment_base, container = ident[i]
        result += segment_base

        if container is not None and include_containers:
            surround, idlist = container
            result += surround[0] + ', '.join(map(tostr_ident, idlist)) + surround[1]

        if i != len(ident) - 1:
            result += '.'

    return result

"""
idlist = identifier , { COMMA , identifier } ;
identifier = segment , { DOT , segment } ;
segment = STR , [ container ] ;
container = LPAREN , idlist , RPAREN
          | LBRACKET , [ idlist ] , RBRACKET
          | LT , idlist , GT
          | LBRACE , ( idlist | LBRACE , STR , RBRACE ) , RBRACE
          ;
"""

def parse(string):
    tokens = deque(tokenize(string))

    idlist = _idlist(tokens)
    if len(tokens) != 0:
        raise ValueError()
    return idlist

def _idlist(queue):
    identifiers = []
    identifier = _identifier(queue)
    if identifier is None:
        return None
    identifiers.append(identifier)

    while len(queue) != 0:
        token = queue.popleft()
        if token[0] != TOKEN_COMMA:
            queue.appendleft(token)
            break

        identifier = _identifier(queue)
        if identifier is None:
            raise ValueError()
        identifiers.append(identifier)

    return identifiers

def _identifier(queue):
    segments = []
    segment = _segment(queue)
    if segment is None:
        return None
    segments.append(segment)

    while len(queue) != 0:
        token = queue.popleft()
        if token[0] != TOKEN_DOT:
            queue.appendleft(token)
            break

        segment = _segment(queue)
        if segment is None:
            raise ValueError()
        segments.append(segment)

    return segments

def _segment(queue):
    if len(queue) == 0:
        return None

    token = queue.popleft()
    if token[0] != TOKEN_STR:
        queue.appendleft(token)
        return None
    return (token[1], _container(queue))

def _container(queue):
    if len(queue) == 0:
        return None

    token = queue.popleft()

    def handle(close_token, wrapper, on_none=None):
        idlist = _idlist(queue)
        if idlist is None:
            if on_none is None:
                raise ValueError()
            idlist = on_none()

        if len(queue) == 0:
            raise ValueError()
        token = queue.popleft()
        if token[0] != close_token:
            raise ValueError()
        return (wrapper, idlist)

    if token[0] == TOKEN_LPAREN:
        return handle(TOKEN_RPAREN, '()')
    if token[0] == TOKEN_LBRACKET:
        return handle(TOKEN_RBRACKET, '[]', on_none=lambda: [])
    if token[0] == TOKEN_LT:
        return handle(TOKEN_GT, '<>')

    def lbrace_or_idlist():
        token = queue.popleft()
        if token[0] != TOKEN_LBRACE:
            raise ValueError()

        token = queue.popleft()
        if token[0] != TOKEN_STR:
            raise ValueError()
        value = token[1]

        token = queue.popleft()
        if token[0] != TOKEN_RBRACE:
            raise ValueError()

        return [[(value, None)]]

    if token[0] == TOKEN_LBRACE:
        return handle(TOKEN_RBRACE, '<>', on_none=lbrace_or_idlist)

    queue.appendleft(token)
    return None
