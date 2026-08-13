from enum import Enum, auto

class TaskStatus(str, Enum):
    TO_DO =  "To Do"
    DONE = "Done"
    CANCELLED = "Cancelled"


class FriendshipStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    DENIED = "Denied"
