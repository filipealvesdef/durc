from abc import ABC, abstractmethod


class DB(ABC):
    @staticmethod
    @abstractmethod
    def init(config):
        pass

    @abstractmethod
    def get(self, id, collection_id):
        # This method returns an entry by the given id from a collection
        pass

    @abstractmethod
    def get_one(self, collection_id):
        # This method must returns a single entry from the given collection
        pass

    @abstractmethod
    def get_all(self, collection_id):
        # This must return all entries from the given collection
        pass

    @abstractmethod
    def update(self, id, collection_id, **data):
        # This method updates the given entry from the specified collection with
        # the provided data
        pass

    @abstractmethod
    def create(self, collection_id, **data):
        # This creates an entry in the given collection
        pass


    @abstractmethod
    def delete(self, id, collection_id):
        # This deletes the given entry from the specified  collection
        pass
