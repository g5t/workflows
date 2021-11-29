#!/usr/bin/env python3
import os
import sys
import unittest
import numpy as np
from pathlib import Path
from importlib.util import find_spec
addpaths = [Path(), Path('..')] # we might be in .../build/wrap/
config = os.environ.get('CMAKE_CONFIG_TYPE') # set by ctest -C <cfg>
if config:
  for path in addpaths:
    if Path(path, config).exists():
      addpaths.append(Path(path,config))
sys.path[:0] = [str(path.absolute()) for path in addpaths]

if find_spec('_module') is not None:
    import _module as s
elif find_spec('module') is not None and find_spec('module._module') is not None:
    import module as s
else:
    abspaths = [str(path.absolute()) for path in addpaths]
    raise Exception("module not found in {}!".format(abspaths))

class ModuleTester (unittest.TestCase):
  def test_01(self):
    one, two, three = 1, 2 ,3
    self.assertEqual(s.add(one, two), three)
    self.assertEqual(s.subtract(three, one), two)

if __name__ == '__main__':
  unittest.main()
