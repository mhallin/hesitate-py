import ast
import imp
import itertools
import os.path
import sys


class RewriterHook(object):
    def __init__(self):
        self.loaded_modules = {}

    def find_module(self, full_name, path=None):
        if path and not isinstance(path, list):
            path = list(path)

        if path and len(path) == 1:
            path = path[0]
            modpath = os.path.join(path, full_name.rpartition('.')[2] + '.py')
            desc = ('.py', 'r', imp.PY_SOURCE)
            fobj = open(modpath)
        else:
            try:
                fobj, modpath, desc = imp.find_module(full_name, path)
            except ImportError:
                return None

        suffix, mode, modtype = desc

        try:
            if modtype == imp.PY_SOURCE:
                code = rewrite_source(fobj.read(), modpath)
                self.loaded_modules[full_name] = code

                return self
        finally:
            if fobj:
                fobj.close()

    def load_module(self, name):
        code = self.loaded_modules[name]
        mod = imp.new_module(name)

        exec(code, mod.__dict__)

        sys.modules[name] = mod

        return mod


def attach_hook():
    sys.meta_path.insert(0, RewriterHook())


def rewrite_source(source, modpath):
    try:
        parsed = ast.parse(source)
    except SyntaxError:
        return None

    rewritten = AssertionTransformer(modpath).visit(parsed)
    return compile(rewritten, modpath, 'exec')


class AssertionTransformer(ast.NodeTransformer):
    ASSERTION_TEST_IMPORTED_NAME = '@hesitate_should_assert'
    ASSERTION_TIMER_IMPORTED_NAME = '@hesitate_timed'

    def __init__(self, modpath):
        self.modpath = modpath

    def _is_docstring(self, node):
        return isinstance(node, ast.Expr) \
            and isinstance(node.value, ast.Str)

    def _is_future_import(self, node):
        return isinstance(node, ast.ImportFrom) \
            and node.level == 0 \
            and node.module == '__future__'

    def visit_Module(self, node):
        importnode = ast.ImportFrom(
            module='hesitate.driver',
            names=[
                ast.alias(
                    name='should_assert',
                    asname=self.ASSERTION_TEST_IMPORTED_NAME),
                ast.alias(
                    name='timed',
                    asname=self.ASSERTION_TIMER_IMPORTED_NAME)],
            lineno=0,
            col_offset=0)

        pre_nodes = list(itertools.takewhile(
            lambda node: (self._is_docstring(node)
                         or self._is_future_import(node)),
            node.body))
        rest_nodes = [self.visit(n) for n in node.body[len(pre_nodes):]]

        new_mod = ast.Module(
            body=pre_nodes + [importnode] + rest_nodes,
            lineno=0,
            col_offset=0)

        return new_mod

    def visit_Assert(self, node):
        srcname_node = ast.copy_location(ast.Str(self.modpath), node)
        lineno_node = ast.copy_location(ast.Num(node.lineno), node)
        col_offset_node = ast.copy_location(ast.Num(node.col_offset), node)

        assertion_test_name = ast.copy_location(
            ast.Name(self.ASSERTION_TEST_IMPORTED_NAME, ast.Load()),
            node)
        func_call = ast.copy_location(
            ast.Call(
                func=assertion_test_name,
                args=[srcname_node, lineno_node, col_offset_node],
                keywords=[]),
            node)

        timer_name = ast.copy_location(
            ast.Name(self.ASSERTION_TIMER_IMPORTED_NAME, ast.Load()),
            node)
        timer_call = ast.copy_location(
            ast.Call(
                func=timer_name,
                args=[srcname_node, lineno_node, col_offset_node],
                keywords=[]),
            node)
        with_node = ast.copy_location(
            ast.With(
                items=[ast.withitem(
                    context_expr=timer_call,
                    optional_vars=None)],
                body=[node]),
            node)

        new_node = ast.copy_location(
            ast.If(
                test=func_call,
                body=[with_node],
                orelse=[]),
            node)

        return new_node