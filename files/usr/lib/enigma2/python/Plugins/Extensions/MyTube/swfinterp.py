from __future__ import unicode_literals
import collections
import io
import struct
import zlib

def _extract_tags(file_contents):
    if file_contents[1:3] != 'WS':
        print u'[SWFInterpreter] Not an SWF file; header is %r' % file_contents[:3]
    if file_contents[:1] == 'C':
        content = zlib.decompress(file_contents[8:])
    else:
        raise NotImplementedError(u'Unsupported compression format %r' % file_contents[:1])
    framesize_nbits = struct.unpack(u'!B', content[:1])[0] >> 3
    framesize_len = (5 + 4 * framesize_nbits + 7) // 8
    pos = framesize_len + 2 + 2
    while pos < len(content):
        header16 = struct.unpack(u'<H', content[pos:pos + 2])[0]
        pos += 2
        tag_code = header16 >> 6
        tag_len = header16 & 63
        if tag_len == 63:
            tag_len = struct.unpack(u'<I', content[pos:pos + 4])[0]
            pos += 4
        yield (tag_code, content[pos:pos + tag_len])
        pos += tag_len


class _AVMClass_Object(object):

    def __init__(self, avm_class):
        self.avm_class = avm_class

    def __repr__(self):
        return u'%s#%x' % (self.avm_class.name, id(self))


class _ScopeDict(dict):

    def __init__(self, avm_class):
        super(_ScopeDict, self).__init__()
        self.avm_class = avm_class

    def __repr__(self):
        return u'%s__Scope(%s)' % (self.avm_class.name, super(_ScopeDict, self).__repr__())


class _AVMClass(object):

    def __init__(self, name_idx, name, static_properties = None):
        self.name_idx = name_idx
        self.name = name
        self.method_names = {}
        self.method_idxs = {}
        self.methods = {}
        self.method_pyfunctions = {}
        self.static_properties = static_properties if static_properties else {}
        self.variables = _ScopeDict(self)
        self.constants = {}

    def make_object(self):
        return _AVMClass_Object(self)

    def __repr__(self):
        return u'_AVMClass(%s)' % self.name

    def register_methods(self, methods):
        self.method_names.update(methods.items())
        self.method_idxs.update(dict(((idx, name) for name, idx in methods.items())))


class _Multiname(object):

    def __init__(self, kind):
        self.kind = kind

    def __repr__(self):
        return u'[MULTINAME kind: 0x%x]' % self.kind


def _read_int(reader):
    res = 0
    shift = 0
    for _ in range(5):
        buf = reader.read(1)
        b = struct.unpack(u'<B', buf)[0]
        res = res | (b & 127) << shift
        if b & 128 == 0:
            break
        shift += 7

    return res


def _u30(reader):
    res = _read_int(reader)
    return res


_u32 = _read_int

def _s32(reader):
    v = _read_int(reader)
    if v & 2147483648 != 0:
        v = -((v ^ 4294967295) + 1)
    return v


def _s24(reader):
    bs = reader.read(3)
    last_byte = '\xff' if ord(bs[2:3]) >= 128 else '\x00'
    return struct.unpack(u'<i', bs + last_byte)[0]


def _read_string(reader):
    slen = _u30(reader)
    resb = reader.read(slen)
    return resb.decode(u'utf-8')


def _read_bytes(count, reader):
    resb = reader.read(count)
    return resb


def _read_byte(reader):
    resb = _read_bytes(1, reader=reader)
    res = struct.unpack(u'<B', resb)[0]
    return res


StringClass = _AVMClass(u'(no name idx)', u'String')
ByteArrayClass = _AVMClass(u'(no name idx)', u'ByteArray')
TimerClass = _AVMClass(u'(no name idx)', u'Timer')
TimerEventClass = _AVMClass(u'(no name idx)', u'TimerEvent', {u'TIMER': u'timer'})
_builtin_classes = {StringClass.name: StringClass,
 ByteArrayClass.name: ByteArrayClass,
 TimerClass.name: TimerClass,
 TimerEventClass.name: TimerEventClass}

class _Undefined(object):

    def __bool__(self):
        return False

    __nonzero__ = __bool__

    def __hash__(self):
        return 0

    def __str__(self):
        return u'undefined'

    __repr__ = __str__


undefined = _Undefined()

