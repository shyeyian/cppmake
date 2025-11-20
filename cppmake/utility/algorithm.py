from cppmake.execution.operation import when_all

def recursive_collect(node, next, collect, root=True, flatten=False): ...



def recursive_collect(node, next, collect, root=True, flatten=False):
    return _recursive_collect_impl(node, next, collect, root, flatten, cached=list(), visited=set())

def _recursive_collect_impl(node, next, collect, root, flatten, cached, visited):
    if type(node) != list:
        if node not in visited:
            visited |= {node}
            if root:
                try:
                    collected = collect(node)
                    if collected is not None:
                        if type(collect) != list:
                            cached += [collected]
                        else:
                            cached += collected
                except AttributeError:
                    pass
            for subnode in next(node):
                _recursive_collect_impl(subnode, next, collect, True, flatten, cached, visited)
    else:
        for subnode in node:
            _recursive_collect_impl(subnode, next, collect, root, flatten, cached, visited)
    if not flatten:
        return list(set(cached))
    else:
        return list(set(value for line in cached for value in line))
