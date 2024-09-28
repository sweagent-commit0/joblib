"""Utility function to construct a loky.ReusableExecutor with custom pickler.

This module provides efficient ways of working with data stored in
shared memory with numpy.memmap arrays without inducing any memory
copy between the parent and child processes.
"""
from ._memmapping_reducer import get_memmapping_reducers
from ._memmapping_reducer import TemporaryResourcesManager
from .externals.loky.reusable_executor import _ReusablePoolExecutor
_executor_args = None

class MemmappingExecutor(_ReusablePoolExecutor):

    @classmethod
    def get_memmapping_executor(cls, n_jobs, timeout=300, initializer=None, initargs=(), env=None, temp_folder=None, context_id=None, **backend_args):
        """Factory for ReusableExecutor with automatic memmapping for large
        numpy arrays.
        """
        pass

class _TestingMemmappingExecutor(MemmappingExecutor):
    """Wrapper around ReusableExecutor to ease memmapping testing with Pool
    and Executor. This is only for testing purposes.

    """

    def apply_async(self, func, args):
        """Schedule a func to be run"""
        pass