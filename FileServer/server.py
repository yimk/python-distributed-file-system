from flask import Flask
from flask import jsonify
from flask import request
import constant
import os
import sys

import helper


app = Flask(__name__)


@app.route('/user/upload', methods=['POST'])
def upload_file():

    # retrieve essential information
    data = request.get_json(force=True)['data']
    user_id = request.headers.get('id')
    encrypted_file_code = request.headers.get('file_code')
    encrypted_tmp_pvk= request.headers.get('access_key')
    ticket = request.headers.get('ticket')

    # validate the ticket
    if helper.decrypt(ticket, constant.FILE_SERVER_PRIVATE_KEY[0]) != constant.AUTHENTICATION_SERVER_PUBLIC_KEY:
        return None

    # decrypt the data and write the file
    tmp_pvk = helper.decrypt(encrypted_tmp_pvk, constant.FILE_SERVER_PRIVATE_KEY[0])
    data = helper.decrypt(data, tmp_pvk)
    file_code = helper.decrypt(encrypted_file_code, tmp_pvk)
    open(os.getcwd() + "/tmp/" + file_code, 'w').write(data)

    return True

@app.route('/user/download', methods=['POST'])
def download_file():

    # retrieve essential information
    user_id = request.headers.get('id')
    encrypted_file_code = request.headers.get('file_code')
    encrypted_tmp_pvk = request.headers.get('access_key')
    ticket = request.headers.get('ticket')

    # validate the ticket
    if helper.decrypt(ticket, constant.FILE_SERVER_PRIVATE_KEY[0]) != constant.AUTHENTICATION_SERVER_PUBLIC_KEY:
        return None

    # read the data the data and write the file
    tmp_pvk = helper.decrypt(encrypted_tmp_pvk, constant.FILE_SERVER_PRIVATE_KEY[0])
    file_code = helper.decrypt(encrypted_file_code, tmp_pvk)
    data = open(os.getcwd() + "/tmp/" + file_code, 'rb').read()

    # encrypt file data with tmp key and return it
    return jsonify({'data': helper.encrypt(data, tmp_pvk)})




if __name__ == '__main__':
    app.run(host=constant.FILE_SERVER_PORT[sys.argv[1]])

