class ITTicket:
    """Represents an IT support ticket."""

    def __init__(self, ticket_id, title, priority, status, assigned_to):
        self.__id = ticket_id
        self.__title = title
        self.__priority = priority
        self.__status = status
        self.__assigned_to = assigned_to

    def get_id(self):
        return self.__id

    def get_title(self):
        return self.__title

    def get_priority(self):
        return self.__priority

    def get_status(self):
        return self.__status

    def get_assigned_to(self):
        return self.__assigned_to

    def assign(self, name):
        self.__assigned_to = name

    def close(self):
        self.__status = "Closed"
