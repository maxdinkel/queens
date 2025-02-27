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
"""Tests for cli utils."""

from pathlib import Path

import pytest

from queens.utils.cli import get_cli_options
from queens.utils.exceptions import CLIError


@pytest.fixture(name="debug_flag", params=[True, False])
def fixture_debug_flag(request):
    """Debug flag."""
    return request.param


def test_get_cli_options_no_input():
    """Test if no input is provided."""
    args = ["--output_dir", "output_dir"]
    with pytest.raises(CLIError, match="No input file was provided with option --input"):
        get_cli_options(args)


def test_get_cli_options_no_output():
    """Test if no output is provided."""
    args = ["--input", "input_file"]
    with pytest.raises(
        CLIError, match="No output directory was provided with option --output_dir."
    ):
        get_cli_options(args)


def test_get_cli_options_default_debug():
    """Test if default debug option is set correctly."""
    args = ["--input", "input_file", "--output_dir", "output_dir"]
    _, _, debug = get_cli_options(args)
    assert not debug


def test_get_cli_options_debug(debug_flag):
    """Test if options are read in correctly."""
    args = ["--input", "input_file", "--output_dir", "output_dir", "--debug", str(debug_flag)]
    input_file, output_dir, debug = get_cli_options(args)
    assert input_file == Path("input_file")
    assert output_dir == Path("output_dir")
    assert debug == debug_flag
