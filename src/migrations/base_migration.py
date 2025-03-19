import abc


class BaseMigration(abc.ABC):

    def __init__(self, table_name: str):
        self.table_name = table_name
    @abc.abstractmethod
    def up(self):
        pass

    @abc.abstractmethod
    def down(self):
        pass
