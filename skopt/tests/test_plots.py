"""Scikit-optimize plotting tests."""

import matplotlib.pyplot as plt
import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier

from skopt import (
    Optimizer,
    expected_minimum,
    expected_minimum_random_sampling,
    gp_minimize,
    plots,
)
from skopt.benchmarks import bench3
from skopt.plots import (
    _evaluate_min_params,
    partial_dependence_1D,
    partial_dependence_2D,
)
from skopt.space import Categorical, Integer


def save_axes(ax, filename):
    """Save matplotlib axes `ax` to an image `filename`."""
    fig = plt.gcf()
    fig.add_axes(ax)
    fig.savefig(filename)


@pytest.mark.slow_test
def test_plots_work():
    """Basic smoke tests to make sure plotting doesn't crash."""
    SPACE = [
        Integer(1, 20, name='max_depth'),
        Integer(2, 100, name='min_samples_split'),
        Integer(5, 30, name='min_samples_leaf'),
        Integer(1, 30, name='max_features'),
        Categorical(['gini', 'entropy'], name='criterion'),
        Categorical(list('abcdefghij'), name='dummy'),
    ]

    def objective(params):
        clf = DecisionTreeClassifier(
            random_state=3,
            **{dim.name: val for dim, val in zip(SPACE, params) if dim.name != 'dummy'}
        )
        X, y = load_breast_cancer(return_X_y=True)
        return -np.mean(cross_val_score(clf, X, y))

    res = gp_minimize(objective, SPACE, n_calls=10, random_state=3)

    x = [
        [11, 52, 8, 14, 'entropy', 'f'],
        [14, 90, 10, 2, 'gini', 'a'],
        [7, 90, 6, 14, 'entropy', 'f'],
    ]
    samples = res.space.transform(x)
    xi_ = [1.0, 10.5, 20.0]
    yi_ = [-0.9240883492576596, -0.9240745890422687, -0.9240586402439884]
    xi, yi = partial_dependence_1D(res.space, res.models[-1], 0, samples, n_points=3)
    assert_array_almost_equal(xi, xi_)
    assert_array_almost_equal(yi, yi_, 2)

    xi_ = [0, 1]
    yi_ = [-0.9241087603770617, -0.9240188905968352]
    xi, yi = partial_dependence_1D(res.space, res.models[-1], 4, samples, n_points=3)
    assert_array_almost_equal(xi, xi_)
    assert_array_almost_equal(yi, yi_, 2)

    xi_ = [0, 1]
    yi_ = [1.0, 10.5, 20.0]
    zi_ = [
        [-0.92412562, -0.92403575],
        [-0.92411186, -0.92402199],
        [-0.92409591, -0.92400604],
    ]
    xi, yi, zi = partial_dependence_2D(
        res.space, res.models[-1], 0, 4, samples, n_points=3
    )
    assert_array_almost_equal(xi, xi_)
    assert_array_almost_equal(yi, yi_)
    assert_array_almost_equal(zi, zi_, 2)

    x_min, f_min = expected_minimum_random_sampling(res, random_state=1)
    x_min2, f_min2 = expected_minimum(res, random_state=1)

    assert x_min == x_min2
    assert f_min == f_min2

    plots.plot_convergence(res)
    plots.plot_evaluations(res)
    plots.plot_objective(res)
    plots.plot_objective(res, dimensions=["a", "b", "c", "d", "e", "f"])
    plots.plot_objective(res, minimum='expected_minimum_random')
    plots.plot_objective(
        res, sample_source='expected_minimum_random', n_minimum_search=10000
    )
    plots.plot_objective(res, sample_source='result')
    plots.plot_regret(res)
    plots.plot_objective_2D(res, 0, 4)
    plots.plot_histogram(res, 0, 4)

    # TODO: Compare plots to known good results?
    # Look into how matplotlib does this.


