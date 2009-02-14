from pypy.conftest import gettestobjspace

import sys

class AppTestLocaleTrivia:
    def setup_class(cls):
        cls.space = gettestobjspace(usemodules=['_locale'])

        #cls.w_locale = cls.space.appexec([], """():
        #    import locale
        #    return locale""")

    def test_import(self):
        import _locale
        assert _locale

        import locale
        assert locale

    def test_contants(self):
        _CONSTANTS = (
            'LC_CTYPE',
            'LC_NUMERIC',
            'LC_TIME',
            'LC_COLLATE',
            'LC_MONETARY',
            'LC_MESSAGES',
            'LC_ALL',
            'LC_PAPER',
            'LC_NAME',
            'LC_ADDRESS',
            'LC_TELEPHONE',
            'LC_MEASUREMENT',
            'LC_IDENTIFICATION',
        )

        import _locale
        
        for constant in _CONSTANTS:
            assert hasattr(_locale, constant)

    def test_setlocale(self):
        import _locale

        raises(TypeError, _locale.setlocale, "", "en_US")
        raises(TypeError, _locale.setlocale, _locale.LC_ALL, 6)
        raises(_locale.Error, _locale.setlocale, 123456, "en_US")

        assert _locale.setlocale(_locale.LC_ALL, None)
        assert _locale.setlocale(_locale.LC_ALL)

    def test_string_ulcase(self):
        import _locale, string

        lcase = "abcdefghijklmnopqrstuvwxyz"
        ucase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        _locale.setlocale(_locale.LC_ALL, "en_US.UTF-8")
        assert string.lowercase == lcase
        assert string.uppercase == ucase

        _locale.setlocale(_locale.LC_ALL, "en_US")
        assert string.lowercase != lcase
        assert string.uppercase != ucase

    def test_localeconv(self):
        import _locale

        lconv_c = {
            "currency_symbol": "",
            "decimal_point": ".",
            "frac_digits": 127,
            "grouping": [],
            "int_curr_symbol": "",
            "int_frac_digits": 127,
            "mon_decimal_point": "",
            "mon_grouping": [],
            "mon_thousands_sep": "",
            "n_cs_precedes": 127,
            "n_sep_by_space": 127,
            "n_sign_posn": 127,
            "negative_sign": "",
            "p_cs_precedes": 127,
            "p_sep_by_space": 127,
            "p_sign_posn": 127,
            "positive_sign": "",
            "thousands_sep": "" }

        _locale.setlocale(_locale.LC_ALL, "C")

        lconv = _locale.localeconv()
        for k, v in lconv_c.items():
            assert lconv[k] == v

    def test_strcoll(self):
        import _locale

        _locale.setlocale(_locale.LC_ALL, "pl_PL.UTF-8")
        assert _locale.strcoll("a", "b") < 0
        assert _locale.strcoll('\xc4\x85', "b") < 0

        assert _locale.strcoll('\xc4\x87', "b") > 0
        assert _locale.strcoll("c", "b") > 0

        assert _locale.strcoll("b", "b") == 0

        raises(TypeError, _locale.strcoll, 1, "b")
        raises(TypeError, _locale.strcoll, "b", 1)

    def test_strcoll_unicode(self):
        skip("not implemented, rffi.unicode2wcharp needed")
        import _locale

        _locale.setlocale(_locale.LC_ALL, "pl_PL.UTF-8")
        assert _locale.strcoll(u"b", u"b") == 0
        assert _locale.strcoll(u'\xc4\x85', "b") < 0
        assert _locale.strcoll(u'\xc4\x87', "b") > 0

        raises(TypeError, _locale.strcoll, 1, u"b")
        raises(TypeError, _locale.strcoll, u"b", 1)

    def test_str_float(self):
        import _locale
        import locale

        _locale.setlocale(_locale.LC_ALL, "en_US")
        assert locale.str(1.1) == '1.1'
        _locale.setlocale(_locale.LC_ALL, "pl_PL")
        assert locale.str(1.1) == '1,1'

