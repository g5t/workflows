import g5t_module as m

def test_main():
    assert m.add(1, 2) == 3
    assert m.subtract(1, 2) == -1

def test_module():
    import g5t_module._module as cm
    assert hasattr(cm, '__version__')
    assert hasattr(cm, '__build_datetime')
    assert hasattr(cm, '__build_hostname')
    assert hasattr(cm, '__git_branch')
    assert hasattr(cm, '__git_revision')