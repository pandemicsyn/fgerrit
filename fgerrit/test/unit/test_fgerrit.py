#!/usr/bin/env python

import unittest

import fgerrit


class TestFGerrit(unittest.TestCase):

    def test_arg_encode(self):
        self.assertEquals(fgerrit.arg_encode('test'), "'test'")
        self.assertEquals(fgerrit.arg_encode('"test"'), '\'"test"\'')
        self.assertEquals(fgerrit.arg_encode("'test'"), '"\'"\'test\'"\'"')
        self.assertEquals(fgerrit.arg_encode('"it\'s"'), '\'"it\'"\'"\'s"\'')


if __name__ == '__main__':
    unittest.main()
