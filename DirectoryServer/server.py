from flask import Flask
from flask import jsonify
from flask import request
import constant

import helper


app = Flask(__name__)


@app.route('/user/upload-assign', methods=['POST'])
def assign_upload_directory():

    # retrieve essential information
    data = request.get_json(force=True)
    user_id = request.headers.get('id')
    encrypted_file_name = data.get('filename')
    encrypted_client_pbk= data.get('access_key')
    ticket = data.get('ticket')

    # validate the ticket and fail the request if validation failed
    if helper.decrypt(ticket, constant.DIRECTORY_SERVER_PRIVATE_KEY) != constant.AUTHENTICATION_SERVER_PUBLIC_KEY:
        return None

    # decrypt the encrypted_key with auth server's private key
    # this helps client to ensure we are the right auth server, not man-in-middle
    client_pbk = helper.decrypt(encrypted_client_pbk, constant.PRIVATE_KEY)
    fs_pbk = helper.decrypt()
    file_name = helper.decrypt(encrypted_file_name, client_pbk)


    """
    if file name already exists
    the file system will overwrite the old file with the new file
    however, the directory server should inform that to the client with the response
    """
    
    if not helper.db_get_directory(file_name):
        return jsonify({'exists': True})
    else:
        # return ticket
        (tmp_pbk, tmp_pvk) = helper.generate_ticket()
        encrypted_pbk = helper.encrypt(tmp_pbk, client_pbk)
        encrypted_pvk = helper.encrypt(tmp_pvk, fs_pbk)
        return jsonify({'client': encrypted_pbk, 'filer_server': encrypted_pvk})

@app.route('/user/download-assign', methods=['POST'])
def assign_download_directory():

    # retrieve essential information
    data = request.get_json(force=True)
    user_id = data.get('id')
    file_server = data.get('file_server')
    security_check = data.get('security_check')

    """
    Security Check, on the authentication server side, we do need to worry about the fake Client issue. To make authetication server trust our request,
    we upload the encrypted public key of auth server(encrypted with client's private key), the authentication server will decrypt(with out client's public key) and compare the public key
    This ensures the client 
        - has auth server's public key
        - has target client's private key
    """
    client_pbk = constant.CLIENT_PUBLIC_KEY[user_id]
    fs_pbk = constant.FILE_SERVER_PUBLIC_KEY[file_server]
    security_check = helper.decrypt(security_check, client_pbk)

    if not security_check == constant.PUBLIC_KEY:
        return None
    else:
        (tmp_pbk, tmp_pvk) = helper.generate_ticket()
        encrypted_pbk = helper.encrypt(tmp_pbk, client_pbk)
        encrypted_pvk = helper.encrypt(tmp_pvk, fs_pbk)
        return jsonify({'client': encrypted_pbk, 'filer_server': encrypted_pvk})




if __name__ == '__main__':
    app.run(debug=False, use_reloader=False, port=constant.DIRECTORY_SERVER_PORT)
