from . import *
import typing as _t

P = _t.ParamSpec("P")
F = _t.TypeVar("F", bound=_t.Callable)
F2 = _t.TypeVar("F2", bound=_t.Callable)
T = _t.TypeVar("T")
SelfT = _t.TypeVar("SelfT")


def echo():
    print("do nothing()")


class ContextedFunc(ContextedFuncBase[P, T], resolver=echo): ...


class ContextedMethod(ContextedMethodBase[SelfT, P, T], resolver=echo): ...


@ContextedFunc
def foo(x: int) -> str:
    return f"input: {x}"


class Foo:
    @ContextedMethod
    def echo(self, x: int) -> str:
        return f"input: {x}"


_t.reveal_type(Foo.echo)  # (Foo, x: int) -> str
_t.reveal_type(Foo().echo)  # (x: int) -> str
