"""Random Variables module."""


class RandomVariable:
    """RandomVariable class."""

    def __init__(self, distribution, dimension, lower_bound, upper_bound, data_type):
        """Initialize random variable object.

        Args:
            distribution (Distribution): Underlying distribution of random variable
            dimension (int): Dimension of the random variable
            lower_bound (list, int): Lower bound of the random variable
            upper_bound (list, int): Upper bound of the random variable
            data_type (str): Specifies the data type of the random variable ("INT" or "FLOAT")
        """
        self.distribution = distribution
        self.dimension = dimension
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.data_type = data_type

    def draw_samples(self, num_samples):
        """Draw samples from the random variable.

        Returns:
            samples (np.ndarray): Drawn samples
        """
        return self.distribution.draw(num_samples).reshape(-1, self.dimension)
