import os
import shutil
import sys
import signal
import warnings
import threading
from _multiprocessing import sem_unlink
from multiprocessing import util
from . import spawn
if sys.platform == 'win32':
    import _winapi
    import msvcrt
    from multiprocessing.reduction import duplicate
__all__ = ['ensure_running', 'register', 'unregister']
_HAVE_SIGMASK = hasattr(signal, 'pthread_sigmask')
_IGNORED_SIGNALS = (signal.SIGINT, signal.SIGTERM)
_CLEANUP_FUNCS = {'folder': shutil.rmtree, 'file': os.unlink}
if os.name == 'posix':
    _CLEANUP_FUNCS['semlock'] = sem_unlink
VERBOSE = False

class ResourceTracker:

    def __init__(self):
        self._lock = threading.Lock()
        self._fd = None
        self._pid = None

    def ensure_running(self):
        """Make sure that resource tracker process is running.

        This can be run from any process.  Usually a child process will use
        the resource created by its parent."""
        pass

    def _check_alive(self):
        """Check for the existence of the resource tracker process."""
        pass

    def register(self, name, rtype):
        """Register a named resource, and increment its refcount."""
        pass

    def unregister(self, name, rtype):
        """Unregister a named resource with resource tracker."""
        pass

    def maybe_unlink(self, name, rtype):
        """Decrement the refcount of a resource, and delete it if it hits 0"""
        pass
_resource_tracker = ResourceTracker()
ensure_running = _resource_tracker.ensure_running
register = _resource_tracker.register
maybe_unlink = _resource_tracker.maybe_unlink
unregister = _resource_tracker.unregister
getfd = _resource_tracker.getfd

def main(fd, verbose=0):
    """Run resource tracker."""
    pass