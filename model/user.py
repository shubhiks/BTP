class User:
    def __init__(self, name, id, email, password):
        self.name = name
        self.id = id
        self.email = email
        self.password = password

    def to_string(self):
        return self.name + " " + self.id + " " + self.email + " " + self.password


class TriggerRequest:
    def __init__(self, user_id, destination_id, timestamp):
        self.user_id = user_id
        self.destination_id = destination_id
        self.timestamp = timestamp

    def to_string(self):
        return self.user_id + " " + self.destination_id + " " + self.timestamp