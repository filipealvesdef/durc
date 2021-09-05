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
        c.set_model(c.model_class.load(db, id))
        return c


    @classmethod
    def load_all(cls, db):
        models = cls.model_class.load_all(db)
        ctrls = []
        for m in models:
            c = cls()
            c.set_model(m)
            ctrls.append(c)
        return ctrls


    @abstractmethod
    def on_load(self, **data):
        pass


    @classmethod
    def create(cls, db, **data):
        c = cls()
        c.set_model(cls.model_class.create(db, **data))
        return c


    def set_model(self, model):
        self.model = model
        self.on_load(**model.to_dict())


    def delete(self):
        self.model.delete()


    def update(self, **data):
        try:
            self.model.update(**data)
        except Exception as e:
            raise e


    def to_dict(self):
        return self.model.to_dict()
