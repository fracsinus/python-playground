from __future__ import annotations
from types import MethodType
from typing_extensions import TypeIs
import typing as _t

P = _t.ParamSpec("P")
T = _t.TypeVar("T")
SelfT = _t.TypeVar("SelfT")

# HKTs are not supported
# https://github.com/python/typing/issues/548


class ContextedFuncBase(_t.Generic[P, T]):
    _wrapped: _t.Callable[_t.Concatenate[P], T]
    _resolver: _t.Callable

    @classmethod
    def _check(cls, obj: _t.Callable[P, T]) -> TypeIs[ContextedFuncBase[P, T]]:
        return isinstance(obj, cls)

    def __init_subclass__(cls, resolver: _t.Callable) -> None:
        cls._resolver = resolver
        return super().__init_subclass__()

    def __init__(self, f: _t.Callable[P, T]) -> None:
        if self._check(f):
            self._wrapped = f._wrapped
            self._self = f._self
        else:
            self._wrapped = f

    def __call__(self, *args: P.args, **kwargs: P.kwargs):
        self.__class__._resolver()
        return self._wrapped(*args, **kwargs)


class ContextedMethodBase(_t.Generic[SelfT, P, T]):
    _wrapped: _t.Callable[_t.Concatenate[SelfT, P], T]
    _self: _t.Optional[SelfT] = None
    _resolver: _t.Callable

    @classmethod
    def _check(cls, f) -> TypeIs[ContextedMethodBase[SelfT, P, T]]:
        return isinstance(f, cls)

    def __init_subclass__(cls, resolver: _t.Callable) -> None:
        cls._resolver = resolver
        return super().__init_subclass__()

    def __init__(
        self,
        f: _t.Union[
            _t.Self,
            _t.Callable[_t.Concatenate[SelfT, P], T],
        ],
    ) -> None:
        if self._check(f):
            self._wrapped = f._wrapped
            self._self = f._self
        else:
            self._wrapped = f

    @_t.overload
    def __get__(self, obj: SelfT, _) -> _t.Callable[P, T]: ...
    @_t.overload
    def __get__(self, obj: None, _) -> _t.Callable[_t.Concatenate[SelfT, P], T]: ...
    def __get__(self, obj: _t.Union[SelfT, None], _) -> _t.Union[
        _t.Callable[P, T],
        _t.Callable[_t.Concatenate[SelfT, P], T],
    ]:
        if obj is not None:
            self._self = obj
            return _t.cast(_t.Callable[P, T], self)
        else:
            return _t.cast(_t.Callable[_t.Concatenate[SelfT, P], T], self)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        self.__class__._resolver()
        if self._self:
            return MethodType(self._wrapped, self._self)(*args, **kwargs)
        else:
            raise
