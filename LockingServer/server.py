from flask import Flask
from flask import jsonify
from flask import request
import config

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
    if helper.decrypt(ticket, config.LOCK_SERVER_PRIVATE_KEY) != config.AUTHENTICATION_SERVER_PUBLIC_KEY:
        return None

    # decrypt the encrypted_key with the temporary public key
    # this helps client to ensure we are the right directory server, not man-in-middle
    tmp_pvk = helper.decrypt(encrypted_tmp_pvk, config.LOCK_SERVER_PRIVATE_KEY)
    file_code = helper.decrypt(encrypted_file_code, tmp_pvk)
    server = helper.decrypt(encrypted_server_addr, tmp_pvk)

    # lock the file
    print(list(helper.db_get_lock(file_code, server)))
    if helper.db_get_lock(file_code, server).count() > 0:
        # already locked
        print(server)
        return jsonify({'result': 'failed'})
    else:
        print(server)
        helper.db_lock(file_code, server, user_id)
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
    if helper.decrypt(ticket, config.LOCK_SERVER_PRIVATE_KEY) != config.AUTHENTICATION_SERVER_PUBLIC_KEY:
        return None

    # decrypt the encrypted_key with the temporary public key
    # this helps client to ensure we are the right directory server, not man-in-middle
    tmp_pvk = helper.decrypt(encrypted_tmp_pvk, config.LOCK_SERVER_PRIVATE_KEY)
    file_code = helper.decrypt(encrypted_file_code, tmp_pvk)
    server = helper.decrypt(encrypted_server_addr, tmp_pvk)

    # lock the file
    result = 'failed'
    if helper.db_unlock(file_code, server, user_id):
        result = 'success'

    return jsonify({'result': result})


@app.route('/user/is-locked', methods=['POST'])
def is_locked():

    # retrieve essential information
    data = request.get_json(force=True)
    user_id = request.headers.get('id')
    encrypted_file_code = request.headers.get('file_code')
    encrypted_server_addr = request.headers.get('server')
    encrypted_tmp_pvk = request.headers.get('access_key')
    ticket = request.headers.get('security_check')

    # validate the ticket and fail the request if validation failed, this ensure the client is authorized by auth server
    if helper.decrypt(ticket, config.LOCK_SERVER_PRIVATE_KEY) != config.AUTHENTICATION_SERVER_PUBLIC_KEY:
        return None

    # decrypt the encrypted_key with the temporary public key
    # this helps client to ensure we are the right directory server, not man-in-middle
    tmp_pvk = helper.decrypt(encrypted_tmp_pvk, config.LOCK_SERVER_PRIVATE_KEY)
    file_code = helper.decrypt(encrypted_file_code, tmp_pvk)
    server = helper.decrypt(encrypted_server_addr, tmp_pvk)
    print(list(helper.db_get_lock(file_code, server)))
    # return the result
    lock = helper.db_get_lock(file_code, server)
    locked = 'False'
    locker = ''
    if helper.db_get_lock(file_code, server).count() > 0:
        locked = ' True'
        locker = lock[0]['uid']
    return jsonify({'locked': helper.encrypt(locked, tmp_pvk), 'locker': helper.encrypt(locker, tmp_pvk)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=int(config.LOCK_SERVER_PORT))
