"""TODO_doc."""

import pickle
from pathlib import Path

import numpy as np
import pytest

from pqueens import run


def test_optimization_lsq_parabula(inputdir, tmp_path):
    """Test special case for optimization iterator with the least squares.

    Special case: 1 unknown and 1 residual.
    """
    run(inputdir.joinpath('optimization_lsq_parabula.yml'), tmp_path)

    result_file = tmp_path.joinpath('ParabulaResLSQ.pickle')
    with open(result_file, 'rb') as handle:
        results = pickle.load(handle)
    np.testing.assert_allclose(results.x, np.array([+0.3]))
    np.testing.assert_allclose(results.fun, np.array([+0.0]))
