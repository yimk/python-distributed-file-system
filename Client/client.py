import rest_messager
import constant
import os
import helper


def handle_upload_command(directory):

    # prepare essential data
    fname = directory.split('/')[-1]
    data = open(directory, 'rb').read()

    # request communication helper to upload the data securely
    # based on pre-decided protocol
    result = rest_messager.secure_upload(data, fname, constant.USER_ID)



def handle_download_command(param):

    # get essential variable
    target = param

    # download the file
    # the file will be decrpyted by communication helper as this is part of the protocol
    data = rest_messager.secure_download(target, constant.USER_ID)

    # write file to the destination
    print("Data: \n" + data)
    os.makedirs(os.getcwd() + "/tmp/")
    open(os.getcwd() + "/tmp/" + target, 'wb').write(data)


def handle_lock_command(param):
    # get essential variable
    target = param

    # lock the file
    rest_messager.lock_or_unlock(param, constant.USER_ID, True)


def handle_unlock_command(param):

    # lock the file
    rest_messager.lock_or_unlock(param, constant.USER_ID, False)


def handle_edit_command(param):

    # download the file
    data = rest_messager.secure_download(param, constant.USER_ID)

    # lock the file
    rest_messager.lock_or_unlock(param, True)

    # print data and ask user to update the file
    print("Data: \n" + data + '\n')
    update_data = input("Please enter the new data in the file")

    # unlock the file
    rest_messager.lock_or_unlock(param, False)

    # update the file
    rest_messager.secure_upload(update_data, param)


def register():
    if not helper.registered():
        pbk, pvk = helper.generate_ticket()
        id = rest_messager.register(pbk)
        helper.db_register(pvk, id)

def run_client():

    register()
    import os
    handle_download_command("MuseLog.txt")

    command = input(constant.ASK_FOR_COMMAND)
    param = command.split(' ').pop()

    handle_lock_command(param)
    if command.startswith(constant.TRANSACTION_UPLOAD):
        handle_upload_command(param)
    elif command.startswith(constant.UPLOAD):
        handle_upload_command(param)
    elif command.startswith(constant.DOWNLOAD):
        handle_download_command(param)
    elif command.startswith(constant.LOCK):
        handle_lock_command(param)
    elif command.startswith(constant.EDIT):
        handle_edit_command(param)




if __name__ == '__main__':
    while True:
        run_client()

