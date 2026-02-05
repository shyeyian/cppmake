import typing

def recursive_collect[T, U, R](node: U, next: typing.Callable[[U | T], list[T]], collect: typing.Callable[[U | T], R | list[R] | None], flatten: bool = False) -> list[R]: ...

if typing.TYPE_CHECKING:
    @typing.overload
    def recursive_collect[T, U, R](node: U, next: typing.Callable[[U | T], list[T]], collect: typing.Callable[[T], R | None], *, flatten: typing.Literal[False] = False) -> list[R]: ...
    @typing.overload
    def recursive_collect[T, U, R](node: U, next: typing.Callable[[U | T], list[T]], collect: typing.Callable[[T], list[R]],  *, flatten: typing.Literal[True])          -> list[R]: ...



# Our goal is to make the caller more pretty (with the algorithm itself to be maybe dirty).
# Feel free to overwrite the implemention when we need something new from it.

def recursive_collect[T, U, R](
    node   : U, 
    next   : typing.Callable[[U | T], list[T]], 
    collect: typing.Callable[[T], R | list[R] | None], 
    flatten: bool = False
) -> list[R]:
   return _recursive_collect_impl(node, next, collect, flatten, True, set(), list())

def _recursive_collect_impl[T, U, R](
    node     : U | T, 
    next     : typing.Callable[[U | T], list[T]], 
    collect  : typing.Callable[[T], R | list[R] | None], 
    flatten  : bool,
    root     : bool,
    visited  : set[T],
    collected: list[R]
) -> list[R]:
    if node not in visited:
        if not root:
            visited |= {typing.cast(T, node)}
            value = collect(typing.cast(T, node))
            if value is not None and value not in collected:
                if not flatten:
                    collected += [typing.cast(R, value)]
                else:
                    collected += typing.cast(list[R], value)
        for subnode in next(node):
            _recursive_collect_impl(subnode, next, collect, flatten, True, visited, collected)
    return collected
