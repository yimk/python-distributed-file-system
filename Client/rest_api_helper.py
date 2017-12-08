import security_helper
import db_helper
import base64
import json
import constant
import requests


def secure_upload(data, fname, uid):

    # encrypt data and fname
    secure_fname = security_helper.encrypt(fname, constant.PUBLIC_KEY)

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

    secure_pbk = security_helper.encrypt(constant.PUBLIC_KEY, constant.DIRECTORY_SERVER_PUBLIC_KEY)
    headers = {'id': uid, 'filename': secure_fname, 'access_key': secure_pbk}
    response = requests.post(constant.DIRECTORY_SERVER_UPLOAD_DESTINATION_ASSIGNING_REQUEST, data=json.dumps(""),
                            headers=headers)

    # parse and decrypt response, the target file server's address is stored in header
    # file will use file code as the file name is distributed file system
    upload_destinations = security_helper.decrypt(response.headers.get('destianations'))
    file_code = security_helper.decrypt(response.headers.get('code'))

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
    To ensure the data is not getting stolen by the man-in-middle, we encrypt file data with the tmp public key provided by the auth server
    The file server will decrypt it with the tmp private key, which needs to be decrypted first with it's own private key
    """

    for destination in upload_destinations:

        # get ticket
        secure_file_server = security_helper.encrypt(destination, constant.PRIVATE_KEY)
        encrypted_auth_server_pbk = security_helper.encrypt(constant.AUTHENTICATION_SERVER_PUBLIC_KEY, constant.PRIVATE_KEY)
        headers = {'id': uid, 'file_server': secure_file_server, 'security_check': encrypted_auth_server_pbk}
        response = requests.post(constant.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps(""),
                            headers=headers)
        encrypted_client_tmp_pbk = response.headers.get('client')
        fs_tmp_pvk = response.headers.get('filer_server')
        client_tmp_pbk = security_helper.encrypt(encrypted_client_tmp_pbk, constant.PRIVATE_KEY)

        # encrypt data with client tmp public key
        secure_data = security_helper.encrypt(data, client_tmp_pbk)
        secure_file_code = security_helper.encrypt(file_code, client_tmp_pbk)

        # send the file
        headers = {'id': uid, 'file_code': secure_file_code, 'access_key': fs_tmp_pvk}
        response = requests.post(constant.UPLOAD_FILE_REQUEST, data=json.dumps(secure_data),
                                 headers=headers)


def secure_download(fname, uid):
    # encrypt data and fname
    secure_fname = security_helper.encrypt(fname, constant.PUBLIC_KEY)

    """
    Communicating with Directory Server:
    request directory server for destination file server(s)
    directory server will return back a file servers that contains the file

    security:
    the Client's uid, Client's public key will be encrypted with directory server's public key
    directory server will then decrypt Client's public key and use it to encrypt the target file servers address
    the encrypted address will then be sent back
    this ensures man-in-middle will not be able to pretend to be the directory server and find out the address of the host that holds the file
    """

    secure_pbk = security_helper.encrypt(constant.PUBLIC_KEY, constant.DIRECTORY_SERVER_PUBLIC_KEY)
    headers = {'id': uid, 'filename': secure_fname, 'access_key': secure_pbk}
    response = requests.post(constant.DIRECTORY_SERVER_DOWNLOAD_DESTINATION_ASSIGNING_REQUEST_DESTINATION_ASSIGNING_REQUEST, data=json.dumps(""),
                             headers=headers)

    # parse and decrypt response, the target file server's address is stored in header
    # file will use file code as the file name is distributed file system
    download_address = security_helper.decrypt(response.headers.get('address'))
    file_code = security_helper.decrypt(response.headers.get('code'))

    """
    Communicating with Authentication Server, get ticket and upload file:
    request authentication server for access key
    authentication server will authenticate the Client, and provide ticket to the Client.
    the ticket is essentially a tmp (public key, private key), and the file name encrypted by the target file server's public key 

    security:
    On Client side, we do not need to worry about man-in-middle attack when we communicate with authentication server as all we need is a ticke 
    if the ticket is fake than, the only risk is that the file uploading will fail.
    However, on the authentication server side, we do need to worry about the fake Client issue. To make authetication server trust our request,
    we upload the unecnrypted file server id and encrypted file server id(with out private key), the authentication server will decrypt(with out public key) and compare the file server id

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


    # get ticket
    secure_file_server = security_helper.encrypt(download_address, constant.PRIVATE_KEY)
    headers = {'id': uid, 'file_server': download_address, 'secure_file_server': secure_file_server}
    response = requests.post(constant.AUTHENTICATION_SERVER_GET_TICKET_REQUEST, data=json.dumps(""),
                             headers=headers)
    (encrypted_client_tmp_pbk, fs_tmp_pvk) = response.headers.get('ticket')
    client_tmp_pbk = security_helper.encrypt(encrypted_client_tmp_pbk, constant.PRIVATE_KEY)

    # encrypt data with client tmp public key
    secure_file_code = security_helper.encrypt(file_code, client_tmp_pbk)

    # send the file
    headers = {'id': uid, 'file_code': secure_file_code, 'access_key': fs_tmp_pvk}
    response = requests.post(constant.DOWNLOAD_FILE_REQUEST, data=json.dumps(""),
                             headers=headers)


def file_exists(fname):
    pass





