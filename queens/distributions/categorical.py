"""General categorical distribution.

Disclaimer: Most of our iterators are not able to handle categorical distributions.
"""

import itertools
import logging

import numpy as np

from queens.distributions.distributions import Distribution

_logger = logging.getLogger(__name__)


class CategoricalDistribution(Distribution):
    """General categorical distribution.

    Attributes:
        probabilities (np.ndarray): Probabilities associated with the categories
        categories (np.ndarray): Categories
    """

    def __init__(self, probabilities, categories):
        """Initialize categorical distribution.

        Args:
            probabilities (np.ndarray): Probabilities associated with the categories
            categories (np.ndarray): Categories
        """
        categories = np.array(categories, dtype=object)
        probabilities = np.array(probabilities)

        if len(categories) != len(probabilities):
            raise ValueError(
                f"The number of probabilities {len(probabilities)} does not match the number of"
                f" categories {len(categories)}"
            )

        super().check_positivity(probabilities=probabilities)

        if not np.isclose(np.sum(probabilities), 1, atol=0):
            _logger.info("Probabilities do not sum up to one, they are going to be normalized.")
            probabilities = probabilities / np.sum(probabilities)

        self.probabilities = probabilities
        self.categories = categories

    def draw(self, num_draws=1):
        """Draw samples.

        Args:
            num_draws (int, optional): Number of draws

        Returns:
            np.ndarray: Samples of the categorical distribution
        """
        samples_per_category = np.random.multinomial(num_draws, self.probabilities)
        samples = (
            [
                [self.categories[category]] * repetitions
                for category, repetitions in enumerate(samples_per_category)
                if repetitions
            ],
        )
        samples = np.array(
            list(itertools.chain.from_iterable(*samples)),
            dtype=object,
        )
        np.random.shuffle(samples)
        return samples.reshape(-1, 1)

    def logpdf(self, x):  # pylint: disable=invalid-name
        """Log of the probability *mass* function.

        Args:
            x (np.ndarray): Positions at which the log pmf is evaluated

        Returns:
            np.ndarray: log pmf
        """
        return np.log(self.pdf(x))

    def pdf(self, x):  # pylint: disable=invalid-name
        """Probability *mass* function.

        Args:
            x (np.ndarray): Positions at which the pdf is evaluated

        Returns:
            np.ndarray: pmf
        """
        index = np.array([np.argwhere(self.categories == xi) for xi in x]).flatten()
        return self.probabilities[index]