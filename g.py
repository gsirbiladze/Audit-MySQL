from dbmanager import DBManager
from sqlstorage import *
import pprint
import sys

def f_1():
    print('This is function f_1')

def f_2():
   print('This is function f_2')

def f_3():
    print('This is function f_3')

def f_4():
    print('This is function f_4')

def f_5():
    print('This is function f_5')

def f_6():
    print('This is function f_6')

fswitcher = {
    'f1' : f_1, 
    'f2' : f_2, 
    'f3' : f_3, 
    'f4' : f_4, 
    'f5' : f_5, 
    'f6' : f_6
}

first_argument = sys.argv[1] if len(sys.argv)>1 else 'fuka'


if first_argument in fswitcher.keys():
    fswitcher[first_argument]()
else:
    print('This is first argument: {0}'.format(first_argument))


