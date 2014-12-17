
"""
rencode -- Web safe object pickling/unpickling.

The rencode module is a modified version of bencode from the
BitTorrent project.  For complex, heterogeneous data structures with
many small elements, r-encodings take up significantly less space than
b-encodings:

 >>> len(rencode.dumps({'a':0, 'b':[1,2], 'c':99}))
 13
 >>> len(bencode.bencode({'a':0, 'b':[1,2], 'c':99}))
 26

The rencode format is not standardized, and may change with different
rencode module versions, so you should check that you are using the
same rencode version throughout your project.
"""

__version__ = '1.0.0-ntk'
__all__ = ['dumps', 'loads', 'serializable']

from base64 import b64encode, b64decode

##TODO
# - Why the hell it encodes both tuples and lists to tuple?
#   Try loads(dumps([1,(2,3)]))
#   Grr
#
# - extend it! Support other basic types, f.e. Set()
#
##

# Original bencode module by Petru Paler, et al.
#
# Modifications by Daniele Tricoli:
#
#  - Added support for instances
#    Only registered instances can be serialized. An instance to be serialized
#    must provide a '_pack` method.
#    E.g.
#
#    class X(object):
#
#        def __init__(self, x):
#            self.x = x
#
#        def _pack(self)
#           return (self.x,) # a tuple
#
#  - Lists are decoded again as list
#
# Modifications by Connelly Barnes:
#
#  - Added support for floats (sent as 32-bit or 64-bit in network
#    order), bools, None.
#  - Allowed dict keys to be of any serializable type.
#  - Lists/tuples are always decoded as tuples (thus, tuples can be
#    used as dict keys).
#  - Embedded extra information in the 'typecodes' to save some space.
#  - Added a restriction on integer length, so that malicious hosts
#    cannot pass us large integers which take a long time to decode.
#
# Licensed by Bram Cohen under the "MIT license":
#
#  "Copyright (C) 2001-2002 Bram Cohen
#
#  Permission is hereby granted, free of charge, to any person
#  obtaining a copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction,
#  including without limitation the rights to use, copy, modify, merge,
#  publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#
#  The Software is provided "AS IS", without warranty of any kind,
#  express or implied, including but not limited to the warranties of
#  merchantability,  fitness for a particular purpose and
#  noninfringement. In no event shall the  authors or copyright holders
#  be liable for any claim, damages or other liability, whether in an
#  action of contract, tort or otherwise, arising from, out of or in
#  connection with the Software or the use or other dealings in the
#  Software."
#
# (The rencode module is licensed under the above license as well).
#

import inspect
import struct

from threading import Lock

from types import (StringType,
                   UnicodeType,
                   IntType,
                   LongType,
                   DictType,
                   ListType,
                   TupleType,
                   FloatType,
                   NoneType)

class AlreadyRegistered(Exception): pass

class NotRegistered(Exception):

    def __init__(self, class_):
        self.class_ = class_

    def __str__(self):
        return 'Class %s is not registered' % self.class_

class NotSerializable(Exception): pass

def add_class_name(func):

    if inspect.ismethod(func):
        def decorate(*args, **kargs):
            result = func(*args, **kargs)
            result = (str(func.im_class.__name__),) + result
            return result

        return decorate

class _SerializableRegistry(object):

    def __init__(self):
        self._registry = {}

    def __contains__(self, item):
        return item in self._registry

    def __getitem__(self, key):
        return self._registry[key]

    def register(self, cls):
        '''   '''
        if inspect.isclass(cls):

            if cls.__name__ in self._registry:
                msg = 'Class %s is already registered' % cls.__name__
                raise AlreadyRegistered(msg)

            try:
                if inspect.ismethod(cls._pack):
                    cls._pack = add_class_name(cls._pack)
                    self._registry[cls.__name__] = cls
            except AttributeError, err:
                raise NotSerializable(err)

    def unregister(self, cls):
        '''   '''
        if inspect.isclass(cls):

            if cls in self._registry:
                del self._registry[cls.__name__]
            else: 
                raise NotRegistered(cls.__name__)

serializable = _SerializableRegistry()

# Number of bits for serialized floats, either 32 or 64.
FLOAT_BITS = 32

# Maximum length of integer when written as base 10 string.
MAX_INT_LENGTH = 64

