import re
from abc import abstractmethod
from colorlog import getLogger
from ..parser import liberty_parser
from . import atomic

logger = getLogger("main")


class LibBuilderError(Exception):
    def __init__(self, msg, line=None):
        super().__init__(f"Line {line}: {msg}" if line else msg)


class LibBuilder:
    def __init__(self, name, db, reference="un-assigned"):
        """
        An example builder class for generating LIB file.
        name: Pin/Bus Name
        db: data dictionary
        reference: template reference file.
        """
        self.name = name
        self.db = db
        self.reference = reference

        self.lib = None
        self.build()

    @abstractmethod
    def build(self):
        pass

    def dump(self, level=0):
        try:
            return self.lib.dump(level=level)
        except AttributeError:
            logger.error(f"LIB object for {self.name} is NOT set up.", exc_info=True)