
.. DO NOT EDIT.
.. THIS FILE WAS AUTOMATICALLY GENERATED BY SPHINX-GALLERY.
.. TO MAKE CHANGES, EDIT THE SOURCE PYTHON FILE:
.. "auto_examples\store-and-load-results.py"
.. LINE NUMBERS ARE GIVEN BELOW.

.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        :ref:`Go to the end <sphx_glr_download_auto_examples_store-and-load-results.py>`
        to download the full example code or to run this example in your browser via Binder

.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_store-and-load-results.py:


===========================================
Store and load `skopt` optimization results
===========================================

Mikhail Pak, October 2016.
Reformatted by Holger Nahrstaedt 2020

.. currentmodule:: skopt

Problem statement
=================

We often want to store optimization results in a file. This can be useful,
for example,

* if you want to share your results with colleagues;
* if you want to archive and/or document your work;
* or if you want to postprocess your results in a different Python instance or on an another computer.

The process of converting an object into a byte stream that can be stored in
a file is called _serialization_.
Conversely, _deserialization_ means loading an object from a byte stream.

**Warning:** Deserialization is not secure against malicious or erroneous
code. Never load serialized data from untrusted or unauthenticated sources!

.. GENERATED FROM PYTHON SOURCE LINES 29-35

.. code-block:: Python


    print(__doc__)
    import numpy as np

    from skopt import gp_minimize








.. GENERATED FROM PYTHON SOURCE LINES 36-41

Simple example
==============

We will use the same optimization problem as in the
:ref:`sphx_glr_auto_examples_bayesian-optimization.py` notebook:

.. GENERATED FROM PYTHON SOURCE LINES 41-60

.. code-block:: Python



    noise_level = 0.1


    def obj_fun(x, noise_level=noise_level):
        return np.sin(5 * x[0]) * (1 - np.tanh(x[0] ** 2)) + np.random.randn() * noise_level


    res = gp_minimize(
        obj_fun,  # the function to minimize
        [(-2.0, 2.0)],  # the bounds on each dimension of x
        x0=[0.0],  # the starting point
        acq_func="LCB",  # the acquisition function (optional)
        n_calls=15,  # the number of evaluations of f including at x0
        n_random_starts=3,  # the number of random initial points
        random_state=777,
    )





