"""Simple module tests"""

def test_main():
    """Test the the compile functionality works"""
    import g5t_module as m
    assert m.add(1, 2) == 3
    assert m.subtract(1, 2) == -1

def test_module():
    """Test that the compiled module has the expected attributes"""
    import g5t_module._module as cm
    assert hasattr(cm, '__version__')
    assert hasattr(cm, '__build_datetime')
    assert hasattr(cm, '__build_hostname')
    assert hasattr(cm, '__git_branch')
    assert hasattr(cm, '__git_revision')