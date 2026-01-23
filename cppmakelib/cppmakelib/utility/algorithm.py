import typing

def recursive_collect[T, R](node: T, next: typing.Callable[[T], list[T]], collect: typing.Callable[[T], R], root: bool = True) -> list[R]: ...

if typing.TYPE_CHECKING:
    @typing.overload
    def recursive_collect[T, R]   (node: T, next: typing.Callable[[T],     list[T]], collect: typing.Callable[[T], R], root: typing.Literal[True] = True) -> list[R]: ...
    @typing.overload
    def recursive_collect[T, U, R](node: U, next: typing.Callable[[U | T], list[T]], collect: typing.Callable[[T], R], root: typing.Literal[False]      ) -> list[R]: ...



# Our goal is to make the caller more pretty (with the algorithm itself to be maybe dirty).
# Feel free to overwrite the implemention when we need something new from it.

def recursive_collect[T, R](
    node   : T, 
    next   : typing.Callable[[T], list[T]], 
    collect: typing.Callable[[T], R | None], 
    root   : bool = True
) -> list[R]:
   return _recursive_collect_impl(node, next, collect, root, visited=set(), cached=list())

def _recursive_collect_impl[T, R](
    node   : T, 
    next   : typing.Callable[[T], list[T]], 
    collect: typing.Callable[[T], R | None], 
    root   : bool,
    visited: set[T],
    cached : list[R] 
) -> list[R]:
    if node not in visited:
        visited |= {node}
        if root:
            collected = collect(node)
            if collected is not None and collected not in cached:
                cached += [collected]
        for subnode in next(node):
            _recursive_collect_impl(subnode, next, collect, True, visited, cached)
    return cached
