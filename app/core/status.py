from enum import Enum

class Status(str, Enum):
    TO_DO =  "To Do"
    DONE = "Done"
    CANCELLED = "Cancelled"