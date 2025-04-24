from utils import format_error_message


class CharacterActionError(Exception):
    def __init__(self, response, name, action, location):
        message = format_error_message(response, name, action, location)
        super().__init__(message)


class CharacterRequestBuildError(Exception):
    def __init__(self, message, name, action, location):
        super().__init__(message)
        self.layer = "Request construction"
        self.name = name
        self.action = action
        self.location = location