# The bencode 'typecodes' such as i, d, etc have been extended and
# relocated on the base-256 character set.
# Can't be used chr(48) to chr(57) because they are manually set
CHR_INSTANCE = chr(47) 
CHR_TUPLE = chr(58)
CHR_LIST = chr(59)
CHR_DICT = chr(60)
CHR_INT = chr(61)
CHR_INT1 = chr(62)
CHR_INT2 = chr(63)
CHR_INT4 = chr(64)
CHR_INT8 = chr(65)
CHR_FLOAT = chr(66)
CHR_TRUE = chr(67)
CHR_FALSE = chr(68)
CHR_NONE = chr(69)
CHR_TERM = chr(127)

# Positive integers with value embedded in typecode.
INT_POS_FIXED_START = 0
INT_POS_FIXED_COUNT = 32

# Dictionaries with length embedded in typecode.
DICT_FIXED_START = 102
DICT_FIXED_COUNT = 25

# Negative integers with value embedded in typecode.
INT_NEG_FIXED_START = 70
INT_NEG_FIXED_COUNT = 32

# Strings with length embedded in typecode.
STR_FIXED_START = 128
STR_FIXED_COUNT = 64

# Lists with length embedded in typecode.
LIST_FIXED_START = STR_FIXED_START + STR_FIXED_COUNT
LIST_FIXED_COUNT = 32

# Tuples with length embedded in typecode.
TUPLE_FIXED_START = LIST_FIXED_START + LIST_FIXED_COUNT
TUPLE_FIXED_COUNT = 32

def decode_int(x, f):
    f += 1
    newf = x.index(CHR_TERM, f)
    if newf - f >= MAX_INT_LENGTH:
        raise ValueError('overflow')
    try:
        n = int(x[f:newf])
    except (OverflowError, ValueError):
        n = long(x[f:newf])
    if x[f] == '-':
        if x[f + 1] == '0':
            raise ValueError
    elif x[f] == '0' and newf != f+1:
        raise ValueError
    return (n, newf+1)

def decode_intb(x, f):
    f += 1
    return (struct.unpack('!b', x[f:f+1])[0], f+1)

def decode_inth(x, f):
    f += 1
    return (struct.unpack('!h', x[f:f+2])[0], f+2)

def decode_intl(x, f):
    f += 1
    return (struct.unpack('!l', x[f:f+4])[0], f+4)

def decode_intq(x, f):
    f += 1
    return (struct.unpack('!q', x[f:f+8])[0], f+8)

def decode_float(x, f):
    f += 1
    if FLOAT_BITS == 32:
        n = struct.unpack('!f', x[f:f+4])[0]
        return (n, f+4)
    elif FLOAT_BITS == 64:
        n = struct.unpack('!d', x[f:f+8])[0]
        return (n, f+8)
    else:
        raise ValueError

def decode_string(x, f):
    colon = x.index(':', f)
    try:
        n = int(x[f:colon])
    except (OverflowError, ValueError):
        n = long(x[f:colon])
    if x[f] == '0' and colon != f+1:
        raise ValueError
    colon += 1
    return (b64decode(x[colon:colon+n]), colon+n)

def decode_list(x, f):
    r, f = [], f+1
    while x[f] != CHR_TERM:
        v, f = decode_func[x[f]](x, f)
        r.append(v)
    return (r, f + 1)

def decode_tuple(x, f):
    r, f = [], f+1
    while x[f] != CHR_TERM:
        v, f = decode_func[x[f]](x, f)
        r.append(v)
    return (tuple(r), f + 1)

def decode_dict(x, f):
    r, f = {}, f+1
    while x[f] != CHR_TERM:
        k, f = decode_func[x[f]](x, f)
        r[k], f = decode_func[x[f]](x, f)
    return (r, f + 1)

def decode_true(x, f):
  return (True, f+1)

def decode_false(x, f):
  return (False, f+1)

def decode_none(x, f):
  return (None, f+1)

def decode_instance(x, f):
    f += 1
    while x[f] != CHR_TERM:
        v, f = decode_func[x[f]](x, f)
    if v[0] in serializable:
        r = serializable[v[0]](*v[1:])
    else:
        raise NotRegistered(v[0])
    return (r, f+1)

decode_func = {}
decode_func['0'] = decode_string
decode_func['1'] = decode_string
decode_func['2'] = decode_string
decode_func['3'] = decode_string
decode_func['4'] = decode_string
decode_func['5'] = decode_string
decode_func['6'] = decode_string
decode_func['7'] = decode_string
decode_func['8'] = decode_string
decode_func['9'] = decode_string
decode_func[CHR_LIST ] = decode_list
decode_func[CHR_TUPLE] = decode_tuple
decode_func[CHR_DICT ] = decode_dict
decode_func[CHR_INT  ] = decode_int
decode_func[CHR_INT1 ] = decode_intb
decode_func[CHR_INT2 ] = decode_inth
decode_func[CHR_INT4 ] = decode_intl
decode_func[CHR_INT8 ] = decode_intq
decode_func[CHR_FLOAT] = decode_float
decode_func[CHR_TRUE ] = decode_true
decode_func[CHR_FALSE] = decode_false
decode_func[CHR_NONE ] = decode_none
decode_func[CHR_INSTANCE] = decode_instance

