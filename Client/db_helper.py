import constant
from pymongo import MongoClient


def directory_table():
    client = MongoClient("localhost", 27017)
    return client['test-database'].get_collection('test-collection-directory')


def db_insert_single_directory(file, file_code):
    post = {
        "file": file,
        "file_code": file_code,
    }
    directory_table().insert_one(post)


def db_get_directory(file):
    return directory_table().find({"file": file})
