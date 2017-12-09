import constant
from pymongo import MongoClient


class Helper:
    """
    Security Helper
    """
    @classmethod
    def encrypt(cls, data, key):
        return data

    @classmethod
    def decrypt(cls, data, key):
        return data

    @classmethod
    def generate_ticket(cls):
        return ('pbk', 'pvk')
