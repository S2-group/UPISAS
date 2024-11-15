class Tester:
    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data.get_data()

    def say_hello(self):
        print(f"Hello, {self.name}!")


class Data:
    def __init__(self, data):
        self.data = data

    def get_data(self):
        return self.data