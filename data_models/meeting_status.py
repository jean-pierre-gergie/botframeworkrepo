from enum import Enum


class Status(Enum):
    """JPG
        declared  so no confusion is made
    """
    FAILED = 1
    SUCCESS = 2
    AMBIGUOUS = 3
    BUSY = 4
    OUT_OF_WORKING_HOURS =5
