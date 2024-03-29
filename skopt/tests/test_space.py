import numbers
import os
import re
from tempfile import NamedTemporaryFile

import numpy as np
import pytest
from numpy.testing import (
    assert_array_almost_equal,
    assert_array_equal,
    assert_equal,
    assert_raises_regex,
)

from skopt import Optimizer
from skopt.space import Categorical, Integer, Real, Space
from skopt.space import check_dimension as space_check_dimension
from skopt.space.space import _check_dimension as new_check_dimension
from skopt.utils import normalize_dimensions


def check_dimension(Dimension, vals, random_val):
    x = Dimension(*vals)
    assert_equal(x, Dimension(*vals))
    assert x != Dimension(vals[0], vals[1] + 1)
    assert x != Dimension(vals[0] + 1, vals[1])
    y = x.rvs(random_state=1)
    if isinstance(y, list):
        y = np.array(y)
    assert_equal(y, random_val)


def check_categorical(vals, random_val):
    x = Categorical(vals)
    assert_equal(x, Categorical(vals))
    assert x != Categorical(vals[:-1] + ("zzz",))
    assert_equal(x.rvs(random_state=1), random_val)


def check_limits(value, low, high):
    # check if low <= value <= high
    if isinstance(value, list):
        value = np.array(value)
    assert np.all(low <= value)
    assert np.all(high >= value)


@pytest.mark.fast_test
def test_dimensions():
    check_dimension(Real, (1.0, 4.0), 2.251066014107722)
    check_dimension(Real, (1, 4), 2.251066014107722)
    check_dimension(Integer, (1, 4), 2)
    check_dimension(Integer, (1.0, 4.0), 2)
    check_dimension(Integer, (1, 4), 2)
    check_categorical(("a", "b", "c", "d"), "b")
    check_categorical((1.0, 2.0, 3.0, 4.0), 2.0)
    check_categorical((1, 2, 3, 4), 2)


@pytest.mark.fast_test
def test_real_log_sampling_in_bounds():
    dim = Real(low=1, high=32, prior='log-uniform', transform='normalize')

    # round trip a value that is within the bounds of the space
    #
    # x = dim.inverse_transform(dim.transform(31.999999999999999))
    for n in (32.0, 31.999999999999999):
        round_tripped = dim.inverse_transform(dim.transform([n]))
        assert np.allclose([n], round_tripped)
        assert n in dim
        assert round_tripped in dim


@pytest.mark.fast_test
def test_real():
    a = Real(1, 25)
    for i in range(50):
        r = a.rvs(random_state=i)
        check_limits(r, 1, 25)
        assert r in a

    random_values = a.rvs(random_state=0, n_samples=10)
    assert len(random_values) == 10
    assert_array_equal(a.transform(random_values), random_values)
    assert_array_almost_equal(
        a.inverse_transform(random_values), random_values, decimal=12
    )

    log_uniform = Real(10**-5, 10**5, prior="log-uniform")
    assert log_uniform != Real(10**-5, 10**5)
    for i in range(50):
        random_val = log_uniform.rvs(random_state=i)
        check_limits(random_val, 10**-5, 10**5)
    random_values = log_uniform.rvs(random_state=0, n_samples=10)
    assert len(random_values) == 10
    transformed_vals = log_uniform.transform(random_values)
    assert_array_equal(transformed_vals, np.log10(random_values))
    assert_array_almost_equal(
        log_uniform.inverse_transform(transformed_vals), random_values, decimal=12
    )


@pytest.mark.fast_test
def test_real_bounds():
    # should give same answer as using check_limits() but this is easier
    # to read
    a = Real(1.0, 2.1)
    assert 0.99 not in a
    assert 1.0 in a
    assert 2.09 in a
    assert 2.1 in a
    assert np.nextafter(2.1, 3.0) not in a


@pytest.mark.fast_test
def test_integer():
    a = Integer(1, 10)
    for i in range(50):
        r = a.rvs(random_state=i)
        assert 1 <= r
        assert 11 >= r
        assert r in a

    random_values = a.rvs(random_state=0, n_samples=10)
    assert_array_equal(random_values.shape, (10))
    assert_array_equal(a.transform(random_values), random_values)
    assert_array_equal(a.inverse_transform(random_values), random_values)


