from flask import Flask
from flask import jsonify
from flask import request
import constant

import helper


app = Flask(__name__)


@app.route('/user/lock', methods=['POST'])
def lock():

    # retrieve essential information
    data = request.get_json(force=True)
    user_id = request.headers.get('id')
    encrypted_file_code = request.headers.get('file_code')
    encrypted_server_addr = request.headers.get('server')
    encrypted_tmp_pvk = request.headers.get('access_key')
    ticket = request.headers.get('ticket')

    # validate the ticket and fail the request if validation failed, this ensure the client is authorized by auth server
    if helper.decrypt(ticket, constant.DIRECTORY_SERVER_PRIVATE_KEY) != constant.AUTHENTICATION_SERVER_PUBLIC_KEY:
        return None

    # decrypt the encrypted_key with the temporary public key
    # this helps client to ensure we are the right directory server, not man-in-middle
    tmp_pvk = helper.decrypt(encrypted_tmp_pvk, constant.DIRECTORY_SERVER_PRIVATE_KEY)
    file_code = helper.decrypt(encrypted_file_code, tmp_pvk)
    server = helper.decrypt(encrypted_server_addr, tmp_pvk)

    # lock the file
    helper.db_lock(file_code, server)

    return jsonify({'result': 'success'})


@app.route('/user/unlock', methods=['POST'])
def unlock():

    # retrieve essential information
    data = request.get_json(force=True)
    user_id = request.headers.get('id')
    encrypted_file_code = request.headers.get('file_code')
    encrypted_server_addr = request.headers.get('server')
    encrypted_tmp_pvk = request.headers.get('access_key')
    ticket = request.headers.get('ticket')

    # validate the ticket and fail the request if validation failed, this ensure the client is authorized by auth server
    if helper.decrypt(ticket, constant.DIRECTORY_SERVER_PRIVATE_KEY) != constant.AUTHENTICATION_SERVER_PUBLIC_KEY:
        return None

    # decrypt the encrypted_key with the temporary public key
    # this helps client to ensure we are the right directory server, not man-in-middle
    tmp_pvk = helper.decrypt(encrypted_tmp_pvk, constant.DIRECTORY_SERVER_PRIVATE_KEY)
    file_code = helper.decrypt(encrypted_file_code, tmp_pvk)
    server = helper.decrypt(encrypted_server_addr, tmp_pvk)

    # lock the file
    helper.db_unlock(file_code, server)

    return jsonify({'result': 'success'})


@app.route('/user/islocked', methods=['POST'])
def islocked():

    # retrieve essential information
    data = request.get_json(force=True)
    user_id = request.headers.get('id')
    encrypted_file_code = request.headers.get('file_code')
    encrypted_server_addr = request.headers.get('server')
    encrypted_tmp_pvk = request.headers.get('access_key')
    ticket = request.headers.get('ticket')

    # validate the ticket and fail the request if validation failed, this ensure the client is authorized by auth server
    if helper.decrypt(ticket, constant.DIRECTORY_SERVER_PRIVATE_KEY) != constant.AUTHENTICATION_SERVER_PUBLIC_KEY:
        return None

    # decrypt the encrypted_key with the temporary public key
    # this helps client to ensure we are the right directory server, not man-in-middle
    tmp_pvk = helper.decrypt(encrypted_tmp_pvk, constant.DIRECTORY_SERVER_PRIVATE_KEY)
    file_code = helper.decrypt(encrypted_file_code, tmp_pvk)
    server = helper.decrypt(encrypted_server_addr, tmp_pvk)

    # return the result
    locked = 'False'
    if helper.db_is_locked(file_code, server) > 0:
        locked = ' True'
    return jsonify({'locked': helper.encrypt(locked, tmp_pvk)})

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False, port=constant.DIRECTORY_SERVER_PORT)
