import base64
import json
import requests
import helper

import config


directory_cache = {}


def register(pbk):
    headers = {'pbk': helper.encrypt(pbk, config.AUTHENTICATION_SERVER_PUBLIC_KEY)}
    response = requests.post(config.AUTHENTICATION_SERVER_REGISTER_REQUEST, data=json.dumps(""),
                             headers=headers)

    return json.loads(response.text)['id']


def secure_upload(data, fname):

    """
    Distributes the file to the file servers under replication schema
    :param data: the data of the file
    :param fname: the name of the file
    :return:
    """

    """
    Get the registration information of the client
    """
    info = helper.db_get_registration_info()
    client_private_key = info['pvk']
    uid = info['id']

    """
    Try to get file directories, before we do it, we check if the file directory is cached
    if yes, then we simply use it
    """
    if fname not in directory_cache:

        """
        Communicating with Authentication Server, get ticket for directory server    
        """
        # get ticket
        directory_server = helper.encrypt("directory", client_private_key)
        encrypted_auth_server_pbk = helper.encrypt(config.AUTHENTICATION_SERVER_PUBLIC_KEY, client_private_key)
        headers = {'id': uid, 'server': directory_server, 'security_check': encrypted_auth_server_pbk}
        response = requests.post(config.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps(""),
                                 headers=headers)

        # parse respones data
        json_data = json.loads(response.text)

        # decrypt the pbk and use it to encrypt sensitive information
        encrypted_client_tmp_pbk = json_data['client']
        encrpyted_directory_sever_tmp_pvk = json_data['server']
        ticket = json_data['ticket']
        client_tmp_pbk_for_directory_server = helper.decrypt(encrypted_client_tmp_pbk, client_private_key)

        """
        Communicating with Directory Server:
        request directory server for destination file server(s)
        directory server will return back a number of file servers and Client is required to distribute the files across these servers
        
        security:
        the Client's uid, Client's public key will be encrypted with directory server's public key
        directory server will then decrypt Client's public key and use it to encrypt the target file servers address
        the encrypted address will then be sent back
        this ensures man-in-middle will not be able to pretend to be the directory server and MAKE CLIENT UPLOAD FILES TO SPY SERVER 
        """

        # encrypt file name with client tmp public key
        secure_fname = helper.encrypt(fname, client_tmp_pbk_for_directory_server)

        headers = {'id': uid, 'filename': secure_fname, 'access_key': encrpyted_directory_sever_tmp_pvk, 'ticket': ticket}
        response = requests.post(config.DIRECTORY_SERVER_UPLOAD_DESTINATION_ASSIGNING_REQUEST, data=json.dumps({}),
                                headers=headers)

        # parse respones data
        json_data = json.loads(response.text)

        # parse and decrypt response, the target file server's address is stored in header
        # file will use file code as the file name is distributed file system
        encrypted_upload_destinations = json_data['destinations']
        file_code = helper.decrypt(json_data['code'], client_tmp_pbk_for_directory_server)

        """
        Cache the file directory
        """
        cache_directory(fname, file_code, encrypted_upload_destinations, client_tmp_pbk_for_directory_server)
    else:
        """
        Use the file directory cache
        """
        file_code = directory_cache[fname][0]
        encrypted_upload_destinations = directory_cache[fname][1]
        client_tmp_pbk_for_directory_server = directory_cache[fname][2]

    print(encrypted_upload_destinations)
    """
    Start to upload the file
    """
    while True:
        for encrypted_destination in encrypted_upload_destinations:

            # decrypt the destination
            destination = helper.decrypt(encrypted_destination, client_tmp_pbk_for_directory_server)
            secure_file_server = helper.encrypt(destination, client_private_key)

            """
            Communicating with Authentication Server, get ticket for lock checking: 
            """

            # get ticket from auth server
            encrypted_auth_server_pbk = helper.encrypt(config.AUTHENTICATION_SERVER_PUBLIC_KEY, client_private_key)
            headers = {'id': uid, 'server': 'locking', 'security_check': encrypted_auth_server_pbk}
            response = requests.post(config.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps({}),
                                     headers=headers)

            # parse respones data
            json_data = json.loads(response.text)

            # decypt keys and ticket
            sever_tmp_pvk = json_data['server']
            ticket = json_data['ticket']
            client_tmp_pbk_for_locking_server = helper.encrypt(json_data['client'], client_private_key)

            """
            Communicating with Locking Server, check if the file is locked in the given destination
            """
            # check if the file has been locked
            headers = {'id': uid, 'server': secure_file_server, 'security_check': ticket, 'access_key': sever_tmp_pvk, 'ticket': ticket}
            response = requests.post(config.ISLOCK_REQUEST, data=json.dumps({}),
                                     headers=headers)

            # parse respones data
            json_data = json.loads(response.text)

            # decypt keys and ticket
            locked = helper.decrypt(json_data['locked'], client_tmp_pbk_for_locking_server)
            locker = helper.decrypt(json_data['locker'], client_tmp_pbk_for_locking_server)

            if locked == 'True' and not locker == uid:
                break

            """
            Send the file
            """

            """
            Communicating with Authentication Server, get ticket for file uploading:
            """
            # get ticket from auth server
            encrypted_auth_server_pbk = helper.encrypt(config.AUTHENTICATION_SERVER_PUBLIC_KEY, client_private_key)
            headers = {'id': uid, 'server': secure_file_server, 'security_check': encrypted_auth_server_pbk}
            response = requests.post(config.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps({}),
                                headers=headers)

            # parse respones data
            json_data = json.loads(response.text)

            # decypt keys and ticket
            fs_tmp_pvk = json_data['server']
            ticket = json_data['ticket']
            client_tmp_pbk = helper.encrypt(json_data['client'], client_private_key)

            """
            Upload the file
            """
            # encrypt data with client tmp public key
            secure_data = helper.encrypt(data, client_tmp_pbk)
            secure_file_code = helper.encrypt(file_code, client_tmp_pbk)

            # send the file
            headers = {'id': uid, 'file_code': secure_file_code, 'access_key': fs_tmp_pvk, 'ticket': ticket}
            response = requests.post(config.UPLOAD_FILE_REQUEST.format(destination), data=secure_data,
                                     headers=headers)

            if encrypted_destination == encrypted_upload_destinations[-1]:
                return True

        """
        if all the destination are locked, then the file must be locked, wait for 5 minute and try again
        """
        print("File is locked. Upload will restart after 5 minutes. It you do not want to wait, you can terminate the application by pressing ctrl+c.")
        helper.wait_for_while(300)
        print("Upload restart.")