def make_fixed_length_string_decoders():
    def make_decoder(slen):
        def f_fixed_string(x, f):
            return (b64decode(x[f+1:f+1+slen]), f+1+slen)
        return f_fixed_string
    for i in range(STR_FIXED_COUNT):
        decode_func[chr(STR_FIXED_START+i)] = make_decoder(i)

make_fixed_length_string_decoders()

def make_fixed_length_list_decoders():
    def make_decoder(slen):
        def f_fixed_list(x, f):
            r, f = [], f+1
            for i in range(slen):
                v, f = decode_func[x[f]](x, f)
                r.append(v)
            return (r, f)
        return f_fixed_list
    for i in range(LIST_FIXED_COUNT):
        decode_func[chr(LIST_FIXED_START+i)] = make_decoder(i)

make_fixed_length_list_decoders()

def make_fixed_length_tuple_decoders():
    def make_decoder(slen):
        def f_fixed_tuple(x, f):
            r, f = [], f+1
            for i in range(slen):
                v, f = decode_func[x[f]](x, f)
                r.append(v)
            return (tuple(r), f)
        return f_fixed_tuple
    for i in range(TUPLE_FIXED_COUNT):
        decode_func[chr(TUPLE_FIXED_START+i)] = make_decoder(i)

make_fixed_length_tuple_decoders()

def make_fixed_length_int_decoders():
    def make_decoder(j):
        def f(x, f):
            return (j, f+1)
        return f
    for i in range(INT_POS_FIXED_COUNT):
        decode_func[chr(INT_POS_FIXED_START+i)] = make_decoder(i)
    for i in range(INT_NEG_FIXED_COUNT):
        decode_func[chr(INT_NEG_FIXED_START+i)] = make_decoder(-1-i)

make_fixed_length_int_decoders()

def make_fixed_length_dict_decoders():
    def make_decoder(slen):
        def f(x, f):
            r, f = {}, f+1
            for j in range(slen):
                k, f = decode_func[x[f]](x, f)
                r[k], f = decode_func[x[f]](x, f)
            return (r, f)
        return f
    for i in range(DICT_FIXED_COUNT):
        decode_func[chr(DICT_FIXED_START+i)] = make_decoder(i)

make_fixed_length_dict_decoders()

def loads(x):
    try:
        r, l = decode_func[x[0]](x, 0)
    except (IndexError, KeyError):
        raise 
    if l != len(x):
        raise ValueError
    return r

def encode_int(x, r):
    if 0 <= x < INT_POS_FIXED_COUNT:
        r.append(chr(INT_POS_FIXED_START+x))
    elif -INT_NEG_FIXED_COUNT <= x < 0:
        r.append(chr(INT_NEG_FIXED_START-1-x))
    elif -128 <= x < 128:
        r.extend((CHR_INT1, struct.pack('!b', x)))
    elif -32768 <= x < 32768:
        r.extend((CHR_INT2, struct.pack('!h', x)))
    elif -2147483648 <= x < 2147483648:
        r.extend((CHR_INT4, struct.pack('!l', x)))
    elif -9223372036854775808 <= x < 9223372036854775808:
        r.extend((CHR_INT8, struct.pack('!q', x)))
    else:
        s = str(x)
        if len(s) >= MAX_INT_LENGTH:
            raise ValueError('overflow')
        r.extend((CHR_INT, s, CHR_TERM))

def encode_float(x, r):
    if FLOAT_BITS == 32:
        r.extend((CHR_FLOAT, struct.pack('!f', x)))
    elif FLOAT_BITS == 64:
        r.extend((CHR_FLOAT, struct.pack('!d', x)))
    else:
        raise ValueError

def encode_bool(x, r):
    r.extend({False: CHR_FALSE, True: CHR_TRUE}[bool(x)])

def encode_none(x, r):
    r.extend(CHR_NONE)

def encode_string(x, r):
    x = b64encode(x)
    if len(x) < STR_FIXED_COUNT:
        r.extend((chr(STR_FIXED_START + len(x)), x))
    else:
        r.extend((str(len(x)), ':', x))

