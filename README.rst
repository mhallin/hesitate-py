********
Hestiate
********

.. image:: https://travis-ci.org/mhallin/hesitate-py.svg?branch=master
   :target: https://travis-ci.org/mhallin/hesitate-py

Like ``assert``, but less... assertive.

----

Are you skipping on writing your ``assert`` statements because of performance reasons? Skip no more!
Hesitate will, through probabilistic means, make your Design by Contract-assertions faster!

How?
----

By not executing them.

Yeah.

Hesitate will measure the execution time on every assert statement you write, and execute the slow
ones less frequently than the fast ones. You decide on what you think is a reasonable amount of time
per assertion, and Hesitate will control how often your assertions run in order to match that.

For assertions with unknown timings, it will use a user configurable initial probability to ensure
that a newly started system isn't flooded by slow assertions.

It looks like this:

.. code-block:: python

    # worker.py

    def do_work(data):
        assert data_is_valid(data)  # Super slow!

        return work_work(data)


    # main.py

    import hesitate
    hesitate.attach_hook()

    import worker
    worker.do_work(invalid_data)  # Might not raise AssertionError! Who knows?

Hesitate works with an AST rewriter influenced to py.test_. It hooks on to Python's module loader
where it intercepts and rewrites code on the fly as it is loaded.


.. _py.test: http://pytest.org
