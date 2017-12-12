import config
from pymongo import MongoClient


# from .. import helper
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
    return 'tmp_pbk', 'tmp_pvk'

"""
Directory server db helper
"""
def directory_table():
    client = MongoClient("localhost", 27017)
    return client['test-database'].get_collection('test-collection-directory')


def db_insert_single_directory(file, file_code, fs_id, fs_host, fs_port):
    post = {
        "file": file,
        "file_code": file_code,
        "fs_id": fs_id,
        "fs_host": fs_host,
        "fs_port": fs_port
    }
    directory_table().insert_one(post)


def db_get_directories(file):
    return directory_table().find({"file": file})


"""
Lock Server db helper
"""
def lock_table():
    client = MongoClient("localhost", 27017)
    return client['test-database'].get_collection('test-collection-locking')


def db_lock(file_code, addr, uid):
    post = {
        "file_code": file_code,
        "server": addr,
        "uid": uid
    }
    lock_table().insert_one(post)


def db_unlock(file_code, addr, uid):
    lock_table().delete_one({"file_code": file_code, "server": addr, 'uid': uid})


def db_get_lock(file_code, addr):
    return lock_table().find({"file_code": file_code, "server": addr})

