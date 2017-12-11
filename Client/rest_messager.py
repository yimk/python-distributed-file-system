import base64
import json
import requests
import helper

import constant


directory_cache = {}

def secure_upload(data, fname, uid):

    """
    Communicating with Authentication Server, get ticket for directory server    
    """
    if fname not in directory_cache:
        # get ticket
        directory_server = helper.encrypt("directory", constant.PRIVATE_KEY)
        encrypted_auth_server_pbk = helper.encrypt(constant.AUTHENTICATION_SERVER_PUBLIC_KEY, constant.PRIVATE_KEY)
        headers = {'id': uid, 'server': directory_server, 'security_check': encrypted_auth_server_pbk}
        response = requests.post(constant.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps(""),
                                 headers=headers)

        # parse respones data
        json_data = json.loads(response.text)

        # decrypt the pbk and use it to encrypt sensitive information
        encrypted_client_tmp_pbk = json_data['client']
        encrpyted_directory_sever_tmp_pvk = json_data['server']
        ticket = json_data['ticket']
        client_tmp_pbk_for_directory_server = helper.decrypt(encrypted_client_tmp_pbk, constant.PRIVATE_KEY)

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
        response = requests.post(constant.DIRECTORY_SERVER_UPLOAD_DESTINATION_ASSIGNING_REQUEST, data=json.dumps({}),
                                headers=headers)

        # parse respones data
        json_data = json.loads(response.text)

        # parse and decrypt response, the target file server's address is stored in header
        # file will use file code as the file name is distributed file system
        encrypted_upload_destinations = json_data['destinations']
        file_code = helper.decrypt(json_data['code'], client_tmp_pbk_for_directory_server)

        cache_directory(fname, file_code, encrypted_upload_destinations, client_tmp_pbk_for_directory_server)
    else:
        file_code = directory_cache[fname][0]
        encrypted_upload_destinations = directory_cache[fname][1]
        client_tmp_pbk_for_directory_server = directory_cache[fname][2]



    """
    Communicating with Authentication Server, get ticket and upload file:
    request authentication server for access key
    authentication server will authenticate the Client, and provide ticket to the Client.
    the ticket is essentially a tmp (public key, private key), and the file name encrypted by the target file server's public key 

    security:
    On Client side, we do not need to worry about man-in-middle attack when we communicate with authentication server as all we need is a ticke 
    if the ticket is fake than, the only risk is that the file uploading will fail.
    However, on the authentication server side, we do need to worry about the fake Client issue. To make authetication server trust our request,
    we upload the encrypted public key of auth server(encrypted with client's private key), the authentication server will decrypt(with out client's public key) and compare the public key
    This ensures the client 
        - has auth server's public key
        - has target client's private key
    
    The ticket compose of 
        - a tmp public key for client(needs to be decrypted by client's privet key)
        - a tmp private key for file server(needs to be decrypted by file server's private key)
    
    Once we got the ticket, we can then upload the file
    """

    """
    Communication with the File Server, Replication
    security:
    To ensure the data is not getting stolen by the man-in-middle, we encrypt file data with the tmp public key provided by the auth server
    The file server will decrypt it with the tmp private key, which needs to be decrypted first with it's own private key
    """

    for encrypted_destination in encrypted_upload_destinations:

        # decrypt the destination
        destination = helper.decrypt(encrypted_destination, client_tmp_pbk_for_directory_server)

        # get ticket from auth server
        secure_file_server = helper.encrypt(destination, constant.PRIVATE_KEY)
        encrypted_auth_server_pbk = helper.encrypt(constant.AUTHENTICATION_SERVER_PUBLIC_KEY, constant.PRIVATE_KEY)
        headers = {'id': uid, 'server': 'locking', 'security_check': encrypted_auth_server_pbk}
        response = requests.post(constant.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps({}),
                                 headers=headers)

        # parse respones data
        json_data = json.loads(response.text)

        # decypt keys and ticket
        sever_tmp_pvk = json_data['server']
        ticket = json_data['ticket']
        client_tmp_pbk_for_locking_server = helper.encrypt(json_data['client'], constant.PRIVATE_KEY)

        # check if the file has been locked
        headers = {'id': uid, 'server': destination, 'security_check': ticket, 'access_key': sever_tmp_pvk}
        response = requests.post(constant.ISLOCK_REQUEST, data=json.dumps({}),
                                 headers=headers)

        # parse respones data
        json_data = json.loads(response.text)

        # decypt keys and ticket
        locked = helper.decrypt(json_data['locked'], client_tmp_pbk_for_locking_server)

        if locked:

            # get ticket from auth server
            secure_file_server = helper.encrypt(destination, constant.PRIVATE_KEY)
            encrypted_auth_server_pbk = helper.encrypt(constant.AUTHENTICATION_SERVER_PUBLIC_KEY, constant.PRIVATE_KEY)
            headers = {'id': uid, 'server': secure_file_server, 'security_check': encrypted_auth_server_pbk}
            response = requests.post(constant.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps({}),
                                headers=headers)

            # parse respones data
            json_data = json.loads(response.text)

            # decypt keys and ticket
            fs_tmp_pvk = json_data['server']
            ticket = json_data['ticket']
            client_tmp_pbk = helper.encrypt(json_data['client'], constant.PRIVATE_KEY)

            # encrypt data with client tmp public key
            secure_data = helper.encrypt(data, client_tmp_pbk)
            secure_file_code = helper.encrypt(file_code, client_tmp_pbk)

            # send the file
            headers = {'id': uid, 'file_code': secure_file_code, 'access_key': fs_tmp_pvk, 'ticket': ticket}
            response = requests.post(constant.UPLOAD_FILE_REQUEST.format(destination), data=secure_data,
                                     headers=headers)

            return True

    # if failed, then the file must be locked, wait for 5 minute and try again
    helper.wait_for_while(300)
    secure_upload(data, fname, uid)