@pytest.mark.fast_test
def test_categorical_transform():
    categories = ["apple", "orange", "banana", None, True, False, 3]
    cat = Categorical(categories)

    apple = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    orange = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    banana = [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    none = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
    true = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    false = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
    three = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]

    assert_equal(cat.transformed_size, 7)
    assert_equal(cat.transformed_size, cat.transform(["apple"]).size)
    assert_array_equal(
        cat.transform(categories), [apple, orange, banana, none, true, false, three]
    )
    assert_array_equal(cat.transform(["apple", "orange"]), [apple, orange])
    assert_array_equal(cat.transform(["apple", "banana"]), [apple, banana])
    assert_array_equal(cat.inverse_transform([apple, orange]), ["apple", "orange"])
    assert_array_equal(cat.inverse_transform([apple, banana]), ["apple", "banana"])
    ent_inverse = cat.inverse_transform(
        [apple, orange, banana, none, true, false, three]
    )
    assert_array_equal(ent_inverse, categories)


@pytest.mark.fast_test
def test_categorical_transform_binary():
    categories = ["apple", "orange"]
    cat = Categorical(categories)

    apple = [0.0]
    orange = [1.0]

    assert_equal(cat.transformed_size, 1)
    assert_equal(cat.transformed_size, cat.transform(["apple"]).size)
    assert_array_equal(cat.transform(categories), [apple, orange])
    assert_array_equal(cat.transform(["apple", "orange"]), [apple, orange])
    assert_array_equal(cat.inverse_transform([apple, orange]), ["apple", "orange"])
    ent_inverse = cat.inverse_transform([apple, orange])
    assert_array_equal(ent_inverse, categories)


@pytest.mark.fast_test
def test_categorical_repr():
    small_cat = Categorical([1, 2, 3, 4, 5])
    assert small_cat.__repr__() == "Categorical(categories=(1, 2, 3, 4, 5), prior=None)"

    big_cat = Categorical([1, 2, 3, 4, 5, 6, 7, 8])
    assert (
        big_cat.__repr__()
        == 'Categorical(categories=(1, 2, 3, ..., 6, 7, 8), prior=None)'
    )


@pytest.mark.fast_test
def test_space_consistency():
    # Reals (uniform)

    s1 = Space([Real(0.0, 1.0)])
    s2 = Space([Real(0.0, 1.0)])
    s3 = Space([Real(0, 1)])
    s4 = Space([(0.0, 1.0)])
    s5 = Space([(0.0, 1.0, "uniform")])
    s6 = Space([(0, 1.0)])
    s7 = Space([(np.float64(0.0), 1.0)])
    s8 = Space([(0, np.float64(1.0))])
    a1 = s1.rvs(n_samples=10, random_state=0)
    a2 = s2.rvs(n_samples=10, random_state=0)
    a3 = s3.rvs(n_samples=10, random_state=0)
    a4 = s4.rvs(n_samples=10, random_state=0)
    a5 = s5.rvs(n_samples=10, random_state=0)
    assert_equal(s1, s2)
    assert_equal(s1, s3)
    assert_equal(s1, s4)
    assert_equal(s1, s5)
    assert_equal(s1, s6)
    assert_equal(s1, s7)
    assert_equal(s1, s8)
    assert_array_equal(a1, a2)
    assert_array_equal(a1, a3)
    assert_array_equal(a1, a4)
    assert_array_equal(a1, a5)

    # Reals (log-uniform)
    s1 = Space([Real(10**-3.0, 10**3.0, prior="log-uniform", base=10)])
    s2 = Space([Real(10**-3.0, 10**3.0, prior="log-uniform", base=10)])
    s3 = Space([Real(10**-3, 10**3, prior="log-uniform", base=10)])
    s4 = Space([(10**-3.0, 10**3.0, "log-uniform", 10)])
    s5 = Space([(np.float64(10**-3.0), 10**3.0, "log-uniform", 10)])
    a1 = s1.rvs(n_samples=10, random_state=0)
    a2 = s2.rvs(n_samples=10, random_state=0)
    a3 = s3.rvs(n_samples=10, random_state=0)
    a4 = s4.rvs(n_samples=10, random_state=0)
    assert_equal(s1, s2)
    assert_equal(s1, s3)
    assert_equal(s1, s4)
    assert_equal(s1, s5)
    assert_array_equal(a1, a2)
    assert_array_equal(a1, a3)
    assert_array_equal(a1, a4)

    # Integers
    s1 = Space([Integer(1, 5)])
    s2 = Space([Integer(1.0, 5.0)])
    s3 = Space([(1, 5)])
    s4 = Space([(np.int64(1.0), 5)])
    s5 = Space([(1, np.int64(5.0))])
    a1 = s1.rvs(n_samples=10, random_state=0)
    a2 = s2.rvs(n_samples=10, random_state=0)
    a3 = s3.rvs(n_samples=10, random_state=0)
    assert_equal(s1, s2)
    assert_equal(s1, s3)
    assert_equal(s1, s4)
    assert_equal(s1, s5)
    assert_array_equal(a1, a2)
    assert_array_equal(a1, a3)

    # Integers (log-uniform)
    s1 = Space([Integer(16, 512, prior="log-uniform", base=2)])
    s2 = Space([Integer(16.0, 512.0, prior="log-uniform", base=2)])
    s3 = Space([(16, 512, "log-uniform", 2)])
    s4 = Space([(np.int64(16.0), 512, "log-uniform", 2)])
    s5 = Space([(16, np.int64(512.0), "log-uniform", 2)])
    a1 = s1.rvs(n_samples=10, random_state=0)
    a2 = s2.rvs(n_samples=10, random_state=0)
    a3 = s3.rvs(n_samples=10, random_state=0)
    assert_equal(s1, s2)
    assert_equal(s1, s3)
    assert_equal(s1, s4)
    assert_equal(s1, s5)
    assert_array_equal(a1, a2)
    assert_array_equal(a1, a3)

    # Categoricals
    s1 = Space([Categorical(["a", "b", "c"])])
    s2 = Space([Categorical(["a", "b", "c"])])
    s3 = Space([["a", "b", "c"]])
    a1 = s1.rvs(n_samples=10, random_state=0)
    a2 = s2.rvs(n_samples=10, random_state=0)
    a3 = s3.rvs(n_samples=10, random_state=0)
    assert_equal(s1, s2)
    assert_array_equal(a1, a2)
    assert_equal(s1, s3)
    assert_array_equal(a1, a3)

    s1 = Space([[True, False]])
    s2 = Space([Categorical([True, False])])
    s3 = Space([np.array([True, False])])
    assert s1 == s2 == s3

    # Categoricals Integer
    s1 = Space([Categorical([1, 2, 3])])
    s2 = Space([Categorical([1, 2, 3])])
    s3 = Space([[1, 2, 3]])
    a1 = s1.rvs(n_samples=10, random_state=0)
    a2 = s2.rvs(n_samples=10, random_state=0)
    a3 = s3.rvs(n_samples=10, random_state=0)
    assert_equal(s1, s2)
    assert_array_equal(a1, a2)
    assert_equal(s1, s3)
    assert_array_equal(a1, a3)

    s1 = Space([(True, False)])
    s2 = Space([Categorical([True, False])])
    s3 = Space([np.array([True, False])])
    assert s1 == s2 == s3


