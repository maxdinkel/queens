import os
import sys

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

"""
A module that provides utilities and a class for visualization in BMFIA analysis.
It is designed such that the BMFIAVisualization class needs only to be initialized once
and can then be accessed and modified in the entire project.

In this context "this" is a pointer to the module object instance itself and can be compared to the
"self" keyword in classes.

Attributes:
    bmfia_visualization_instance (obj): Instance of the BMFIAVisualization class

Returns:
    None

"""

this = sys.modules[__name__]
this.bmfia_visualization_instance = None


def from_config_create(config, model_name):
    """
    Module function that calls the class function `from_config_create` and creates instance of the
    BMFIAVisualization class from the problem description.

    Args:
        config (dict): Dictionary created from the input file, containing the problem description
    """
    this.bmfia_visualization_instance = BMFIAVisualization.from_config_create(config, model_name)


class BMFIAVisualization(object):
    """
    Visualization class for BMFIA that containts several plotting, storing and visualization
    methods that can be used anywhere in QUEENS.

    Attributes:
       paths (list): List with paths to save the plots.
       save_bools (list): List with booleans to save plots.
       plot_booleans (list): List of booleans for determining whether individual plots should be
                             plotted or not.

    Returns:
        BMFIAVisualization (obj): Instance of the BMIAVisualization Class

    """

    # some overall class states
    plt.rcParams.update(plt.rcParamsDefault)
    plt.rcParams["mathtext.fontset"] = "cm"
    plt.rcParams.update({'font.size': 15})

    def __init__(self, paths, save_bools, plot_booleans):
        self.paths = paths
        self.save_bools = save_bools
        self.plot_booleans = plot_booleans

    @classmethod
    def from_config_create(cls, config, model_name):
        """
        Create the BMFIA visualization object from the problem description

        Args:
            config (dict): Dictionary containing the problem description
            model_name (str): Name of the BMFIA model in the config file

        Returns:
            Instance of BMFIA visualization (obj)

        """
        plotting_options = config[model_name].get("plotting_options")
        paths = [
            os.path.join(plotting_options.get("plotting_dir"), name)
            for name in plotting_options["plot_names"]
        ]
        save_bools = plotting_options.get("save_bool")
        plot_booleans = plotting_options.get("plot_booleans")
        return cls(paths, save_bools, plot_booleans)

    def plot(self, z_train, Y_HF_train, regression_obj_lst):
        """
        Plot the probabilistic manifold of high-fidelity, low-fidelity outputs and informative
        features of the input space, depending on the description in the input file. Also plot
        the probabilistic mapping along with its training points. Potentially animate and save
        these plots.

        Args:
            Y_HF_train (np.array): High-fidelity output training points
            z_train (np.array): Low-fidelity feature vector
            regression_obj_lst (lst): List of involved regression objects

        Returns:
            Plots of the probabilistic manifold

        """
        if self.plot_booleans[0]:
            plot_model_dependency(z_train, Y_HF_train, regression_obj_lst)
            if self.save_bools[0] is not None:
                _save_plot(self.save_bools[0], self.paths[0])


def plot_model_dependency(z_train, Y_HF_train, regression_obj_lst):
    """
    Plot the multi-fidelity dependency in :math:`\\Omega_{y_{lf}\\times y_{hf}}`
    or in :math:`\\Omega_{y_{lf}\\times y_{hf}\\times \\gamma_1}`

    Args:
        z_train (np.array): Training data for the low-fidelity vector that contains the
                            output of the low-fidelity model and potentially informative
                            low-fidelity features.
        Y_HF_train (np.array): Training vector of the high-fidelity model outputs
        regression_obj_lst (list): List containing (probabilistic)

    Returns:
        None

    """
    z_train = z_train.squeeze()
    Y_HF_train = Y_HF_train.squeeze()

    if z_train.ndim == 2:  # one array is already 2 dim due potentially several GPs
        _plot_2d_dependency(z_train, Y_HF_train, regression_obj_lst)
    elif z_train.ndim == 3:  # one array is already 3 dim due potentially several GPs
        _plot_3d_dependency(z_train, Y_HF_train, regression_obj_lst)
    else:
        raise RuntimeError("Dimension of intended surrogate is too high to be plotted! Abort")