def secure_download(fname, uid):

    """
    Communicating with Authentication Server, get ticket for directory server
    """
    if fname not in directory_cache:
        # get ticket
        directory_server = helper.encrypt("directory", constant.PRIVATE_KEY)
        encrypted_auth_server_pbk = helper.encrypt(constant.AUTHENTICATION_SERVER_PUBLIC_KEY, constant.PRIVATE_KEY)
        headers = {'id': uid, 'server': directory_server, 'security_check': encrypted_auth_server_pbk}
        response = requests.post(constant.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps(""),
                                 headers=headers)

        # parse respones data
        json_data = json.loads(response.text)

        # decrypt the pbk and use it to encrypt sensitive information
        encrypted_client_tmp_pbk = json_data['client']
        encrpyted_directory_sever_tmp_pvk = json_data['server']
        ticket = json_data['ticket']
        client_tmp_pbk_for_directory_server = helper.decrypt(encrypted_client_tmp_pbk, constant.PRIVATE_KEY)

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
        response = requests.post(constant.DIRECTORY_SERVER_DOWNLOAD_DESTINATION_ASSIGNING_REQUEST, data=json.dumps({}),
                                 headers=headers)

        # parse respones data
        json_data = json.loads(response.text)

        # parse and decrypt response, the target file server's address is stored in header
        # file will use file code as the file name is distributed file system
        encrypted_download_directories = json_data['directories']
        file_code = helper.decrypt(json_data['code'], client_tmp_pbk_for_directory_server)

        cache_directory(fname, file_code, encrypted_download_directories, client_tmp_pbk_for_directory_server)

    else:
        file_code = directory_cache[fname][0]
        encrypted_download_directories = directory_cache[fname][1]
        client_tmp_pbk_for_directory_server = directory_cache[fname][2]

    """
    Communicating with Authentication Server, get ticket and upload file:
    request authentication server for access key
    authentication server will authenticate the Client, and provide ticket to the Client.
    the ticket is essentially a tmp (public key, private key), and the file name encrypted by the target file server's public key 

    security:
    On Client side, we do not need to worry about man-in-middle attack when we communicate with authentication server as all we need is a ticke 
    if the ticket is fake than, the only risk is that the file uploading will fail.
    However, on the authentication server side, we do need to worry about the fake Client issue. To make authetication server trust our request,
    we upload the encrypted public key of auth server(encrypted with client's private key), the authentication server will decrypt(with out client's public key) and compare the public key
    This ensures the client 
        - has auth server's public key
        - has target client's private key

    The ticket compose of 
        - a tmp public key for client(needs to be decrypted by client's privet key)
        - a tmp private key for file server(needs to be decrypted by file server's private key)

    Once we got the ticket, we can then upload the file
    """

    """
    Communication with the File Server
    security:
    To ensure the data is not getting stolen by the man-in-middle, file server encrypt file data with the tmp private key provided by the auth server
    The file server will then be decrypted by us with the tmp public key, which needs to be decrypted first with our own private key
    """

    for directory in encrypted_download_directories:

        # decrypt the destination
        directory = helper.decrypt(directory, client_tmp_pbk_for_directory_server)

        # get ticket from auth server
        secure_file_server = helper.encrypt(directory, constant.PRIVATE_KEY)
        encrypted_auth_server_pbk = helper.encrypt(constant.AUTHENTICATION_SERVER_PUBLIC_KEY, constant.PRIVATE_KEY)
        headers = {'id': uid, 'server': secure_file_server, 'security_check': encrypted_auth_server_pbk}
        response = requests.post(constant.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps({}),
                                 headers=headers)

        # parse respones data
        json_data = json.loads(response.text)

        # decypt keys and ticket
        fs_tmp_pvk = json_data['server']
        ticket = json_data['ticket']
        client_tmp_pbk_for_file_server = helper.encrypt(json_data['client'], constant.PRIVATE_KEY)

        # encrypt data with client tmp public key
        secure_file_code = helper.encrypt(file_code, client_tmp_pbk_for_file_server)

        # send the file
        headers = {'id': uid, 'file_code': secure_file_code, 'access_key': fs_tmp_pvk, 'ticket': ticket}
        response = requests.post(constant.DOWNLOAD_FILE_REQUEST.format(directory), data=json.dumps({}),
                                 headers=headers)

        # return the file
        encrypted_data = response.text
        data = helper.decrypt(encrypted_data, client_tmp_pbk_for_file_server)
        return data


