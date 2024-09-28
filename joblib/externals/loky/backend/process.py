import sys
from multiprocessing.context import assert_spawning
from multiprocessing.process import BaseProcess

class LokyProcess(BaseProcess):
    _start_method = 'loky'

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, daemon=None, init_main_module=False, env=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self.env = {} if env is None else env
        self.authkey = self.authkey
        self.init_main_module = init_main_module

class LokyInitMainProcess(LokyProcess):
    _start_method = 'loky_init_main'

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, daemon=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon, init_main_module=True)

class AuthenticationKey(bytes):

    def __reduce__(self):
        try:
            assert_spawning(self)
        except RuntimeError:
            raise TypeError('Pickling an AuthenticationKey object is disallowed for security reasons')
        return (AuthenticationKey, (bytes(self),))