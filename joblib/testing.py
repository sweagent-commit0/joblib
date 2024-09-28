"""
Helper for testing.
"""
import sys
import warnings
import os.path
import re
import subprocess
import threading
import pytest
import _pytest
raises = pytest.raises
warns = pytest.warns
SkipTest = _pytest.runner.Skipped
skipif = pytest.mark.skipif
fixture = pytest.fixture
parametrize = pytest.mark.parametrize
timeout = pytest.mark.timeout
xfail = pytest.mark.xfail
param = pytest.param

def warnings_to_stdout():
    """ Redirect all warnings to stdout.
    """
    pass

def check_subprocess_call(cmd, timeout=5, stdout_regex=None, stderr_regex=None):
    """Runs a command in a subprocess with timeout in seconds.

    A SIGTERM is sent after `timeout` and if it does not terminate, a
    SIGKILL is sent after `2 * timeout`.

    Also checks returncode is zero, stdout if stdout_regex is set, and
    stderr if stderr_regex is set.
    """
    pass