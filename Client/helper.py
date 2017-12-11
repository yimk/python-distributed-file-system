import constant

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