import unittest

import name_parser
from name_parser import TOKEN_STR, TOKEN_DOT, TOKEN_LPAREN, TOKEN_RPAREN, TOKEN_LBRACKET, TOKEN_RBRACKET, TOKEN_LBRACE, TOKEN_RBRACE, TOKEN_COMMA, TOKEN_LT, TOKEN_GT


TOKENIZE = {
    'abcdef': [(TOKEN_STR, 'abcdef')],
    '123abc': None,
    '=': None,
    'abc (def, [_123])': [
        (TOKEN_STR, 'abc'),
        (TOKEN_LPAREN, None),
        (TOKEN_STR, 'def'),
        (TOKEN_COMMA, None),
        (TOKEN_LBRACKET, None),
        (TOKEN_STR, '_123'),
        (TOKEN_RBRACKET, None),
        (TOKEN_RPAREN, None),
    ],
    '<.> {yote}': [
        (TOKEN_LT, None),
        (TOKEN_DOT, None),
        (TOKEN_GT, None),
        (TOKEN_LBRACE, None),
        (TOKEN_STR, 'yote'),
        (TOKEN_RBRACE, None),
    ]
}

PARSE = {
    'abcdef': [[('abcdef', None)]],
    '123abc': None,
    '=': None,
    'abc(': None,
    'abc(a': None,
    'abc(a.b': None,
    'abc.': None,
    'abc.def(zz<yy.x>)': [[
        ('abc', None),
        ('def', ('()', [
            [('zz', ('<>', [[
                ('yy', None),
                ('x', None)
            ]]))]
        ]))
    ]],
    'string[]': [[
        ('string', ('[]', []))
    ]],
}


class NameParserTest(unittest.TestCase):
    def test_tokenize(self):
        for key, val in TOKENIZE.items():
            if val is None:
                self.assertRaises(ValueError, name_parser.tokenize, key)
            else:
                self.assertListEqual(name_parser.tokenize(key), val)

    def test_parse(self):
        for key, val in PARSE.items():
            if val is None:
                self.assertRaises(ValueError, name_parser.parse, key)
            else:
                self.assertListEqual(name_parser.parse(key), val)
