import os
import sys
import signal
import pickle
from io import BytesIO
from multiprocessing import util, process
from multiprocessing.connection import wait
from multiprocessing.context import set_spawning_popen
from . import reduction, resource_tracker, spawn
__all__ = ['Popen']

class _DupFd:

    def __init__(self, fd):
        self.fd = reduction._mk_inheritable(fd)

class Popen:
    method = 'loky'
    DupFd = _DupFd

    def __init__(self, process_obj):
        sys.stdout.flush()
        sys.stderr.flush()
        self.returncode = None
        self._fds = []
        self._launch(process_obj)
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('Command line parser')
    parser.add_argument('--pipe', type=int, required=True, help='File handle for the pipe')
    parser.add_argument('--process-name', type=str, default=None, help='Identifier for debugging purpose')
    args = parser.parse_args()
    info = {}
    exitcode = 1
    try:
        with os.fdopen(args.pipe, 'rb') as from_parent:
            process.current_process()._inheriting = True
            try:
                prep_data = pickle.load(from_parent)
                spawn.prepare(prep_data)
                process_obj = pickle.load(from_parent)
            finally:
                del process.current_process()._inheriting
        exitcode = process_obj._bootstrap()
    except Exception:
        print('\n\n' + '-' * 80)
        print(f'{args.process_name} failed with traceback: ')
        print('-' * 80)
        import traceback
        print(traceback.format_exc())
        print('\n' + '-' * 80)
    finally:
        if from_parent is not None:
            from_parent.close()
        sys.exit(exitcode)