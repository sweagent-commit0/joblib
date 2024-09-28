"""
My own variation on function-specific inspect-like features.
"""
import inspect
import warnings
import re
import os
import collections
from itertools import islice
from tokenize import open as open_py_source
from .logger import pformat
full_argspec_fields = 'args varargs varkw defaults kwonlyargs kwonlydefaults annotations'
full_argspec_type = collections.namedtuple('FullArgSpec', full_argspec_fields)

def get_func_code(func):
    """ Attempts to retrieve a reliable function code hash.

        The reason we don't use inspect.getsource is that it caches the
        source, whereas we want this to be modified on the fly when the
        function is modified.

        Returns
        -------
        func_code: string
            The function code
        source_file: string
            The path to the file in which the function is defined.
        first_line: int
            The first line of the code in the source file.

        Notes
        ------
        This function does a bit more magic than inspect, and is thus
        more robust.
    """
    pass

def _clean_win_chars(string):
    """Windows cannot encode some characters in filename."""
    pass

def get_func_name(func, resolv_alias=True, win_characters=True):
    """ Return the function import path (as a list of module names), and
        a name for the function.

        Parameters
        ----------
        func: callable
            The func to inspect
        resolv_alias: boolean, optional
            If true, possible local aliases are indicated.
        win_characters: boolean, optional
            If true, substitute special characters using urllib.quote
            This is useful in Windows, as it cannot encode some filenames
    """
    pass

def _signature_str(function_name, arg_sig):
    """Helper function to output a function signature"""
    pass

def _function_called_str(function_name, args, kwargs):
    """Helper function to output a function call"""
    pass

def filter_args(func, ignore_lst, args=(), kwargs=dict()):
    """ Filters the given args and kwargs using a list of arguments to
        ignore, and a function specification.

        Parameters
        ----------
        func: callable
            Function giving the argument specification
        ignore_lst: list of strings
            List of arguments to ignore (either a name of an argument
            in the function spec, or '*', or '**')
        *args: list
            Positional arguments passed to the function.
        **kwargs: dict
            Keyword arguments passed to the function

        Returns
        -------
        filtered_args: list
            List of filtered positional and keyword arguments.
    """
    pass

def format_call(func, args, kwargs, object_name='Memory'):
    """ Returns a nicely formatted statement displaying the function
        call with the given arguments.
    """
    pass