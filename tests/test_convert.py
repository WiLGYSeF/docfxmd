import unittest

import convert

STR = 'str'
REPL = 'repl'
VALUE = 'value'

REPLACE_STRINGS = [
    {
        STR: 'a.p.p.l.e',
        REPL: {
            '.': '',
            'l': '',
            'pp': 'p',
        },
        VALUE: 'ape'
    },
]

NEWLINE_TO_BR = {
    'abc\n123': 'abc<br/>123'
}


class ConvertTest(unittest.TestCase):
    def test_replace_strings(self):
        for entry in REPLACE_STRINGS:
            self.assertEqual(convert.replace_strings(entry[STR], entry[REPL]), entry[VALUE])

    def test_newline_to_br(self):
        for key, val in NEWLINE_TO_BR.items():
            self.assertEqual(convert.newline_to_br(key), val)
