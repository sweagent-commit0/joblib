"""Classes and functions for managing compressors."""
import io
import zlib
from joblib.backports import LooseVersion
try:
    from threading import RLock
except ImportError:
    from dummy_threading import RLock
try:
    import bz2
except ImportError:
    bz2 = None
try:
    import lz4
    from lz4.frame import LZ4FrameFile
except ImportError:
    lz4 = None
try:
    import lzma
except ImportError:
    lzma = None
LZ4_NOT_INSTALLED_ERROR = 'LZ4 is not installed. Install it with pip: https://python-lz4.readthedocs.io/'
_COMPRESSORS = {}
_ZFILE_PREFIX = b'ZF'
_ZLIB_PREFIX = b'x'
_GZIP_PREFIX = b'\x1f\x8b'
_BZ2_PREFIX = b'BZ'
_XZ_PREFIX = b'\xfd7zXZ'
_LZMA_PREFIX = b']\x00'
_LZ4_PREFIX = b'\x04"M\x18'

def register_compressor(compressor_name, compressor, force=False):
    """Register a new compressor.

    Parameters
    ----------
    compressor_name: str.
        The name of the compressor.
    compressor: CompressorWrapper
        An instance of a 'CompressorWrapper'.
    """
    pass

class CompressorWrapper:
    """A wrapper around a compressor file object.

    Attributes
    ----------
    obj: a file-like object
        The object must implement the buffer interface and will be used
        internally to compress/decompress the data.
    prefix: bytestring
        A bytestring corresponding to the magic number that identifies the
        file format associated to the compressor.
    extension: str
        The file extension used to automatically select this compressor during
        a dump to a file.
    """

    def __init__(self, obj, prefix=b'', extension=''):
        self.fileobj_factory = obj
        self.prefix = prefix
        self.extension = extension

    def compressor_file(self, fileobj, compresslevel=None):
        """Returns an instance of a compressor file object."""
        pass

    def decompressor_file(self, fileobj):
        """Returns an instance of a decompressor file object."""
        pass

class BZ2CompressorWrapper(CompressorWrapper):
    prefix = _BZ2_PREFIX
    extension = '.bz2'

    def __init__(self):
        if bz2 is not None:
            self.fileobj_factory = bz2.BZ2File
        else:
            self.fileobj_factory = None

    def compressor_file(self, fileobj, compresslevel=None):
        """Returns an instance of a compressor file object."""
        pass

    def decompressor_file(self, fileobj):
        """Returns an instance of a decompressor file object."""
        pass

class LZMACompressorWrapper(CompressorWrapper):
    prefix = _LZMA_PREFIX
    extension = '.lzma'
    _lzma_format_name = 'FORMAT_ALONE'

    def __init__(self):
        if lzma is not None:
            self.fileobj_factory = lzma.LZMAFile
            self._lzma_format = getattr(lzma, self._lzma_format_name)
        else:
            self.fileobj_factory = None

    def compressor_file(self, fileobj, compresslevel=None):
        """Returns an instance of a compressor file object."""
        pass

    def decompressor_file(self, fileobj):
        """Returns an instance of a decompressor file object."""
        pass

class XZCompressorWrapper(LZMACompressorWrapper):
    prefix = _XZ_PREFIX
    extension = '.xz'
    _lzma_format_name = 'FORMAT_XZ'

class LZ4CompressorWrapper(CompressorWrapper):
    prefix = _LZ4_PREFIX
    extension = '.lz4'

    def __init__(self):
        if lz4 is not None:
            self.fileobj_factory = LZ4FrameFile
        else:
            self.fileobj_factory = None

    def compressor_file(self, fileobj, compresslevel=None):
        """Returns an instance of a compressor file object."""
        pass

    def decompressor_file(self, fileobj):
        """Returns an instance of a decompressor file object."""
        pass
_MODE_CLOSED = 0
_MODE_READ = 1
_MODE_READ_EOF = 2
_MODE_WRITE = 3
_BUFFER_SIZE = 8192

