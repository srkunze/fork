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


## What about results? ##

    result = fork(my_func, *args, **kwargs)


## And what is result? ##

A future that behaves almost exactly as if it were the result. That in turn means, as soon as you access the result and it is not ready yet, the main thread blocks.


## Speaking of threads ... ##

and processes? That depends on whether your function is @io_bound or @cpu_bound. Not decorated means @cpu_bound.

If necessary, decorate your functions:

    @io_bound
    def my_webservice():
        # implementation

    @cpu_bound
    def fib(n):
        # naive implementation of Fibonacci numbers

    @unsafe # don't fork; run sequentially
    def weird_side_effects(*args, **kwargs):
        # implementation

## Conclusion ##

### Good ###

- easy way back and forth (from sequential to parallel and vice versa)

### Bad ###

- weird calling syntax (no syntax support)
- type(result) == BlockingFuture
- only Python 3 for now
- not working with lambdas
- not thread-safe
