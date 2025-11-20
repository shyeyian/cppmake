def assert_(value, message=None):
    if message is None:
        assert value
    else:
        assert value, message

def raise_(error):
    raise error