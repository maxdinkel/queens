"""Test custom errors."""
import pytest

from queens.utils.exceptions import SubprocessError
from queens.utils.run_subprocess import run_subprocess


def test_subprocess_correct_message_construction():
    """Check if SubprocessError message is constructed correctly."""
    command = "dummy command"
    command_output = "dummy command output"
    error_message = "dummy error message"
    additional_message = "additional error message"
    sp_error = SubprocessError.construct_error_from_command(command, command_output, error_message)

    expected_message = (
        "\n\nQUEENS' subprocess wrapper caught the following error:\ndummy"
        " error message\n\n\nwith commandline output:\ndummy command output\n\n\nwhile executing"
        " the command:\ndummy command"
    )
    assert expected_message == str(sp_error)

    expected_message += "\n\nadditional error message"
    sp_error = SubprocessError.construct_error_from_command(
        command, command_output, error_message, additional_message
    )
    assert expected_message == str(sp_error)


def test_subprocess_raises_error():
    """Check if non existing command raises an SubprocessError."""
    with pytest.raises(SubprocessError):
        run_subprocess("NonExistingCommand")