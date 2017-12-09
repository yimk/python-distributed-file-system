from .. import constant
from pymongo import MongoClient
from .. import helper


# class Helper(helper):
#
#     """Helper class"""
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


def generate_ticket():
    return ('pbk', 'pvk')

"""
Directory server db helper
"""
def directory_table(self):
    client = MongoClient("localhost", 27017)
    return client['test-database'].get_collection('test-collection-directory')


def db_insert_single_directory(self, file, file_code):
    post = {
        "file": file,
        "file_code": file_code,
    }
    self.directory_table().insert_one(post)


def db_get_directory(self, file):
    return self.directory_table().find({"file": file})
