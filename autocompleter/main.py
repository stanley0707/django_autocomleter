import re
import json
import sys
import collections 
import sys, inspect
from abc import ABCMeta
from functools import wraps
from collections import OrderedDict
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    raise ImportError("django autocomputer needs psycopg2 library and works only with Postgres")
try:
    from django.conf import settings
    from django.db import connection
except ImportError:
    raise ImportError("To run autocompeter version 0.0.1 you need Django")
try:
    from celery import task
    from celery.result import AsyncResult
    static_or_class = staticmethod
except ImportError:
    
    def stub(f):
        def decorated_function(self, *args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    
    static_or_class = classmethod
    task = stub
    AsyncResult = stub


class SearcherSerializer(object):
    """ Сериализация данным.
    Исключительно для автокомплита и кастомному
    поиску в бд.
    
    Все дочерние модели сериализации должны
    включать в себя class Meta с полем field
    значением которого будет список или кортеж
    полей который нужно отдать в API.

    TODO: в дальнейшей будет нужно строго задать
    тип fields как список или кортеж
    """
    __slots__ = ('list', 'res')
    
    __metaclass__ = ABCMeta
    
    def __init__(self, data=[], *args, **kwargs):
        self.fields = self.init_field()
        # принимаем обязательно асинхронный результат
        self.list = data
        self.res = {}
        self.__data()


    def init_field(self):
        try:
            return self.Meta.fields
        except AttributeError:
            return None        

    def __data(self):
        # срелизация записей
        i = 0
        
        for i2 in self.list:
            data = {}
            
            for i1 in self.fields:
                
                data[i1] = i2.get(i1)
                self.res[i] = data
                
            del data
            
            i+=1

    
    @property
    def data(self, *args, **kwargs):
        return self.res


class Searcher():
    """ Модель поиска подсторк Searcher.
    Подключаемся к db соединению djando.

    Разбираем api интерфейса в классе ApiView:
    создаем экземпляр, каждый раз отправляем 
    разные и необходимые модели для поиска
    вызывая метод get. Принимаем модель - model и
    и имя поля по которому будет производить поиск - column

    TODO: пока ищем только подстроку, но в дальнейшем можно
    будет учесть индексы и ошибки. 
    """
    
    SQL = """SELECT * 
                FROM {}
                WHERE lower({}) ILIKE lower('%{}%') limit {};"""
    
    def __init__(self, *args, **kwargs):
        self.connection = connection 
        # возможно может быть быстрее и полеезне
        # ипользовать отдельное содединение к базе
        # но пока использует коннект джанги
        # psycopg2.connect(user=db_user,
        #                         password="123",
        #                         host="127.0.0.1",
        #                         port="5432",
        #                         database=db_name
        #                     )
        self.cursor = self.processor
        self.serializer = SearcherSerializer
        self.data = []
        self.limit = None
        self.table = None
        self.cell = None
        self.value = None
        self.args = args
        self.kwargs = kwargs
    
    def dictfetchall(self, cursor):
        # комбинируем значение и ключи отвева
        # в генератора. Возвращаем список значений
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    
    def processor(self):
        # инициализируем курсор с SQL значением
        # инициализируем результат self.data 
        cursor = self.connection.cursor()
        cursor.execute(self.SQL)
        self.data = self.dictfetchall(cursor)
        return cursor
    
    def init_params(self, *args, **kwargs):
        try:
            self.limit = settings.AUTOCOMPLETER['LIMIT']
            self.table = re.sub('[!@#$)(;:]', '', kwargs['table'])
            self.cell = re.sub('[!@#$)(;:]', '', kwargs['cell'])
            self.value = re.sub('[!@#$)(;:]', '', kwargs['value'])
            
            for name, obj in inspect.getmembers(sys.modules[
                    settings.AUTOCOMPLETER['SERILEZER_CLASSES']]):
                try:
                    if inspect.isclass(obj):
                        if issubclass(obj, self.serializer) and obj.Meta.model._meta.db_table == self.table:
                            self.serializer = obj 
                
                except AttributeError:
                    pass
        
        except KeyError:
            pass
    
    @static_or_class
    @task
    def auctocomplete_run(cls, table, cell, value):
        
        if not cls:
            cls = Searcher()
        
        cls.init_params(table=table, cell=cell, value=value)

        cls.SQL = cls.SQL.format(
                cls.table, cls.cell, cls.value, cls.limit
            )

        cls.cursor().close()
        cls.connection.commit()
        return cls.serializer(cls.data).data


class Autocomleter(Searcher):
    
    def get(self, model, cell, value):
        model = model()
        try:
            if settings.AUTOCOMPLETER['CELERY']:
                
                return  AsyncResult(str(
                            self.auctocomplete_run.delay(cls=False, table=model._meta.db_table, cell=cell, value=value)
                            )
                        ).get()
            
            return  self.auctocomplete_run(self, table=model._meta.db_table, cell=cell, value=value)
        
        except KeyError:
            return  self.auctocomplete_run(self, table=model._meta.db_table, cell=cell, value=value)

        except AttributeError:
            raise AttributeError('needs AUTOCOMPLETER parameters in project settings')
