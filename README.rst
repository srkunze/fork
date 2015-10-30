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

It's a proxy object that behaves almost exactly like the real return value of ``my_func``.
Furthermore, it evaluates only if needed; also in combination with operators (like +, - etc.).


Exception handling
------------------

Original (sequential) tracebacks are preserved. That should make debugging easier.
However, don't try to catch exceptions. You better want to exit and see them.
Use ``fork.evaluate`` to force evaluation in order to raise potential exceptions.


Speaking of threads ...
-----------------------

and processes? fork will take care of that for you.

You can assist fork by decorating your functions (not decorating defaults to cpu_bound):

.. code:: python

    @io_bound
    def call_remote_webservice():
        # implementation

    @cpu_bound
    def fib(n):
        # naive implementation of Fibonacci numbers

    @unsafe # don't fork; run sequentially
    def weird_side_effects(*args, **kwargs):
        # implementation

Advanced Feature: Force Specific Type of Execution
--------------------------------------------------
If you really need more control over the type of exeution, use ``fork.process`` or ``fork.thread``.
They work just like ``fork.fork`` but enforce the corresponding type of background execution.

.. code:: python

    import pkg_resources
    for worker_function in pkg_resources.iter_entry_points(group='worker'):
        process(worker_function)

Advanced Feature: Implicit Forks
--------------------------------

If you don't like the fork calling syntax, you can convert functions into stand-alone forks.

**Use with caution.**

.. code:: python

    @io_bound_fork
    def create_thumbnail_by_webservice(image):
        # implementation
    
    @cpu_bound_fork
    def create_thumbnail_by_bare_processing_power(image):
        # implementation
    
    # the following two lines spawn two forks
    create_thumbnail_by_webservice(image1)
    create_thumbnail_by_bare_processing_power(image2)


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
