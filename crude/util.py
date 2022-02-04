"""Utils"""

from contextlib import suppress

ignore_import_problems = suppress(ImportError, ModuleNotFoundError)
