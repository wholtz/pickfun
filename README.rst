PickFun
=======
A python decorator and higher-order function for checkpointing functions.
PickFun (pickle function) saves the result of a function to a checkpoint
file on disk. If your program returns to the same line, it will load the
result from the checkpoint file rather than running the function again. 

WARNING
-------
PickFun obtaining the result from the checkpoint file is not conditional
on the function being passed the same arguments as the invocation when
the checkpoint file was created. This package was designed for simple
linear scripts (such as Jupyter notebooks), where looping does not occur,
but system restarts can break up long running computations.

Usage
----
There are two ways to use pickfun.

1. Decorate a function:

    .. code:: python

        import pickfun

        @pickfun.checkpoint
        def square(x):
            return x * x

        square(3)

2. Call your function from a higher-order function:

    .. code:: python

        import pickfun
        pickfun.checkpoint(sum)([1, 2])

Method (1) is best if you are adding a checkpoint to your own
function and you want the checkpoint active on every call to that
function. Method (2) is for when you can't directly decorate a 
function (because it is someone eles's code and you don't want to 
wrap the function) or if you only want checkpoints active on a
subset of the function invocations.

If either of the above examples are run twice, the first invocation
will execute the called function and write a checkpoint file.
A second invocation will load the previous result of the square or sum
function from the checkpoint file.

Checkpoint files
----------------
The checkpoint files are written to the current working directory and are
named '.<source file name>:<line number>:<function name>.ckpnt'. They are
python pickle files.

Development setup
-----------------
1. ``git clone https://github.com/wholtz/pickfun && cd pickfun``
2. Install `poetry <https://python-poetry.org/>`_  with ``curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -``
3. Install `pyenv <https://github.com/pyenv/pyenv>`_ with ``curl https://pyenv.run | bash``
4. Use pyenv to install the most recent versions of Python 3.8.x and 3.9.x with ``pyenv install 3.8.8 &&  pyenv install 3.9.2 && pyenv local``
5. ``poetry install``
6. ``poetry run nox``