def _plot_3d_dependency(z_train, Y_HF_train, regression_obj_lst):
    """
    Plot the 3D-dependency meaning the LF-HF dependency with one more informative feature.

    Args:
        z_train (np.array): Array of low-fidelity model output and informative features.
                            One sample per row
        Y_HF_train (np.array): Array of high-fidelity model outputs. One sample per row.
        regression_obj_lst (np.aray): List with regression models

    Returns:
        None

    """
    y_lf_test = np.linspace(np.min(z_train), np.max(z_train), 50)
    x_test, y_test = np.meshgrid(y_lf_test, y_lf_test)
    z_test = np.hstack((x_test.reshape(-1, 1), y_test.reshape(-1, 1)))
    fig = make_subplots(
        rows=4,
        cols=4,
        specs=[
            [{'type': 'surface'}, {'type': 'surface'}, {'type': 'surface'}, {'type': 'surface'}],
            [{'type': 'surface'}, {'type': 'surface'}, {'type': 'surface'}, {'type': 'surface'}],
            [{'type': 'surface'}, {'type': 'surface'}, {'type': 'surface'}, {'type': 'surface'}],
            [{'type': 'surface'}, {'type': 'surface'}, {'type': 'surface'}, {'type': 'surface'}],
        ],
    )
    for i in np.arange(4):
        for j in np.arange(4):
            reg_obj = regression_obj_lst[j + i * 4]
            output = reg_obj.predict(z_test, support='y')
            mu = output['mean']
            var = output['variance']
            row = j + 1
            col = i + 1

            fig.add_trace(
                go.Scatter3d(
                    x=z_train[0, :, 0].flatten(),
                    y=z_train[1, :, 0].flatten(),
                    z=Y_HF_train[:, 0].flatten(),
                    mode='markers',
                    marker=dict(size=5,),
                ),
                row=row,
                col=col,
            )

            fig.add_trace(
                go.Surface(
                    x=x_test,
                    y=y_test,
                    z=mu.reshape(x_test.shape),
                    colorscale='Viridis',
                    showscale=False,
                ),
                row=row,
                col=col,
            )
            fig.add_trace(
                go.Surface(
                    x=x_test,
                    y=y_test,
                    z=(mu.reshape(x_test.shape) - np.sqrt(var).reshape(x_test.shape)),
                    colorscale='Viridis',
                    showscale=False,
                    opacity=0.5,
                ),
                row=row,
                col=col,
            )
            fig.add_trace(
                go.Surface(
                    x=x_test,
                    y=y_test,
                    z=(mu.reshape(x_test.shape) + np.sqrt(var).reshape(x_test.shape)),
                    colorscale='Viridis',
                    showscale=False,
                    opacity=0.5,
                ),
                row=row,
                col=col,
            )

    fig.update_layout(
        scene=dict(
            xaxis=dict(title=r"$y_{LF}$"),
            yaxis=dict(title=r"$\gamma$"),
            zaxis=dict(title=r"$y_{HF}$"),
        )
    )

    fig.show()


