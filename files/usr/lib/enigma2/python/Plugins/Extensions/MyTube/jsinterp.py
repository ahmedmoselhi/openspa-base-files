from __future__ import unicode_literals
import json
import operator
import re
_OPERATORS = [(u'|', operator.or_),
 (u'^', operator.xor),
 (u'&', operator.and_),
 (u'>>', operator.rshift),
 (u'<<', operator.lshift),
 (u'-', operator.sub),
 (u'+', operator.add),
 (u'%', operator.mod),
 (u'/', operator.truediv),
 (u'*', operator.mul)]
_ASSIGN_OPERATORS = [ (op + u'=', opfunc) for op, opfunc in _OPERATORS ]
_ASSIGN_OPERATORS.append((u'=', lambda cur, right: right))
_NAME_RE = u'[a-zA-Z_$][a-zA-Z_$0-9]*'

class JSInterpreter(object):

    def __init__(self, code, objects = None):
        if objects is None:
            objects = {}
        self.code = code
        self._functions = {}
        self._objects = objects

    def interpret_statement(self, stmt, local_vars, allow_recursion = 100):
        if allow_recursion < 0:
            print u'[JSInterpreter] Recursion limit reached'
            return None
        should_abort = False
        stmt = stmt.lstrip()
        stmt_m = re.match(u'var\\s', stmt)
        if stmt_m:
            expr = stmt[len(stmt_m.group(0)):]
        else:
            return_m = re.match(u'return(?:\\s+|$)', stmt)
            if return_m:
                expr = stmt[len(return_m.group(0)):]
                should_abort = True
            else:
                expr = stmt
        v = self.interpret_expression(expr, local_vars, allow_recursion)
        return (v, should_abort)

    def interpret_expression(self, expr, local_vars, allow_recursion):
        expr = expr.strip()
        if expr == u'':
            return
        if expr.startswith(u'('):
            parens_count = 0
            for m in re.finditer(u'[()]', expr):
                if m.group(0) == u'(':
                    parens_count += 1
                else:
                    parens_count -= 1
                    if parens_count == 0:
                        sub_expr = expr[1:m.start()]
                        sub_result = self.interpret_expression(sub_expr, local_vars, allow_recursion)
                        remaining_expr = expr[m.end():].strip()
                        if not remaining_expr:
                            return sub_result
                        expr = json.dumps(sub_result) + remaining_expr
                        break
            else:
                print u'[JSInterpreter] Premature end of parens in %r' % expr
                return

        for op, opfunc in _ASSIGN_OPERATORS:
            m = re.match(u'(?x)\n                (?P<out>%s)(?:\\[(?P<index>[^\\]]+?)\\])?\n                \\s*%s\n                (?P<expr>.*)$' % (_NAME_RE, re.escape(op)), expr)
            if not m:
                continue
            right_val = self.interpret_expression(m.group(u'expr'), local_vars, allow_recursion - 1)
            if m.groupdict().get(u'index'):
                lvar = local_vars[m.group(u'out')]
                idx = self.interpret_expression(m.group(u'index'), local_vars, allow_recursion)
                cur = lvar[idx]
                val = opfunc(cur, right_val)
                lvar[idx] = val
                return val
            cur = local_vars.get(m.group(u'out'))
            val = opfunc(cur, right_val)
            local_vars[m.group(u'out')] = val
            return val

        if expr.isdigit():
            return int(expr)
        var_m = re.match(u'(?!if|return|true|false)(?P<name>%s)$' % _NAME_RE, expr)
        if var_m:
            return local_vars[var_m.group(u'name')]
        try:
            return json.loads(expr)
        except ValueError:
            pass

        m = re.match(u'(?P<var>%s)\\.(?P<member>[^(]+)(?:\\(+(?P<args>[^()]*)\\))?$' % _NAME_RE, expr)
        if m:
            variable = m.group(u'var')
            member = m.group(u'member')
            arg_str = m.group(u'args')
            if variable in local_vars:
                obj = local_vars[variable]
            else:
                if variable not in self._objects:
                    self._objects[variable] = self.extract_object(variable)
                obj = self._objects[variable]
            if arg_str is None:
                if member == u'length':
                    return len(obj)
                return obj[member]
            if arg_str == u'':
                argvals = tuple()
            else:
                argvals = tuple([ self.interpret_expression(v, local_vars, allow_recursion) for v in arg_str.split(u',') ])
            if member == u'split':
                return list(obj)
            if member == u'join':
                return argvals[0].join(obj)
            if member == u'reverse':
                obj.reverse()
                return obj
            if member == u'slice':
                return obj[argvals[0]:]
            if member == u'splice':
                index, howMany = argvals
                res = []
                for i in range(index, min(index + howMany, len(obj))):
                    res.append(obj.pop(index))

                return res
            return obj[member](argvals)
        m = re.match(u'(?P<in>%s)\\[(?P<idx>.+)\\]$' % _NAME_RE, expr)
        if m:
            val = local_vars[m.group(u'in')]
            idx = self.interpret_expression(m.group(u'idx'), local_vars, allow_recursion - 1)
            return val[idx]
        for op, opfunc in _OPERATORS:
            m = re.match(u'(?P<x>.+?)%s(?P<y>.+)' % re.escape(op), expr)
            if not m:
                continue
            x, abort = self.interpret_statement(m.group(u'x'), local_vars, allow_recursion - 1)
            if abort:
                print u'[JSInterpreter] Premature left-side return of %s in %r' % (op, expr)
                return
            y, abort = self.interpret_statement(m.group(u'y'), local_vars, allow_recursion - 1)
            if abort:
                print u'[JSInterpreter] Premature right-side return of %s in %r' % (op, expr)
                return
            return opfunc(x, y)

        m = re.match(u'^(?P<func>%s)\\((?P<args>[a-zA-Z0-9_$,]+)\\)$' % _NAME_RE, expr)
        if m:
            fname = m.group(u'func')
            argvals = tuple([ (int(v) if v.isdigit() else local_vars[v]) for v in m.group(u'args').split(u',') ])
            if fname not in self._functions:
                self._functions[fname] = self.extract_function(fname)
            return self._functions[fname](argvals)
        print u'[JSInterpreter] Unsupported JS expression %r' % expr

    def extract_object(self, objname):
        obj = {}
        obj_m = re.search(u'(?:var\\s+)?%s\\s*=\\s*\\{' % re.escape(objname) + u'\\s*(?P<fields>([a-zA-Z$0-9]+\\s*:\\s*function\\(.*?\\)\\s*\\{.*?\\}(?:,\\s*)?)*)' + u'\\}\\s*;', self.code)
        fields = obj_m.group(u'fields')
        fields_m = re.finditer(u'(?P<key>[a-zA-Z$0-9]+)\\s*:\\s*function\\((?P<args>[a-z,]+)\\){(?P<code>[^}]+)}', fields)
        for f in fields_m:
            argnames = f.group(u'args').split(u',')
            obj[f.group(u'key')] = self.build_function(argnames, f.group(u'code'))

        return obj

    def extract_function(self, funcname):
        func_m = re.search(u'(?x)\n                (?:function\\s+%s|[{;,]%s\\s*=\\s*function|var\\s+%s\\s*=\\s*function)\\s*\n                \\((?P<args>[^)]*)\\)\\s*\n                \\{(?P<code>[^}]+)\\}' % (re.escape(funcname), re.escape(funcname), re.escape(funcname)), self.code)
        if func_m is None:
            print u'[JSInterpreter] Could not find JS function %r' % funcname
            return
        argnames = func_m.group(u'args').split(u',')
        return self.build_function(argnames, func_m.group(u'code'))

    def call_function(self, funcname, *args):
        f = self.extract_function(funcname)
        return f(args)

    def build_function(self, argnames, code):

        def resf(args):
            local_vars = dict(zip(argnames, args))
            for stmt in code.split(u';'):
                res, abort = self.interpret_statement(stmt, local_vars)
                if abort:
                    break

            return res

        return resf
