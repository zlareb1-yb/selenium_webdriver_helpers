# -*- coding: utf-8 -*-
'''Python module that implements singleton'''

class Singleton(type):
    """class that provides a Singleton, kind of a hack"""

    _instancesDict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instancesDict:
            cls._instancesDict[cls] = super().__call__(*args, **kwargs)

        return cls._instancesDict[cls]
