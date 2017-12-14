from flask import Flask
from flask import jsonify
from flask import request
import config

import helper


app = Flask(__name__)


@app.route('/user/upload-assign', methods=['POST'])
def assign_upload_directory():

    # retrieve essential information
    data = request.get_json(force=True)
    user_id = request.headers.get('id')
    encrypted_file_name = request.headers.get('filename')
    encrypted_tmp_pvk= request.headers.get('access_key')
    ticket = request.headers.get('ticket')

    # validate the ticket and fail the request if validation failed, this ensure the client is authorized by auth server
    if helper.decrypt(ticket, config.DIRECTORY_SERVER_PRIVATE_KEY) != config.AUTHENTICATION_SERVER_PUBLIC_KEY:
        return None

    # decrypt the encrypted_key with the temporary public key
    # this helps client to ensure we are the right directory server, not man-in-middle
    tmp_pvk = helper.decrypt(encrypted_tmp_pvk, config.DIRECTORY_SERVER_PRIVATE_KEY)
    file_name = helper.decrypt(encrypted_file_name, tmp_pvk)

    """
    We will make every file server have a copy of the file
    """

    if helper.db_get_directories(file_name).count() > 0:
        # if file already exists, send back the old directory and old file will be replaced
        directories = helper.db_get_directories(file_name)
        encrypted_file_code = helper.encrypt(directories[0]['file_code'], tmp_pvk)
        encrypted_destinations = []
        for directory in directories:
            encryted_directory = helper.encrypt(directory['fs_host'] + ':' + directory['fs_port'], tmp_pvk)
            encrypted_destinations.append(encryted_directory)
    else:
        # generate a file code, this is the name of the file in the actual file server
        # encrypt the file code with the tmp pbk
        file_code = "file{}.{}".format( helper.directory_table().count(), file_name.split('.')[-1])
        encrypted_file_code = helper.encrypt(file_code, tmp_pvk)

        # generate the diretory list and add them to record
        encrypted_destinations = []
        for i in config.FILE_SERVER_PORT:

            # add the directory record into db
            helper.db_insert_single_directory(file_name, file_code, i, config.FILE_SERVER_HOST[i], config.FILE_SERVER_PORT[i])

            # append encrypted directories to the returning list
            destination = config.FILE_SERVER_HOST[i] + ":" + config.FILE_SERVER_PORT[i]
            encrypted_destination = helper.encrypt(destination, tmp_pvk)
            encrypted_destinations.append(encrypted_destination)

    # return the response
    return jsonify({'code': encrypted_file_code, 'destinations': encrypted_destinations})


@app.route('/user/download-assign', methods=['POST'])
def assign_download_directory():

    # retrieve essential information
    data = request.get_json(force=True)
    user_id = request.headers.get('id')
    encrypted_file_name = request.headers.get('filename')
    encrypted_tmp_pvk = request.headers.get('access_key')
    ticket = request.headers.get('ticket')

    # validate the ticket and fail the request if validation failed, this ensure the client is authorized by auth server
    if helper.decrypt(ticket, config.DIRECTORY_SERVER_PRIVATE_KEY) != config.AUTHENTICATION_SERVER_PUBLIC_KEY:
        return None

    # decrypt the encrypted_key with the directory server's public key
    # this helps client to ensure we are the right directory server, not man-in-middle
    tmp_pvk = helper.decrypt(encrypted_tmp_pvk, config.DIRECTORY_SERVER_PRIVATE_KEY)
    file_name = helper.decrypt(encrypted_file_name, tmp_pvk)

    """
    We will return all the directory possible, client may pick the one that is available(e.g unlock)
    the directory information will be encrypted by tmp pvk generated by the auth server
    """

    directories = helper.db_get_directories(file_name)
    encrypted_file_code = helper.encrypt(directories[0]['file_code'], tmp_pvk)
    encryped_directories = []
    for directory in directories:
        encryted_directory = helper.encrypt(directory['fs_host'] + ':' +  directory['fs_port'], tmp_pvk)
        encrypted_fs_id = helper.encrypt(directory['fs_id'], tmp_pvk)
        encryped_directories.append(encryted_directory)

    # return the response
    return jsonify({'code': encrypted_file_code, 'directories': encryped_directories})




if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=int(config.DIRECTORY_SERVER_PORT))