def secure_download(fname):

    """

    :param fname:
    :return:
    """

    """
    Get the registration information of the client
    """
    info = helper.db_get_registration_info()
    client_private_key = info['pvk']
    uid = info['id']

    """
    Try to get file directories, before we do it, we check if the file directory is cached
    if yes, then we simply use it
    """
    if fname not in directory_cache:

        """
        Communicating with Authentication Server, get ticket for directory server    
        """

        # get ticket
        directory_server = helper.encrypt("directory", client_private_key)
        encrypted_auth_server_pbk = helper.encrypt(config.AUTHENTICATION_SERVER_PUBLIC_KEY, client_private_key)
        headers = {'id': uid, 'server': directory_server, 'security_check': encrypted_auth_server_pbk}
        response = requests.post(config.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps({}),
                                 headers=headers)

        # parse respones data
        json_data = json.loads(response.text)

        # decrypt the pbk and use it to encrypt sensitive information
        encrypted_client_tmp_pbk = json_data['client']
        encrpyted_directory_sever_tmp_pvk = json_data['server']
        ticket = json_data['ticket']
        client_tmp_pbk_for_directory_server = helper.decrypt(encrypted_client_tmp_pbk, client_private_key)

        """
        Communicating with Directory Server:
        request directory server for destination file server(s)
        directory server will return back a number of file servers and Client is required to distribute the files across these servers
    
        security:
        the Client's uid, Client's public key will be encrypted with directory server's public key
        directory server will then decrypt Client's public key and use it to encrypt the target file servers address
        the encrypted address will then be sent back
        this ensures man-in-middle will not be able to pretend to be the directory server and MAKE CLIENT UPLOAD FILES TO SPY SERVER 
        """

        # encrypt file name with client tmp public key
        secure_fname = helper.encrypt(fname, client_tmp_pbk_for_directory_server)

        headers = {'id': uid, 'filename': secure_fname, 'access_key': encrpyted_directory_sever_tmp_pvk, 'ticket': ticket}
        response = requests.post(config.DIRECTORY_SERVER_DOWNLOAD_DESTINATION_ASSIGNING_REQUEST, data=json.dumps({}),
                                 headers=headers)

        # parse respones data
        json_data = json.loads(response.text)

        # parse and decrypt response, the target file server's address is stored in header
        # file will use file code as the file name is distributed file system
        encrypted_download_directories = json_data['directories']
        file_code = helper.decrypt(json_data['code'], client_tmp_pbk_for_directory_server)

        """
        Cache the file directory
        """
        cache_directory(fname, file_code, encrypted_download_directories, client_tmp_pbk_for_directory_server)

    else:
        """
        Use the file directory cache
        """
        file_code = directory_cache[fname][0]
        encrypted_download_directories = directory_cache[fname][1]
        client_tmp_pbk_for_directory_server = directory_cache[fname][2]

    """
    Start download the file
    """
    while True:
        for directory in encrypted_download_directories:

            # decrypt the destination
            directory = helper.decrypt(directory, client_tmp_pbk_for_directory_server)

            """
            Communicating with Authentication Server, get ticket for lock checking: 
            """

            # get ticket from auth server

            encrypted_auth_server_pbk = helper.encrypt(config.AUTHENTICATION_SERVER_PUBLIC_KEY, client_private_key)
            headers = {'id': uid, 'server': 'locking', 'security_check': encrypted_auth_server_pbk}
            response = requests.post(config.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps({}),
                                     headers=headers)

            # parse respones data
            json_data = json.loads(response.text)

            # decypt keys and ticket
            sever_tmp_pvk = json_data['server']
            ticket = json_data['ticket']
            client_tmp_pbk_for_locking_server = helper.encrypt(json_data['client'], client_private_key)

            """
            Communicating with Locking Server, check if the file is locked in the given destination
            """
            # check if the file has been locked
            secure_file_server = helper.encrypt(directory, client_private_key)
            headers = {'id': uid, 'server': secure_file_server, 'security_check': ticket, 'access_key': sever_tmp_pvk}
            response = requests.post(config.ISLOCK_REQUEST, data=json.dumps({}),
                                     headers=headers)

            # parse respones data
            json_data = json.loads(response.text)

            # decypt keys and ticket
            locked = helper.decrypt(json_data['locked'], client_tmp_pbk_for_locking_server)
            locker = helper.decrypt(json_data['locker'], client_tmp_pbk_for_locking_server)

            if not locked == 'True' or locker == uid:
                """
                Download the file
                """

                """
                Communicating with Authentication Server, get ticket for file uploading:
                """
                # get ticket from auth server
                secure_file_server = helper.encrypt(directory, client_private_key)
                encrypted_auth_server_pbk = helper.encrypt(config.AUTHENTICATION_SERVER_PUBLIC_KEY, client_private_key)
                headers = {'id': uid, 'server': secure_file_server, 'security_check': encrypted_auth_server_pbk}
                response = requests.post(config.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps({}),
                                         headers=headers)

                # parse respones data
                json_data = json.loads(response.text)

                # decypt keys and ticket
                fs_tmp_pvk = json_data['server']
                ticket = json_data['ticket']
                client_tmp_pbk_for_file_server = helper.encrypt(json_data['client'], client_private_key)

                # encrypt data with client tmp public key
                secure_file_code = helper.encrypt(file_code, client_tmp_pbk_for_file_server)

                """
                Download the file
                """
                # download the file
                headers = {'id': uid, 'file_code': secure_file_code, 'access_key': fs_tmp_pvk, 'ticket': ticket}
                response = requests.post(config.DOWNLOAD_FILE_REQUEST.format(directory), data=json.dumps({}),
                                         headers=headers)

                # return the file
                encrypted_data = response.content
                data = helper.decrypt(encrypted_data, client_tmp_pbk_for_file_server)
                return data

        """
        if all the destination are locked, then the file must be locked, wait for 5 minute and try again
        """
        print("File is locked. Download will restart after 5 minutes. It you do not want to wait, you can terminate the application by pressing ctrl+c.")
        helper.wait_for_while(300)
        print("Upload restart.")


