#!/usr/bin/env python3

""" Class Checkpoint is a decorator for use on pure functions.  """

import datetime as dt
import functools
import inspect
import logging
import pickle
from typing import Any, Callable, Final, Optional, TypeVar
import os

import humanize  # type: ignore

logger = logging.getLogger(__name__)

LOAD_FAILURE_MESSAGE: Final[str] = (
    "There was a problem while loading checkpoint data from file. "
    "Reverting to executing the function."
)
CREATE_FAILURE_MESSAGE: Final[str] = (
    "There was a problem while creating checkpoint file but function completed sucessfully. "
    "Returning value without writing checkpoint file."
)


def set_log_level(level: int) -> None:
    """ Set log level """
    logger.setLevel(level)


def _get_mtime_in_tz(file_name: str, timezone: Optional[dt.tzinfo]) -> dt.datetime:
    """ Returns the modification time of file_name in timezone """
    timestamp: dt.datetime = dt.datetime.fromtimestamp(os.path.getmtime(file_name))
    return timestamp.astimezone(timezone)


def _get_my_timezone() -> Optional[dt.tzinfo]:
    """ Returns the local timezone """
    return dt.datetime.utcnow().astimezone().tzinfo


def _get_time_ago(time_in_tz: dt.datetime, timezone: Optional[dt.tzinfo]) -> str:
    """ Returns human readable time since time_in_tz """
    return humanize.naturaltime(time_in_tz, when=dt.datetime.now().astimezone(timezone))


def _get_caller_up(levels_up: int) -> str:
    call_location: str = ""
    caller: inspect.FrameInfo = inspect.stack()[levels_up]
    try:
        base: str = os.path.basename(caller.filename)
        call_location = f"{base}:{caller.lineno}"
    finally:
        # see note on 'Keeping references to stack objects' here:
        # https://docs.python.org/3/library/inspect.html#inspect-stack
        del caller
    return call_location


def _pickled(value: Any, file_name: str) -> bool:
    try:
        pickle.dump(value, open(file_name, "wb"))
        return True
    except (pickle.PicklingError, PermissionError):
        return False


TIMEZONE: Final[Optional[dt.tzinfo]] = _get_my_timezone()

# generic type, use for decorated function return type
GenericType = TypeVar("GenericType")


def checkpoint(func: Callable[..., Any]) -> Callable[..., GenericType]:
    """
    A decorator for use on pure functions.

    Pickles the function output and uses the saved value on subsequent executions
    of the same line of code. Writes .*.ckpnt files to current working directory.
    """

    @functools.wraps(func)
    def wrapper_checkpoint(*args, **kwargs) -> GenericType:
        checkpoint_time_in_tz: dt.datetime
        call_location: str = _get_caller_up(2) + f":{func.__name__}"
        pickle_base_file_name: str = f".{call_location}.ckpnt"
        pickle_file_name: str = os.path.join(os.getcwd(), pickle_base_file_name)
        if os.path.isfile(pickle_file_name):
            checkpoint_time_in_tz = _get_mtime_in_tz(pickle_file_name, TIMEZONE)
            logger.info(
                (
                    "Checkpoint from %s found (%s). "
                    "Skipping function execution and loading result from file."
                ),
                _get_time_ago(checkpoint_time_in_tz, TIMEZONE),
                checkpoint_time_in_tz,
            )
            try:
                return pickle.load(open(pickle_file_name, "rb"))
            except (pickle.UnpicklingError, PermissionError):
                logger.warning(LOAD_FAILURE_MESSAGE)
        value: GenericType = func(*args, **kwargs)
        if _pickled(value, pickle_file_name):
            checkpoint_time_in_tz = _get_mtime_in_tz(pickle_file_name, TIMEZONE)
            logger.info(
                "Checkpoint created at: %s with filename %s.",
                _get_mtime_in_tz(pickle_file_name, TIMEZONE),
                pickle_base_file_name,
            )
        else:
            logger.warning(CREATE_FAILURE_MESSAGE)
        return value

    return wrapper_checkpoint
