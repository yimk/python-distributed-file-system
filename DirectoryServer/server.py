import constant
from flask import Flask
from flask import jsonify
from flask import request
import security_helper


app = Flask(__name__)

@app.route('/user/upload-assign', methods=['POST'])
def assign_upload_directory():

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
    security_check = security_helper.decrypt(security_check, client_pbk)

    if not security_check == constant.PUBLIC_KEY:
        return None
    else:

        # return ticket
        (tmp_pbk, tmp_pvk) = security_helper.generate_ticket()
        encrypted_pbk = security_helper.encrypt(tmp_pbk, client_pbk)
        encrypted_pvk = security_helper.encrypt(tmp_pvk, fs_pbk)
        return jsonify({'client': encrypted_pbk, 'filer_server': encrypted_pvk})

@app.route('/user/download-assign', methods=['POST'])
def generate_ticket():

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
    security_check = security_helper.decrypt(security_check, client_pbk)

    if not security_check == constant.PUBLIC_KEY:
        return None
    else:
        (tmp_pbk, tmp_pvk) = security_helper.generate_ticket()
        encrypted_pbk = security_helper.encrypt(tmp_pbk, client_pbk)
        encrypted_pvk = security_helper.encrypt(tmp_pvk, fs_pbk)
        return jsonify({'client': encrypted_pbk, 'filer_server': encrypted_pvk})




if __name__ == '__main__':
    app.run()

