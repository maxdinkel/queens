import os
import pickle

import numpy as np
import pandas as pd
import pytest
from mock import patch

from pqueens.iterators.metropolis_hastings_iterator import MetropolisHastingsIterator

# fmt: on
from pqueens.iterators.sequential_monte_carlo_iterator import SequentialMonteCarloIterator
from pqueens.main import main

# fmt: off
from pqueens.tests.integration_tests.example_simulator_functions.gaussian_logpdf import (
    gaussian_2d,
    gaussian_2d_logpdf,
)
from pqueens.utils import injector


@pytest.mark.integration_tests
def test_metropolis_hastings_multivariate_gaussian(inputdir, tmpdir, dummy_data):
    """Test case for metropolis hastings iterator."""
    template = os.path.join(inputdir, "metropolis_hastings_multivariate_gaussian.json")
    experimental_data_path = tmpdir
    dir_dict = {"experimental_data_path": experimental_data_path}
    input_file = os.path.join(tmpdir, "multivariate_gaussian_metropolis_hastings_realiz.json")
    injector.inject(dir_dict, template, input_file)
    arguments = [
        '--input=' + input_file,
        '--output=' + str(tmpdir),
    ]

    # mock methods related to likelihood
    with patch.object(SequentialMonteCarloIterator, "eval_log_likelihood", target_density):
        with patch.object(MetropolisHastingsIterator, "eval_log_likelihood", target_density):
            main(arguments)

    result_file = str(tmpdir) + '/' + 'xxx.pickle'
    with open(result_file, 'rb') as handle:
        results = pickle.load(handle)

    # note that the analytical solution would be:
    # posterior mean: [0.29378531 -1.97175141]
    # posterior cov: [[0.42937853 0.00282486] [0.00282486 0.00988701]]
    # however, we only have a very inaccurate approximation here:

    np.testing.assert_allclose(
        results['mean'], np.array([[0.7240107551260684, -2.045891088599629]])
    )
    np.testing.assert_allclose(
        results['cov'],
        np.array(
            [
                [
                    [0.30698538649168755, -0.027059991075557278],
                    [-0.027059991075557278, 0.004016365725389411],
                ]
            ]
        ),
    )


def target_density(self, samples):
    samples = np.atleast_2d(samples)
    log_likelihood = gaussian_2d_logpdf(samples).reshape(-1, 1)

    return log_likelihood


@pytest.fixture()
def dummy_data(tmpdir):
    # generate 10 samples from the same gaussian
    samples = gaussian_2d.draw(10)
    pdf = (gaussian_2d_logpdf(samples))

    pdf = np.array(pdf)

    # write the data to a csv file in tmpdir
    data_dict = {'y_obs': pdf}
    experimental_data_path = os.path.join(tmpdir, 'experimental_data.csv')
    df = pd.DataFrame.from_dict(data_dict)
    df.to_csv(experimental_data_path, index=False)