class SWFInterpreter(object):

    def __init__(self, file_contents):
        self._patched_functions = {(TimerClass, u'addEventListener'): lambda params: undefined}
        code_tag = next((tag for tag_code, tag in _extract_tags(file_contents) if tag_code == 82))
        p = code_tag.index('\x00', 4) + 1
        code_reader = io.BytesIO(code_tag[p:])
        u30 = lambda *args: _u30(reader=code_reader, *args)
        s32 = lambda *args: _s32(reader=code_reader, *args)
        u32 = lambda *args: _u32(reader=code_reader, *args)
        read_bytes = lambda *args: _read_bytes(reader=code_reader, *args)
        read_byte = lambda *args: _read_byte(reader=code_reader, *args)
        read_bytes(4)
        int_count = u30()
        self.constant_ints = [0]
        for _c in range(1, int_count):
            self.constant_ints.append(s32())

        self.constant_uints = [0]
        uint_count = u30()
        for _c in range(1, uint_count):
            self.constant_uints.append(u32())

        double_count = u30()
        read_bytes(max(0, double_count - 1) * 8)
        string_count = u30()
        self.constant_strings = [u'']
        for _c in range(1, string_count):
            s = _read_string(code_reader)
            self.constant_strings.append(s)

        namespace_count = u30()
        for _c in range(1, namespace_count):
            read_bytes(1)
            u30()

        ns_set_count = u30()
        for _c in range(1, ns_set_count):
            count = u30()
            for _c2 in range(count):
                u30()

        multiname_count = u30()
        MULTINAME_SIZES = {7: 2,
         13: 2,
         15: 1,
         16: 1,
         17: 0,
         18: 0,
         9: 2,
         14: 2,
         27: 1,
         28: 1}
        self.multinames = [u'']
        for _c in range(1, multiname_count):
            kind = u30()
            if kind == 7:
                u30()
                name_idx = u30()
                self.multinames.append(self.constant_strings[name_idx])
            elif kind == 9:
                name_idx = u30()
                u30()
                self.multinames.append(self.constant_strings[name_idx])
            else:
                self.multinames.append(_Multiname(kind))
                for _c2 in range(MULTINAME_SIZES[kind]):
                    u30()

        method_count = u30()
        MethodInfo = collections.namedtuple(u'MethodInfo', [u'NEED_ARGUMENTS', u'NEED_REST'])
        method_infos = []
        for method_id in range(method_count):
            param_count = u30()
            u30()
            for _ in range(param_count):
                u30()

            u30()
            flags = read_byte()
            if flags & 8 != 0:
                option_count = u30()
                for c in range(option_count):
                    u30()
                    read_bytes(1)

            if flags & 128 != 0:
                for _ in range(param_count):
                    u30()

            mi = MethodInfo(flags & 1 != 0, flags & 4 != 0)
            method_infos.append(mi)

        metadata_count = u30()
        for _c in range(metadata_count):
            u30()
            item_count = u30()
            for _c2 in range(item_count):
                u30()
                u30()

        def parse_traits_info():
            trait_name_idx = u30()
            kind_full = read_byte()
            kind = kind_full & 15
            attrs = kind_full >> 4
            methods = {}
            constants = None
            if kind == 0:
                u30()
                u30()
                vindex = u30()
                if vindex != 0:
                    read_byte()
            elif kind == 6:
                u30()
                u30()
                vindex = u30()
                vkind = u'any'
                if vindex != 0:
                    vkind = read_byte()
                if vkind == 3:
                    value = self.constant_ints[vindex]
                elif vkind == 4:
                    value = self.constant_uints[vindex]
                else:
                    return ({}, None)
                constants = {self.multinames[trait_name_idx]: value}
            elif kind in (1, 2, 3):
                u30()
                method_idx = u30()
                methods[self.multinames[trait_name_idx]] = method_idx
            elif kind == 4:
                u30()
                u30()
            elif kind == 5:
                u30()
                function_idx = u30()
                methods[function_idx] = self.multinames[trait_name_idx]
            else:
                print u'[SWFInterpreter] Unsupported trait kind %d' % kind
                return
            if attrs & 4 != 0:
                metadata_count = u30()
                for _c3 in range(metadata_count):
                    u30()

            return (methods, constants)

        class_count = u30()
        classes = []
        for class_id in range(class_count):
            name_idx = u30()
            cname = self.multinames[name_idx]
            avm_class = _AVMClass(name_idx, cname)
            classes.append(avm_class)
            u30()
            flags = read_byte()
            if flags & 8 != 0:
                u30()
            intrf_count = u30()
            for _c2 in range(intrf_count):
                u30()

            u30()
            trait_count = u30()
            for _c2 in range(trait_count):
                trait_methods, trait_constants = parse_traits_info()
                avm_class.register_methods(trait_methods)
                if trait_constants:
                    avm_class.constants.update(trait_constants)

        self._classes_by_name = dict(((c.name, c) for c in classes))
        for avm_class in classes:
            avm_class.cinit_idx = u30()
            trait_count = u30()
            for _c2 in range(trait_count):
                trait_methods, trait_constants = parse_traits_info()
                avm_class.register_methods(trait_methods)
                if trait_constants:
                    avm_class.constants.update(trait_constants)

        script_count = u30()
        for _c in range(script_count):
            u30()
            trait_count = u30()
            for _c2 in range(trait_count):
                parse_traits_info()

        method_body_count = u30()
        Method = collections.namedtuple(u'Method', [u'code', u'local_count'])
        self._all_methods = []
        for _c in range(method_body_count):
            method_idx = u30()
            u30()
            local_count = u30()
            u30()
            u30()
            code_length = u30()
            code = read_bytes(code_length)
            m = Method(code, local_count)
            self._all_methods.append(m)
            for avm_class in classes:
                if method_idx in avm_class.method_idxs:
                    avm_class.methods[avm_class.method_idxs[method_idx]] = m

            exception_count = u30()
            for _c2 in range(exception_count):
                u30()
                u30()
                u30()
                u30()
                u30()

            trait_count = u30()
            for _c2 in range(trait_count):
                parse_traits_info()

    def patch_function(self, avm_class, func_name, f):
        self._patched_functions[avm_class, func_name] = f

    def extract_class(self, class_name, call_cinit = True):
        try:
            res = self._classes_by_name[class_name]
        except KeyError:
            print u'[SWFInterpreter] Class %r not found' % class_name
            return None

        if call_cinit and hasattr(res, u'cinit_idx'):
            res.register_methods({u'$cinit': res.cinit_idx})
            res.methods[u'$cinit'] = self._all_methods[res.cinit_idx]
            cinit = self.extract_function(res, u'$cinit')
            cinit([])
        return res

    def extract_function(self, avm_class, func_name):
        p = self._patched_functions.get((avm_class, func_name))
        if p:
            return p
        if func_name in avm_class.method_pyfunctions:
            return avm_class.method_pyfunctions[func_name]
        if func_name in self._classes_by_name:
            return self._classes_by_name[func_name].make_object()
        if func_name not in avm_class.methods:
            print u'[SWFInterpreter] Cannot find function %s.%s' % (avm_class.name, func_name)
            return None
        m = avm_class.methods[func_name]

        def resfunc(args):
            coder = io.BytesIO(m.code)
            s24 = lambda : _s24(coder)
            u30 = lambda : _u30(coder)
            registers = [avm_class.variables] + list(args) + [None] * m.local_count
            stack = []
            scopes = collections.deque([self._classes_by_name, avm_class.constants, avm_class.variables])
            while True:
                opcode = _read_byte(coder)
                if opcode == 9:
                    pass
                elif opcode == 16:
                    offset = s24()
                    coder.seek(coder.tell() + offset)
                elif opcode == 17:
                    offset = s24()
                    value = stack.pop()
                    if value:
                        coder.seek(coder.tell() + offset)
                elif opcode == 18:
                    offset = s24()
                    value = stack.pop()
                    if not value:
                        coder.seek(coder.tell() + offset)
                elif opcode == 19:
                    offset = s24()
                    value2 = stack.pop()
                    value1 = stack.pop()
                    if value2 == value1:
                        coder.seek(coder.tell() + offset)
                elif opcode == 20:
                    offset = s24()
                    value2 = stack.pop()
                    value1 = stack.pop()
                    if value2 != value1:
                        coder.seek(coder.tell() + offset)
                elif opcode == 21:
                    offset = s24()
                    value2 = stack.pop()
                    value1 = stack.pop()
                    if value1 < value2:
                        coder.seek(coder.tell() + offset)
                elif opcode == 32:
                    stack.append(None)
                elif opcode == 33:
                    stack.append(undefined)
                elif opcode == 36:
                    v = _read_byte(coder)
                    stack.append(v)
                elif opcode == 37:
                    v = u30()
                    stack.append(v)
                elif opcode == 38:
                    stack.append(True)
                elif opcode == 39:
                    stack.append(False)
                elif opcode == 40:
                    stack.append(float(u'NaN'))
                elif opcode == 42:
                    value = stack[-1]
                    stack.append(value)
                elif opcode == 44:
                    idx = u30()
                    stack.append(self.constant_strings[idx])
                elif opcode == 48:
                    new_scope = stack.pop()
                    scopes.append(new_scope)
                elif opcode == 66:
                    arg_count = u30()
                    args = list(reversed([ stack.pop() for _ in range(arg_count) ]))
                    obj = stack.pop()
                    res = obj.avm_class.make_object()
                    stack.append(res)
                elif opcode == 70:
                    index = u30()
                    mname = self.multinames[index]
                    arg_count = u30()
                    args = list(reversed([ stack.pop() for _ in range(arg_count) ]))
                    obj = stack.pop()
                    if obj == StringClass:
                        if mname == u'String':
                            if args[0] == undefined:
                                res = u'undefined'
                            else:
                                res = unicode(args[0])
                            stack.append(res)
                            continue
                        else:
                            raise NotImplementedError(u'Function String.%s is not yet implemented' % mname)
                    elif isinstance(obj, _AVMClass_Object):
                        func = self.extract_function(obj.avm_class, mname)
                        res = func(args)
                        stack.append(res)
                        continue
                    elif isinstance(obj, _AVMClass):
                        func = self.extract_function(obj, mname)
                        res = func(args)
                        stack.append(res)
                        continue
                    elif isinstance(obj, _ScopeDict):
                        if mname in obj.avm_class.method_names:
                            func = self.extract_function(obj.avm_class, mname)
                            res = func(args)
                        else:
                            res = obj[mname]
                        stack.append(res)
                        continue
                    elif isinstance(obj, unicode):
                        if mname == u'split':
                            if args[0] == u'':
                                res = list(obj)
                            else:
                                res = obj.split(args[0])
                            stack.append(res)
                            continue
                        elif mname == u'charCodeAt':
                            idx = 0 if len(args) == 0 else args[0]
                            res = ord(obj[idx])
                            stack.append(res)
                            continue
                    elif isinstance(obj, list):
                        if mname == u'slice':
                            res = obj[args[0]:]
                            stack.append(res)
                            continue
                        elif mname == u'join':
                            res = args[0].join(obj)
                            stack.append(res)
                            continue
                    raise NotImplementedError(u'Unsupported property %r on %r' % (mname, obj))
                else:
                    if opcode == 71:
                        res = undefined
                        return res
                    if opcode == 72:
                        res = stack.pop()
                        return res
                    if opcode == 73:
                        arg_count = u30()
                        args = list(reversed([ stack.pop() for _ in range(arg_count) ]))
                        obj = stack.pop()
                    elif opcode == 74:
                        index = u30()
                        arg_count = u30()
                        args = list(reversed([ stack.pop() for _ in range(arg_count) ]))
                        obj = stack.pop()
                        mname = self.multinames[index]
                        stack.append(obj.make_object())
                    elif opcode == 79:
                        index = u30()
                        mname = self.multinames[index]
                        arg_count = u30()
                        args = list(reversed([ stack.pop() for _ in range(arg_count) ]))
                        obj = stack.pop()
                        if isinstance(obj, _AVMClass_Object):
                            func = self.extract_function(obj.avm_class, mname)
                            res = func(args)
                            continue
                        if isinstance(obj, _ScopeDict):
                            func = self.extract_function(obj.avm_class, mname)
                            res = func(args)
                            continue
                        if mname == u'reverse':
                            obj.reverse()
                        else:
                            raise NotImplementedError(u'Unsupported (void) property %r on %r' % (mname, obj))
                    elif opcode == 86:
                        arg_count = u30()
                        arr = []
                        for i in range(arg_count):
                            arr.append(stack.pop())

                        arr = arr[::-1]
                        stack.append(arr)
                    elif opcode == 93:
                        index = u30()
                        mname = self.multinames[index]
                        for s in reversed(scopes):
                            if mname in s:
                                res = s
                                break
                        else:
                            res = scopes[0]

                        if mname not in res and mname in _builtin_classes:
                            stack.append(_builtin_classes[mname])
                        else:
                            stack.append(res[mname])
                    elif opcode == 94:
                        index = u30()
                        mname = self.multinames[index]
                        for s in reversed(scopes):
                            if mname in s:
                                res = s
                                break
                        else:
                            res = avm_class.variables

                        stack.append(res)
                    elif opcode == 96:
                        index = u30()
                        mname = self.multinames[index]
                        for s in reversed(scopes):
                            if mname in s:
                                scope = s
                                break
                        else:
                            scope = avm_class.variables

                        if mname in scope:
                            res = scope[mname]
                        elif mname in _builtin_classes:
                            res = _builtin_classes[mname]
                        else:
                            res = undefined
                        stack.append(res)
                    elif opcode == 97:
                        index = u30()
                        value = stack.pop()
                        idx = self.multinames[index]
                        if isinstance(idx, _Multiname):
                            idx = stack.pop()
                        obj = stack.pop()
                        obj[idx] = value
                    elif opcode == 98:
                        index = u30()
                        stack.append(registers[index])
                    elif opcode == 99:
                        index = u30()
                        value = stack.pop()
                        registers[index] = value
                    elif opcode == 102:
                        index = u30()
                        pname = self.multinames[index]
                        if pname == u'length':
                            obj = stack.pop()
                            stack.append(len(obj))
                        elif isinstance(pname, unicode):
                            obj = stack.pop()
                            if isinstance(obj, _AVMClass):
                                res = obj.static_properties[pname]
                                stack.append(res)
                                continue
                            res = obj.get(pname, undefined)
                            stack.append(res)
                        else:
                            idx = stack.pop()
                            obj = stack.pop()
                            stack.append(obj[idx])
                    elif opcode == 104:
                        index = u30()
                        value = stack.pop()
                        idx = self.multinames[index]
                        if isinstance(idx, _Multiname):
                            idx = stack.pop()
                        obj = stack.pop()
                        obj[idx] = value
                    elif opcode == 115:
                        value = stack.pop()
                        intvalue = int(value)
                        stack.append(intvalue)
                    elif opcode == 128:
                        u30()
                    elif opcode == 130:
                        value = stack.pop()
                        stack.append(value)
                    elif opcode == 133:
                        pass
                    elif opcode == 147:
                        value = stack.pop()
                        stack.append(value - 1)
                    else:
                        if opcode == 149:
                            value = stack.pop()
                            return {_Undefined: u'undefined',
                             unicode: u'String',
                             int: u'Number',
                             float: u'Number'}[type(value)]
                        if opcode == 160:
                            value2 = stack.pop()
                            value1 = stack.pop()
                            res = value1 + value2
                            stack.append(res)
                        elif opcode == 161:
                            value2 = stack.pop()
                            value1 = stack.pop()
                            res = value1 - value2
                            stack.append(res)
                        elif opcode == 162:
                            value2 = stack.pop()
                            value1 = stack.pop()
                            res = value1 * value2
                            stack.append(res)
                        elif opcode == 164:
                            value2 = stack.pop()
                            value1 = stack.pop()
                            res = value1 % value2
                            stack.append(res)
                        elif opcode == 168:
                            value2 = stack.pop()
                            value1 = stack.pop()
                            res = value1 & value2
                            stack.append(res)
                        elif opcode == 171:
                            value2 = stack.pop()
                            value1 = stack.pop()
                            result = value1 == value2
                            stack.append(result)
                        elif opcode == 175:
                            value2 = stack.pop()
                            value1 = stack.pop()
                            result = value1 >= value2
                            stack.append(result)
                        elif opcode == 192:
                            value = stack.pop()
                            stack.append(value + 1)
                        elif opcode == 208:
                            stack.append(registers[0])
                        elif opcode == 209:
                            stack.append(registers[1])
                        elif opcode == 210:
                            stack.append(registers[2])
                        elif opcode == 211:
                            stack.append(registers[3])
                        elif opcode == 212:
                            registers[0] = stack.pop()
                        elif opcode == 213:
                            registers[1] = stack.pop()
                        elif opcode == 214:
                            registers[2] = stack.pop()
                        elif opcode == 215:
                            registers[3] = stack.pop()
                        else:
                            raise NotImplementedError(u'Unsupported opcode %d' % opcode)

        avm_class.method_pyfunctions[func_name] = resfunc
        return resfunc
