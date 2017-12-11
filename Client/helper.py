import constant
from pymongo import MongoClient

# from pymongo import MongoClient
# # from .. import helper
#
#
# class Helper(helper):
#
#     """Helper class"""
#
#     """
#     Security Helper
#     """
#     def encrypt(self, data, key):
#         return data
#
#     def decrypt(self, data, key):
#         return data
#
#     def generate_ticket(self):
#         return ('pbk', 'pvk')


"""
Security Helper
"""
def encrypt(data, key):
    return data


def decrypt(data, key):
    return data


def generate_ticket():
    return 'tmp_pbk', 'tmp_pvk'


def wait_for_while(timer):
    from time import sleep
    sleep(timer)


def registration_table():
    client = MongoClient("localhost", 27017)
    return client['test-database'].get_collection('test-collection-registration')


def registered():
    return registration_table().count() > 0


def db_register(self, pvk, id):

    post = {
        "pvk": pvk,
        "id": id
    }
    self.registration_table().insert_one(post)


def db_get_registration_info():
    return registration_table().find({})[0]