def lock_or_unlock(fname, lock):
    """

    :param fname:
    :param uid:
    :param lock:
    :return:
    """

    """
    Get the registration information of the client
    """
    info = helper.db_get_registration_info()
    client_private_key = info['pvk']
    uid = info['id']
    """
    Communicating with Authentication Server, get ticket for directory server
    """

    # authenticate client to get access to the directory server
    directory_server = helper.encrypt("directory", client_private_key)
    encrypted_auth_server_pbk = helper.encrypt(config.AUTHENTICATION_SERVER_PUBLIC_KEY, client_private_key)
    headers = {'id': uid, 'server': directory_server, 'security_check': encrypted_auth_server_pbk}
    response = requests.post(config.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps(""),
                             headers=headers)

    # parse respones data
    json_data = json.loads(response.text)

    # decrypt the pbk and use it to encrypt sensitive information
    encrypted_client_tmp_pbk = json_data['client']
    encrpyted_directory_sever_tmp_pvk = json_data['server']
    ticket = json_data['ticket']
    client_tmp_pbk_for_directory_server = helper.decrypt(encrypted_client_tmp_pbk, client_private_key)

    """
    Communicating with Directory Server:
    request directory server for all the file server(s) holding the file
    directory server will return back a number of file servers and Client is required to distribute the files across these servers

    security:
    the Client's uid, Client's public key will be encrypted with directory server's public key
    directory server will then decrypt Client's public key and use it to encrypt the target file servers address
    the encrypted address will then be sent back
    this ensures man-in-middle will not be able to pretend to be the directory server and MAKE CLIENT UPLOAD FILES TO SPY SERVER 
    """

    # encrypt file name with client tmp public key
    secure_fname = helper.encrypt(fname, client_tmp_pbk_for_directory_server)

    headers = {'id': uid, 'filename': secure_fname, 'access_key': encrpyted_directory_sever_tmp_pvk, 'ticket': ticket}
    response = requests.post(config.DIRECTORY_SERVER_DOWNLOAD_DESTINATION_ASSIGNING_REQUEST, data=json.dumps({}),
                             headers=headers)

    # parse respones data
    json_data = json.loads(response.text)

    # parse and decrypt response, the target file server's address is stored in header
    # file will use file code as the file name is distributed file system
    encrypted_download_directories = json_data['directories']
    file_code = helper.decrypt(json_data['code'], client_tmp_pbk_for_directory_server)

    """
    Communicating with Authentication Server, get ticket and lock the file:
    """


    while True:
        for encrypted_directory in encrypted_download_directories:

            # decrypt the destination
            directory = helper.decrypt(encrypted_directory, client_tmp_pbk_for_directory_server)

            # get ticket from auth server
            secure_file_server = helper.encrypt(directory, client_private_key)
            encrypted_auth_server_pbk = helper.encrypt(config.AUTHENTICATION_SERVER_PUBLIC_KEY, client_private_key)
            headers = {'id': uid, 'server': secure_file_server, 'security_check': encrypted_auth_server_pbk}
            response = requests.post(config.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps({}),
                                     headers=headers)

            # parse respones data
            json_data = json.loads(response.text)

            # decypt keys and ticket
            fs_tmp_pvk = json_data['server']
            ticket = json_data['ticket']
            client_tmp_pbk_for_file_server = helper.encrypt(json_data['client'], client_private_key)

            # encrypt data with client tmp public key
            secure_file_code = helper.encrypt(file_code, client_tmp_pbk_for_file_server)
            secure_directory = helper.encrypt(directory, client_tmp_pbk_for_file_server)

            # send the file
            headers = {'id': uid, 'file_code': secure_file_code, 'server': secure_directory, 'access_key': fs_tmp_pvk, 'ticket': ticket}

            if lock:
                response = requests.post(config.LOCK_REQUEST.format(directory), data=json.dumps({}),
                                         headers=headers)

                if json.loads(response.text)['result'] == 'failed':
                    print("Locking Failed. Locking will restart after 5 minutes. It you do not want to wait, you can terminate the application by pressing ctrl+c.")
                    helper.wait_for_while(300)
                    print("Locking restart.")
                    break

            else:
                response = requests.post(config.UNLOCK_REQUEST.format(directory), data=json.dumps({}),
                                         headers=headers)

                print(json.loads(response.text))
                if json.loads(response.text)['result'] == 'failed':
                    print("Unocking Failed. Locking will restart after 5 minutes. It you do not want to wait, you can terminate the application by pressing ctrl+c.")
                    helper.wait_for_while(300)
                    print("Unocking restart.")
                    break

            if encrypted_directory == encrypted_download_directories[-1]:
                print("Locking Successful. File is locked")
                return True



"""
private
"""


def cache_directory(file_name, file_code, directories, client_tmp_pbk_for_directory_server):
    directory_cache[file_name] = (file_code, directories, client_tmp_pbk_for_directory_server)
    if len(directory_cache) > 50:
        # if more then 50 items, pop one(the oldest one added)
        directory_cache.pop(0)


def file_exists(fname):
    pass