@pytest.mark.fast_test
def test_space_api():
    space = Space(
        [(0.0, 1.0), (-5, 5), ["a", "b", "c"], (1.0, 5.0, "log-uniform"), ["e", "f"]]
    )

    cat_space = Space([[1, "r"], [1.0, "r"]])
    assert isinstance(cat_space.dimensions[0], Categorical)
    assert isinstance(cat_space.dimensions[1], Categorical)

    assert_equal(len(space.dimensions), 5)
    assert isinstance(space.dimensions[0], Real)
    assert isinstance(space.dimensions[1], Integer)
    assert isinstance(space.dimensions[2], Categorical)
    assert isinstance(space.dimensions[3], Real)
    assert isinstance(space.dimensions[4], Categorical)

    samples = space.rvs(n_samples=10, random_state=0)
    assert_equal(len(samples), 10)
    assert_equal(len(samples[0]), 5)

    assert isinstance(samples, list)
    for n in range(4):
        assert isinstance(samples[n], list)

    assert isinstance(samples[0][0], numbers.Real)
    assert isinstance(samples[0][1], numbers.Integral)
    assert isinstance(samples[0][2], str)
    assert isinstance(samples[0][3], numbers.Real)
    assert isinstance(samples[0][4], str)

    samples_transformed = space.transform(samples)
    assert_equal(samples_transformed.shape[0], len(samples))
    assert_equal(samples_transformed.shape[1], 1 + 1 + 3 + 1 + 1)

    # our space contains mixed types, this means we can't use
    # `array_allclose` or similar to check points are close after a round-trip
    # of transformations
    for orig, round_trip in zip(samples, space.inverse_transform(samples_transformed)):
        assert space.distance(orig, round_trip) < 1.0e-8

    samples = space.inverse_transform(samples_transformed)
    assert isinstance(samples[0][0], numbers.Real)
    assert isinstance(samples[0][1], numbers.Integral)
    assert isinstance(samples[0][2], str)
    assert isinstance(samples[0][3], numbers.Real)
    assert isinstance(samples[0][4], str)

    for b1, b2 in zip(
        space.bounds,
        [
            (0.0, 1.0),
            (-5, 5),
            np.asarray(["a", "b", "c"]),
            (1.0, 5.0),
            np.asarray(["e", "f"]),
        ],
    ):
        assert_array_equal(b1, b2)

    for b1, b2 in zip(
        space.transformed_bounds,
        [
            (0.0, 1.0),
            (-5, 5),
            (0.0, 1.0),
            (0.0, 1.0),
            (0.0, 1.0),
            (np.log10(1.0), np.log10(5.0)),
            (0.0, 1.0),
        ],
    ):
        assert_array_equal(b1, b2)


