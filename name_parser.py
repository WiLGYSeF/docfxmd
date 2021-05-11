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
        else:
            raise ValueError('cannot parse name: ' + string)
        idx += 1

    return tokens

"""
idlist = identifier , { COMMA , identifier} ;
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
        print('=' * 16, idlist, tokens)
    else:
        #print(idlist)
        pass

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

    if token[0] == TOKEN_LPAREN:
        idlist = _idlist(queue)
        if idlist is None:
            raise ValueError()

        token = queue.popleft()
        if token[0] != TOKEN_RPAREN:
            raise ValueError()
        return idlist

    if token[0] == TOKEN_LBRACKET:
        idlist = _idlist(queue)
        token = queue.popleft()
        if token[0] != TOKEN_RBRACKET:
            raise ValueError()
        return idlist

    if token[0] == TOKEN_LT:
        idlist = _idlist(queue)
        if idlist is None:
            raise ValueError()

        token = queue.popleft()
        if token[0] != TOKEN_GT:
            raise ValueError()
        return idlist

    if token[0] == TOKEN_LBRACE:
        idlist = _idlist(queue)
        if idlist is None:
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

            idlist = '<%s>' % value

        token = queue.popleft()
        if token[0] != TOKEN_RBRACE:
            raise ValueError()
        return idlist

    queue.appendleft(token)
    return None
