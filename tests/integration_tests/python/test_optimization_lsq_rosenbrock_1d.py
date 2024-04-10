"""TODO_doc."""

import pickle

import numpy as np

from queens.distributions.free import FreeVariable
from queens.global_settings import GlobalSettings
from queens.interfaces.direct_python_interface import DirectPythonInterface
from queens.iterators.optimization_iterator import OptimizationIterator
from queens.main import run_iterator
from queens.models.simulation_model import SimulationModel
from queens.parameters.parameters import Parameters


def test_optimization_lsq_rosenbrock_1d(tmp_path):
    """Test special case for optimization iterator with least squares.

    Special case: 1 unknown but 2 residuals.
    """
    # Global settings
    experiment_name = "ResRosenbrock1DLSQ"
    output_dir = tmp_path

    with GlobalSettings(experiment_name=experiment_name, output_dir=output_dir, debug=False) as gs:
        # Parameters
        x1 = FreeVariable(dimension=1)
        parameters = Parameters(x1=x1)

        # Setup QUEENS stuff
        interface = DirectPythonInterface(
            function="rosenbrock60_residual_1d", parameters=parameters
        )
        model = SimulationModel(interface=interface)
        iterator = OptimizationIterator(
            algorithm="LSQ",
            initial_guess=[3.0],
            result_description={"write_results": True},
            bounds=[float("-inf"), float("inf")],
            model=model,
            parameters=parameters,
        )

        # Actual analysis
        run_iterator(iterator)

        # Load results
        result_file = gs.output_dir / f"{gs.experiment_name}.pickle"
    with open(result_file, 'rb') as handle:
        results = pickle.load(handle)
    np.testing.assert_allclose(results.x, np.array([+1.0]))
    np.testing.assert_allclose(results.fun, np.array([+0.0, +0.0]))
