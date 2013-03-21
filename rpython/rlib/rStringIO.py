from rpython.rlib.rstring import StringBuilder

AT_END = -1


class RStringIO(object):
    """RPython-level StringIO object.
    The fastest path through this code is for the case of a bunch of write()
    followed by getvalue().
    """
    _mixin_ = True        # for interp_stringio.py

    def __init__(self):
        # The real content is the join of the following data:
        #  * the list of characters self.bigbuffer;
        #  * each of the strings in self.strings.
        #
        self.strings = StringBuilder()
        self.bigbuffer = []
        self.pos = AT_END

    def close(self):
        self.strings = None
        self.bigbuffer = None

    def is_closed(self):
        return self.strings is None

    def getvalue(self):
        """If self.strings contains more than 1 string, join all the
        strings together.  Return the final single string."""
        if len(self.bigbuffer):
            self.copy_into_bigbuffer()
            return ''.join(self.bigbuffer)
        return self.strings.build()

    def getsize(self):
        result = len(self.bigbuffer)
        result += self.strings.getlength()
        return result

    def copy_into_bigbuffer(self):
        """Copy all the data into the list of characters self.bigbuffer."""
        if self.strings.getlength():
            self.bigbuffer += self.strings.build()
            self.strings = StringBuilder()

    def write(self, buffer):
        # Idea: for the common case of a sequence of write() followed
        # by only getvalue(), self.bigbuffer remains empty.  It is only
        # used to handle the more complicated cases.
        p = self.pos
        if p != AT_END:    # slow or semi-fast paths
            assert p >= 0
            endp = p + len(buffer)
            if len(self.bigbuffer) >= endp:
                # semi-fast path: the write is entirely inside self.bigbuffer
                for i in range(len(buffer)):
                    self.bigbuffer[p + i] = buffer[i]
                self.pos = endp
                return
            else:
                # slow path: collect all data into self.bigbuffer and
                # handle the various cases
                self.copy_into_bigbuffer()
                fitting = len(self.bigbuffer) - p
                if fitting > 0:
                    # the write starts before the end of the data
                    fitting = min(len(buffer), fitting)
                    for i in range(fitting):
                        self.bigbuffer[p+i] = buffer[i]
                    if len(buffer) > fitting:
                        # the write extends beyond the end of the data
                        self.bigbuffer += buffer[fitting:]
                        endp = AT_END
                    self.pos = endp
                    return
                else:
                    # the write starts at or beyond the end of the data
                    self.bigbuffer += '\x00' * (-fitting)
                    self.pos = AT_END      # fall-through to the fast path
        # Fast path.
        self.strings.append(buffer)

    def seek(self, position, mode=0):
        if mode == 1:
            if self.pos == AT_END:
                self.pos = self.getsize()
            position += self.pos
        elif mode == 2:
            if position == 0:
                self.pos = AT_END
                return
            position += self.getsize()
        if position < 0:
            position = 0
        self.pos = position

    def tell(self):
        if self.pos == AT_END:
            result = self.getsize()
        else:
            result = self.pos
        assert result >= 0
        return result

    def read(self, n=-1):
        p = self.pos
        if p == 0 and n < 0:
            self.pos = AT_END
            return self.getvalue()     # reading everything
        if p == AT_END:
            return ''
        assert p >= 0
        self.copy_into_bigbuffer()
        mysize = len(self.bigbuffer)
        count = mysize - p
        if n >= 0:
            count = min(n, count)
        if count <= 0:
            return ''
        if p == 0 and count == mysize:
            self.pos = AT_END
            return ''.join(self.bigbuffer)
        else:
            self.pos = p + count
            return ''.join(self.bigbuffer[p:p+count])

    def truncate(self, size):
        # NB. 'size' is mandatory.  This has the same un-Posix-y semantics
        # than CPython: it never grows the buffer, and it sets the current
        # position to the end.
        assert size >= 0
        if size > len(self.bigbuffer):
            self.copy_into_bigbuffer()
        else:
            # we can drop all extra strings
            if self.strings.getlength():
                self.strings = StringBuilder()
        if size < len(self.bigbuffer):
            del self.bigbuffer[size:]
        self.pos = AT_END
