import os
import sys
import tempfile
import threading
import _multiprocessing
from time import time as _time
from multiprocessing import process, util
from multiprocessing.context import assert_spawning
from . import resource_tracker
__all__ = ['Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Condition', 'Event']
try:
    from _multiprocessing import SemLock as _SemLock
    from _multiprocessing import sem_unlink
except ImportError:
    raise ImportError('This platform lacks a functioning sem_open implementation, therefore, the required synchronization primitives needed will not function, see issue 3770.')
RECURSIVE_MUTEX, SEMAPHORE = range(2)
SEM_VALUE_MAX = _multiprocessing.SemLock.SEM_VALUE_MAX

class SemLock:
    _rand = tempfile._RandomNameSequence()

    def __init__(self, kind, value, maxvalue, name=None):
        unlink_now = False
        if name is None:
            for _ in range(100):
                try:
                    self._semlock = _SemLock(kind, value, maxvalue, SemLock._make_name(), unlink_now)
                except FileExistsError:
                    pass
                else:
                    break
            else:
                raise FileExistsError('cannot find name for semaphore')
        else:
            self._semlock = _SemLock(kind, value, maxvalue, name, unlink_now)
        self.name = name
        util.debug(f'created semlock with handle {self._semlock.handle} and name "{self.name}"')
        self._make_methods()

        def _after_fork(obj):
            obj._semlock._after_fork()
        util.register_after_fork(self, _after_fork)
        resource_tracker.register(self._semlock.name, 'semlock')
        util.Finalize(self, SemLock._cleanup, (self._semlock.name,), exitpriority=0)

    def __enter__(self):
        return self._semlock.acquire()

    def __exit__(self, *args):
        return self._semlock.release()

    def __getstate__(self):
        assert_spawning(self)
        sl = self._semlock
        h = sl.handle
        return (h, sl.kind, sl.maxvalue, sl.name)

    def __setstate__(self, state):
        self._semlock = _SemLock._rebuild(*state)
        util.debug(f'recreated blocker with handle {state[0]!r} and name "{state[3]}"')
        self._make_methods()

class Semaphore(SemLock):

    def __init__(self, value=1):
        SemLock.__init__(self, SEMAPHORE, value, SEM_VALUE_MAX)

    def __repr__(self):
        try:
            value = self._semlock._get_value()
        except Exception:
            value = 'unknown'
        return f'<{self.__class__.__name__}(value={value})>'

class BoundedSemaphore(Semaphore):

    def __init__(self, value=1):
        SemLock.__init__(self, SEMAPHORE, value, value)

    def __repr__(self):
        try:
            value = self._semlock._get_value()
        except Exception:
            value = 'unknown'
        return f'<{self.__class__.__name__}(value={value}, maxvalue={self._semlock.maxvalue})>'

class Lock(SemLock):

    def __init__(self):
        super().__init__(SEMAPHORE, 1, 1)

    def __repr__(self):
        try:
            if self._semlock._is_mine():
                name = process.current_process().name
                if threading.current_thread().name != 'MainThread':
                    name = f'{name}|{threading.current_thread().name}'
            elif self._semlock._get_value() == 1:
                name = 'None'
            elif self._semlock._count() > 0:
                name = 'SomeOtherThread'
            else:
                name = 'SomeOtherProcess'
        except Exception:
            name = 'unknown'
        return f'<{self.__class__.__name__}(owner={name})>'

class RLock(SemLock):

    def __init__(self):
        super().__init__(RECURSIVE_MUTEX, 1, 1)

    def __repr__(self):
        try:
            if self._semlock._is_mine():
                name = process.current_process().name
                if threading.current_thread().name != 'MainThread':
                    name = f'{name}|{threading.current_thread().name}'
                count = self._semlock._count()
            elif self._semlock._get_value() == 1:
                name, count = ('None', 0)
            elif self._semlock._count() > 0:
                name, count = ('SomeOtherThread', 'nonzero')
            else:
                name, count = ('SomeOtherProcess', 'nonzero')
        except Exception:
            name, count = ('unknown', 'unknown')
        return f'<{self.__class__.__name__}({name}, {count})>'

class Condition:

    def __init__(self, lock=None):
        self._lock = lock or RLock()
        self._sleeping_count = Semaphore(0)
        self._woken_count = Semaphore(0)
        self._wait_semaphore = Semaphore(0)
        self._make_methods()

    def __getstate__(self):
        assert_spawning(self)
        return (self._lock, self._sleeping_count, self._woken_count, self._wait_semaphore)

    def __setstate__(self, state):
        self._lock, self._sleeping_count, self._woken_count, self._wait_semaphore = state
        self._make_methods()

    def __enter__(self):
        return self._lock.__enter__()

    def __exit__(self, *args):
        return self._lock.__exit__(*args)

    def __repr__(self):
        try:
            num_waiters = self._sleeping_count._semlock._get_value() - self._woken_count._semlock._get_value()
        except Exception:
            num_waiters = 'unknown'
        return f'<{self.__class__.__name__}({self._lock}, {num_waiters})>'

class Event:

    def __init__(self):
        self._cond = Condition(Lock())
        self._flag = Semaphore(0)