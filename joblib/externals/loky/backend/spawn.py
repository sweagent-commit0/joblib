import os
import sys
import runpy
import textwrap
import types
from multiprocessing import process, util
if sys.platform != 'win32':
    WINEXE = False
    WINSERVICE = False
else:
    import msvcrt
    from multiprocessing.reduction import duplicate
    WINEXE = sys.platform == 'win32' and getattr(sys, 'frozen', False)
    WINSERVICE = sys.executable.lower().endswith('pythonservice.exe')
if WINSERVICE:
    _python_exe = os.path.join(sys.exec_prefix, 'python.exe')
else:
    _python_exe = sys.executable

def get_preparation_data(name, init_main_module=True):
    """Return info about parent needed by child to unpickle process object."""
    pass
old_main_modules = []

def prepare(data, parent_sentinel=None):
    """Try to get current process ready to unpickle process object."""
    pass