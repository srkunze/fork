FORK_
=====

Convert a classic sequential program into a parallel one.


Why?
----

It runs faster.


What if not?
------------

Don't use it.


How?
----

.. code:: python

    for image in images:
        create_thumbnail(image)       # original

    for image in images:
        fork(create_thumbnail, image) # parallelized explicitly 

    for image in images:
        create_thumbnail(image)       # parallelized implicitly (read below)


What about return values?
-------------------------

.. code:: python

    result = fork(my_func, *args, **kwargs)


And what is this result?
------------------------

A future that behaves almost exactly as if it were the return value of my_func. That in turn means, as soon as you access the result and it is not ready yet, the main thread blocks.


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


Parallelize implicitly?
-----------------------

If you don't like the fork calling syntax, you can convert certain functions into forks.

**Use with caution**

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


Contagious futures?
-------------------

You feel like debugging is too easy, don't you? Go ahead.

**Use with extreme caution**

.. code:: python

    @io_bound
    def item():
        # implementation

    result = 0
    for item in items:
        result += fork_contagious(item) # explicit
    print(result)

    # or

    @io_bound
    @contagious
    def item():
        # implementation

    result = 0
    for item in items:
        result += fork(item)            # implicit
    print(result)


Conclusion
----------

Good
****

- easy way back and forth (from sequential to parallel and vice versa)
- cascading possible (thread-safe)
- compatible with Python 2 and 3

Bad
***

- weird calling syntax (no syntax support)
- type(result) == BlockingFuture
- not working with coroutines (asyncio_) yet
- not working with lambdas due to PickleError


.. _FORK: https://pypi.python.org/pypi/xfork
.. _futures: https://pypi.python.org/pypi/futures
.. _asyncio: https://docs.python.org/3/library/asyncio.html