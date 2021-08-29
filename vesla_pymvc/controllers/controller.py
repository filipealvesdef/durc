from abc import ABC, abstractmethod


class Controller(ABC):
    model_class = None


    def __init__(self):
        self.model = None


    @property
    def id(self): return self.model.id


    @classmethod
    def load(cls, db, id):
        c = cls()
        c.model = c.model_class.load(db, id)
        c.on_load(**c.model.to_dict())
        return c


    @classmethod
    def load_all(cls, db):
        models = cls.model_class.load_all(db)
        ctrls = []
        for m in models:
            c = cls()
            c.model = m
            c.on_load(**m.to_dict())
            ctrls.append(c)
        return ctrls


    @abstractmethod
    def on_load(self, **data):
        pass


    @classmethod
    def create(cls, db, **data):
        c = cls()
        c.model = cls.model_class.create(db, **data)
        return c


    @classmethod
    def delete(cls, db, id):
        c = cls()
        c.model_class.delete(db, id)


    def update(self, **data):
        try:
            self.model.update(**data)
        except Exception as e:
            raise e


    def to_dict(self):
        return self.model.to_dict()