def _plot_2d_dependency(z_train, Y_HF_train, regression_obj_lst):
    """
     Plot the 2D-dependency meaning the LF-HF dependency.

    Args:
        z_train (np.array): Array of low-fidelity model output and informative features.
                            One sample per row
        Y_HF_train (np.array): Array of high-fidelity model outputs. One sample per row.
        regression_obj_lst (np.aray): List with regression models

    Returns:
        None
   
    """

    sub_plot_square = int(np.ceil(np.sqrt(len(regression_obj_lst))))

    fig1, axs = plt.subplots(sub_plot_square, sub_plot_square)
    axs = axs.reshape(-1, 1)

    # --------------------------------------------------------------------------------

    # posterior mean
    for axx, regression_obj, z, yhf in zip(axs, regression_obj_lst, z_train.T, Y_HF_train.T):

        # generate support for plotting
        y_lf_test = np.linspace(np.min(yhf), np.max(yhf), 100)

        ax = axx[0]
        output_dict = regression_obj.predict(y_lf_test.T, 'y')
        mean_vec = output_dict['mean']
        var_vec = output_dict['variance']
        std_vec = np.atleast_2d(np.sqrt(var_vec)).T

        # identity
        ax.plot(
            Y_HF_train.reshape(-1, 1).squeeze(),
            Y_HF_train.reshape(-1, 1).squeeze(),
            linestyle='-',
            marker='',
            color='g',
            alpha=1,
            linewidth=2,
            label=r'$y_{\mathrm{HF}}=y_{\mathrm{LF}}$, (Identity)',
        )

        ax.scatter(
            z,
            yhf,
            marker='x',
            s=70,
            color='r',
            label=r'$\mathcal{D}_{y}=\{Y_{\mathrm{LF}},Y_{\mathrm{HF}}\}$, (Training)',
        )

        ax.plot(
            y_lf_test,
            mean_vec,
            color='darkblue',
            linewidth=1,
            label=r'$\mathrm{m}_{\mathcal{D}_y}(y_{\mathrm{LF}})$, (Posterior mean)',
        )

        # posterior confidence
        ax.plot(
            y_lf_test,
            np.add(mean_vec, 2 * std_vec),
            color='darkblue',
            linewidth=1,
            linestyle='--',
            alpha=0.5,
            label=r'$\mathrm{m}_{\mathcal{D}_y}(y_{\mathrm{LF}})\pm 2\cdot\sqrt{\mathrm{v}_'
            r'{\mathcal{D}_y}(y_{\mathrm{LF}})}$, (Confidence)',
        )

        ax.plot(
            y_lf_test,
            np.add(mean_vec, -2 * std_vec),
            color='darkblue',
            alpha=0.5,
            linewidth=1,
            linestyle='--',
        )

        ax.set_xlabel(r'$y_{\mathrm{LF}}$')
        ax.set_ylabel(r'$y_{\mathrm{HF}}$')
        ax.grid(which='major', linestyle='-')
        ax.grid(which='minor', linestyle='--', alpha=0.5)
        ax.set_xlim([min(y_lf_test), max(y_lf_test)])
        ax.set_ylim([min(y_lf_test), max(y_lf_test)])
        ax.minorticks_on()
        ax.legend()

    fig1.set_size_inches(25, 25)


def plot_posterior_from_samples(self, samples, weights, dim_labels_lst):
    """
    Visualize the multi-fideltiy posterior distribution (up to 2D) or its marginals
    for higher dimensional posteriors.

    Args:
        samples (np.array): Samples of the posterior. Each row is a differnt sample-vector.
                            Different columns represent the different dimensions of the posterior.
        weights (np.array): Weights of the posterior samples. One weight for each sample row.
        dim_labels_lst (lst): List with labels/naming of the involved dimensions.
                              Order of the list corresponds to order of columns in sample matrix.

    Returns:
        None

    """
    if self.plot_booleans[1]:

        if samples.shape[1] > 2:
            RuntimeError(
                f"At the moment we only support posterior plots up to two dimensions. "
                f"Your posterior has {samples.shape[1]}-dimensions. Abort ...."
            )

        sns.set_theme(style='whitegrid')
        f, ax = plt.subplots(figsize=(6, 6))
        sns.scatterplot(x=samples[:, 0], y=samples[:, 1], s=5)
        sns.kdeplot(
            x=samples[:, 0],
            y=samples[:, 1],
            weights=weights,
            thresh=0.1,
            levels=15,
            color='k',
            linewidths=1,
        )

        ax.set_title(r"Posterior distribution $p(x,y|D)$")
        ax.set_xlabel(fr'${dim_labels_lst[0]}$')
        ax.set_ylabel(fr'${dim_labels_lst[1]}$')
        ax.set_xlim(-0.2, 1.2)
        ax.set_ylim(-0.2, 1.2)

        plt.show()

        if self.save_bools[1] is not None:
            _save_plot(self.save_bools[1], self.paths[1])


def _save_plot(save_bool, path):
    """
    Save the plot to specified path.

    Args:
        save_bool (bool): Flag to decide whether saving option is triggered.
        path (str): Path where to save the plot.

    Returns:
        Saved plot.

    """
    if save_bool:
        plt.savefig(path, dpi=300)