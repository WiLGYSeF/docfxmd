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


class ConvertTest(unittest.TestCase):
    def test_replace_strings(self):
        for entry in REPLACE_STRINGS:
            self.assertEqual(convert.replace_strings(entry[STR], entry[REPL]), entry[VALUE])