@pytest.mark.slow_test
def test_plots_work_without_cat():
    """Basic smoke tests to make sure plotting doesn't crash."""
    SPACE = [
        Integer(1, 20, name='max_depth'),
        Integer(2, 100, name='min_samples_split'),
        Integer(5, 30, name='min_samples_leaf'),
        Integer(1, 30, name='max_features'),
    ]

    def objective(params):
        clf = DecisionTreeClassifier(
            random_state=3,
            **{dim.name: val for dim, val in zip(SPACE, params) if dim.name != 'dummy'}
        )
        X, y = load_breast_cancer(return_X_y=True)
        return -np.mean(cross_val_score(clf, X, y))

    res = gp_minimize(objective, SPACE, n_calls=10, random_state=3)
    plots.plot_convergence(res)
    plots.plot_evaluations(res)
    plots.plot_objective(res)
    plots.plot_objective(res, minimum='expected_minimum')
    plots.plot_objective(res, sample_source='expected_minimum', n_minimum_search=10)
    plots.plot_objective(res, sample_source='result')
    plots.plot_regret(res)

    # TODO: Compare plots to known good results?
    # Look into how matplotlib does this.


def test_plots_skip_constant():
    """Test that constant dimension are properly skipped."""
    SPACE = [
        Categorical([0], name="dummy"),
        Categorical([0], name="dummy"),
        Integer(1, 20, name='max_depth'),
        Integer(1, 20, name='max_depth'),
    ]
    X, y = load_breast_cancer(return_X_y=True)

    def objective(params):
        clf = DecisionTreeClassifier(
            random_state=3,
            **{dim.name: val for dim, val in zip(SPACE, params) if dim.name != 'dummy'}
        )
        return -np.mean(cross_val_score(clf, X, y))

    res = gp_minimize(objective, SPACE, n_calls=10, random_state=3)
    print(res.space)
    print(plots._map_categories(res.space, res.x_iters, res.x))
    plots.plot_evaluations(res)


@pytest.mark.fast_test
def test_evaluate_min_params():
    res = gp_minimize(
        bench3,
        [(-2.0, 2.0)],
        x0=[0.0],
        noise=1e-8,
        n_calls=8,
        n_random_starts=3,
        random_state=1,
    )

    x_min, f_min = expected_minimum(res, random_state=1)
    x_min2, f_min2 = expected_minimum_random_sampling(
        res, n_random_starts=1000, random_state=1
    )
    plots.plot_gaussian_process(res)
    assert _evaluate_min_params(res, params='result') == res.x
    assert _evaluate_min_params(res, params=[1.0]) == [1.0]
    assert _evaluate_min_params(res, params='expected_minimum', random_state=1) == x_min
    assert (
        _evaluate_min_params(
            res, params='expected_minimum', n_minimum_search=20, random_state=1
        )
        == x_min
    )
    assert (
        _evaluate_min_params(
            res, params='expected_minimum_random', n_minimum_search=1000, random_state=1
        )
        == x_min2
    )


def test_names_dimensions():
    # Define objective
    def objective(x, noise_level=0.1):
        return (
            np.sin(5 * x[0]) * (1 - np.tanh(x[0] ** 2))
            + np.random.randn() * noise_level
        )

    # Initialize Optimizer
    opt = Optimizer([(-2.0, 2.0)], n_initial_points=2)

    # Optimize
    for _ in range(3):
        next_x = opt.ask()
        f_val = objective(next_x)
        res = opt.tell(next_x, f_val)

    # Plot results
    plots.plot_objective(res)


@pytest.mark.slow_test
@pytest.mark.parametrize('acq_func', ['EI', 'EIps', 'PI', 'PIps', 'gp_hedge', 'LCB'])
def test_plot_gaussian_process_works(acq_func):

    def objective(x):
        return x[0] ** 2

    def objective_ps(x):
        return x[0] ** 2, x[0] + 1

    if acq_func.endswith("ps"):
        obj = objective_ps
    else:
        obj = objective

    res = gp_minimize(
        obj, [(-1, 1)], n_calls=2, n_initial_points=2, random_state=1, acq_func=acq_func
    )

    plots.plot_gaussian_process(res)