class BinaryZlibFile(io.BufferedIOBase):
    """A file object providing transparent zlib (de)compression.

    TODO python2_drop: is it still needed since we dropped Python 2 support A
    BinaryZlibFile can act as a wrapper for an existing file object, or refer
    directly to a named file on disk.

    Note that BinaryZlibFile provides only a *binary* file interface: data read
    is returned as bytes, and data to be written should be given as bytes.

    This object is an adaptation of the BZ2File object and is compatible with
    versions of python >= 2.7.

    If filename is a str or bytes object, it gives the name
    of the file to be opened. Otherwise, it should be a file object,
    which will be used to read or write the compressed data.

    mode can be 'rb' for reading (default) or 'wb' for (over)writing

    If mode is 'wb', compresslevel can be a number between 1
    and 9 specifying the level of compression: 1 produces the least
    compression, and 9 produces the most compression. 3 is the default.
    """
    wbits = zlib.MAX_WBITS

    def __init__(self, filename, mode='rb', compresslevel=3):
        self._lock = RLock()
        self._fp = None
        self._closefp = False
        self._mode = _MODE_CLOSED
        self._pos = 0
        self._size = -1
        self.compresslevel = compresslevel
        if not isinstance(compresslevel, int) or not 1 <= compresslevel <= 9:
            raise ValueError("'compresslevel' must be an integer between 1 and 9. You provided 'compresslevel={}'".format(compresslevel))
        if mode == 'rb':
            self._mode = _MODE_READ
            self._decompressor = zlib.decompressobj(self.wbits)
            self._buffer = b''
            self._buffer_offset = 0
        elif mode == 'wb':
            self._mode = _MODE_WRITE
            self._compressor = zlib.compressobj(self.compresslevel, zlib.DEFLATED, self.wbits, zlib.DEF_MEM_LEVEL, 0)
        else:
            raise ValueError('Invalid mode: %r' % (mode,))
        if isinstance(filename, str):
            self._fp = io.open(filename, mode)
            self._closefp = True
        elif hasattr(filename, 'read') or hasattr(filename, 'write'):
            self._fp = filename
        else:
            raise TypeError('filename must be a str or bytes object, or a file')

    def close(self):
        """Flush and close the file.

        May be called more than once without error. Once the file is
        closed, any other operation on it will raise a ValueError.
        """
        pass

    @property
    def closed(self):
        """True if this file is closed."""
        pass

    def fileno(self):
        """Return the file descriptor for the underlying file."""
        pass

    def seekable(self):
        """Return whether the file supports seeking."""
        pass

    def readable(self):
        """Return whether the file was opened for reading."""
        pass

    def writable(self):
        """Return whether the file was opened for writing."""
        pass

    def read(self, size=-1):
        """Read up to size uncompressed bytes from the file.

        If size is negative or omitted, read until EOF is reached.
        Returns b'' if the file is already at EOF.
        """
        pass

    def readinto(self, b):
        """Read up to len(b) bytes into b.

        Returns the number of bytes read (0 for EOF).
        """
        pass

    def write(self, data):
        """Write a byte string to the file.

        Returns the number of uncompressed bytes written, which is
        always len(data). Note that due to buffering, the file on disk
        may not reflect the data written until close() is called.
        """
        pass

    def seek(self, offset, whence=0):
        """Change the file position.

        The new position is specified by offset, relative to the
        position indicated by whence. Values for whence are:

            0: start of stream (default); offset must not be negative
            1: current stream position
            2: end of stream; offset must not be positive

        Returns the new file position.

        Note that seeking is emulated, so depending on the parameters,
        this operation may be extremely slow.
        """
        pass

    def tell(self):
        """Return the current file position."""
        pass

class ZlibCompressorWrapper(CompressorWrapper):

    def __init__(self):
        CompressorWrapper.__init__(self, obj=BinaryZlibFile, prefix=_ZLIB_PREFIX, extension='.z')

class BinaryGzipFile(BinaryZlibFile):
    """A file object providing transparent gzip (de)compression.

    If filename is a str or bytes object, it gives the name
    of the file to be opened. Otherwise, it should be a file object,
    which will be used to read or write the compressed data.

    mode can be 'rb' for reading (default) or 'wb' for (over)writing

    If mode is 'wb', compresslevel can be a number between 1
    and 9 specifying the level of compression: 1 produces the least
    compression, and 9 produces the most compression. 3 is the default.
    """
    wbits = 31

class GzipCompressorWrapper(CompressorWrapper):

    def __init__(self):
        CompressorWrapper.__init__(self, obj=BinaryGzipFile, prefix=_GZIP_PREFIX, extension='.gz')