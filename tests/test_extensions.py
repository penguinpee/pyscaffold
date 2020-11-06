import argparse
import sys

import pytest

from pyscaffold import extensions
from pyscaffold.exceptions import ErrorLoadingExtension

from .extensions import __name__ as test_extensions_pkg
from .extensions.helpers import make_extension

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import EntryPoint  # pragma: no cover
else:
    from importlib_metadata import EntryPoint  # pragma: no cover


def test_extension():
    parser = argparse.ArgumentParser()
    extension = make_extension("MyExtension")
    extension.augment_cli(parser)
    opts = vars(parser.parse_args(["--my-extension"]))
    assert opts["extensions"] == [extension]


def test_extension_append():
    parser = argparse.ArgumentParser()
    extension1 = make_extension("MyExtension1")
    extension2 = make_extension("MyExtension2")
    parser.set_defaults(extensions=[extension1])

    extension2.augment_cli(parser)
    opts = vars(parser.parse_args(["--my-extension2"]))
    assert opts["extensions"] == [extension1, extension2]


def test_include():
    parser = argparse.ArgumentParser()
    my_extensions = [make_extension(f"MyExtension{n}") for n in range(7)]
    parser.add_argument("--opt", nargs=0, action=extensions.include(*my_extensions))
    opts = vars(parser.parse_args(["--opt"]))
    assert opts["extensions"] == my_extensions


def test_store_with():
    parser = argparse.ArgumentParser()
    my_extensions = [make_extension(f"MyExtension{n}") for n in range(7)]
    parser.add_argument("--opt", action=extensions.store_with(*my_extensions))
    opts = vars(parser.parse_args(["--opt", "42"]))
    assert opts["extensions"] == my_extensions
    assert opts["opt"] == "42"


def test_store_with_type():
    parser = argparse.ArgumentParser()
    my_extensions = [make_extension(f"MyExtension{n}") for n in range(7)]
    parser.add_argument("--opt", type=int, action=extensions.store_with(*my_extensions))
    opts = vars(parser.parse_args(["--opt", "42"]))
    assert opts["extensions"] == my_extensions
    assert opts["opt"] == 42


def test_load_from_entry_point__error():
    # This module does not exist, so Python will have some trouble loading it
    # EntryPoint(name, value, group)
    fake = EntryPoint("fake", "pyscaffoldext.SOOOOO___fake___:Fake", "pyscaffold.cli")
    with pytest.raises(ErrorLoadingExtension):
        extensions.load_from_entry_point(fake)


def test_load_from_entry_point__old_api():
    # The following module/class exists but uses an old version of the extensions API
    # therefore, we should have a meaningful error when trying to load it.
    entry = f"{test_extensions_pkg}.incompatible_v3_api_fake_extension:FakeExtension"
    fake = EntryPoint("fake", entry, "pyscaffold.cli")
    with pytest.raises(ErrorLoadingExtension):
        extensions.load_from_entry_point(fake)