@pytest.mark.fast_test
def test_space_from_space():
    # can you pass a Space instance to the Space constructor?
    space = Space(
        [(0.0, 1.0), (-5, 5), ["a", "b", "c"], (1.0, 5.0, "log-uniform"), ["e", "f"]]
    )

    space2 = Space(space)

    assert_equal(space, space2)


@pytest.mark.fast_test
def test_constant_property():
    space = Space([(0.0, 1.0), [1], ["a", "b", "c"], (1.0, 5.0, "log-uniform"), ["e"]])
    assert space.n_constant_dimensions == 2
    for i in [1, 4]:
        assert space.dimensions[i].is_constant
    for i in [0, 2, 3]:
        assert not space.dimensions[i].is_constant


@pytest.mark.fast_test
def test_set_get_transformer():
    # can you pass a Space instance to the Space constructor?
    space = Space(
        [(0.0, 1.0), (-5, 5), ["a", "b", "c"], (1.0, 5.0, "log-uniform"), ["e", "f"]]
    )

    transformer = space.get_transformer()
    assert_array_equal(
        ["identity", "identity", "onehot", "identity", "onehot"], transformer
    )
    space.set_transformer("normalize")
    transformer = space.get_transformer()
    assert_array_equal(["normalize"] * 5, transformer)
    space.set_transformer(transformer)
    assert_array_equal(transformer, space.get_transformer())

    space.set_transformer_by_type("label", Categorical)
    assert space.dimensions[2].transform(["a"]) == [0]


@pytest.mark.fast_test
def test_normalize():
    # can you pass a Space instance to the Space constructor?
    space = Space(
        [(0.0, 1.0), (-5, 5), ["a", "b", "c"], (1.0, 5.0, "log-uniform"), ["e", "f"]]
    )
    space.set_transformer("normalize")
    X = [[0.0, -5, 'a', 1.0, 'e']]
    Xt = np.zeros((1, 5))
    assert_array_equal(space.transform(X), Xt)
    assert_array_equal(space.inverse_transform(Xt), X)
    assert_array_equal(space.inverse_transform(space.transform(X)), X)


@pytest.mark.fast_test
def test_normalize_types():
    # can you pass a Space instance to the Space constructor?
    space = Space([(0.0, 1.0), Integer(-5, 5, dtype=int), [True, False]])
    space.set_transformer("normalize")
    X = [[0.0, -5, True]]
    Xt = np.zeros((1, 3))
    assert_array_equal(space.transform(X), Xt)
    assert_array_equal(space.inverse_transform(Xt), X)
    assert_array_equal(space.inverse_transform(space.transform(X)), X)
    assert isinstance(space.inverse_transform(Xt)[0][0], float)
    assert isinstance(space.inverse_transform(Xt)[0][1], int)
    assert isinstance(space.inverse_transform(Xt)[0][2], (np.bool_, bool))


@pytest.mark.fast_test
def test_normalize_real():

    a = Real(2.0, 30.0, transform="normalize")
    for i in range(50):
        check_limits(a.rvs(random_state=i), 2, 30)

    rng = np.random.RandomState(0)
    X = rng.randn(100)
    X = 28 * (X - X.min()) / (X.max() - X.min()) + 2

    # Check transformed values are in [0, 1]
    assert np.all(a.transform(X) <= np.ones_like(X))
    assert np.all(np.zeros_like(X) <= a.transform(X))

    # Check inverse transform
    assert_array_almost_equal(a.inverse_transform(a.transform(X)), X)

    # log-uniform prior
    a = Real(10**2.0, 10**4.0, prior="log-uniform", transform="normalize")
    for i in range(50):
        check_limits(a.rvs(random_state=i), 10**2, 10**4)

    rng = np.random.RandomState(0)
    X = np.clip(10**3 * rng.randn(100), 10**2.0, 10**4.0)

    # Check transform
    assert np.all(a.transform(X) <= np.ones_like(X))
    assert np.all(np.zeros_like(X) <= a.transform(X))

    # Check inverse transform
    assert_array_almost_equal(a.inverse_transform(a.transform(X)), X)

    a = Real(0, 1, transform="normalize", dtype=float)
    for i in range(50):
        check_limits(a.rvs(random_state=i), 0, 1)
    assert_array_equal(a.transformed_bounds, (0, 1))

    X = rng.rand()
    # Check transformed values are in [0, 1]
    assert np.all(a.transform(X) <= np.ones_like(X))
    assert np.all(np.zeros_like(X) <= a.transform(X))

    # Check inverse transform
    X_orig = a.inverse_transform(a.transform(X))
    assert isinstance(X_orig, float)
    assert_array_equal(X_orig, X)

    a = Real(0, 1, transform="normalize", dtype='float64')
    X = np.float64(rng.rand())
    # Check inverse transform
    X_orig = a.inverse_transform(a.transform(X))
    assert isinstance(X_orig, np.float64)

    a = Real(0, 1, transform="normalize", dtype=np.float64)
    X = np.float64(rng.rand())
    # Check inverse transform
    X_orig = a.inverse_transform(a.transform(X))
    assert isinstance(X_orig, np.float64)

    a = Real(0, 1, transform="normalize", dtype='float64')
    X = np.float64(rng.rand())
    # Check inverse transform
    X_orig = a.inverse_transform(a.transform(X))
    assert isinstance(X_orig, np.float64)


