from __future__ import print_function
import os

__all__ = ['create_dir']

def create_dir(dirpath) -> None:
    """
    Creates nested directories if directory path does not exist.
    """
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
