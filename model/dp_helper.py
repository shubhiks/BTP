class dpstate:
    def __init__(self, taxino, curloc, curtime, users_in_taxi):
        self.taxino = taxino
        self.curloc = curloc
        self.curtime = curtime
        self.users_in_taxi = users_in_taxi

    def to_string(self):
        return self.taxino + " " + self.curloc + " " + self.curtime + " " + self.users_in_taxi;