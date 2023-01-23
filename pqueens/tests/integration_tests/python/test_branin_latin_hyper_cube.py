"""TODO_doc."""

import os
import pickle
from pathlib import Path

import pytest

from pqueens import run


def test_branin_latin_hyper_cube(inputdir, tmpdir):
    """Test case for latin hyper cube iterator."""
    run(Path(Path(inputdir, 'latin_hyper_cube_branin.yml')), Path(tmpdir))

    result_file = str(tmpdir) + '/' + 'xxx.pickle'
    with open(result_file, 'rb') as handle:
        results = pickle.load(handle)
    assert results["mean"] == pytest.approx(53.17279969296224)
    assert results["var"] == pytest.approx(2581.6502630157715)
