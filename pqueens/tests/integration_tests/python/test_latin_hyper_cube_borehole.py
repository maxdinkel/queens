"""TODO_doc."""

import os
import pickle
from pathlib import Path

import pytest

from pqueens import run


def test_latin_hyper_cube_borehole(inputdir, tmpdir):
    """Test case for latin hyper cube iterator."""
    run(Path(Path(inputdir, 'latin_hyper_cube_borehole.yml')), Path(tmpdir))

    result_file = str(tmpdir) + '/' + 'xxx.pickle'
    with open(result_file, 'rb') as handle:
        results = pickle.load(handle)
    assert results["mean"] == pytest.approx(62.05240444441511)
    assert results["var"] == pytest.approx(1371.7554224384000)
