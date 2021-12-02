import os
import pickle
import numpy as np
import pytest

from pqueens.main import main


@pytest.mark.integration_tests
def test_branin_gauss_bayesian_neural_network(inputdir, tmpdir, expected_mean, expected_var):
    """ Test case for bayesian neural network model """
    arguments = [
        '--input=' + os.path.join(inputdir, 'branin_gauss_bayesian_neural_network.json'),
        '--output=' + str(tmpdir),
    ]

    main(arguments)
    result_file = str(tmpdir) + '/' + 'xxx.pickle'
    with open(result_file, 'rb') as handle:
        results = pickle.load(handle)

    np.testing.assert_array_almost_equal(
        results["raw_output_data"]["mean"], expected_mean, decimal=4
    )
    np.testing.assert_array_almost_equal(
        results["raw_output_data"]["variance"], expected_var, decimal=2
    )


@pytest.fixture()
def expected_mean():
    mean = np.array(
        [
            [
                65.3779063,
                65.44938406,
                44.40122105,
                57.19055642,
                64.8677122,
                65.44937106,
                65.44938677,
                65.44938672,
                65.44865757,
                22.31121954,
            ]
        ]
    )
    return mean.T


@pytest.fixture()
def expected_var():
    var = np.array(
        [
            [
                3.31275871,
                3.31793473,
                2.04479705,
                2.7602009,
                3.27651827,
                3.31793384,
                3.31793497,
                3.31793497,
                3.31788235,
                1.08857106,
            ]
        ]
    )
    return var.T
