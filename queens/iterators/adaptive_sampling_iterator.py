"""Adaptive sampling iterator."""

import logging
import pickle
import types
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
from jax import jit
from particles.resampling import stratified

from queens.iterators.grid_iterator import GridIterator
from queens.iterators.iterator import Iterator
from queens.iterators.metropolis_hastings_iterator import MetropolisHastingsIterator
from queens.iterators.sequential_monte_carlo_chopin import SequentialMonteCarloChopinIterator

_logger = logging.getLogger(__name__)
jax.config.update("jax_enable_x64", True)


class AdaptiveSamplingIterator(Iterator):
    """Adaptive sampling iterator.

    Attributes:
        likelihood_model (Model): Likelihood model (Only Gaussian Likelihood supported)
        initial_train_iterator (Iterator): Iterator to draw initial training samples (e.g. MC, LHS)
        solving_iterator (Iterator): Iterator to solve inverse problem
                                     (SequentialMonteCarloChopinIterator,
                                     MetropolisHastingsIterator and GridIterator supported)
        num_new_samples (int): Number of new training samples in each adaptive step
        num_steps (int): Number of adaptive sampling steps
        seed (int, opt): Seed for random number generation
        restart_file (str, opt): Result file path for restarts
        cs_div_criterion (float): Cauchy-Schwarz divergence stopping criterion threshold
        x_train (np.ndarray): Training input samples
        x_train_new (np.ndarray): Newly drawn training samples
        y_train (np.ndarray): Training likelihood output samples
        model_outputs (np.ndarray): Training model output samples
    """

    def __init__(
        self,
        model,
        parameters,
        likelihood_model,
        initial_train_iterator,
        solving_iterator,
        num_new_samples,
        num_steps,
        seed=41,
        restart_file=None,
        cs_div_criterion=0.01,
    ):
        """Initialise AdaptiveSamplingIterator.

        Args:
            model (model): Model to be evaluated by iterator
            parameters (Parameters): Parameters object
            likelihood_model (Model): Likelihood model (Only Gaussian Likelihood supported)
            initial_train_iterator (Iterator): Iterator to draw initial training samples (e.g. MC,
                                               LHS)
            solving_iterator (Iterator): Iterator to solve inverse problem
                                         (SequentialMonteCarloChopinIterator,
                                         MetropolisHastingsIterator and GridIterator supported)
            num_new_samples (int): Number of new training samples in each adaptive step
            num_steps (int): Number of adaptive sampling steps
            seed (int, opt): Seed for random number generation
            restart_file (str, opt): Result file path for restarts
            cs_div_criterion (float): Cauchy-Schwarz divergence stopping criterion threshold
        """
        super().__init__(model, parameters)
        self.seed = seed
        self.likelihood_model = likelihood_model
        self.initial_train_iterator = initial_train_iterator
        self.solving_iterator = solving_iterator
        self.num_new_samples = num_new_samples
        self.num_steps = num_steps
        self.restart_file = restart_file
        self.cs_div_criterion = cs_div_criterion
        self.x_train = None
        self.x_train_new = None
        self.y_train = None
        self.model_outputs = None

    def pre_run(self):
        """Pre run."""
        np.random.seed(self.seed)

        if self.restart_file:
            with open(self.restart_file, 'rb') as handle:
                results = pickle.load(handle)
            self.x_train = results['x_train'][-1]
            self.model_outputs = results['model_outputs'][-1]
            self.y_train = results['y_train'][-1]
            self.x_train_new = results['x_train_new'][-1]

        else:
            self.initial_train_iterator.pre_run()
            self.x_train_new = self.initial_train_iterator.samples
            self.x_train = np.empty((0, self.parameters.num_parameters))
            self.y_train = np.empty((0, 1))
            self.model_outputs = np.empty((0, self.likelihood_model.normal_distribution.mean.size))

    def core_run(self):
        """Core run."""
        for i in range(self.num_steps):
            _logger.info('Step: %i / %i', i + 1, self.num_steps)
            self.x_train = np.concatenate([self.x_train, self.x_train_new], axis=0)
            self.y_train = self.eval_log_likelihood().reshape(-1, 1)
            _logger.info('Number of solver evaluations: %i', self.x_train.shape[0])
            self.model.initialize(
                self.x_train, self.y_train, self.likelihood_model.normal_distribution.mean.size
            )
            self.solving_iterator.pre_run()

            def _m(self_, _, xp):
                x_train_ml = self.x_train[np.argmax(self.y_train[:, 0])]
                epn = xp.shared['exponents'][-1]
                target = self_.current_target(epn)
                for j, par in enumerate(self.solving_iterator.random_variable_keys):
                    xp.theta[par][0] = x_train_ml[j]
                target(xp)
                return self_.move(xp, target)

            if isinstance(self.solving_iterator, SequentialMonteCarloChopinIterator):
                self.solving_iterator.smc_obj.fk.M = types.MethodType(
                    _m, self.solving_iterator.smc_obj.fk
                )

            self.solving_iterator.core_run()

            particles, weights, log_posterior = self.get_particles_and_weights()
            self.x_train_new = self.choose_new_samples(particles, weights)

            cs_div = self.write_results(particles, weights, log_posterior, i)

            if cs_div < self.cs_div_criterion:
                break

    def eval_log_likelihood(self):
        """Evaluate log likelihood.

        Returns:
            log_likelihood (np.ndarray): Log likelihood
        """
        model_output = self.likelihood_model.forward_model.evaluate(self.x_train_new)['result']
        self.model_outputs = np.concatenate([self.model_outputs, model_output], axis=0)
        if self.likelihood_model.noise_type.startswith('MAP'):
            self.likelihood_model.update_covariance(model_output)
        log_likelihood = self.likelihood_model.normal_distribution.logpdf(self.model_outputs)
        log_likelihood -= self.likelihood_model.normal_distribution.logpdf_const
        return log_likelihood

    def choose_new_samples(self, particles, weights):
        """Choose new training samples.

        Choose new training samples from approximated posterior distribution.

        Args:
            particles (np.ndarray): Particles of approximated posterior
            weights (np.ndarray): Particle weights of approximated posterior

        Returns:
            x_train_new (np.ndarray): New training samples
        """
        indices = stratified(weights, self.num_new_samples)
        x_train_new = particles[indices]
        return x_train_new

    def write_results(self, particles, weights, log_posterior, iteration):
        """Write results to output file and calculate cs_div.

        Args:
            particles (np.ndarray): Particles of approximated posterior
            weights (np.ndarray): Particle weights of approximated posterior
            log_posterior (np.ndarray): Log posterior value of particles
            iteration (int): Iteration count

        Returns:
            cs_div (float): Maximum Cauchy-Schwarz divergence between marginals of the current and
                            previous step
        """
        pickle_file = Path(self.output_dir, self.experiment_name + ".pickle")

        if iteration == 0 and not self.restart_file:
            results = {
                'x_train': [],
                'model_outputs': [],
                'y_train': [],
                'x_train_new': [],
                'particles': [],
                'weights': [],
                'log_posterior': [],
                'cs_div': [],
            }
            cs_div = np.nan
        else:
            with open(pickle_file, 'rb') as handle:
                results = pickle.load(handle)

            particles_prev = results['particles'][-1]
            weights_prev = results['weights'][-1]
            samples_prev = particles_prev[
                np.random.choice(np.arange(weights_prev.size), 5_000, p=weights_prev)
            ]
            samples_curr = particles[np.random.choice(np.arange(weights.size), 5_000, p=weights)]
            cs_div = float(cauchy_schwarz_divergence(samples_prev, samples_curr))
            _logger.info('Cauchy Schwarz divergence: %.2e', cs_div)

        results['x_train'].append(self.x_train)
        results['model_outputs'].append(self.model_outputs)
        results['y_train'].append(self.y_train)
        results['x_train_new'].append(self.x_train_new)
        results['particles'].append(particles)
        results['weights'].append(weights)
        results['log_posterior'].append(log_posterior)
        results['cs_div'].append(cs_div)

        with open(pickle_file, 'wb') as handle:
            pickle.dump(results, handle, protocol=pickle.HIGHEST_PROTOCOL)

        return cs_div

    def get_particles_and_weights(self):
        """Get particles and weights of solving iterator.

        Returns:
            particles (np.ndarray): particles from approximated posterior distribution
            weights (np.ndarray): weights corresponding to particles
            log_posterior (np.ndarray): log_posterior values corresponding to particles
        """
        if isinstance(self.solving_iterator, SequentialMonteCarloChopinIterator):
            particles = self.solving_iterator.smc_obj.fk.model.particles_array_to_numpy(
                self.solving_iterator.smc_obj.X.theta
            )
            weights = self.solving_iterator.smc_obj.W.reshape(-1)
            particles, unique_indices, unique_count = np.unique(
                particles, axis=0, return_index=True, return_counts=True
            )
            weights = weights[unique_indices] * unique_count
            weights /= np.sum(weights)
            log_posterior = self.solving_iterator.smc_obj.X.lpost[unique_indices]
        elif isinstance(self.solving_iterator, MetropolisHastingsIterator):
            particles = self.solving_iterator.chains[self.solving_iterator.num_burn_in + 1 :]
            particles = particles.reshape(-1, self.parameters.num_parameters)
            log_posterior = self.solving_iterator.log_posterior[
                self.solving_iterator.num_burn_in + 1 :
            ].reshape(-1)
            weights = np.ones(log_posterior.size) / log_posterior.size
        elif isinstance(self.solving_iterator, GridIterator):
            particles = self.solving_iterator.samples
            log_posterior = self.solving_iterator.output
            log_posterior_ = log_posterior - np.max(log_posterior)
            weights = np.exp(log_posterior_) / np.sum(np.exp(log_posterior_))
        else:
            raise NotImplementedError
        return particles, weights, log_posterior

    def post_run(self):
        """Post run."""


