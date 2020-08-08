import dataset
import sys
from pyrecorder import record
import os


def get_db():
    return dataset.connect(f'mysql://root@localhost/my_db')


@record
def play():
    print("before get db")
    db = get_db()
    print("after db")
    my_table = db.create_table('my_table')
    print("after table")
    my_table.insert({
        'a': 'b',
        'c': 'd'
    })
    print("after insert")
    aa = my_table.find_one(a='b')
    print("after find")
    assert aa['c'] == 'd'


play()
