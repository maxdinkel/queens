"""Database module."""

import abc
import logging
import sys

from pqueens.database import from_config_create_database as create_database

_logger = logging.getLogger(__name__)

# This construct follows the spirit of singleton design patterns
# Informally: there only exists one database instance
this = sys.modules[__name__]
this.database = None


def from_config_create_database(config):
    """Create a QUEENS DB object from config.

    Args:
        config (dict): Problem configuration
    """
    this.database = create_database(config)


class Database(metaclass=abc.ABCMeta):
    """QUEENS database base-class.

        This class is implemented such that it can be used in a context framework

        with database_obj:
            do_stuff()

    Attributes:
        database_name (str): Database name
        reset_existing_db (boolean): Flag to reset database
    """

    def __init__(self, db_name, reset_existing_db):
        """Initialize the database.

        Args:
            db_name (str): Name of the database
            reset_existing_db (bool): True if existing db is to be reset.
        """
        self.db_name = db_name
        self.reset_existing_db = reset_existing_db

    def __enter__(self):
        """'enter'-function in order to use the db objects as a context.

        This function is called
        prior to entering the context
        In this function:
            1. the connection is established
            2. the database may be reset

        Returns:
            self
        """
        self._connect()
        self._clean_database()
        _logger.info(self)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """'exit'-function in order to use the db objects as a context.

        This function is called at the end of the context in order to close the connection to the
        database.

        The exception as well as traceback arguments are required to implement the `__exit__`
        method, however, we do not use them explicitly.

        Args:
            exception_type: indicates class of exception (e.g. ValueError)
            exception_value: indicates exception instance
            traceback: traceback object
        """
        if exception_type:
            _logger.exception(exception_type(exception_value).with_traceback(traceback))

        self._disconnect()

    @abc.abstractmethod
    def save(self):
        """Save an entry to the database."""

    @abc.abstractmethod
    def load(self):
        """Load an entry from the database."""

    @abc.abstractmethod
    def remove(self):
        """Remove an entry from the database."""

    @abc.abstractmethod
    def _connect(self):
        """Connect to the database."""

    @abc.abstractmethod
    def _disconnect(self):
        """Close connection to the database."""

    @abc.abstractmethod
    def _delete_database(self):
        """Remove a single database."""

    def _delete_databases_by_prefix(self):
        """Remove all databases based on a prefix."""

    @abc.abstractmethod
    def _clean_database(self):
        """Clean up the database prior to a queens run.

        This includes actions like resetting existing databases delete
        all related databases or similar.
        """


class QUEENSDatabaseError(Exception):
    """QUEENS database error."""
