# HashTable.py
# Author: Kristen Friday
# Date: September 5, 2021

# Contains the basic implementation of the following 4 operations:
#  insert(key, value)
#  lookup(key)
#  remove(key)
#  scan(regex)


import re


class HashTable:

    '''An implementation of a Hash Table with the 4 operations listed above'''

    def __init__(self):
        '''Intialize HashTable with an underlying dictionary data member'''
        self.dictionary = {}
        self.num_trxns = 0
        self.trxn_fh = None


    def insert(self, key, value):
        '''Insert a (key, value) pair into dictionary'''

        self.dictionary[key] = value
        res = f'Inserted {key}'
        
        return res

    
    def lookup(self, key):
        '''Returns the value associated with a given key'''

        try:
            value = self.dictionary[key]
            return value
        except KeyError as err:
            return 'ERROR: KeyError'

    
    def remove(self, key):
        '''Removes the key and associated value from the hash table and
        returns value to the caller'''

        try:
            value = self.dictionary.pop(key)
            return value
        except KeyError:
            return 'ERROR: KeyError'

    
    def scan(self, reg_string):
        '''Returns a list of (key, value) pairs where the key matches
        the given regular expression.'''

        matches = []
        try:
            regex = re.compile(reg_string)
        except re.error as err:
            return f'ERROR: {err}'

        matches = [(k, v) for k, v in self.dictionary.items() if regex.search(k)]

        return matches