@jit
def cauchy_schwarz_divergence(samples_1, samples_2):
    """Maximum Cauchy-Schwarz divergence between marginals of two sample sets.

    Args:
        samples_1 (np.ndarray): Sample set 1
        samples_2 (np.ndarray): Sample set 2

    Returns:
        cs_div_max (np.ndarray): Maximum Cauchy-Schwarz divergence between marginals of two sample
                                 sets.
    """
    n_1 = samples_1.shape[0]
    n_2 = samples_2.shape[0]

    factor_1 = n_1 ** (-1.0 / 5)
    factor_2 = n_2 ** (-1.0 / 5)

    var_1 = jnp.var(samples_1, axis=0) * factor_1**2
    var_2 = jnp.var(samples_2, axis=0) * factor_2**2

    def normalizing_factor(variance):
        return (2 * jnp.pi * variance) ** (-1 / 2)

    def normal(x_1, x_2, variance):
        d = x_1[:, jnp.newaxis, :] - x_2[jnp.newaxis, :, :]
        norm = d**2 / variance
        return normalizing_factor(variance), -0.5 * norm

    z_1_2 = normal(samples_1, samples_2, var_1 + var_2)
    z_1_1 = normal(samples_1, samples_1, var_1 + var_1)
    z_1_1 = z_1_1[0] * jnp.exp(z_1_1[1])
    z_2_2 = normal(samples_2, samples_2, var_2 + var_2)
    z_2_2 = z_2_2[0] * jnp.exp(z_2_2[1])

    max_1_2 = jnp.max(z_1_2[1], axis=(0, 1))
    term_1 = (
        -jnp.log(jnp.sum(1 / n_1 * 1 / n_2 * z_1_2[0] * jnp.exp(z_1_2[1] - max_1_2), axis=(0, 1)))
        - max_1_2
    )
    term_2 = 0.5 * jnp.log(
        1 / n_1 * normalizing_factor(var_1)
        + jnp.sum(
            2 / n_1**2 * z_1_1 * jnp.tri(*z_1_1.shape[:2], k=-1)[:, :, jnp.newaxis], axis=(0, 1)
        )
    )
    term_3 = 0.5 * jnp.log(
        1 / n_2 * normalizing_factor(var_2)
        + jnp.sum(
            2 / n_2**2 * z_2_2 * jnp.tri(*z_1_1.shape[:2], k=-1)[:, :, jnp.newaxis], axis=(0, 1)
        )
    )
    cs_div_max = jnp.max(term_1 + term_2 + term_3)
    return cs_div_max
