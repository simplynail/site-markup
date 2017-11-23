from tinydb import *

from .decorators import *


@singleton
class Store(TinyDB):
    pass

# http://eli.thegreenplace.net/2011/08/14/python-metaclasses-by-example
# http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Metaprogramming.html
class EntityManagerMeta(type):
    def __init__(cls, what, bases=None, dict=None):
        if cls.__name__ is not 'Model':
            cls.em = cls.store.table(cls.__name__)
        super(EntityManagerMeta,cls).__init__(what, bases, dict)


# base model object
class Model(object):
    tables = []
    db_columns = []

    @staticmethod
    def define_db(db_path,*args):
        Model.store = Store(db_path)
        for additional_class in args:
            Model.tables.append(additional_class)
        for one_class in Model.tables:
            one_class.em = Model.store.table(one_class.__name__)

    def __init__(self, *args, **kwargs):
        #super(Model,self).__init__(*args,**kwargs)
        for key, value in kwargs.items():
            #if not callable(value) and not key.startswith('_'):
            self.__dict__[key] = value
        print('received to Model constrctor: ',kwargs)
        '''
        if key=='belly_pos' or key=='belly_text':
            continue
        print(type(key),':',key,' ; ',type(value),':', value)
        try:
            self.__dict__[key].set(value)
        except:
            setattr(self,key,value)
        '''

    @classmethod
    def objects(cls):
        return Manager(cls)

    @property
    def dictify(self):
        fields = dict((key,getattr(self,key)) for key in dir(self) if key in self.db_columns)
        #if not callable(value) and not key.startswith('_')
        return fields

    def save(self):
        if hasattr(self, 'db_id') and self.db_id:
            self.em.update(self.dictify, eids=[self.db_id])
        else:
            self.db_id = self.em.insert(self.dictify)
        print('saving: ', self.dictify)
        return self.db_id

    def delete(self):
        if hasattr(self, 'db_id') and self.db_id:
            self.em.remove(eids=[self.db_id])

    def __str__(self):
        return str(self.__dict__)

    def __unicode__(self):
        return str(self.__dict__)


# accompanying object for querying against models
class Manager(object):
    def __init__(self, model_class):
        self.model_class = model_class
        self.em = model_class.em

    def _model(self, result):
        if result is None: return None
        instance = self.model_class(**result)
        instance.db_id = result.eid
        return instance

    def exists(self, query=None):
        query = Query() if query is None else query
        return self.em.exists(query)

    def first(self, query=None):
        if isinstance(query, int):
            return self._model(self.em.get(eid=query))
        query = Query() if query is None else query
        return self._model(self.em.get(query))

    def find(self, query=None):
        if isinstance(query, int):
            return self._model(self.em.get(eid=query))
        query = Query() if query is None else query
        return list(map(self._model, self.em.search(query)))

    def all(self):
        return list(map(self._model, self.em.all()))
