"""
Backends for embarrassingly parallel code.
"""
import gc
import os
import warnings
import threading
import contextlib
from abc import ABCMeta, abstractmethod
from ._utils import _TracebackCapturingWrapper, _retrieve_traceback_capturing_wrapped_call
from ._multiprocessing_helpers import mp
if mp is not None:
    from .pool import MemmappingPool
    from multiprocessing.pool import ThreadPool
    from .executor import get_memmapping_executor
    from .externals.loky import process_executor, cpu_count
    from .externals.loky.process_executor import ShutdownExecutorError

class ParallelBackendBase(metaclass=ABCMeta):
    """Helper abc which defines all methods a ParallelBackend must implement"""
    supports_inner_max_num_threads = False
    supports_retrieve_callback = False
    default_n_jobs = 1
    nesting_level = None

    def __init__(self, nesting_level=None, inner_max_num_threads=None, **kwargs):
        super().__init__(**kwargs)
        self.nesting_level = nesting_level
        self.inner_max_num_threads = inner_max_num_threads
    MAX_NUM_THREADS_VARS = ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'BLIS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMBA_NUM_THREADS', 'NUMEXPR_NUM_THREADS']
    TBB_ENABLE_IPC_VAR = 'ENABLE_IPC'

    @abstractmethod
    def effective_n_jobs(self, n_jobs):
        """Determine the number of jobs that can actually run in parallel

        n_jobs is the number of workers requested by the callers. Passing
        n_jobs=-1 means requesting all available workers for instance matching
        the number of CPU cores on the worker host(s).

        This method should return a guesstimate of the number of workers that
        can actually perform work concurrently. The primary use case is to make
        it possible for the caller to know in how many chunks to slice the
        work.

        In general working on larger data chunks is more efficient (less
        scheduling overhead and better use of CPU cache prefetching heuristics)
        as long as all the workers have enough work to do.
        """
        pass

    @abstractmethod
    def apply_async(self, func, callback=None):
        """Schedule a func to be run"""
        pass

    def retrieve_result_callback(self, out):
        """Called within the callback function passed in apply_async.

        The argument of this function is the argument given to a callback in
        the considered backend. It is supposed to return the outcome of a task
        if it succeeded or raise the exception if it failed.
        """
        pass

    def configure(self, n_jobs=1, parallel=None, prefer=None, require=None, **backend_args):
        """Reconfigure the backend and return the number of workers.

        This makes it possible to reuse an existing backend instance for
        successive independent calls to Parallel with different parameters.
        """
        pass

    def start_call(self):
        """Call-back method called at the beginning of a Parallel call"""
        pass

    def stop_call(self):
        """Call-back method called at the end of a Parallel call"""
        pass

    def terminate(self):
        """Shutdown the workers and free the shared memory."""
        pass

    def compute_batch_size(self):
        """Determine the optimal batch size"""
        pass

    def batch_completed(self, batch_size, duration):
        """Callback indicate how long it took to run a batch"""
        pass

    def get_exceptions(self):
        """List of exception types to be captured."""
        pass

    def abort_everything(self, ensure_ready=True):
        """Abort any running tasks

        This is called when an exception has been raised when executing a task
        and all the remaining tasks will be ignored and can therefore be
        aborted to spare computation resources.

        If ensure_ready is True, the backend should be left in an operating
        state as future tasks might be re-submitted via that same backend
        instance.

        If ensure_ready is False, the implementer of this method can decide
        to leave the backend in a closed / terminated state as no new task
        are expected to be submitted to this backend.

        Setting ensure_ready to False is an optimization that can be leveraged
        when aborting tasks via killing processes from a local process pool
        managed by the backend it-self: if we expect no new tasks, there is no
        point in re-creating new workers.
        """
        pass

    def get_nested_backend(self):
        """Backend instance to be used by nested Parallel calls.

        By default a thread-based backend is used for the first level of
        nesting. Beyond, switch to sequential backend to avoid spawning too
        many threads on the host.
        """
        pass

    @contextlib.contextmanager
    def retrieval_context(self):
        """Context manager to manage an execution context.

        Calls to Parallel.retrieve will be made inside this context.

        By default, this does nothing. It may be useful for subclasses to
        handle nested parallelism. In particular, it may be required to avoid
        deadlocks if a backend manages a fixed number of workers, when those
        workers may be asked to do nested Parallel calls. Without
        'retrieval_context' this could lead to deadlock, as all the workers
        managed by the backend may be "busy" waiting for the nested parallel
        calls to finish, but the backend has no free workers to execute those
        tasks.
        """
        pass

    def _prepare_worker_env(self, n_jobs):
        """Return environment variables limiting threadpools in external libs.

        This function return a dict containing environment variables to pass
        when creating a pool of process. These environment variables limit the
        number of threads to `n_threads` for OpenMP, MKL, Accelerated and
        OpenBLAS libraries in the child processes.
        """
        pass

