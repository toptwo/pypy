"""
Plain Python definition of the builtin functions related to run-time
program introspection.
"""

import sys

from __pypy__ import lookup_special

def _caller_locals(): 
    return sys._getframe(0).f_locals 

def vars(*obj):
    """Return a dictionary of all the attributes currently bound in obj.  If
    called with no argument, return the variables bound in local scope."""

    if len(obj) == 0:
        return _caller_locals()
    elif len(obj) != 1:
        raise TypeError("vars() takes at most 1 argument.")
    else:
        try:
            return obj[0].__dict__
        except AttributeError:
            raise TypeError("vars() argument must have __dict__ attribute")

def dir(*args):
    """dir([object]) -> list of strings

    Return an alphabetized list of names comprising (some of) the attributes
    of the given object, and of attributes reachable from it:

    No argument:  the names in the current scope.
    Module object:  the module attributes.
    Type or class object:  its attributes, and recursively the attributes of
        its bases.
    Otherwise:  its attributes, its class's attributes, and recursively the
        attributes of its class's base classes.
    """
    if len(args) > 1:
        raise TypeError("dir expected at most 1 arguments, got %d"
                        % len(args))
    if len(args) == 0:
        local_names = list(_caller_locals().keys()) # 2 stackframes away
        local_names.sort()
        return local_names

    import types

    obj = args[0]

    dir_meth = lookup_special(obj, "__dir__")
    if dir_meth is not None:
        result = dir_meth()
        if not isinstance(result, list):
            result = list(result)  # Will throw TypeError if not iterable
        result.sort()
        return result
    elif isinstance(obj, types.ModuleType):
        try:
            result = list(obj.__dict__)
            result.sort()
            return result
        except AttributeError:
            return []

    elif isinstance(obj, type):
        #Don't look at __class__, as metaclass methods would be confusing.
        result = list(_classdir(obj).keys())
        result.sort()
        return result

    else: #(regular item)
        Dict = {}
        try:
            if isinstance(obj.__dict__, dict):
                Dict.update(obj.__dict__)
        except AttributeError:
            pass
        try:
            Dict.update(_classdir(obj.__class__))
        except AttributeError:
            pass
        result = list(Dict.keys())
        result.sort()
        return result

def _classdir(klass):
    """Return a dict of the accessible attributes of class/type klass.

    This includes all attributes of klass and all of the
    base classes recursively.

    The values of this dict have no meaning - only the keys have
    meaning.  
    """
    Dict = {}
    try:
        Dict.update(klass.__dict__)
    except AttributeError: pass 
    try:
        # XXX - Use of .__mro__ would be suggested, if the existance
        #   of that attribute could be guarranted.
        bases = klass.__bases__
    except AttributeError: pass
    else:
        try:
            #Note that since we are only interested in the keys,
            #  the order we merge classes is unimportant
            for base in bases:
                Dict.update(_classdir(base))
        except TypeError: pass
    return Dict
