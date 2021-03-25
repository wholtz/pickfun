"""
Many of the tests in the file reference specific line numbers in this
file where checkpointed functions are called. When adding or removing
lines, you'll need to check all tests below your edit to see if
there are line number references that need to be updated
(search for '.test_pickfun.py:').
"""
import logging
import os
import pickle
import pickfun.pickfun as pickfun
import pytest
import datetime as dt

from pickfun import __version__


@pickfun.checkpoint
def check_square(i):
    return i * i


@pytest.fixture
def cwd_to_tmp(tmpdir):
    os.chdir(tmpdir)


def test_get_caller_up():
    assert pickfun._get_caller_up(1) == "test_pickfun.py:29"


def test_pickled(cwd_to_tmp):
    file_name = "foo"
    pickfun._pickled(5, file_name)
    assert pickle.load(open(file_name, "rb")) == 5


def test_get_time_ago():
    current = dt.datetime.now().astimezone(pickfun._get_my_timezone())
    timezone = current.astimezone().tzinfo
    old = current - dt.timedelta(minutes=8)
    assert pickfun._get_time_ago(old, timezone) == "8 minutes ago"


def test_write(cwd_to_tmp):
    check_square(10)
    assert pickle.load(open(".test_pickfun.py:46:check_square.ckpnt", "rb")) == 100


def test_load(cwd_to_tmp):
    pickle.dump(7, open(".test_pickfun.py:52:check_square.ckpnt", "wb"))
    assert check_square(999) == 7


def test_repeat(cwd_to_tmp):
    for x in [1, 2, 3]:
        result = check_square(x)
    assert result == 1


def test_load_failure(cwd_to_tmp, caplog):
    with open(".test_pickfun.py:65:check_square.ckpnt", "a") as f:
        f.write("Hello\n")
    logging.getLogger(__name__)
    assert check_square(10) == 100
    assert "There was a problem while loading checkpoint data from file." in caplog.text


def test_write_failure(tmpdir, cwd_to_tmp, caplog):
    os.chmod(str(tmpdir), 0o555)
    logging.getLogger(__name__)
    assert check_square(10) == 100
    assert "There was a problem while creating checkpoint file" in caplog.text


def test_set_log_level(cwd_to_tmp, caplog):
    pickfun.set_log_level(logging.ERROR)
    assert check_square(10) == 100
    assert "Checkpoint created at: " not in caplog.text


def test_version():
    assert __version__ == "0.1.0"


def test_higher_order_function_init(cwd_to_tmp):
    assert pickfun.checkpoint(sum)([1, 2]) == 3


def test_higher_order_function_repeat(cwd_to_tmp):
    my_list = [1, 2]
    for i in range(3):
        out = pickfun.checkpoint(sum)([1, 2])
        my_list.append(i)
    assert out == 3
