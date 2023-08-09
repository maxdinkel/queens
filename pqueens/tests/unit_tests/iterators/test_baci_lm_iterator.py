"""Test for baci LM iterator."""

import logging

import numpy as np
import pandas as pd
import plotly.express as px
import pytest

from pqueens.distributions.free import FreeVariable
from pqueens.iterators.baci_lm_iterator import BaciLMIterator
from pqueens.models.simulation_model import SimulationModel
from pqueens.parameters.parameters import Parameters

_logger = logging.getLogger(__name__)


@pytest.fixture(scope='module', params=['method'])
def iterator_name_cases(request):
    """TODO_doc."""
    return request.param


@pytest.fixture(scope='module', params=[None, 'dummy_model'])
def model_cases(request):
    """TODO_doc."""
    return request.param


@pytest.fixture(scope='module', params=['grad', 'res', 'not_valid'])
def fix_update_reg(request):
    """TODO_doc."""
    return request.param


@pytest.fixture(scope='module', params=[1e-6, 1e0])
def fix_tolerance(request):
    """TODO_doc."""
    return request.param


@pytest.fixture()
def output_csv(dummy_global_settings):
    """Absolute path to output csv file."""
    return dummy_global_settings.output_dir / (dummy_global_settings.experiment_name + '.csv')


@pytest.fixture()
def output_html(dummy_global_settings):
    """Absolute path to output html file."""
    return dummy_global_settings.output_dir / (dummy_global_settings.experiment_name + '.html')


@pytest.fixture()
def default_baci_lm_iterator(dummy_global_settings):
    """TODO_doc."""
    parameters = Parameters(x1=FreeVariable(1), x2=FreeVariable(1))
    model = SimulationModel(interface="interface")

    my_baci_lm_iterator = BaciLMIterator(
        model=model,
        parameters=parameters,
        result_description={'write_results': True, 'plot_results': True},
        initial_guess=[0.1, 0.2],
        jac_rel_step=1e-05,
        jac_abs_step=0.001,
        init_reg=1.0,
        update_reg='grad',
        convergence_tolerance=1e-06,
        max_feval=99,
    )

    return my_baci_lm_iterator


@pytest.fixture(scope='module', params=[True, False])
def fix_true_false_param(request):
    """TODO_doc."""
    return request.param


@pytest.fixture(scope='module')
def fix_plotly_fig():
    """TODO_doc."""
    data = pd.DataFrame({'x': [1.0, 2.0], 'y': [1.1, 2.1], 'z': [1.2, 2.2]})
    fig = px.line_3d(
        data,
        x='x',
        y='y',
        z='z',
    )
    return fig


def test_init(dummy_global_settings):
    """TODO_doc."""
    initial_guess = np.array([1, 2.2])
    bounds = np.array([[0.0, 1.0], [1.0, 2.0]])
    jac_rel_step = 1e-3
    jac_abs_step = 1e-2
    init_reg = 1.0
    update_reg = 'grad'
    tolerance = 1e-8
    max_feval = 99
    model = 'dummy_model'
    result_description = (True,)
    verbose_output = (True,)

    my_baci_lm_iterator = BaciLMIterator(
        model=model,
        parameters="dummy_parameters",
        result_description=result_description,
        initial_guess=initial_guess,
        bounds=bounds,
        jac_rel_step=jac_rel_step,
        jac_abs_step=jac_abs_step,
        init_reg=init_reg,
        update_reg=update_reg,
        convergence_tolerance=tolerance,
        max_feval=max_feval,
        verbose_output=verbose_output,
    )

    np.testing.assert_equal(my_baci_lm_iterator.initial_guess, initial_guess)
    np.testing.assert_equal(my_baci_lm_iterator.param_current, initial_guess)
    assert my_baci_lm_iterator.model == model
    assert my_baci_lm_iterator.jac_rel_step == jac_rel_step
    assert my_baci_lm_iterator.max_feval == max_feval
    assert my_baci_lm_iterator.result_description == result_description
    assert my_baci_lm_iterator.jac_abs_step == jac_abs_step
    assert my_baci_lm_iterator.reg_param == init_reg
    assert my_baci_lm_iterator.update_reg == update_reg
    assert my_baci_lm_iterator.verbose_output == verbose_output