.. rst-class:: sphx-glr-script-out

 .. code-block:: none

    D:\git\scikit-optimize\skopt\optimizer\optimizer.py:517: UserWarning: The objective has been evaluated at point [5.2414561579894325e-09] before, using random point [-1.1498279780295497]
      warnings.warn(




.. GENERATED FROM PYTHON SOURCE LINES 61-77

As long as your Python session is active, you can access all the
optimization results via the `res` object.

So how can you store this data in a file? `skopt` conveniently provides
functions :class:`skopt.dump` and :class:`skopt.load` that handle this for you.
These functions are essentially thin wrappers around the
`joblib <https://joblib.readthedocs.io/en/latest/>`_ module's :obj:`joblib.dump` and :obj:`joblib.load`.

We will now show how to use :class:`skopt.dump` and :class:`skopt.load` for storing
and loading results.

Using `skopt.dump()` and `skopt.load()`
=======================================

For storing optimization results into a file, call the :class:`skopt.dump`
function:

.. GENERATED FROM PYTHON SOURCE LINES 77-82

.. code-block:: Python


    from skopt import dump, load

    dump(res, 'result.pkl')








.. GENERATED FROM PYTHON SOURCE LINES 83-84

And load from file using :class:`skopt.load`:

.. GENERATED FROM PYTHON SOURCE LINES 84-89

.. code-block:: Python


    res_loaded = load('result.pkl')

    res_loaded.fun





.. rst-class:: sphx-glr-script-out

 .. code-block:: none


    -0.33287005499757594



.. GENERATED FROM PYTHON SOURCE LINES 90-98

You can fine-tune the serialization and deserialization process by calling
:class:`skopt.dump` and :class:`skopt.load` with additional keyword arguments. See the
`joblib <https://joblib.readthedocs.io/en/latest/>`_ documentation
:obj:`joblib.dump` and
:obj:`joblib.load` for the additional parameters.

For instance, you can specify the compression algorithm and compression
level (highest in this case):

.. GENERATED FROM PYTHON SOURCE LINES 98-106

.. code-block:: Python


    dump(res, 'result.gz', compress=9)

    from os.path import getsize

    print('Without compression: {} bytes'.format(getsize('result.pkl')))
    print('Compressed with gz:  {} bytes'.format(getsize('result.gz')))





.. rst-class:: sphx-glr-script-out

 .. code-block:: none

    Without compression: 75397 bytes
    Compressed with gz:  27335 bytes




.. GENERATED FROM PYTHON SOURCE LINES 107-115

Unserializable objective functions
----------------------------------

Notice that if your objective function is non-trivial (e.g. it calls MATLAB
engine from Python), it might be not serializable and :class:`skopt.dump` will
raise an exception when you try to store the optimization results.
In this case you should disable storing the objective function by calling
:class:`skopt.dump` with the keyword argument `store_objective=False`:

.. GENERATED FROM PYTHON SOURCE LINES 115-118

.. code-block:: Python


    dump(res, 'result_without_objective.pkl', store_objective=False)








.. GENERATED FROM PYTHON SOURCE LINES 119-121

Notice that the entry `'func'` is absent in the loaded object but is still
present in the local variable:

.. GENERATED FROM PYTHON SOURCE LINES 121-128

.. code-block:: Python



    res_loaded_without_objective = load('result_without_objective.pkl')

    print('Loaded object: ', res_loaded_without_objective.specs['args'].keys())
    print('Local variable:', res.specs['args'].keys())





.. rst-class:: sphx-glr-script-out

 .. code-block:: none

    Loaded object:  dict_keys(['dimensions', 'base_estimator', 'n_calls', 'n_random_starts', 'n_initial_points', 'initial_point_generator', 'acq_func', 'acq_optimizer', 'x0', 'y0', 'random_state', 'verbose', 'callback', 'n_points', 'n_restarts_optimizer', 'xi', 'kappa', 'n_jobs', 'model_queue_size', 'space_constraint'])
    Local variable: dict_keys(['func', 'dimensions', 'base_estimator', 'n_calls', 'n_random_starts', 'n_initial_points', 'initial_point_generator', 'acq_func', 'acq_optimizer', 'x0', 'y0', 'random_state', 'verbose', 'callback', 'n_points', 'n_restarts_optimizer', 'xi', 'kappa', 'n_jobs', 'model_queue_size', 'space_constraint'])




.. GENERATED FROM PYTHON SOURCE LINES 129-143

Possible problems
=================

* **Python versions incompatibility:** In general, objects serialized in
  Python 2 cannot be deserialized in Python 3 and vice versa.
* **Security issues:** Once again, do not load any files from untrusted
  sources.
* **Extremely large results objects:** If your optimization results object

is extremely large, calling :class:`skopt.dump` with `store_objective=False` might
cause performance issues. This is due to creation of a deep copy without the
objective function. If the objective function it is not critical to you, you
can simply delete it before calling :class:`skopt.dump`. In this case, no deep
copy is created:

.. GENERATED FROM PYTHON SOURCE LINES 143-147

.. code-block:: Python


    del res.specs['args']['func']

    dump(res, 'result_without_objective_2.pkl')








.. rst-class:: sphx-glr-timing

   **Total running time of the script:** (0 minutes 1.543 seconds)


.. _sphx_glr_download_auto_examples_store-and-load-results.py:

.. only:: html

  .. container:: sphx-glr-footer sphx-glr-footer-example

    .. container:: binder-badge

      .. image:: images/binder_badge_logo.svg
        :target: https://mybinder.org/v2/gh/holgern/scikit-optimize/master?urlpath=lab/tree/notebooks/auto_examples/store-and-load-results.ipynb
        :alt: Launch binder
        :width: 150 px

    .. container:: sphx-glr-download sphx-glr-download-jupyter

      :download:`Download Jupyter notebook: store-and-load-results.ipynb <store-and-load-results.ipynb>`

    .. container:: sphx-glr-download sphx-glr-download-python

      :download:`Download Python source code: store-and-load-results.py <store-and-load-results.py>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
