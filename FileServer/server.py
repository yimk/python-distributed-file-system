from flask import Flask
from flask import jsonify
from flask import request
import config
import os
import sys

import helper


app = Flask(__name__)

file_server_id = sys.argv[1]
data_cache = {}

@app.route('/user/upload', methods=['POST'])
def upload_file():

    # retrieve essential information
    data = request.get_data()
    user_id = request.headers.get('id')
    encrypted_file_code = request.headers.get('file_code')
    encrypted_tmp_pvk= request.headers.get('access_key')
    ticket = request.headers.get('ticket')

    # validate the ticket
    if helper.decrypt(ticket, config.FILE_SERVER_PRIVATE_KEY[file_server_id]) != config.AUTHENTICATION_SERVER_PUBLIC_KEY:
        return None

    # decrypt the data and write the file
    tmp_pvk = helper.decrypt(encrypted_tmp_pvk, config.FILE_SERVER_PRIVATE_KEY[file_server_id])
    data = helper.decrypt(data, tmp_pvk)
    file_code = helper.decrypt(encrypted_file_code, tmp_pvk)

    # write the file
    if not os.path.exists(os.getcwd() + "/tmp" + "_" + file_server_id + "/"):
        os.makedirs(os.getcwd() + "/tmp" + "_" + file_server_id + "/")
    open(os.getcwd() + "/tmp" + "_" + file_server_id + "/" + file_code, 'wb').write(data)

    # cache the file
    cache_data(file_code, data)

    return jsonify({'result': 'success'})

@app.route('/user/download', methods=['POST'])
def download_file():

    # retrieve essential information
    user_id = request.headers.get('id')
    encrypted_file_code = request.headers.get('file_code')
    encrypted_tmp_pvk = request.headers.get('access_key')
    ticket = request.headers.get('ticket')

    # validate the ticket
    if helper.decrypt(ticket, config.FILE_SERVER_PRIVATE_KEY[file_server_id]) != config.AUTHENTICATION_SERVER_PUBLIC_KEY:
        return None


    # decrypt the essentail information
    tmp_pvk = helper.decrypt(encrypted_tmp_pvk, config.FILE_SERVER_PRIVATE_KEY[file_server_id])
    file_code = helper.decrypt(encrypted_file_code, tmp_pvk)

    if file_code not in data_cache:
        data = data_cache[file_code]
    else:
        # read the file
        data = open(os.getcwd() + "/tmp" + "_" + file_server_id + "/" + file_code, 'rb').read()

        # cache the file
        cache_data(file_code, data)



    # encrypt file data with tmp key and return it
    return helper.encrypt(data, tmp_pvk)

def cache_data(file_code, data):
    data_cache[file_code] = data
    if len(data_cache) > 50:
        # if more then 50 items, pop one(the oldest one added)
        data_cache.pop(0)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=int(config.FILE_SERVER_PORT[file_server_id]))

