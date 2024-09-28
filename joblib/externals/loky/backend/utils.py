import os
import sys
import time
import errno
import signal
import warnings
import subprocess
import traceback
try:
    import psutil
except ImportError:
    psutil = None

def kill_process_tree(process, use_psutil=True):
    """Terminate process and its descendants with SIGKILL"""
    pass

def _kill_process_tree_without_psutil(process):
    """Terminate a process and its descendants."""
    pass

def _posix_recursive_kill(pid):
    """Recursively kill the descendants of a process before killing it."""
    pass

def get_exitcodes_terminated_worker(processes):
    """Return a formatted string with the exitcodes of terminated workers.

    If necessary, wait (up to .25s) for the system to correctly set the
    exitcode of one terminated worker.
    """
    pass

def _format_exitcodes(exitcodes):
    """Format a list of exit code with names of the signals if possible"""
    pass