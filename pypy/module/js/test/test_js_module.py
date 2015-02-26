from __future__ import with_statement

import os

import py
try:
    import PyV8
except ImportError:
    py.test.skip("PyV8 module not available")

from pypy.interpreter.gateway import unwrap_spec, interp2app


class AppTestJS(object):

    spaceconfig = {
        "usemodules": ["js"]
    }

    def test_js_string(self):
        import js
        s = js.String("hello world")
        assert str(s) == "hello world"
        assert len(s) == 11

    def test_js_number(self):
        import js
        s = js.Number(42)
        assert s == 42
        assert str(s) == "42"
        assert s + 1 == 43
        assert s * 2 == 84
        assert s + js.Number(17) == js.Number(59)

    def test_js_object(self):
        import js
        s = js.Object()
        assert str(s) == "[object Object]"

    def test_js_truthiness(self):
        import js
        assert not js.null
        assert not js.undefined
        assert not js.false
        assert not js.Number(0)
        assert not js.String("")
        assert js.true
        assert js.Number(12)
        assert js.String("xyz")

    def test_js_array_access(self):
        import js
        a = js.eval("[1,2,3]")
        assert a[0] == 1
        assert a[1] == 2
        assert a[2] == 3
        assert a.length == len(a) == 3
