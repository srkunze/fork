# FORK #

Convert a classic sequential program into parallel one.


## Why? ##

It runs faster.


## What if not? ##

Don't use it.


## How? ##

Like this:

    # sequential
    for image in images:
        create_thumbnail(image)

    # parallel
    for image in images:
        fork(create_thumbnail, image)


## What about return values? ##

    result = fork(my_func, *args, **kwargs)


## And what is this result? ##

A future that behaves almost exactly as if it were the return value of my_func. That in turn means, as soon as you access the result and it is not ready yet, the main thread blocks.


## Speaking of threads ... ##

and processes? That depends on whether your function is @io_bound or @cpu_bound. Not decorated means @cpu_bound.

If necessary, decorate your functions:

    @io_bound
    def call_remote_webservice():
        # implementation

    @cpu_bound
    def fib(n):
        # naive implementation of Fibonacci numbers

    @unsafe # don't fork; run sequentially
    def weird_side_effects(*args, **kwargs):
        # implementation

## Something else? ##

Sure. If you don't like the fork calling syntax, try those decorators:

    @io_bound_fork
    def create_thumbnail_by_webservice(image):
        # implementation
    
    @cpu_bound_fork
    def create_thumbnail_by_bare_processing_power(image):
        # implementation
    
    # the following two lines spawn two forks
    create_thumbnail_by_webservice()
    create_thumbnail_by_bare_processing_power()
    

## Conclusion ##

### Good ###

- easy way back and forth (from sequential to parallel and vice versa)
- cascading possible (thread-safe)
- Python 3 (out of the box)
- Python 2 (via pip install futures)

### Bad ###

- weird calling syntax (no syntax support)
- type(result) == BlockingFuture
- not working with coroutines (asyncio) yet
- future is not contagious yet
- not working with lambdas due to PickleError