def encode_list(x, r):
    if len(x) < LIST_FIXED_COUNT:
        r.append(chr(LIST_FIXED_START + len(x)))
        for i in x:
            encode_func.get(type(i), encode_instance)(i, r)
    else:
        r.append(CHR_LIST)
        for i in x:
            encode_func.get(type(i), encode_instance)(i, r)
        r.append(CHR_TERM)


def encode_tuple(x, r):
    if len(x) < TUPLE_FIXED_COUNT:
        r.append(chr(TUPLE_FIXED_START + len(x)))
        for i in x:
            encode_func.get(type(i), encode_instance)(i, r)
    else:
        r.append(CHR_TUPLE)
        for i in x:
            encode_func.get(type(i), encode_instance)(i, r)
        r.append(CHR_TERM)

def encode_dict(x,r):
    if len(x) < DICT_FIXED_COUNT:
        r.append(chr(DICT_FIXED_START + len(x)))
        for k, v in x.items():
            encode_func[type(k)](k, r)
            encode_func[type(v)](v, r)
    else:
        r.append(CHR_DICT)
        for k, v in x.items():
            encode_func[type(k)](k, r)
            encode_func[type(v)](v, r)
        r.append(CHR_TERM)

encode_func = {}
encode_func[IntType] = encode_int
encode_func[LongType] = encode_int
encode_func[FloatType] = encode_float
encode_func[StringType] = encode_string
encode_func[UnicodeType] = encode_string
encode_func[ListType] = encode_list
encode_func[TupleType] = encode_tuple
encode_func[DictType] = encode_dict
encode_func[NoneType] = encode_none

try:
    from types import BooleanType
    encode_func[BooleanType] = encode_bool
except ImportError:
    pass

def encode_instance(x, r):
    if hasattr(x, '_pack'):
        if x.__class__.__name__ in serializable:
            # Calling the class of instance `x' passing it to the
            # unbound method
            result = serializable[x.__class__.__name__]._pack(x)
            r.append(CHR_INSTANCE)
            encode_func[type(result)](result, r)
            r.append(CHR_TERM)
        else:
            raise NotRegistered(x.__class__.__name__)

lock = Lock()

def dumps(x):
    lock.acquire()
    r = []
    encode_func.get(type(x), encode_instance)(x, r)
    lock.release()
    return ''.join(r)

def test():
    f1 = struct.unpack('!f', struct.pack('!f', 25.5))[0]
    f2 = struct.unpack('!f', struct.pack('!f', 29.3))[0]
    f3 = struct.unpack('!f', struct.pack('!f', -0.6))[0]
    L = (({'a':15, 'bb':f1, 'ccc':f2, '':(f3,(),False,True,'')},('a',10**20),tuple(range(-100000,100000)),'b'*31,'b'*62,'b'*64,2**30,2**33,2**62,2**64,2**30,2**33,2**62,2**64,False,False, True, -1, 2, 0),)
    assert loads(dumps(L)) == L
    d = dict(zip(range(-100000,100000),range(-100000,100000)))
    d.update({'a':20, 20:40, 40:41, f1:f2, f2:f3, f3:False, False:True, True:False})
    L = (d, {}, {5:6}, {7:7,True:8}, {9:10, 22:39, 49:50, 44: ''})
    assert loads(dumps(L)) == L
    L = ('', 'a'*10, 'a'*100, 'a'*1000, 'a'*10000, 'a'*100000, 'a'*1000000, 'a'*10000000)
    assert loads(dumps(L)) == L
    L = tuple([dict(zip(range(n),range(n))) for n in range(100)]) + ('b',)
    assert loads(dumps(L)) == L
    L = tuple([dict(zip(range(n),range(-n,0))) for n in range(100)]) + ('b',)
    assert loads(dumps(L)) == L
    L = tuple([tuple(range(n)) for n in range(100)]) + ('b',)
    assert loads(dumps(L)) == L
    L = tuple(['a'*n for n in range(100)]) + ('b',)
    assert loads(dumps(L)) == L
    L = tuple(['a'*n for n in range(100)]) + (None,True,None)
    assert loads(dumps(L)) == L
    L = list(['a'*n for n in range(100)]) + [None,True,None]
    assert loads(dumps(L)) == L
    assert loads(dumps(None)) == None
    assert loads(dumps({None:None})) == {None:None}

    class A(object):
        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c

        def _pack(self):
            return (self.a, self.b, self.c)

    serializable.register(A)

    instance = [A(1,2,3), 1, A(1,3,4), 'sss']
    print loads(dumps(instance))

if __name__ == '__main__':
  test()
