import ast
import imp
import itertools
import os.path
import sys

from . import conf


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
            try:
                fobj = open(modpath)
            except IOError:
                return None
        else:
            try:
                fobj, modpath, desc = imp.find_module(full_name, path)
            except ImportError:
                return None

        suffix, mode, modtype = desc

        try:
            if modtype == imp.PY_SOURCE:
                code = rewrite_source(fobj.read(), modpath)
                self.loaded_modules[full_name] = code, modpath

                return self
        finally:
            if fobj:
                fobj.close()

    def load_module(self, name):
        code, modpath = self.loaded_modules[name]
        mod = imp.new_module(name)
        mod.__file__ = modpath

        sys.modules[name] = mod

        exec(code, mod.__dict__)

        return mod


def attach_hook(initial_probability=None,
                target_timing=None,
                convergence_factor=None):
    if initial_probability is not None:
        conf.set_initial_probability(initial_probability)

    if target_timing is not None:
        conf.set_target_timing(target_timing)

    if convergence_factor is not None:
        conf.set_convergence_factor(convergence_factor)

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
    HAS_WITHITEM = hasattr(ast, 'withitem')

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
        pre_nodes = list(itertools.takewhile(
            lambda node: (self._is_docstring(node)
                         or self._is_future_import(node)),
            node.body))
        rest_nodes = [self.visit(n) for n in node.body[len(pre_nodes):]]

        importnode = ast.ImportFrom(
            module='hesitate.driver',
            names=[
                ast.alias(
                    name='should_assert',
                    asname=self.ASSERTION_TEST_IMPORTED_NAME),
                ast.alias(
                    name='timed',
                    asname=self.ASSERTION_TIMER_IMPORTED_NAME)],
            lineno=1,
            col_offset=0,
            level=0)

        if pre_nodes:
            importnode = ast.copy_location(importnode, pre_nodes[0])

        new_mod = ast.Module(
            body=pre_nodes + [importnode] + rest_nodes,
            lineno=1,
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
                keywords=[],
                starargs=None,
                kwargs=None),
            node)

        timer_name = ast.copy_location(
            ast.Name(self.ASSERTION_TIMER_IMPORTED_NAME, ast.Load()),
            node)
        timer_call = ast.copy_location(
            ast.Call(
                func=timer_name,
                args=[srcname_node, lineno_node, col_offset_node],
                keywords=[],
                starargs=None,
                kwargs=None),
            node)
        with_node = ast.copy_location(
            self._make_with_node(timer_call, [node]),
            node)

        new_node = ast.copy_location(
            ast.If(
                test=func_call,
                body=[with_node],
                orelse=[]),
            node)

        return new_node

    def _make_with_node(self, with_expr, body):
        if self.HAS_WITHITEM:
            return ast.With(
                items=[ast.withitem(
                    context_expr=with_expr,
                    optional_vars=None)],
                body=body)
        else:
            return ast.With(
                context_expr=with_expr,
                optional_vars=None,
                body=body)
