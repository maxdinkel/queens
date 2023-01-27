"""Deterministic optimization toolbox."""

import glob
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.optimize
from scipy.optimize import curve_fit

import pqueens.database.database as DB_module
from pqueens.iterators.iterator import Iterator
from pqueens.models import from_config_create_model
from pqueens.utils.fd_jacobian import compute_step_with_bounds, fd_jacobian, get_positions
from pqueens.utils.process_outputs import write_results

_logger = logging.getLogger(__name__)


class OptimizationIterator(Iterator):
    """Iterator for deterministic optimization problems.

    Based on the *scipy.optimize* optimization toolbox [1].

    References:
        [1]: https://docs.scipy.org/doc/scipy/reference/optimize.html

    Attributes:
        algorithm (str): String that defines the optimization algorithm to be used:

                         - CG: Conjugate gradient optimization (unconstrained), using Jacobian
                         - BFGS: Broyden–Fletcher–Goldfarb–Shanno algorithm (quasi-Newton) for
                                optimization (iterative method for unconstrained
                                nonlinear optimization), using Jacobian
                         - L-BFGS-B: Limited memory Broyden–Fletcher–Goldfarb–Shanno algorithm
                                     with box constraints (for large number of variables)
                         - TNC: Truncated Newton method (Hessian free) for nonlinear optimization
                                with bounds involving a large number of variables. Jacobian
                                necessary
                         - SLSQP: Sequential Least Squares Programming minimization with bounds
                                  and constraints using Jacobian
                         - LSQ: Nonlinear least squares with bounds using Jacobian
                         - LM: Levenberg-Marquardt optimization for nonlinear problems without
                               the need for a Jacobian
                         - COBYLA: Constrained Optimization BY Linear Approximation (no Jacobian)
                         - NELDER-MEAD: Downhill-simplex search method (unconstrained, unbounded)
                                        without the need for a Jacobian
                         - POWELL: Powell's conjugate direction method (unconstrained) without the
                                   need for a Jacobian. Minimizes the function by a
                                   bi-directional search along each search vector
        bounds (np.array): Boundaries for the optimization (does not work with LM).
        cons (np.array): Nonlinear constraints for the optimization (does not work with LM).
        initial_guess (np.array): Initial guess, i.e. start point of
                                  optimization.
        jac_method (str): Method to calculate a finite difference based approximation of the
                          Jacobian matrix:

                          - '2-point': a one sided scheme by definition
                          - '3-point': more exact but needs twice as many function evaluations
        jac_rel_step: TODO_doc
        max_feval (int): Maximal number of function evaluations.
                         (**TODO_doc:** max_feval is defined twice)
        max_feval (int): Maximum number of forward simulation runs.
                         (**TODO_doc:** max_feval is defined twice)
        result_description (dict): Description of desired post-processing.
                                   (**TODO_doc:** result_description is defined twice)
        result_description (dict): Dictionary containing descriptions for result handling.
                                   (**TODO_doc:** result_description is defined twice)
        experimental_data_path_list (list): List containing the path to base directories with
                                            experimental data csv-files.
        experimental_data_dict: TODO_doc
        output_column (int): Specifies the columns that belong to the *y_obs* in the experimental
                             data set (currently only scalar output possible but could be
                             extended to vector-valued output).
        eval_jacobian: TODO_doc
        verbose_output (int): Integer encoding which kind of verbose information should be
                              printed by the optimizers (not applicable for LM).
        db: TODO_doc
        experiment_name: TODO_doc
        coordinate_labels: TODO_doc
        output_label: TODO_doc
        axis_scaling_experimental: TODO_doc
        output_scaling_experimental: TODO_doc
        precalculated_positions (dict): Dictionary containing precalculated positions and
                                        corresponding model responses.

    Returns:
        OptimizationIterator (obj): Instance of the OptimizationIterator
    """

    def __init__(
        self,
        algorithm,
        axis_scaling_experimental,
        bounds,
        constraints,
        coordinate_labels,
        db,
        experimental_data_path_list,
        experiment_name,
        global_settings,
        initial_guess,
        jac_method,
        jac_rel_step,
        max_feval,
        model,
        output_column,
        output_label,
        output_scaling_experimental,
        result_description,
        verbose_output,
    ):
        """TODO_doc.

        Args:
            algorithm: TODO_doc
            axis_scaling_experimental: TODO_doc
            bounds: TODO_doc
            constraints: TODO_doc
            coordinate_labels: TODO_doc
            db: TODO_doc
            experimental_data_path_list: TODO_doc
            experiment_name: TODO_doc
            global_settings: TODO_doc
            initial_guess: TODO_doc
            jac_method: TODO_doc
            jac_rel_step: TODO_doc
            max_feval: TODO_doc
            model: TODO_doc
            output_column: TODO_doc
            output_label: TODO_doc
            output_scaling_experimental: TODO_doc
            result_description: TODO_doc
            verbose_output: TODO_doc
        """
        super().__init__(model, global_settings)

        self.algorithm = algorithm
        self.bounds = bounds
        self.cons = constraints
        self.initial_guess = initial_guess
        self.jac_method = jac_method
        self.jac_rel_step = jac_rel_step
        self.max_feval = max_feval
        self.result_description = result_description
        self.experimental_data_path_list = experimental_data_path_list
        self.experimental_data_dict = None
        self.output_column = output_column

        self.eval_jacobian = False
        if self.algorithm in ['CG', 'BFGS', 'L-BFGS-B', 'TNC', 'SLSQP', 'LSQ']:
            self.eval_jacobian = True

        self.verbose_output = verbose_output
        self.db = db
        self.experiment_name = experiment_name
        self.coordinate_labels = coordinate_labels
        self.output_label = output_label
        self.axis_scaling_experimental = axis_scaling_experimental
        self.output_scaling_experimental = output_scaling_experimental
        self.precalculated_positions = {'position': [], 'output': []}

    @classmethod
    def from_config_create_iterator(cls, config, iterator_name, model=None):
        """Create Optimization iterator from problem description.

        Args:
            config (dict): Dictionary with QUEENS problem description
            iterator_name (str): Name of iterator (optional)
            model (model):       Model to use (optional)

        Returns:
            iterator: OptimizationIterator object
        """
        _logger.info(
            "Optimization Iterator for experiment: %s",
            config.get('global_settings').get('experiment_name'),
        )
        method_options = config[iterator_name]
        if model is None:
            model_name = method_options['model_name']
            model = from_config_create_model(model_name, config)

        result_description = method_options.get('result_description', None)
        global_settings = config.get('global_settings', None)

        initial_guess = np.atleast_1d(np.array(method_options['initial_guess']))

        bounds = method_options.get("bounds", None)

        if bounds is None:
            bounds = [(-np.inf, np.inf)] * initial_guess.shape[0]

        constraints_dict = method_options.get('constraints', None)

        constraints = list()
        if constraints_dict:
            for _, value in constraints_dict.items():
                # evaluate string of lambda function into real lambda function
                value['fun'] = eval(value['fun'])
                constraints.append(value)

        max_feval = method_options.get('max_feval', None)
        algorithm = method_options.get('algorithm', 'L-BFGS-B')
        algorithm = algorithm.upper()

        jac_method = method_options.get('jac_method', '2-point')
        jac_rel_step = method_options.get('jac_rel_step', None)

        verbose_output = method_options.get('verbose_output', False)
        experimental_data_path_list = method_options.get('experimental_csv_data_base_dirs', None)
        output_column = method_options.get('output_observation_column_in_csv')
        if experimental_data_path_list is not None:
            db = DB_module.database
        else:
            db = None
        experiment_name = config['global_settings']['experiment_name']
        coordinate_labels = config['method'].get('coordinate_labels')
        output_label = config['method'].get('output_label')
        axis_scaling_experimental = config['method'].get('axis_scaling_experimental')
        output_scaling_experimental = config['method'].get('output_scaling_experimental')

        # initialize objective function
        return cls(
            algorithm=algorithm,
            axis_scaling_experimental=axis_scaling_experimental,
            bounds=bounds,
            constraints=constraints,
            coordinate_labels=coordinate_labels,
            db=db,
            experimental_data_path_list=experimental_data_path_list,
            experiment_name=experiment_name,
            global_settings=global_settings,
            initial_guess=initial_guess,
            jac_method=jac_method,
            jac_rel_step=jac_rel_step,
            max_feval=max_feval,
            model=model,
            output_column=output_column,
            output_label=output_label,
            output_scaling_experimental=output_scaling_experimental,
            result_description=result_description,
            verbose_output=verbose_output,
        )

    def objective_function(self, x_vec, coordinates=None):
        """Evaluate objective function at *x_vec*.

        Args:
            x_vec (np.array): Input vector for model/objective function. The variable *x_vec*
                              corresponds to the parameters that should be calibrated in an
                              inverse problem.
            coordinates (np.array): Coordinates that specify where to evaluate the model response.
                                    For inverse problems this corresponds to the input that is
                                    not part of the parameters which should be calibrated, but
                                    rather coordinates, e.g. in space and time.
                                    We already preselect the to the coordinates corresponding
                                    response vector of the model in the *data_processor*
                                    class, to not have to store the entire model response.

        Returns:
            f_value (float): Response of objective function or model
        """
        f_value = self.eval_model(x_vec)

        parameter_list = self.parameters.parameters_keys
        _logger.info("The intermediate, iterated parameters %s are:\n\t%s", parameter_list, x_vec)

        return f_value

    def jacobian(self, x0):
        """Evaluate Jacobian of objective function at *x0*.

        Args:
            x0: TODO_doc
        Returns:
            TODO_doc
        """
        positions, delta_positions = get_positions(
            x0, method=self.jac_method, rel_step=self.jac_rel_step, bounds=self.bounds
        )
        _, use_one_sided = compute_step_with_bounds(
            x0, method=self.jac_method, rel_step=self.jac_rel_step, bounds=self.bounds
        )

        # model response should now correspond to objective function evaluated at positions
        f_batch = self.eval_model(positions)

        f0 = f_batch[0].reshape(-1)  # first entry corresponds to f(x0)
        f_perturbed = f_batch[1:].reshape(-1, f0.size)

        J = fd_jacobian(f0, f_perturbed, delta_positions, use_one_sided, method=self.jac_method)
        # sanity checks:
        # in the case of LSQ, the number of residuals needs to be
        # greater or equal to the number of parameters to be fitted
        if self.algorithm == 'LSQ' and J.ndim == 2:
            num_res, num_par = J.shape
            if num_res < num_par:
                raise ValueError(
                    f"Number of residuals (={num_res}) has to be greater or equal to"
                    f" number of parameters (={num_par})."
                    f" You have {num_res}<{num_par}."
                )
        return J

    def pre_run(self):
        """Get initial guess."""
        _logger.info("Initialize Optimization run.")
        self._get_experimental_data_and_write_to_db()

    def core_run(self):
        """Core run of Optimization iterator."""
        _logger.info('Welcome to Optimization core run.')
        start = time.time()
        # nonlinear least squares optimization with Levenberg-Marquardt (without Jacobian here!)
        # Jacobian of the model could be integrated for better performance
        if self.algorithm == 'LM':
            # extract experimental coordinates as numpy array
            experimental_coordinates = (
                np.array(
                    [
                        self.experimental_data_dict[coordinate]
                        for coordinate in self.coordinate_labels
                    ]
                ),
            )[0].T
            self.solution = curve_fit(
                lambda coordinates, *x_vec: self.objective_function(
                    x_vec=x_vec, coordinates=coordinates
                ),
                experimental_coordinates,
                np.array(self.experimental_data_dict[self.output_label]).flatten(),
                p0=self.initial_guess.tolist(),
                method="lm",
                maxfev=self.max_feval,
            )

        # nonlinear least squares with bounds using Jacobian
        elif self.algorithm == 'LSQ':
            self.solution = scipy.optimize.least_squares(
                self.objective_function,
                self.initial_guess,
                jac=self.jacobian,
                bounds=self.bounds,
                max_nfev=self.max_feval,
                verbose=int(self.verbose_output),
            )
        # minimization with bounds using Jacobian
        elif self.algorithm in {'L-BFGS-B', 'TNC'}:
            self.solution = scipy.optimize.minimize(
                self.objective_function,
                self.initial_guess,
                method=self.algorithm,
                jac=self.jacobian,
                bounds=self.bounds,
                options={'maxiter': int(1e4), 'disp': self.verbose_output},
            )
        # Constrained Optimization BY Linear Approximation:
        # minimization with constraints without Jacobian
        elif self.algorithm in {'COBYLA'}:
            self.solution = scipy.optimize.minimize(
                self.objective_function,
                self.initial_guess,
                method=self.algorithm,
                constraints=self.cons,
                options={'disp': self.verbose_output},
            )
        # Sequential Least SQuares Programming:
        # minimization with bounds and constraints using Jacobian
        elif self.algorithm in {'SLSQP'}:
            self.solution = scipy.optimize.minimize(
                self.objective_function,
                self.initial_guess,
                method=self.algorithm,
                jac=self.jacobian,
                bounds=self.bounds,
                constraints=self.cons,
                options={'disp': self.verbose_output},
            )
        # minimization (unconstrained, unbounded) without Jacobian
        elif self.algorithm in {'NELDER-MEAD', 'POWELL'}:
            self.solution = scipy.optimize.minimize(
                self.objective_function,
                self.initial_guess,
                method=self.algorithm,
                options={'disp': self.verbose_output},
            )
        # minimization (unconstrained, unbounded) using Jacobian
        elif self.algorithm in {'CG', 'BFGS'}:
            self.solution = scipy.optimize.minimize(
                self.objective_function,
                self.initial_guess,
                method=self.algorithm,
                jac=self.jacobian,
                options={'disp': self.verbose_output},
            )
        end = time.time()
        _logger.info("Optimization took %E seconds.", end - start)

    def post_run(self):
        """Analyze the resulting optimum."""
        if self.algorithm == 'LM':
            parameter_list = self.parameters.parameters_keys()
            _logger.info(
                "The optimum of the parameters " "%s is:\n\t%s", *parameter_list, self.solution[0]
            )
        else:
            _logger.info("The optimum:\n\t%s", self.solution.x)
            if self.algorithm == 'LSQ':
                _logger.info("Optimality:\n\t%s", self.solution.optimality)
                _logger.info("Cost:\n\t%s", self.solution.cost)

        if self.result_description:
            if self.result_description["write_results"]:
                write_results(
                    self.solution,
                    self.global_settings["output_dir"],
                    self.global_settings["experiment_name"],
                )

    # -------------- private helper functions --------------------------
    def _get_experimental_data_and_write_to_db(self):
        """Loop over post files in given output directory."""
        if self.experimental_data_path_list is not None:
            # iteratively load all csv files in specified directory
            files_of_interest_list = []
            all_files_list = []
            for experimental_data_path in self.experimental_data_path_list:
                prefix_expr = '*.csv'  # only read csv files
                files_of_interest_paths = Path(experimental_data_path, prefix_expr)
                files_of_interest_list.extend(glob.glob(files_of_interest_paths))
                all_files_path = Path(experimental_data_path, '*')
                all_files_list.extend(glob.glob(all_files_path))

            #  check if some files are not csv files and throw a warning
            non_csv_files = [x for x in all_files_list if x not in files_of_interest_list]

            if non_csv_files:
                _logger.info(
                    '#####################################################################'
                )
                _logger.info(
                    'The following experimental data files could not be read-in as they do '
                    'not have a .csv file-ending: %s',
                    non_csv_files,
                )
                _logger.info(
                    '#####################################################################'
                )

            # read all experimental data into one numpy array
            # TODO filter out / handle corrupted data and NaNs
            data_list = []
            for filename in files_of_interest_list:
                try:
                    new_experimental_data = pd.read_csv(
                        filename, sep=r'[,\s]\s*', header=0, engine='python', index_col=None
                    )
                    data_list.append(new_experimental_data)

                except IOError:
                    raise IOError(
                        'An error occurred while reading in the experimental data '
                        'files. Abort...'
                    )
            self.experimental_data_dict = pd.concat(data_list, axis=0, ignore_index=True).to_dict(
                'list'
            )

            # potentially scale experimental data
            self._scale_experimental_data()

            self.db.save(self.experimental_data_dict, self.experiment_name, 'experimental_data', 1)

    def _scale_experimental_data(self):
        # scale the experimental coordinates
        for key, scaling in zip(self.coordinate_labels, self.axis_scaling_experimental):
            if scaling == 'log':
                self.experimental_data_dict[key] = np.log(self.experimental_data_dict[key])
            elif scaling == 'linear':
                pass
            else:
                raise ValueError(
                    f'The scaling option <{scaling}> for the experimental coordinates is not a '
                    f'valid choice! Please '
                    f'choose a valid scaling! Abort...'
                )

        # scale experimental output
        if self.output_scaling_experimental == 'linear':
            pass
        elif self.output_scaling_experimental == 'log':
            self.experimental_data_dict[self.output_label] = np.log(
                self.experimental_data_dict[self.output_label]
            )
        else:
            raise ValueError(
                f'The scaling option <{self.output_scaling_experimental}> for the experimental '
                f'data output is not a valid choice! Please '
                f'choose a valid scaling! Abort...'
            )

    def eval_model(self, positions):
        """Evaluate model at defined positions.

        Args:
            positions (np.ndarray): Positions at which the model is evaluated

        Returns:
            f_batch (np.ndarray): Model response
        """
        positions = positions.reshape(-1, self.parameters.num_parameters)
        f_batch = []
        for position in positions:
            precalculated_output = self.check_precalculated(position)
            if precalculated_output is not None:
                f_batch.append(precalculated_output)
            else:
                f_batch.append(self.model.evaluate(position.reshape(1, -1))['mean'].reshape(-1))
                self.precalculated_positions['position'].append(position)
                self.precalculated_positions['output'].append(f_batch[-1])
        f_batch = np.array(f_batch).squeeze()
        return f_batch

    def check_precalculated(self, position):
        """Check if the model was already evaluated at defined position.

        Args:
            position (np.ndarray): Position at which the model should be evaluated

        Returns:
            np.ndarray: Precalculated model response or *None*
        """
        for i, precalculated_position in enumerate(self.precalculated_positions['position']):
            if np.equal(position, precalculated_position).all():
                return self.precalculated_positions['output'][i]
        return None
