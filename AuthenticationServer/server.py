import constant
import communication_helper
from flask import Flask
from flask import jsonify
from flask import request
import security_helper


app = Flask(__name__)

@app.route('/user/get-ticket', methods=['POST'])
def generate_ticket():

    # retrieve essential information
    data = request.get_json(force=True)
    user_id = data.get('id')
    file_server = data.get('file_server')
    security_check = data.get('security_check')

    # do the security check
    client_pbk = constant.CLIENT_PUBLIC_KEY[user_id]


    (pbk, pvk) = security_helper.generate_ticket()
    encrypted_pbk = security_helper.encrypt(pbk, )


if __name__ == '__main__':
    app.run()