@pytest.mark.fast_test
def test_normalize_integer():
    a = Integer(2, 30, transform="normalize")
    for i in range(50):
        check_limits(a.rvs(random_state=i), 2, 30)
    assert_array_equal(a.transformed_bounds, (0, 1))
    rng = np.random.RandomState(0)
    X = rng.randint(2, 31, dtype=np.int64)
    # Check transformed values are in [0, 1]
    assert np.all(a.transform(X) <= np.ones_like(X))
    assert np.all(np.zeros_like(X) <= a.transform(X))

    # Check inverse transform
    X_orig = a.inverse_transform(a.transform(X))
    assert isinstance(X_orig, np.int64)
    assert_array_equal(X_orig, X)

    a = Integer(2, 30, transform="normalize", dtype=int)
    X = rng.randint(2, 31, dtype=int)
    # Check inverse transform
    X_orig = a.inverse_transform(a.transform(X))
    assert isinstance(X_orig, int)

    a = Integer(2, 30, transform="normalize", dtype='int')
    X = rng.randint(2, 31, dtype=int)
    # Check inverse transform
    X_orig = a.inverse_transform(a.transform(X))
    assert isinstance(X_orig, int)

    a = Integer(2, 30, prior="log-uniform", base=2, transform="normalize", dtype=int)
    for i in range(50):
        check_limits(a.rvs(random_state=i), 2, 30)
    assert_array_equal(a.transformed_bounds, (0, 1))

    X = rng.randint(2, 31, dtype=int)
    # Check transformed values are in [0, 1]
    assert np.all(a.transform(X) <= np.ones_like(X))
    assert np.all(np.zeros_like(X) <= a.transform(X))

    # Check inverse transform
    X_orig = a.inverse_transform(a.transform(X))
    assert isinstance(X_orig, int)
    assert_array_equal(X_orig, X)


@pytest.mark.fast_test
def test_normalize_categorical():
    categories = ["cat", "dog", "rat"]
    a = Categorical(categories, transform="normalize")
    for i in range(len(categories)):
        assert a.rvs(random_state=i)[0] in categories
    assert a.inverse_transform([0.0]) == [categories[0]]
    assert a.inverse_transform([0.5]) == [categories[1]]
    assert a.inverse_transform([1.0]) == [categories[2]]
    assert_array_equal(categories, a.inverse_transform([0.0, 0.5, 1]))

    categories = [1, 2, 3]
    a = Categorical(categories, transform="normalize")
    assert_array_equal(categories, np.sort(np.unique(a.rvs(100, random_state=1))))
    assert_array_equal(categories, a.inverse_transform([0.0, 0.5, 1.0]))

    categories = [1.0, 2.0, 3.0]
    a = Categorical(categories, transform="normalize")
    assert_array_equal(categories, np.sort(np.unique(a.rvs(100, random_state=1))))
    assert_array_equal(categories, a.inverse_transform([0.0, 0.5, 1.0]))

    categories = [1, 2, 3]
    a = Categorical(categories, transform="string")
    a.set_transformer("normalize")
    assert_array_equal(categories, np.sort(np.unique(a.rvs(100, random_state=1))))
    assert_array_equal(categories, a.inverse_transform([0.0, 0.5, 1.0]))


@pytest.mark.fast_test
def test_normalize_int():
    for dtype in [
        'int',
        'int8',
        'int16',
        'int32',
        'int64',
        'uint8',
        'uint16',
        'uint32',
        'uint64',
    ]:
        a = Integer(2, 30, transform="normalize", dtype=dtype)
        for X in range(2, 31):
            X_orig = a.inverse_transform(a.transform(X))
            assert_array_equal(X_orig, X)
    for dtype in [
        int,
        np.int8,
        np.int16,
        np.int32,
        np.int64,
        np.uint8,
        np.uint16,
        np.uint32,
        np.uint64,
    ]:
        a = Integer(2, 30, transform="normalize", dtype=dtype)
        for X in range(2, 31):
            X_orig = a.inverse_transform(a.transform(X))
            assert_array_equal(X_orig, X)
            assert isinstance(X_orig, dtype)