def test_model_evaluate(default_baci_lm_iterator, mocker):
    """TODO_doc."""
    mp = mocker.patch('pqueens.models.simulation_model.SimulationModel.evaluate', return_value=None)
    default_baci_lm_iterator.model.evaluate(None)
    mp.assert_called_once()


def test_residual(default_baci_lm_iterator, fix_true_false_param, mocker):
    """TODO_doc."""
    mocker.patch(
        'pqueens.iterators.baci_lm_iterator.BaciLMIterator.get_positions_raw_2pointperturb',
        return_value=[np.array([[1.0, 2.2], [1.00101, 2.2], [1.0, 2.201022]]), 1],
    )

    m2 = mocker.patch(
        'pqueens.models.simulation_model.SimulationModel.evaluate',
        return_value=None,
    )

    default_baci_lm_iterator.model.response = {'mean': np.array([[3.0, 4.2], [99.9, 99.9]])}

    _, result = default_baci_lm_iterator.jacobian_and_residual(np.array([1.0, 2.2]))

    np.testing.assert_equal(result, np.array([3.0, 4.2]))
    m2.assert_called_once()


def test_jacobian(default_baci_lm_iterator, fix_true_false_param, mocker):
    """TODO_doc."""
    mocker.patch(
        'pqueens.iterators.baci_lm_iterator.BaciLMIterator.get_positions_raw_2pointperturb',
        return_value=[
            np.array([[1.0, 2.2], [1.00101, 2.2], [1.0, 2.201022]]),
            np.array([0.00101, 0.201022]),
        ],
    )

    m3 = mocker.patch(
        'pqueens.models.simulation_model.SimulationModel.evaluate',
        return_value=None,
    )

    default_baci_lm_iterator.model.response = {'mean': np.array([[3.0, 4.2], [99.9, 99.9]])}

    m5 = mocker.patch(
        'pqueens.iterators.baci_lm_iterator.fd_jacobian',
        return_value=np.array([[1.0, 0.0], [0.0, 1.0]]),
    )

    jacobian, _ = default_baci_lm_iterator.jacobian_and_residual(np.array([1.0, 2.2]))

    m3.assert_called_once()

    m5.assert_called_once()

    np.testing.assert_equal(jacobian, np.array([[1.0, 0.0], [0.0, 1.0]]))

    if fix_true_false_param:
        with pytest.raises(ValueError):
            m5.return_value = np.array([[1.1, 2.2]])
            default_baci_lm_iterator.jacobian_and_residual(np.array([0.1]))


def test_pre_run(mocker, fix_true_false_param, default_baci_lm_iterator, output_csv):
    """TODO_doc."""
    default_baci_lm_iterator.result_description['write_results'] = fix_true_false_param

    mock_pandas_dataframe_to_csv = mocker.patch('pandas.core.generic.NDFrame.to_csv')
    default_baci_lm_iterator.pre_run()
    if fix_true_false_param:
        mock_pandas_dataframe_to_csv.assert_called_once_with(
            output_csv, mode='w', sep='\t', index=None
        )
    else:
        assert not mock_pandas_dataframe_to_csv.called
        default_baci_lm_iterator.result_description = None
        default_baci_lm_iterator.pre_run()


def test_core_run(default_baci_lm_iterator, mocker, fix_update_reg, fix_tolerance):
    """TODO_doc."""
    m1 = mocker.patch(
        'pqueens.iterators.baci_lm_iterator.BaciLMIterator.jacobian_and_residual',
        return_value=(np.array([[1.0, 2.0], [0.0, 1.0]]), np.array([0.1, 0.01])),
    )

    m3 = mocker.patch('pqueens.iterators.baci_lm_iterator.BaciLMIterator.printstep')
    default_baci_lm_iterator.update_reg = fix_update_reg
    default_baci_lm_iterator.max_feval = 2
    default_baci_lm_iterator.tolerance = fix_tolerance

    if fix_update_reg not in ['grad', 'res']:
        with pytest.raises(ValueError):
            default_baci_lm_iterator.core_run()
    else:
        default_baci_lm_iterator.core_run()
        if fix_tolerance == 1.0:
            assert m1.call_count == 1
            assert m3.call_count == 1
        else:
            assert m1.call_count == 3
            assert m3.call_count == 3
            np.testing.assert_almost_equal(
                default_baci_lm_iterator.param_current, np.array([-0.00875, 0.15875]), 8
            )
            np.testing.assert_almost_equal(
                default_baci_lm_iterator.param_opt, np.array([0.1, 0.2]), 8
            )


