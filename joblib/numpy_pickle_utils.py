"""Utilities for fast persistence of big data, with optional compression."""
import pickle
import io
import sys
import warnings
import contextlib
from .compressor import _ZFILE_PREFIX
from .compressor import _COMPRESSORS
try:
    import numpy as np
except ImportError:
    np = None
Unpickler = pickle._Unpickler
Pickler = pickle._Pickler
xrange = range
try:
    import bz2
except ImportError:
    bz2 = None
_IO_BUFFER_SIZE = 1024 ** 2

def _is_raw_file(fileobj):
    """Check if fileobj is a raw file object, e.g created with open."""
    pass

def _is_numpy_array_byte_order_mismatch(array):
    """Check if numpy array is having byte order mismatch"""
    pass

def _ensure_native_byte_order(array):
    """Use the byte order of the host while preserving values

    Does nothing if array already uses the system byte order.
    """
    pass

def _detect_compressor(fileobj):
    """Return the compressor matching fileobj.

    Parameters
    ----------
    fileobj: file object

    Returns
    -------
    str in {'zlib', 'gzip', 'bz2', 'lzma', 'xz', 'compat', 'not-compressed'}
    """
    pass

def _buffered_read_file(fobj):
    """Return a buffered version of a read file object."""
    pass

def _buffered_write_file(fobj):
    """Return a buffered version of a write file object."""
    pass

@contextlib.contextmanager
def _read_fileobject(fileobj, filename, mmap_mode=None):
    """Utility function opening the right fileobject from a filename.

    The magic number is used to choose between the type of file object to open:
    * regular file object (default)
    * zlib file object
    * gzip file object
    * bz2 file object
    * lzma file object (for xz and lzma compressor)

    Parameters
    ----------
    fileobj: file object
    compressor: str in {'zlib', 'gzip', 'bz2', 'lzma', 'xz', 'compat',
                        'not-compressed'}
    filename: str
        filename path corresponding to the fileobj parameter.
    mmap_mode: str
        memory map mode that should be used to open the pickle file. This
        parameter is useful to verify that the user is not trying to one with
        compression. Default: None.

    Returns
    -------
        a file like object

    """
    pass

def _write_fileobject(filename, compress=('zlib', 3)):
    """Return the right compressor file object in write mode."""
    pass
BUFFER_SIZE = 2 ** 18

def _read_bytes(fp, size, error_template='ran out of data'):
    """Read from file-like object until size bytes are read.

    TODO python2_drop: is it still needed? The docstring mentions python 2.6
    and it looks like this can be at least simplified ...

    Raises ValueError if not EOF is encountered before size bytes are read.
    Non-blocking objects only supported if they derive from io objects.

    Required as e.g. ZipExtFile in python 2.6 can return less data than
    requested.

    This function was taken from numpy/lib/format.py in version 1.10.2.

    Parameters
    ----------
    fp: file-like object
    size: int
    error_template: str

    Returns
    -------
    a bytes object
        The data read in bytes.

    """
    pass