def lockOrUnLock(fname, uid, lock):

    """
    Communicating with Authentication Server, get ticket for directory server
    """

    # get ticket
    directory_server = helper.encrypt("directory", constant.PRIVATE_KEY)
    encrypted_auth_server_pbk = helper.encrypt(constant.AUTHENTICATION_SERVER_PUBLIC_KEY, constant.PRIVATE_KEY)
    headers = {'id': uid, 'server': directory_server, 'security_check': encrypted_auth_server_pbk}
    response = requests.post(constant.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps(""),
                             headers=headers)

    # parse respones data
    json_data = json.loads(response.text)

    # decrypt the pbk and use it to encrypt sensitive information
    encrypted_client_tmp_pbk = json_data['client']
    encrpyted_directory_sever_tmp_pvk = json_data['server']
    ticket = json_data['ticket']
    client_tmp_pbk_for_directory_server = helper.decrypt(encrypted_client_tmp_pbk, constant.PRIVATE_KEY)

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
    response = requests.post(constant.DIRECTORY_SERVER_DOWNLOAD_DESTINATION_ASSIGNING_REQUEST, data=json.dumps({}),
                             headers=headers)

    # parse respones data
    json_data = json.loads(response.text)

    # parse and decrypt response, the target file server's address is stored in header
    # file will use file code as the file name is distributed file system
    encrypted_download_directories = json_data['directories']
    file_code = helper.decrypt(json_data['code'], client_tmp_pbk_for_directory_server)

    """
    Communicating with Authentication Server, get ticket and lock the file:
    request authentication server for access key
    authentication server will authenticate the Client, and provide ticket to the Client.
    the ticket is essentially a tmp (public key, private key), and the file name encrypted by the target file server's public key 

    security:
    On Client side, we do not need to worry about man-in-middle attack when we communicate with authentication server as all we need is a ticke 
    if the ticket is fake than, the only risk is that the file uploading will fail.
    However, on the authentication server side, we do need to worry about the fake Client issue. To make authetication server trust our request,
    we upload the encrypted public key of auth server(encrypted with client's private key), the authentication server will decrypt(with out client's public key) and compare the public key
    This ensures the client 
        - has auth server's public key
        - has target client's private key

    The ticket compose of 
        - a tmp public key for client(needs to be decrypted by client's privet key)
        - a tmp private key for file server(needs to be decrypted by file server's private key)

    Once we got the ticket, we can then upload the file
    """

    """
    Communication with the File Server
    security:
    To ensure the data is not getting stolen by the man-in-middle, we encrypt file data with the tmp public key provided by the auth server
    The file server will decrypt it with the tmp private key, which needs to be decrypted first with it's own private key
    """

    for directory in encrypted_download_directories:

        # decrypt the destination
        directory = helper.decrypt(directory, client_tmp_pbk_for_directory_server)

        # get ticket from auth server
        secure_file_server = helper.encrypt(directory, constant.PRIVATE_KEY)
        encrypted_auth_server_pbk = helper.encrypt(constant.AUTHENTICATION_SERVER_PUBLIC_KEY, constant.PRIVATE_KEY)
        headers = {'id': uid, 'server': secure_file_server, 'security_check': encrypted_auth_server_pbk}
        response = requests.post(constant.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps({}),
                                 headers=headers)

        # parse respones data
        json_data = json.loads(response.text)

        # decypt keys and ticket
        fs_tmp_pvk = json_data['server']
        ticket = json_data['ticket']
        client_tmp_pbk_for_file_server = helper.encrypt(json_data['client'], constant.PRIVATE_KEY)

        # encrypt data with client tmp public key
        secure_file_code = helper.encrypt(file_code, client_tmp_pbk_for_file_server)

        # send the file
        headers = {'id': uid, 'file_code': secure_file_code, 'access_key': fs_tmp_pvk, 'ticket': ticket}

        if lock:
            response = requests.post(constant.LOCK_REQUEST.format(directory), data=json.dumps({}),
                                     headers=headers)
        else:
            response = requests.post(constant.UNLOCK_REQUEST.format(directory), data=json.dumps({}),
                                     headers=headers)
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





