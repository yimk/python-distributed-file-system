import constant
from pymongo import MongoClient


# from .. import helper
# class Helper(helper):
#
#     """Helper class"""
#     pass
#
#     """
#     Directory server db helper
#     """
#     @staticmethod
#     def directory_table(self):
#         client = MongoClient("localhost", 27017)
#         return client['test-database'].get_collection('test-collection-directory')
#
#     def db_insert_single_directory(self, file, file_code):
#         post = {
#             "file": file,
#             "file_code": file_code,
#         }
#         self.directory_table().insert_one(post)
#
#     def db_get_directory(self, file):
#         return self.directory_table().find({"file": file})
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


def user_table():
    client = MongoClient("localhost", 27017)
    return client['test-database'].get_collection('test-collection-user')


def db_register(self, pbk):

    id = user_table().count()
    post = {
        "pbk": pbk,
        "id": id
    }
    self.user_table().insert_one(post)
    return id


def db_find_pbk(self, id):
    return self.user_table().find({"id": id})['pbk']


