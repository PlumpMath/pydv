from visitor import visitor
from entity import entity, action, cmd
from utils import require
from os import environ

if 'DVPY_PRELOAD' in environ:
    for f  in environ['DVPY_PRELOAD'].split(':'):
        require(f)
