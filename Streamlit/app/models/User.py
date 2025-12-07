class User:
    """Represents a user of the platform."""

    def __init__(self, username: str, password_hash: str, role: str):
        self.__username = username
        self.__password_hash = password_hash
        self.__role = role

    def get_username(self):
        return self.__username

    def get_role(self):
        return self.__role

    def get_hash(self):
        return self.__password_hash
 