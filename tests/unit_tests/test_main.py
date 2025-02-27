#
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (c) 2024-2025, QUEENS contributors.
#
# This file is part of QUEENS.
#
# QUEENS is free software: you can redistribute it and/or modify it under the terms of the GNU
# Lesser General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version. QUEENS is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details. You
# should have received a copy of the GNU Lesser General Public License along with QUEENS. If not,
# see <https://www.gnu.org/licenses/>.
#
"""Test the main module."""

import json
import logging
import sys
from pathlib import Path

import pytest
from mock import patch

from queens.global_settings import GlobalSettings
from queens.main import main, run
from queens.utils.io import load_input_file


@pytest.fixture(name="input_file")
def fixture_input_file(tmp_path):
    """Creating input file."""
    input_file_dict = {"experiment_name": "test_experiment_name", "Iterator": "A"}
    input_file_path = tmp_path / "input_file.yml"
    with open(input_file_path, "w", encoding="utf-8") as stream:
        json.dump(input_file_dict, stream)
    return input_file_path


@pytest.fixture(name="debug_flag", params=[True, False])
def fixture_debug_flag(request):
    """Debug flag."""
    return request.param


def test_get_config_dict_output_dir_fail():
    """Test if config fails for non-existing output directory."""
    with pytest.raises(FileNotFoundError, match="Output directory"):
        GlobalSettings(None, Path("path/that/doesnt/esxits"))


def test_get_config_dict_input_fail(tmp_path):
    """Test if config fails for non-existing input file."""
    input_file = Path("this/does/not/exist")
    with pytest.raises(FileNotFoundError, match="Input file"):
        run(input_file, tmp_path)


def test_get_config_dict_input(input_file):
    """Test if config dict is created properly."""
    input_path = input_file
    config = load_input_file(input_path)
    true_config = {
        "experiment_name": "test_experiment_name",
        "Iterator": "A",
    }
    assert config == true_config


def test_main_greeting_message(caplog):
    """Test if greeting message is provided for in case of no inputs."""
    argv = ["python_file.py"]
    with patch.object(sys, "argv", argv):
        with caplog.at_level(logging.INFO):
            main()
        assert "To use QUEENS run" in caplog.text


def test_main_call(mocker):
    """Test if main calls run properly."""
    run_inputs = ["input", "output", False]
    mock_run = mocker.patch("queens.main.run")
    mocker.patch("queens.main.get_cli_options", return_value=run_inputs)
    argv = ["python_file.py", "input", "output"]
    with patch.object(sys, "argv", argv):
        main()
        mock_run.assert_called_once_with(*run_inputs)
