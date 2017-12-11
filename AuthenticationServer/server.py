import constant
from flask import Flask
from flask import jsonify
from flask import request
import helper

app = Flask(__name__)

@app.route('/user/get-ticket', methods=['POST'])
def generate_ticket():

    # retrieve essential information
    user_id = request.headers.get('id')
    encrypted_server = request.headers.get('server')
    security_check = request.headers.get('security_check')
    client_pbk = constant.CLIENT_PUBLIC_KEY[user_id]

    # find out the server public key based on the request
    server = helper.decrypt(encrypted_server, client_pbk)
    if server == "directory":
        fs_pbk = constant.DIRECTORY_SERVER_PUBLIC_KEY
    elif server == "locking":
        fs_pbk = constant.DIRECTORY_SERVER_PUBLIC_KEY
    elif server == "transaction":
        fs_pbk = constant.DIRECTORY_SERVER_PUBLIC_KEY
    else:
        # find file server id based on addr
        server = helper.decrypt(encrypted_server, client_pbk)
        for key in constant.FILE_SERVER_PORT:
            if server == constant.FILE_SERVER_HOST[key] + ':' + constant.FILE_SERVER_PORT[key]:
                fs_pbk = constant.FILE_SERVER_PUBLIC_KEY[key]
                break


    """
    Security Check, on the authentication server side, we do need to worry about the fake Client issue. To make authetication server trust our request,
    we upload the encrypted public key of auth server(encrypted with client's private key), the authentication server will decrypt(with out client's public key) and compare the public key
    This ensures the client 
        - has auth server's public key
        - has target client's private key
    """
    security_check = helper.decrypt(security_check, client_pbk)

    if not security_check == constant.AUTHENTICATION_SERVER_PUBLIC_KEY:
        # client didn't encrypt auth server's public key with it's private key
        # Hence, the client could be man-in-middle
        # Hence reject the request
        return None
    else:

        """
        Generate the public key and private key pair
        Public key:
            - will be hold by the client. 
            - Hence, encrypt it with client's public key
            - Client needs to decrupt it with it's private key
        
        Private key:
            - will be hold by the target server
            - Hence, encrypt it with server's public key
            
        The key pair will be used to encrypt/decrypt the sensitive data during the data transferring between client and target server
        
        **The auth server will encrypt it's public key with the target server's public key, this is used as the security check for the directory server.
        **This makes the directory server trust the client and we call this security check TICKET
        """
        (tmp_pbk, tmp_pvk) = helper.generate_ticket()
        encrypted_pbk = helper.encrypt(tmp_pbk, client_pbk)
        encrypted_pvk = helper.encrypt(tmp_pvk, fs_pbk)
        security_check = helper.encrypt(constant.AUTHENTICATION_SERVER_PUBLIC_KEY, fs_pbk)
        return jsonify({'client': encrypted_pbk, 'server': encrypted_pvk, 'ticket': security_check})





if __name__ == '__main__':
    app.run(debug=False, use_reloader=False, port=constant.AUTHENTICATION_SERVER_PORT)

