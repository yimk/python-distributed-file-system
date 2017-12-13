import rest_messager
import config
import os
import helper
import sys


def handle_upload_command(directory):

    # prepare essential data
    fname = directory.split('/')[-1]
    data = open(directory, 'rb').read()

    # request communication helper to upload the data securely
    # based on pre-decided protocol
    result = rest_messager.secure_upload(data, fname)


def handle_download_command(param):

    # get essential variable
    target = param

    # download the file
    # the file will be decrpyted by communication helper as this is part of the protocol
    data = rest_messager.secure_download(target)

    # write file to the destination
    print("Data: \n" + str(data))
    if not os.path.exists(os.getcwd() + "/tmp_download/"):
        os.makedirs(os.getcwd() + "/tmp_download/")
    open(os.getcwd() + "/tmp_download" + "_file_server_id/" + target, 'wb').write(data)


def handle_lock_command(param):
    # get essential variable
    target = param

    # lock the file
    rest_messager.lock_or_unlock(param, True)


def handle_unlock_command(param):

    # lock the file
    rest_messager.lock_or_unlock(param, False)


def handle_edit_command(param):

    # lock the file, during the locking, client is the only one that are able to download/upload the file
    rest_messager.lock_or_unlock(param, True)

    # download the file
    data = rest_messager.secure_download(param)



    # print data and ask user to update the file
    print("Data: \n" + str(data) + '\n')
    update_data = input("Please enter the new data in the file.\n")

    # unlock the file
    rest_messager.lock_or_unlock(param, False)

    # update the file
    rest_messager.secure_upload(update_data, param)


def register():
    if not helper.registered():
        pbk, pvk = helper.generate_ticket()
        id = rest_messager.register(pbk)
        helper.db_register(pvk, id)


def test():
    print("test-start")
    handle_upload_command(os.getcwd() + "/tmp" + "_file_server_id/" + "MuseLog.txt")
    handle_download_command("MuseLog.txt")
    handle_edit_command("MuseLog.txt")
    handle_download_command("MuseLog.txt")

def run_client():

    register()
    
    if sys.argv[1] == 'test-mode':
        test()
        sys.exit()
    else:
        command = input(config.ASK_FOR_COMMAND)
        param = command.split(' ').pop()

        handle_lock_command(param)
        if command.startswith(config.TRANSACTION_UPLOAD):
            handle_upload_command(param)
        elif command.startswith(config.UPLOAD):
            handle_upload_command(param)
        elif command.startswith(config.DOWNLOAD):
            handle_download_command(param)
        elif command.startswith(config.LOCK):
            handle_lock_command(param)
        elif command.startswith(config.EDIT):
            handle_edit_command(param)




if __name__ == '__main__':
    while True:
        run_client()

