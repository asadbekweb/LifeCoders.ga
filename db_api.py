#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.sql.elements import TextClause
from sqlalchemy import util
import dataset
import threading
import settings
from dataset.types import Types
import traceback
from queue import Queue

q = Queue()
default_tables = \
{
    'users':{
            'primary':'user_id',
            'column':
                {
                    'user_id':Types.integer,
                    'menu':Types.text,
                    'refs':Types.text,
                    'referal':Types.integer,
                    'balance':Types.integer,
                    'ref_balance':Types.integer,
                    'add_info':Types.text,
                    'channels':Types.text,
                    'username':Types.text
                }
            },
    'channels':{
            'primary':'channel_name',
            'column':
                {
                    'channel_name':Types.text,
                    'channel_id':Types.integer,
                    'chat_id': Types.integer,
                    'views':Types.integer,
                    'active':Types.boolean,
                    'user_id':Types.integer,
                    'cost':Types.integer,
                    'owner':Types.integer,

                }
    },
    'transactions':{
        'primary':'trans_id',
        'column':
            {
                'trans_id':Types.integer,
                'user_id':Types.integer,
                'type':Types.text,
                'count':Types.float,
                'date':Types.text,
                'username':Types.text,
                'qiwi_number':Types.text,
                'status':Types.text
            }
    },
    'activity': {
        'primary': 'trans_id',
        'column':
            {
                'trans_id': Types.integer,
                'comment': Types.text,
                'type': Types.text,
                'currency': Types.integer,
                'count': Types.float,
                'date': Types.text,
                'add': Types.text
            }
    },
    'qiwi': {
        'primary': 'trans_id',
        'column':
            {
                'trans_id': Types.integer,
                'user_id': Types.integer,
                'type': Types.text,
                'count': Types.float,
                'date': Types.text,
                'add': Types.text,
                'currency': Types.integer,
                'comment': Types.text,

            }
    },
    'code_to_qiwi': {
        'primary': 'user',
        'column':
            {
                'user': Types.integer,
                'code': Types.text,
                'chat_id': Types.integer
            }
    },
}



def create_table(tables):
    db = dataset.connect(settings.db_url)
    db_tables = db.tables
    try:
        for tblname in tables:
            if tblname not in db_tables:
                table_created = db.create_table(table_name=tblname,primary_id=tables[tblname]['primary'],primary_type=tables[tblname]['column'][tables[tblname]['primary']])
                print(table_created)
                for clmn in tables[tblname]['column']:
                    table_created.create_column(name=clmn,type=tables[tblname]['column'][clmn])
                print ('Table(s) successfully created')
    except:
        print ('Ooops, error while creating table(s)')
        traceback.print_exc()


class get_from_db(object):
    """dot.notation access to dictionary attributes"""
    def __getattr__ (self,name):
        self.name = name
        return self.get
    def get(self,**kwargs):
        db = dataset.connect(settings.db_url,engine_kwargs={'connect_args':{'check_same_thread':False}})
        if self.name in db.tables:
            table = db.get_table(self.name)
            result = list(table.find(**kwargs))
            return result
        else:
            return None

class insert_to_table(object):
    def __getattr__ (self,name):
        self.name = name
        return self.insert
    def insert(self,**kwargs):
        q.put({'name':self.name,'kwargs':kwargs})
        return


def worker():
    db = dataset.connect(settings.db_url)
    while True:
        try:
            res = q.get(block=True)
            name = res['name']
            kwargs = res['kwargs']


            if name in db.tables:
                table = db.get_table(name)

                if name in default_tables:
                    result = table.upsert(kwargs, default_tables[name]['primary'])
                else:
                    result = table.insert(kwargs)
                    q.task_done()

            else:
                q.task_done()
        except:
            db = dataset.connect(settings.db_url)
            continue




class sum_of(object):
    def __getattr__ (self,name):
        self.name = name
        return self.sumof
    def sumof(self,row,**kwargs):

        db = dataset.connect(settings.db_url,engine_kwargs={'connect_args':{'check_same_thread':False}})
        if self.name in db.tables:
            table = db.get_table(self.name)
            querry = '''SELECT
	sum({})

FROM
	{}
WHERE {};'''.format(row,self.name,' AND '.join(["{}={}".format(i,kwargs[i]) if isinstance(kwargs[i],(int,float)) else '{}="{}"'.format(i,kwargs[i])  for i in kwargs ])
)
            result = db.query(querry)
            return result
        else:
            return False

class count_of(object):
    def __getattr__ (self,name):
        self.name = name
        return self.count
    def count(self,**kwargs):

        db = dataset.connect(settings.db_url,engine_kwargs={'connect_args':{'check_same_thread':False}})
        if self.name in db.tables:
            table = db.get_table(self.name)
            result = table.count(TextClause(util.text_type(" AND ".join(["{}={}".format(i,kwargs[i]) if isinstance(kwargs[i],(int,float)) else '{}="{}"'.format(i,kwargs[i])  for i in kwargs ]))))
            return result
        else:
            return False

class delete_from_table(object):
    def __getattr__ (self,name):
        self.name = name
        return self.delete
    def delete(self,**kwargs):

        db = dataset.connect(settings.db_url,engine_kwargs={'connect_args':{'check_same_thread':False}})

        if self.name in db.tables:
            table = db.get_table(self.name)

            if self.name in default_tables:
                result = table.delete(**kwargs)
            else:
                result = table.delete(**kwargs)
            return result
        else:
            return False

create_table(default_tables)
threading.Thread(target=worker).start()
get = get_from_db()
insert = insert_to_table()
sumof = sum_of()
count = count_of()
delete = delete_from_table()
