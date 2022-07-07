"""Iterator to run a single simulation run."""

import numpy as np

from pqueens.models import from_config_create_model

from .iterator import Iterator


class SingleSimRunIterator(Iterator):
    """Iterator for single simulation run.

    Attributes:
        model (model):              Model to be evaluated by iterator
        seed  (int):                Seed for random number generation
        num_samples (int):          Number of samples to compute
        result_description (dict):  Description of desired results
        samples (np.array):         Array with all samples
        outputs (np.array):         Array with all model outputs
    """

    def __init__(self, model, global_settings):
        """Initialise Single Sim Run Iterator.

        Args:
            model (obj, optional): Model to be evaluated by iterator.
            global_settings (dict, optional): Settings for the QUEENS run.
        """
        super().__init__(model, global_settings)
        self.num_samples = 1
        self.samples = np.zeros(1)
        self.output = None

    @classmethod
    def from_config_create_iterator(cls, config, iterator_name, model=None):
        """Create iterator for single simulation run from problem description.

        Args:
            config (dict): Dictionary with QUEENS problem description
            iterator_name (str): Name of iterator to identify right section
                                 in options dict (optional)
            model (model):       Model to use (optional)

        Returns:
            iterator: MonteCarloIterator object
        """
        method_options = config[iterator_name]['method_options']
        if model is None:
            model_name = method_options['model']
            model = from_config_create_model(model_name, config)

        global_settings = config.get('global_settings', None)

        return cls(
            model,
            global_settings,
        )

    def pre_run(self):
        """Generate samples for subsequent MC analysis and update model."""
        pass

    def core_run(self):
        """Run single simulation."""
        self.output = self.model.evaluate(self.samples)

    def post_run(self):
        """Not required here."""
        pass
