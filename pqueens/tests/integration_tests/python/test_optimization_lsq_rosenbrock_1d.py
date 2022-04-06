import os
import pickle

import numpy as np
import pytest

from pqueens.main import main


@pytest.mark.integration_tests
def test_optimization_lsq_rosenbrock_1d(inputdir, tmpdir):
    """Test special case for optimization iterator with least squares.

    Special case: 1 unknown but 2 residuals
    """
    arguments = [
        '--input=' + os.path.join(inputdir, 'optimization_lsq_rosenbrock_1d.json'),
        '--output=' + str(tmpdir),
    ]

    main(arguments)
    result_file = str(tmpdir) + '/' + 'ResRosenbrock1DLSQ.pickle'
    with open(result_file, 'rb') as handle:
        results = pickle.load(handle)
    np.testing.assert_allclose(results.x, np.array([+1.0]))
    np.testing.assert_allclose(results.fun, np.array([+0.0, +0.0]))