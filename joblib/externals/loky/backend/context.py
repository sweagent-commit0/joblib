import os
import sys
import math
import subprocess
import traceback
import warnings
import multiprocessing as mp
from multiprocessing import get_context as mp_get_context
from multiprocessing.context import BaseContext
from .process import LokyProcess, LokyInitMainProcess
if sys.version_info >= (3, 8):
    from concurrent.futures.process import _MAX_WINDOWS_WORKERS
    if sys.version_info < (3, 10):
        _MAX_WINDOWS_WORKERS = _MAX_WINDOWS_WORKERS - 1
else:
    _MAX_WINDOWS_WORKERS = 60
START_METHODS = ['loky', 'loky_init_main', 'spawn']
if sys.platform != 'win32':
    START_METHODS += ['fork', 'forkserver']
_DEFAULT_START_METHOD = None
physical_cores_cache = None

def cpu_count(only_physical_cores=False):
    """Return the number of CPUs the current process can use.

    The returned number of CPUs accounts for:
     * the number of CPUs in the system, as given by
       ``multiprocessing.cpu_count``;
     * the CPU affinity settings of the current process
       (available on some Unix systems);
     * Cgroup CPU bandwidth limit (available on Linux only, typically
       set by docker and similar container orchestration systems);
     * the value of the LOKY_MAX_CPU_COUNT environment variable if defined.
    and is given as the minimum of these constraints.

    If ``only_physical_cores`` is True, return the number of physical cores
    instead of the number of logical cores (hyperthreading / SMT). Note that
    this option is not enforced if the number of usable cores is controlled in
    any other way such as: process affinity, Cgroup restricted CPU bandwidth
    or the LOKY_MAX_CPU_COUNT environment variable. If the number of physical
    cores is not found, return the number of logical cores.

    Note that on Windows, the returned number of CPUs cannot exceed 61 (or 60 for
    Python < 3.10), see:
    https://bugs.python.org/issue26903.

    It is also always larger or equal to 1.
    """
    pass

def _cpu_count_user(os_cpu_count):
    """Number of user defined available CPUs"""
    pass

def _count_physical_cores():
    """Return a tuple (number of physical cores, exception)

    If the number of physical cores is found, exception is set to None.
    If it has not been found, return ("not found", exception).

    The number of physical cores is cached to avoid repeating subprocess calls.
    """
    pass

class LokyContext(BaseContext):
    """Context relying on the LokyProcess."""
    _name = 'loky'
    Process = LokyProcess
    cpu_count = staticmethod(cpu_count)

    def Queue(self, maxsize=0, reducers=None):
        """Returns a queue object"""
        pass

    def SimpleQueue(self, reducers=None):
        """Returns a queue object"""
        pass
    if sys.platform != 'win32':
        'For Unix platform, use our custom implementation of synchronize\n        ensuring that we use the loky.backend.resource_tracker to clean-up\n        the semaphores in case of a worker crash.\n        '

        def Semaphore(self, value=1):
            """Returns a semaphore object"""
            pass

        def BoundedSemaphore(self, value):
            """Returns a bounded semaphore object"""
            pass

        def Lock(self):
            """Returns a lock object"""
            pass

        def RLock(self):
            """Returns a recurrent lock object"""
            pass

        def Condition(self, lock=None):
            """Returns a condition object"""
            pass

        def Event(self):
            """Returns an event object"""
            pass

class LokyInitMainContext(LokyContext):
    """Extra context with LokyProcess, which does load the main module

    This context is used for compatibility in the case ``cloudpickle`` is not
    present on the running system. This permits to load functions defined in
    the ``main`` module, using proper safeguards. The declaration of the
    ``executor`` should be protected by ``if __name__ == "__main__":`` and the
    functions and variable used from main should be out of this block.

    This mimics the default behavior of multiprocessing under Windows and the
    behavior of the ``spawn`` start method on a posix system.
    For more details, see the end of the following section of python doc
    https://docs.python.org/3/library/multiprocessing.html#multiprocessing-programming
    """
    _name = 'loky_init_main'
    Process = LokyInitMainProcess
ctx_loky = LokyContext()
mp.context._concrete_contexts['loky'] = ctx_loky
mp.context._concrete_contexts['loky_init_main'] = LokyInitMainContext()