def check_valid_transformation(klass):
    assert klass(2, 30, transform="normalize")
    assert klass(2, 30, transform="identity")
    assert_raises_regex(
        ValueError,
        "should be 'normalize' or 'identity'",
        klass,
        2,
        30,
        transform='not a valid transform name',
    )


@pytest.mark.fast_test
def test_valid_transformation():
    check_valid_transformation(Integer)
    check_valid_transformation(Real)


@pytest.mark.fast_test
def test_invalid_dimension():
    assert_raises_regex(
        ValueError, "Invalid dimension '23'", space_check_dimension, "23"
    )
    # single value fixes dimension of space
    space_check_dimension([23])


DIMENSION_TESTS = [
    ((0, 1), Integer(0, 1)),
    ((0, 1, "uniform"), Integer(0, 1, "uniform")),
    ((1, 2, "log-uniform"), Integer(1, 2, "log-uniform")),
    ((0.0, 1), Real(0, 1)),
    ((0, 1.0), Real(0, 1)),
    ((0.0, 1.0), Real(0, 1)),
    ((0.0, 1.0, "uniform"), Real(0, 1, "uniform")),
    ((1.0, 2.0, "log-uniform"), Real(1, 2, "log-uniform")),
    ((1j, 2), ValueError("Invalid dimension")),
]

NEW_DIMENSION_TEST = [
    ({"key": "value"}, ValueError("Invalid dimension"), Categorical(["key"]), None),
    ([0, 1], Integer(0, 1), Categorical([0, 1]), None),
    (
        [1.0, 2.0, "log-uniform"],
        Real(1.0, 2.0, "log-uniform"),
        Categorical([1.0, 2.0, "log-uniform"]),
        None,
    ),
    (
        ("0", 1),
        Categorical(["0", 1]),
        Categorical(["0", 1]),
        UserWarning("miss-spelled"),
    ),
]


@pytest.mark.fast_test
@pytest.mark.parametrize("arg,result_or_error", DIMENSION_TESTS)
def test_check_dimension_inference(arg, result_or_error):
    if isinstance(result_or_error, Exception):
        error = result_or_error
        with pytest.raises(type(error), match=re.escape(str(error))):
            space_check_dimension(arg)
    else:
        result = result_or_error
        assert space_check_dimension(arg) == result


@pytest.mark.fast_test
@pytest.mark.parametrize(
    "arg,old_result_or_error,new_result_or_error,warning", NEW_DIMENSION_TEST
)
def test_new_check_dimension_inference(
    arg, old_result_or_error, new_result_or_error, warning
):
    # test new function interface
    if isinstance(new_result_or_error, Exception):
        error = new_result_or_error
        with pytest.raises(type(error), match=re.escape(str(error))):
            new_check_dimension(arg)
    else:
        new_result = new_result_or_error
        if warning is not None:
            with pytest.warns(type(warning), match=re.escape(warning.args[0])):
                assert new_check_dimension(arg) == new_result
        else:
            assert new_check_dimension(arg) == new_result

    # test that the wrapper warns of the difference
    # and still returns the old value or error
    if isinstance(old_result_or_error, Exception):
        error = old_result_or_error
        with pytest.raises(type(error), match=str(error)):
            space_check_dimension(arg)
    else:
        old_result = old_result_or_error
        if old_result != new_result:
            with pytest.warns(
                UserWarning,
                match=re.escape(f"Dimension {arg!r} was " f"inferred to {old_result}."),
            ):
                assert space_check_dimension(arg) == old_result
        else:
            assert space_check_dimension(arg) == old_result


@pytest.mark.fast_test
def test_categorical_identity():
    categories = ["cat", "dog", "rat"]
    cat = Categorical(categories, transform="identity")
    samples = cat.rvs(100)
    assert all([t in categories for t in cat.rvs(100)])
    transformed = cat.transform(samples)
    assert_array_equal(transformed, samples)
    assert_array_equal(samples, cat.inverse_transform(transformed))


@pytest.mark.fast_test
def test_categorical_string():
    categories = [1, 2, 3]
    categories_transformed = ["1", "2", "3"]
    cat = Categorical(categories, transform="string")
    samples = cat.rvs(100)
    assert all([t in categories for t in cat.rvs(100)])
    transformed = cat.transform(samples)
    assert all([t in categories_transformed for t in transformed])
    assert_array_equal(samples, cat.inverse_transform(transformed))


