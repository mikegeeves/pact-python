class CustomError(Exception):
    def __init__(self, *args):
        if args:
            self.topic = args[0]
        else:
            self.topic = None

    def __str__(self):
        if self.topic:
            return f"Custom Error: {self.topic}"


class DogHandler(object):
    def __init__(self, event):
        self.pass_event(event)

    @staticmethod
    def pass_event(event):
        if not all([x in event.keys() for x in ["id", "name", "type"]]):
            raise CustomError("missing fields")

        # do some other things to dog...
        # e.g. dogRepository.save(dog)