def test_post_run_2param(
    mocker, fix_true_false_param, default_baci_lm_iterator, fix_plotly_fig, output_csv, output_html
):
    """TODO_doc."""
    default_baci_lm_iterator.solution = np.array([1.1, 2.2])
    default_baci_lm_iterator.iter_opt = 3

    pdata = pd.DataFrame({'params': ['[1.0e3 2.0e-2]', '[1.1 2.1]'], 'resnorm': [1.2, 2.2]})
    checkdata = pd.DataFrame({'resnorm': [1.2, 2.2], 'x1': [1000.0, 1.1], 'x2': [0.02, 2.1]})

    default_baci_lm_iterator.result_description['plot_results'] = fix_true_false_param
    m1 = mocker.patch('pandas.read_csv', return_value=pdata)
    m2 = mocker.patch('plotly.express.line_3d', return_value=fix_plotly_fig)
    m3 = mocker.patch('plotly.basedatatypes.BaseFigure.update_traces', return_value=None)
    m4 = mocker.patch('plotly.basedatatypes.BaseFigure.write_html', return_value=None)

    default_baci_lm_iterator.post_run()

    if fix_true_false_param:
        m1.assert_called_once_with(output_csv, sep='\t')
        callargs = m2.call_args
        pd.testing.assert_frame_equal(callargs[0][0], checkdata)
        assert callargs[1]['x'] == 'x1'
        assert callargs[1]['y'] == 'x2'
        assert callargs[1]['z'] == 'resnorm'
        assert callargs[1]['hover_data'] == [
            'iter',
            'resnorm',
            'gradnorm',
            'delta_params',
            'mu',
            'x1',
            'x2',
        ]
        m4.assert_called_once_with(output_html)
        m2.assert_called_once()

    else:
        default_baci_lm_iterator.result_description = None
        default_baci_lm_iterator.post_run()
        m1.assert_not_called()
        m2.assert_not_called()
        m3.assert_not_called()
        m4.assert_not_called()


def test_post_run_1param(mocker, default_baci_lm_iterator, fix_plotly_fig, output_html):
    """TODO_doc."""
    default_baci_lm_iterator.solution = np.array([1.1, 2.2])
    default_baci_lm_iterator.iter_opt = 3

    pdata = pd.DataFrame({'params': ['[1.0e3]', '[1.1]'], 'resnorm': [1.2, 2.2]})
    mocker.patch('pandas.read_csv', return_value=pdata)
    mocker.patch('plotly.basedatatypes.BaseFigure.update_traces', return_value=None)
    m4 = mocker.patch('plotly.basedatatypes.BaseFigure.write_html', return_value=None)
    m6 = mocker.patch('plotly.express.line', return_value=fix_plotly_fig)

    checkdata = pd.DataFrame({'resnorm': [1.2, 2.2], 'x1': [1000.0, 1.1]})

    default_baci_lm_iterator.post_run()
    callargs = m6.call_args
    pd.testing.assert_frame_equal(callargs[0][0], checkdata)
    assert callargs[1]['x'] == 'x1'
    assert callargs[1]['y'] == 'resnorm'
    assert callargs[1]['hover_data'] == [
        'iter',
        'resnorm',
        'gradnorm',
        'delta_params',
        'mu',
        'x1',
    ]
    m4.assert_called_once_with(output_html)
    m6.assert_called_once()


