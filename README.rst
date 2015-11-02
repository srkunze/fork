FORK_
=====

Write a classic sequential program. Then convert it into a parallel one.


Why?
----

It runs faster.


What if not?
------------

Don't use it.


How?
----

Before:

.. code:: python

    for image in images:
        create_thumbnail(image)

After:

.. code:: python

    from fork import fork

    for image in images:
        fork(create_thumbnail, image)


What about return values?
-------------------------

As usual:

.. code:: python

    result = fork(my_func, *args, **kwargs)

It's a proxy object that behaves almost exactly like the real return value of ``my_func`` except that
it's lazy.


How lazy?
---------

Very lazy. You can even add, multiply, etc. such proxy results without blocking which come in
quite hand, especially in loops. Use ``fork.await``, ``str``, ``print``, etc. to force evaluation
and get the real and non-lazy value back.

.. code:: python

    sizes = 0
    for image in images:
        sizes += fork(create_thumbnail, image) # lazy evaluation
    print(sizes)                               # forces evaluation


Threads or Processes?
---------------------

You don't need to bother. fork will take care of that for you.

You can assist fork by decorating your functions; not decorating defaults to ``fork.cpu_bound``:

.. code:: python

    @io_bound
    def call_remote_webservice():
        # implementation

    @cpu_bound
    def heavy_computation(n):
        # implementation


Exception handling
------------------

Original (sequential) tracebacks are preserved. That should make debugging easier.
However, don't try to catch exceptions. You better want to exit and see them.
When you force evaluation potential exceptions will be raised.


Advanced Feature: Force Specific Type of Execution
--------------------------------------------------

If you really need more control over the type of execution, use ``fork.process`` or ``fork.thread``.
They work just like ``fork.fork`` but enforce the corresponding type of background execution.

.. code:: python

    import pkg_resources

    for worker_function in pkg_resources.iter_entry_points(group='worker'):
        process(worker_function)


Advanced Feature: Multiple Execution At Once
--------------------------------------------

You can shorten your programs by using ``fork.map``. It works like ``fork.fork`` but submits
a function multiple times for each item given by an iterable.

.. code:: python

    results = fork.map(create_thumbnail, images)

``fork.map_process`` and ``fork.map_thread`` work accordingly and force a specific type of
execution. Use those if really necessary.
Otherwise, just use ``fork.map``. fork take care for you in this case again.

In order to wait for the completion of a set of result proxies, use ``fork.await_all``. If you want to
unblock by the first unblocking result proxy, call ``fork.await_any``.

There are also blocking variants available: ``fork.block_map``, ``fork.block_map_process`` and
``fork.block_map_thread``; in case you need some syntactic sugar:

.. code:: python

    fork.await_all(fork.map(create_thumbnail, images))
    # equals
    fork.block_map(create_thumbnail, images)


Conclusion
----------

Good
****

- easy to give it a try / easy way from sequential to parallel and back
- results evaluate lazily
- sequential tracebacks are preserved
- it's thread-safe / cascading forks possible
- compatible with Python 2 and 3

Bad
***

- weird calling syntax (no syntax support)
- type(result) == ResultProxy
- not working with lambdas due to PickleError
- needs fix:

  - not working with coroutines (asyncio_) yet (working on it)

- cannot fix efficiently:

  - exception handling (force evaluation when entering and leaving try blocks)

- ideas are welcome :-)


.. _FORK: https://pypi.python.org/pypi/xfork
.. _asyncio: https://docs.python.org/3/library/asyncio.html
