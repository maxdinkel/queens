"""Integration test for the Chopin Sequential Monte Carlo iterator.

The tested iterator is based on Chopin's 'particles' library.
"""

import numpy as np
from mock import patch

from queens.distributions.normal import NormalDistribution
from queens.drivers.function_driver import FunctionDriver
from queens.interfaces.job_interface import JobInterface
from queens.iterators.sequential_monte_carlo_chopin import SequentialMonteCarloChopinIterator
from queens.main import run_iterator
from queens.models.likelihood_models.gaussian_likelihood import GaussianLikelihood
from queens.models.simulation_model import SimulationModel
from queens.parameters.parameters import Parameters
from queens.schedulers.pool_scheduler import PoolScheduler
from queens.utils.experimental_data_reader import ExperimentalDataReader
from queens.utils.io_utils import load_result


def test_gaussian_smc_chopin_adaptive_tempering(
    tmp_path,
    target_density_gaussian_1d,
    _create_experimental_data_gaussian_1d,
    global_settings,
):
    """Test Sequential Monte Carlo with univariate Gaussian."""
    # Parameters
    x = NormalDistribution(mean=2.0, covariance=1.0)
    parameters = Parameters(x=x)

    # Setup iterator
    experimental_data_reader = ExperimentalDataReader(
        file_name_identifier="*.csv",
        csv_data_base_dir=tmp_path,
        output_label="y_obs",
    )
    driver = FunctionDriver(function="patch_for_likelihood")
    scheduler = PoolScheduler(experiment_name=global_settings.experiment_name)
    interface = JobInterface(parameters=parameters, scheduler=scheduler, driver=driver)
    forward_model = SimulationModel(interface=interface)
    model = GaussianLikelihood(
        noise_type="fixed_variance",
        noise_value=1.0,
        experimental_data_reader=experimental_data_reader,
        forward_model=forward_model,
    )
    iterator = SequentialMonteCarloChopinIterator(
        seed=42,
        num_particles=100,
        resampling_threshold=0.5,
        resampling_method="residual",
        feynman_kac_model="adaptive_tempering",
        waste_free=True,
        num_rejuvenation_steps=9,
        max_feval=10000,
        result_description={"write_results": True, "plot_results": True},
        model=model,
        parameters=parameters,
        global_settings=global_settings,
    )

    # Actual analysis
    with patch.object(
        SequentialMonteCarloChopinIterator, "eval_log_likelihood", target_density_gaussian_1d
    ):
        run_iterator(iterator, global_settings=global_settings)

    # Load results
    results = load_result(global_settings.result_file(".pickle"))

    # note that the analytical solution would be:
    # posterior mean: [1.]
    # posterior var: [0.5]
    # posterior std: [0.70710678]
    # however, we only have a very inaccurate approximation here:
    assert np.abs(results["raw_output_data"]["mean"] - 1) < 0.2
    assert np.abs(results["raw_output_data"]["var"] - 0.5) < 0.2