def test_post_run_3param(mocker, default_baci_lm_iterator, caplog):
    """Test post run functionality."""
    default_baci_lm_iterator.solution = np.array([1.1, 2.2])
    default_baci_lm_iterator.iter_opt = 3

    mocker.patch('plotly.basedatatypes.BaseFigure.update_traces', return_value=None)
    m4 = mocker.patch('plotly.basedatatypes.BaseFigure.write_html', return_value=None)
    pdata = pd.DataFrame({'params': ['[1.0e3 2.0e-2 3.]', '[1.1 2.1 3.1]'], 'resnorm': [1.2, 2.2]})
    mocker.patch('pandas.read_csv', return_value=pdata)

    parameters = Parameters(x1=FreeVariable(1), x2=FreeVariable(1), x3=FreeVariable(1))
    default_baci_lm_iterator.parameters = parameters

    with caplog.at_level(logging.WARNING):
        default_baci_lm_iterator.post_run()

    expected_warning = (
        "write_results for more than 2 parameters not implemented, "
        "because we are limited to 3 dimensions. "
        "You have: 3. Plotting is skipped."
    )
    assert expected_warning in caplog.text

    m4.assert_not_called()


def test_post_run_0param(mocker, default_baci_lm_iterator, fix_plotly_fig):
    """TODO_doc."""
    default_baci_lm_iterator.solution = np.array([1.1, 2.2])
    default_baci_lm_iterator.iter_opt = 3

    pdata = pd.DataFrame({'params': ['', ''], 'resnorm': [1.2, 2.2]})
    mocker.patch('pandas.read_csv', return_value=pdata)
    with pytest.raises(ValueError):
        default_baci_lm_iterator.post_run()


def test_get_positions_raw_2pointperturb(default_baci_lm_iterator):
    """TODO_doc."""
    x = np.array([1.1, 2.5])
    pos, delta_pos = default_baci_lm_iterator.get_positions_raw_2pointperturb(x)
    np.testing.assert_almost_equal(pos, np.array([[1.1, 2.5], [1.101011, 2.5], [1.1, 2.501025]]), 8)
    np.testing.assert_almost_equal(delta_pos, np.array([[0.001011], [0.001025]]), 8)

    default_baci_lm_iterator.bounds = [[0.0, 0.0], [np.inf, 2.5]]
    default_baci_lm_iterator.havebounds = True
    posb, delta_posb = default_baci_lm_iterator.get_positions_raw_2pointperturb(x)
    np.testing.assert_almost_equal(
        posb, np.array([[1.1, 2.5], [1.101011, 2.5], [1.1, 2.498975]]), 8
    )
    np.testing.assert_almost_equal(delta_posb, np.array([[0.001011], [-0.001025]]), 8)


def test_printstep(mocker, default_baci_lm_iterator, fix_true_false_param, output_csv):
    """TODO_doc."""
    default_baci_lm_iterator.result_description['write_results'] = fix_true_false_param

    mock_pandas_dataframe_to_csv = mocker.patch('pandas.core.generic.NDFrame.to_csv')
    default_baci_lm_iterator.printstep(5, 1e-3, 1e-4, np.array([10.1, 11.2]))
    if fix_true_false_param:
        mock_pandas_dataframe_to_csv.assert_called_once_with(
            output_csv,
            header=None,
            float_format="%.8f",
            mode='a',
            sep='\t',
            index=None,
        )

    else:
        assert not mock_pandas_dataframe_to_csv.called
        default_baci_lm_iterator.result_description = None
        default_baci_lm_iterator.printstep(5, 1e-3, 1e-4, np.array([10.1, 11.2]))


def test_checkbounds(mocker, default_baci_lm_iterator, caplog):
    """Test bound checking."""
    default_baci_lm_iterator.bounds = np.array([[0.0, 0.0], [5.0, 2.0]])
    with caplog.at_level(logging.WARNING):
        stepoutside = default_baci_lm_iterator.checkbounds(np.array([1.0, 2.1]), 3)

    assert stepoutside
    assert default_baci_lm_iterator.reg_param == 2.0

    expected_warning = (
        f"WARNING: STEP #{3} IS OUT OF BOUNDS; double reg_param and compute new iteration.\n "
        f"declined step was: {np.array([1.1, 2.3])}"
    )
    assert expected_warning in caplog.text
