import pytest
import numpy as np
from pqueens.interfaces.bmfmc_interface import BmfmcInterface


# -------- fixtures -----------------------------------
class FakeRegression:
    def __init__(self, map_output_dict):
        self.map_output_dict = map_output_dict

    def predict(self, *args, **kwargs):
        output = self.map_output_dict
        return output

    @staticmethod
    def train():
        pass


@pytest.fixture()
def config():
    config = {
        "type": "gp_approximation_gpy",
        "features_config": "opt_features",
        "num_features": 1,
        "X_cols": 1,
    }
    return config


@pytest.fixture()
def default_interface(config, approx_name):
    interface = BmfmcInterface(config, approx_name)
    return interface


@pytest.fixture()
def probabilistic_mapping_obj(map_output_dict):
    probabilistic_mapping_obj = FakeRegression(map_output_dict)
    return probabilistic_mapping_obj


@pytest.fixture()
def map_output_dict():
    output = {'mean': np.linspace(1.0, 5.0, 5), 'variance': np.linspace(5.0, 10.0, 5)}
    return output


@pytest.fixture()
def approx_name():
    name = 'some_name'
    return name


# --------- actual unittests ---------------------------
def test_init(config, approx_name):

    interface = BmfmcInterface(config, approx_name, variables=None)

    # asserts / tests
    assert interface.variables is None
    assert interface.config == config
    assert interface.probabilistic_mapping_obj is None


def test_map(mocker, default_interface, probabilistic_mapping_obj, map_output_dict):
    mocker.patch(
        "pqueens.regression_approximations.regression_approximation.RegressionApproximation",
        return_value=FakeRegression,
    )

    Z_LF = 1.0
    expected_Y_HF_mean = map_output_dict['mean']
    expected_Y_HF_var = map_output_dict['variance']

    with pytest.raises(RuntimeError):
        mean_Y_HF_given_Z_LF, var_Y_HF_given_Z_LF = default_interface.map(
            Z_LF, support='y', full_cov=False
        )

    default_interface.probabilistic_mapping_obj = probabilistic_mapping_obj
    mean_Y_HF_given_Z_LF, var_Y_HF_given_Z_LF = default_interface.map(
        Z_LF, support='y', full_cov=False
    )

    np.testing.assert_array_almost_equal(mean_Y_HF_given_Z_LF, expected_Y_HF_mean, decimal=6)
    np.testing.assert_array_almost_equal(var_Y_HF_given_Z_LF, expected_Y_HF_var, decimal=6)


def test_build_approximation(mocker, default_interface):
    Z = np.atleast_2d(np.linspace(0.0, 1.0, 10))
    Y = np.atleast_2d(np.linspace(1.0, 2.0, 10))
    mp1 = mocker.patch(
        "pqueens.regression_approximations.regression_approximation.RegressionApproximation"
        ".from_config_create",
        return_value=FakeRegression,
    )
    mp2 = mocker.patch(
        'pqueens.tests.unittests.interfaces.test_bmfmc_interface.FakeRegression.train'
    )
    default_interface.build_approximation(Z, Y)
    mp1.assert_called_once()
    mp2.assert_called_once()