class SequentialBackend(ParallelBackendBase):
    """A ParallelBackend which will execute all batches sequentially.

    Does not use/create any threading objects, and hence has minimal
    overhead. Used when n_jobs == 1.
    """
    uses_threads = True
    supports_timeout = False
    supports_retrieve_callback = False
    supports_sharedmem = True

    def effective_n_jobs(self, n_jobs):
        """Determine the number of jobs which are going to run in parallel"""
        pass

    def apply_async(self, func, callback=None):
        """Schedule a func to be run"""
        pass

class PoolManagerMixin(object):
    """A helper class for managing pool of workers."""
    _pool = None

    def effective_n_jobs(self, n_jobs):
        """Determine the number of jobs which are going to run in parallel"""
        pass

    def terminate(self):
        """Shutdown the process or thread pool"""
        pass

    def _get_pool(self):
        """Used by apply_async to make it possible to implement lazy init"""
        pass

    def apply_async(self, func, callback=None):
        """Schedule a func to be run"""
        pass

    def retrieve_result_callback(self, out):
        """Mimic concurrent.futures results, raising an error if needed."""
        pass

    def abort_everything(self, ensure_ready=True):
        """Shutdown the pool and restart a new one with the same parameters"""
        pass

class AutoBatchingMixin(object):
    """A helper class for automagically batching jobs."""
    MIN_IDEAL_BATCH_DURATION = 0.2
    MAX_IDEAL_BATCH_DURATION = 2
    _DEFAULT_EFFECTIVE_BATCH_SIZE = 1
    _DEFAULT_SMOOTHED_BATCH_DURATION = 0.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._effective_batch_size = self._DEFAULT_EFFECTIVE_BATCH_SIZE
        self._smoothed_batch_duration = self._DEFAULT_SMOOTHED_BATCH_DURATION

    def compute_batch_size(self):
        """Determine the optimal batch size"""
        pass

    def batch_completed(self, batch_size, duration):
        """Callback indicate how long it took to run a batch"""
        pass

    def reset_batch_stats(self):
        """Reset batch statistics to default values.

        This avoids interferences with future jobs.
        """
        pass

class ThreadingBackend(PoolManagerMixin, ParallelBackendBase):
    """A ParallelBackend which will use a thread pool to execute batches in.

    This is a low-overhead backend but it suffers from the Python Global
    Interpreter Lock if the called function relies a lot on Python objects.
    Mostly useful when the execution bottleneck is a compiled extension that
    explicitly releases the GIL (for instance a Cython loop wrapped in a "with
    nogil" block or an expensive call to a library such as NumPy).

    The actual thread pool is lazily initialized: the actual thread pool
    construction is delayed to the first call to apply_async.

    ThreadingBackend is used as the default backend for nested calls.
    """
    supports_retrieve_callback = True
    uses_threads = True
    supports_sharedmem = True

    def configure(self, n_jobs=1, parallel=None, **backend_args):
        """Build a process or thread pool and return the number of workers"""
        pass

    def _get_pool(self):
        """Lazily initialize the thread pool

        The actual pool of worker threads is only initialized at the first
        call to apply_async.
        """
        pass

class MultiprocessingBackend(PoolManagerMixin, AutoBatchingMixin, ParallelBackendBase):
    """A ParallelBackend which will use a multiprocessing.Pool.

    Will introduce some communication and memory overhead when exchanging
    input and output data with the with the worker Python processes.
    However, does not suffer from the Python Global Interpreter Lock.
    """
    supports_retrieve_callback = True
    supports_return_generator = False

    def effective_n_jobs(self, n_jobs):
        """Determine the number of jobs which are going to run in parallel.

        This also checks if we are attempting to create a nested parallel
        loop.
        """
        pass

    def configure(self, n_jobs=1, parallel=None, prefer=None, require=None, **memmappingpool_args):
        """Build a process or thread pool and return the number of workers"""
        pass

    def terminate(self):
        """Shutdown the process or thread pool"""
        pass

class LokyBackend(AutoBatchingMixin, ParallelBackendBase):
    """Managing pool of workers with loky instead of multiprocessing."""
    supports_retrieve_callback = True
    supports_inner_max_num_threads = True

    def configure(self, n_jobs=1, parallel=None, prefer=None, require=None, idle_worker_timeout=300, **memmappingexecutor_args):
        """Build a process executor and return the number of workers"""
        pass

    def effective_n_jobs(self, n_jobs):
        """Determine the number of jobs which are going to run in parallel"""
        pass

    def apply_async(self, func, callback=None):
        """Schedule a func to be run"""
        pass

    def abort_everything(self, ensure_ready=True):
        """Shutdown the workers and restart a new one with the same parameters
        """
        pass

class FallbackToBackend(Exception):
    """Raised when configuration should fallback to another backend"""

    def __init__(self, backend):
        self.backend = backend

def inside_dask_worker():
    """Check whether the current function is executed inside a Dask worker.
    """
    pass