@pytest.mark.fast_test
def test_categorical_distance():
    categories = ['car', 'dog', 'orange']
    cat = Categorical(categories)
    for cat1 in categories:
        for cat2 in categories:
            delta = cat.distance(cat1, cat2)
            if cat1 == cat2:
                assert delta == 0
            else:
                assert delta == 1


@pytest.mark.fast_test
def test_integer_distance():
    ints = Integer(1, 10)
    for i in range(1, 10 + 1):
        assert_equal(ints.distance(4, i), abs(4 - i))


@pytest.mark.fast_test
def test_integer_distance_out_of_range():
    ints = Integer(1, 10)
    assert_raises_regex(
        RuntimeError, "compute distance for values within", ints.distance, 11, 10
    )


@pytest.mark.fast_test
def test_real_distance_out_of_range():
    ints = Real(1, 10)
    assert_raises_regex(
        RuntimeError, "compute distance for values within", ints.distance, 11, 10
    )


@pytest.mark.fast_test
def test_real_distance():
    reals = Real(1, 10)
    for i in range(1, 10 + 1):
        assert_equal(reals.distance(4.1234, i), abs(4.1234 - i))


@pytest.mark.parametrize(
    "dimension, bounds",
    [(Real, (2, 1)), (Integer, (2, 1)), (Real, (2, 2)), (Integer, (2, 2))],
)
def test_dimension_bounds(dimension, bounds):
    with pytest.raises(ValueError) as exc:
        _ = dimension(*bounds)
        assert "has to be less than the upper bound " in exc.value.args[0]


@pytest.mark.parametrize(
    "dimension, name",
    [
        (Real(1, 2, name="learning_rate"), "learning_rate"),
        (Integer(1, 100, name="n_trees"), "n_trees"),
        (Categorical(["red, blue"], name="colors"), "colors"),
    ],
)
def test_dimension_name(dimension, name):
    assert dimension.name == name


def test_dimension_name2():
    notnames = [1, 1.0, True]
    for n in notnames:
        with pytest.raises(ValueError) as exc:
            Real(1, 2, name=n)
            assert (
                "Dimension's name must be either string or" "None." == exc.value.args[0]
            )
    s = Space(
        [
            Real(1, 2, name="a"),
            Integer(1, 100, name="b"),
            Categorical(["red, blue"], name="c"),
        ]
    )
    assert s["a"] == (0, s.dimensions[0])
    assert s["a", "c"] == [(0, s.dimensions[0]), (2, s.dimensions[2])]
    assert s[["a", "c"]] == [(0, s.dimensions[0]), (2, s.dimensions[2])]
    assert s[("a", "c")] == [(0, s.dimensions[0]), (2, s.dimensions[2])]
    assert s[0] == (0, s.dimensions[0])
    assert s[0, "c"] == [(0, s.dimensions[0]), (2, s.dimensions[2])]
    assert s[0, 2] == [(0, s.dimensions[0]), (2, s.dimensions[2])]


@pytest.mark.fast_test
def test_dimension_names_setter():
    s = Space(
        [
            Real(1, 2, name="a"),
            Integer(1, 100, name="b"),
            Categorical(["red, blue"], name="c"),
        ]
    )
    with pytest.raises(ValueError) as exc:
        s.dimension_names = ["d", "e"]
        assert (
            "`names` must be the same length as "
            "`self.dimensions`." == exc.value.args[0]
        )
    s.dimension_names = ["d", "e", "f"]
    assert s.dimension_names == ["d", "e", "f"]


@pytest.mark.parametrize(
    "dimension", [Real(1, 2), Integer(1, 100), Categorical(["red, blue"])]
)
def test_dimension_name_none(dimension):
    assert dimension.name is None


@pytest.mark.fast_test
def test_space_from_yaml():
    with NamedTemporaryFile(delete=False) as tmp:
        tmp.write(
            b"""
        Space:
            - Real:
                low: 0.0
                high: 1.0
            - Integer:
                low: -5
                high: 5
            - Categorical:
                categories:
                - a
                - b
                - c
            - Real:
                low: 1.0
                high: 5.0
                prior: log-uniform
            - Categorical:
                categories:
                - e
                - f
        """
        )
        tmp.flush()

        space = Space(
            [
                (0.0, 1.0),
                (-5, 5),
                ["a", "b", "c"],
                (1.0, 5.0, "log-uniform"),
                ["e", "f"],
            ]
        )

        space2 = Space.from_yaml(tmp.name)
        assert_equal(space, space2)
        tmp.close()
        os.unlink(tmp.name)


