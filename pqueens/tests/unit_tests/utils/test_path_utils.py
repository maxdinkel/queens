"""Test path utils."""
from pathlib import Path, PurePath

import pytest

from pqueens.utils.path_utils import (
    PATH_TO_PQUEENS,
    PATH_TO_QUEENS,
    check_if_path_exists,
    create_folder_if_not_existent,
    relative_path_from_pqueens,
    relative_path_from_queens,
)

pytestmark = pytest.mark.unit_tests


@pytest.fixture(name="path_to_queens")
def fixture_path_to_queens():
    """Path to QUEENS."""
    return str(Path(__file__).parent).split("pqueens")[0]


@pytest.fixture(name="path_to_pqueens")
def fixture_path_to_pqueens():
    """Path to pqueens."""
    return str(Path(__file__).parent).split("tests")[0]


def test_path_to_pqueens(path_to_pqueens):
    """Test path to pqueens."""
    assert str(Path(path_to_pqueens).resolve) == str(Path(PATH_TO_PQUEENS).resolve)


def test_path_to_queens(path_to_queens):
    """Test path to queens."""
    assert str(Path(path_to_queens).resolve) == str(Path(PATH_TO_QUEENS).resolve)


def test_check_if_path_exists():
    """Test if path exists."""
    current_folder = str(Path(__file__).parent)
    assert check_if_path_exists(current_folder)


def test_check_if_path_exists_not_existing():
    """Test if path does not exist."""
    test_path = str(Path(__file__).parent) + "_not_existing"
    with pytest.raises(FileNotFoundError):
        check_if_path_exists(test_path)


def test_create_folder_if_not_existent(tmp_path):
    """Test if folder is created."""
    new_path = PurePath(tmp_path, "new/path")
    new_path = create_folder_if_not_existent(new_path)
    assert check_if_path_exists(new_path)


def test_relative_path_from_pqueens():
    """Test relative path from pqueens."""
    current_folder = str(Path(__file__).parent)
    path_from_pqueens = relative_path_from_pqueens("tests/unit_tests/utils")
    assert str(Path(path_from_pqueens).resolve) == str(Path(current_folder).resolve)


def test_relative_path_from_queens():
    """Test relative path from queens."""
    current_folder = str(Path(__file__).parent)
    path_from_queens = relative_path_from_queens("pqueens/tests/unit_tests/utils")
    assert str(Path(path_from_queens).resolve) == str(Path(current_folder).resolve)
