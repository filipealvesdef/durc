from cerberus import Validator
from .utils import clone, camel_to_snake
import uuid


class Model:
    schema = {
        'id': {
            'type': 'string',
            'required': True,
            'default_setter': lambda _: str(uuid.uuid4())
        },
        'children': {
            'type': 'dict',
            'valuesrules': {
                'type': 'list',
                'schema': { 'type': 'string' },
            },
        },
    }
    validation_opts = {}
    children_model_classes = {}

    @classmethod
    @property
    def collection(cls):
        return camel_to_snake(cls.__name__.replace('Model', ''))


    @classmethod
    @property
    def graphql_name(cls):
        name = cls.__name__.replace('Model', '')
        if name.endswith('s'):
            name = name[:-1]
        return name


    @classmethod
    def clone(cls, name=''):
        class cln(cls):
            pass
        cln.__name__ = name if name else cls.__name__
        cln.schema = clone(cls.schema)
        cln.children_model_classes = clone(cls.children_model_classes)
        return cln


    def __init__(self, db=None, **data):
        self.db = db
        m_cls = [(k, v['class']) for k, v in self.children_model_classes.items()]
        self.on_children_classes(m_cls)
        self.set_attrs(**data)


    def on_children_classes(self, children_classes):
        self.children_classes = children_classes
        self.children_models = dict([(k, []) for k, _ in self.children_classes])


    def __getattr__(self, k):
        try:
            attrs = self.attrs
            if k in attrs:
                return attrs[k]
            for i, d in attrs.items():
                if type(d) == dict and k in d:
                    return d[k]
            raise KeyError
        except KeyError:
            print(f'{k} was not found in {self.id}')


    def set_attrs(self, **data):
        attrs = self.schema_attrs
        updated = {}
        for k, v in data.items():
            if type(v) == dict and k in attrs:
                updated_dict = attrs[k] | v
                if updated_dict != attrs[k]:
                    updated[k] = updated_dict
            elif k not in attrs or v != attrs[k]:
                updated[k] = v
        resulting_attrs = attrs | updated
        try:
            self.validate(resulting_attrs)
        except Exception as e:
            raise e
        resulting_attrs = self.normalize(resulting_attrs)
        defaults_appended = dict(filter(lambda a: a[0] not in attrs and
            a[0] not in updated, resulting_attrs.items()))
        updated |= defaults_appended
        for k, v in updated.items():
            setattr(self, k, v)
        return updated


    @classmethod
    def normalize(cls, data):
        v = Validator(cls.schema, **cls.validation_opts)
        return v.normalized(data)


    @classmethod
    def validate(cls, data):
        v = Validator(cls.schema, **cls.validation_opts)
        if not v.validate(data):
            raise Exception(v.errors)


    @property
    def attrs(self):
        return dict([(k, v) for k, v in self.__dict__.items()])


    @property
    def schema_attrs(self):
        return dict ([(k, v) for k, v in self.attrs.items() if k in self.schema])


    def load_children(self):
        if 'children' not in self.attrs: return
        for col_id, model_cls in self.children_classes:
            if col_id not in self.children: continue
            for id in self.children[col_id]:
                child_model = model_cls.load(self.db, id)
                self.append_child(col_id, child_model)


    def append_child(self, attr_id, model):
        if attr_id not in self.children_models:
            raise Exception('not in children models')
        self.children_models[attr_id].append(model)
        if len(self.children_models[attr_id]) == 1:
            setattr(self, attr_id, model)
        else:
            setattr(self, attr_id, self.children_models[attr_id])


    @classmethod
    def load_from_data(cls, db, **data):
        model = cls(db, **data)
        model.load_children()
        return model


    def create_children(self):
        if 'children' not in self.attrs:
            self.children = {}
        for col_id, model_cls in self.children_classes:
            child_model = model_cls.create(self.db)
            self.append_child(col_id, child_model)


    @classmethod
    def create_from_data(cls, db, **data):
        m = cls(db, **data)
        m.create_children()
        return m


    @classmethod
    def load(cls, db, id):
        try:
            data = db.get(id, cls.collection)
            return cls.load_from_data(db, **data)
        except Exception as e:
            raise e


    @classmethod
    def load_one(cls, db):
        try:
            data = db.get_one(cls.collection)
            return cls.load_from_data(db, **data)
        except Exception as e:
            raise e


    @classmethod
    def load_all(cls, db):
        try:
            data = db.get_all(cls.collection)
            models = []
            for entry in data:
                models.append(cls.load_from_data(db, **entry))
            return models
        except Exception as e:
            raise e


    @classmethod
    def create(cls, db, **data):
        try:
            m = cls.create_from_data(db, **data)
            data = m.to_dict()
            db.create(cls.collection, **data)
            return m
        except Exception as e:
            raise e


    def update(self, **data):
        try:
            updated = self.set_attrs(**data)
            if updated:
                self.db.update(self.id, self.collection, **updated)
        except Exception as e:
            raise e


    def delete(self):
        try:
            self.db.delete(self.id, self.collection)
            for models in self.children_models.values():
                for model in models:
                    model.delete()
            return True
        except Exception as e:
            raise e


    def to_dict(self):
        try:
            return self.schema_attrs
        except Exception as e:
            print(e)


    @staticmethod
    def graphql_fields(schema):
        types_map = {
            'string': 'String',
            'number': 'Float',
            'integer': 'Int',
            'boolean': 'Boolean',
        }
        schema_str = ''
        for k, v in schema.items():
            if v['type'] in types_map:
                t = 'ID' if k == 'id' else types_map[v['type']]
                req = '!' if 'required' in v and v['required'] else ''
                schema_str += f'    {k}: {t}{req}\n'
        return schema_str


    @classmethod
    def to_graphql_type(cls, interface=''):
        interface = f' implements {interface}' if interface else ''
        schema_str = f'type {cls.graphql_name}{interface} ' + '{\n'
        schema_str += Model.graphql_fields(cls.schema)
        for c_id, child in cls.children_model_classes.items():
            child_cls = child['class']
            quantity = child['quantity']
            ob = '[' if quantity == '*' or quantity == '+' else ''
            cb = ']' if ob else ''
            req = '!' if quantity == '+' or quantity == '1' else ''
            schema_str += f'    {c_id}: {ob}{child_cls.graphql_name}{cb}{req}\n'
        schema_str += '}\n'
        return schema_str