@pytest.mark.parametrize("name", [1, 1.0, True])
def test_dimension_with_invalid_names(name):
    with pytest.raises(ValueError) as exc:
        Real(1, 2, name=name)
    assert "Dimension's name must be either string or None." == exc.value.args[0]


@pytest.mark.fast_test
def test_purely_categorical_space():
    # Test reproduces the bug in #908, make sure it doesn't come back
    dims = [Categorical(['a', 'b', 'c']), Categorical(['A', 'B', 'C'])]
    optimizer = Optimizer(dims, n_initial_points=2, random_state=3)

    for _ in range(2):
        x = optimizer.ask()
        # before the fix this call raised an exception
        optimizer.tell(x, np.random.uniform())


@pytest.mark.fast_test
def test_partly_categorical_space():
    dims = Space([Categorical(['a', 'b', 'c']), Categorical(['A', 'B', 'C'])])
    assert dims.is_partly_categorical
    dims = Space([Categorical(['a', 'b', 'c']), Integer(1, 2)])
    assert dims.is_partly_categorical
    assert not dims.is_categorical
    dims = Space([Integer(1, 2), Integer(1, 2)])
    assert not dims.is_partly_categorical


@pytest.mark.fast_test
def test_normalize_bounds():
    bounds = [(-999, 189000), Categorical((True, False))]
    space = Space(normalize_dimensions(bounds))
    for a in np.linspace(1e-9, 0.4999, 1000):
        x = space.inverse_transform([[a, a]])
        check_limits(x[0][0], -999, 189000)
        y = space.transform(x)
        check_limits(y, 0.0, 1.0)
    for a in np.linspace(0.50001, 1e-9 + 1.0, 1000):
        x = space.inverse_transform([[a, a]])
        check_limits(x[0][0], -999, 189000)
        y = space.transform(x)
        check_limits(y, 0.0, 1.0)


@pytest.mark.fast_test
def test_order_categorical_space():
    c = Categorical(("c", "b", "a"), transform="label")
    assert_array_equal(c.transform(["a", "b", "c"]), [2, 1, 0])
    c = Categorical((10, 30, 20), transform="label")
    assert_array_equal(c.transform([10, 20, 30]), [0, 2, 1])


@pytest.mark.fast_test
def test_space_from_df():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame(
        {
            "a": [1.5, 1.0, 2.0],
            "b": [50, 1, 100],
            "c": ["red", "blue", "blue"],
            4: [True, False, True],
        }
    )

    result = Space.from_df(
        df,
        priors={"a": "log-uniform"},
        bases={"b": 2},
        transforms={"b": "normalize", "c": "label"},
    )
    expected = Space(
        [
            Real(1.0, 2.0, prior="log-uniform", name="a"),
            Integer(1, 100, base=2, name="b", transform="normalize"),
            Categorical(["red", "blue"], transform="label", name="c"),
            Categorical([True, False], name="4"),
        ]
    )

    assert_equal(result, expected)


@pytest.mark.fast_test
def test_pandas_dependency_message():
    try:
        import pandas  # noqa

        pytest.skip("This test requires pandas to not be installed")
    except ImportError:
        # Check that pandas is imported lazily and that an informative error
        # message is raised when pandas is missing:
        expected_msg = "from_df requires pandas"
        with pytest.raises(ImportError, match=expected_msg):
            _ = Space.from_df(None)


@pytest.mark.parametrize(
    "dimension, bounds",
    [
        (Real, (-1, 1)),
        (Integer, (-1, 1)),
        (Real, (0, 1)),
        (Integer, (0, 1)),
        (Real, (-1, 0)),
        (Integer, (-1, 0)),
    ],
)
def test_dimension_loguniform_prior(dimension, bounds):
    # Raise error when Integer and Real dimensions
    # contain 0 but are instantiated with log-uniform prior
    lower, upper = bounds
    assert_raises_regex(
        ValueError,
        "search space should not contain 0 when using log-uniform prior",
        dimension,
        lower,
        upper,
        prior='log-uniform',
    )


@pytest.mark.fast_test
def test_constraint():
    def constraint(params):
        x, y, cond = params
        return cond == 'ok' and x**2 + y**2 <= 1

    space = Space(
        [Integer(-1, 3), Real(-1, 3), Categorical(['ok', 'skip'])],
        constraint=constraint,
    )
    for params in space.rvs(1000, random_state=0):
        assert constraint(params)

    # Constraint inherited from space
    space = Space(space, constraint=None)
    for params in space.rvs(1000, random_state=0):
        assert constraint(params)

    # Terminates on unsatisfiable constraint
    space = Space([space.dimensions[0]], constraint=lambda _: False)
    assert_raises_regex(RuntimeError, 'constraint', space.rvs, 1)
