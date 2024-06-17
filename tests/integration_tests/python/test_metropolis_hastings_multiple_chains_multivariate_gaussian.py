"""TODO_doc."""

import numpy as np
from mock import patch

from queens.iterators.metropolis_hastings_iterator import MetropolisHastingsIterator
from queens.iterators.sequential_monte_carlo_iterator import SequentialMonteCarloIterator
from queens.main import run
from queens.utils import injector
from queens.utils.io_utils import load_result


def test_metropolis_hastings_multiple_chains_multivariate_gaussian(
    inputdir, tmp_path, target_density_gaussian_2d, _create_experimental_data_gaussian_2d
):
    """Test case for Metropolis Hastings iterator."""
    # pylint: disable=duplicate-code
    template = inputdir / "metropolis_hastings_multiple_chains_multivariate_gaussian.yml"
    experimental_data_path = tmp_path  # pylint: disable=duplicate-code
    dir_dict = {"experimental_data_path": experimental_data_path}
    input_file = tmp_path / "multivariate_gaussian_metropolis_hastings_multiple_chains_realiz.yml"
    injector.inject(dir_dict, template, input_file)  # pylint: disable=duplicate-code
    # mock methods related to likelihood
    with patch.object(
        SequentialMonteCarloIterator, "eval_log_likelihood", target_density_gaussian_2d
    ):
        with patch.object(
            MetropolisHastingsIterator, "eval_log_likelihood", target_density_gaussian_2d
        ):
            run(input_file, tmp_path)

    results = load_result(tmp_path / 'xxx.pickle')

    # note that the analytical solution would be:
    # posterior mean: [0.29378531 -1.97175141]
    # posterior cov: [[0.42937853 0.00282486] [0.00282486 0.00988701]]
    # however, we only have a very inaccurate approximation here:

    np.testing.assert_allclose(
        results['mean'],
        np.array(
            [
                [1.9538477050387937, -1.980155948698723],
                [-0.024456540006756778, -1.9558862932202299],
                [0.8620026644863327, -1.8385635263327393],
            ]
        ),
    )
    np.testing.assert_allclose(
        results['cov'],
        np.array(
            [
                [
                    [0.15127359388133552, 0.07282531084034029],
                    [0.07282531084034029, 0.05171405742642703],
                ],
                [
                    [0.17850797646369507, -0.012342979562824052],
                    [-0.012342979562824052, 0.0023510303586270057],
                ],
                [
                    [0.0019646760257596243, 0.002417903725921208],
                    [0.002417903725921208, 0.002975685737073754],
                ],
            ]
        ),
    )
