import constant
import rest_api_helper


def handle_upload_command(param, is_transaction):

    # get essential variable
    directory = param[0]

    # prepare essential data
    fname = directory.split('/')[-1]
    data = open(directory, 'rb').read()

    # request communication helper to upload the data securely
    # based on pre-decided protocol
    if is_transaction:
        rest_api_helper.secure_transaction_upload(data, fname, constant.USER_ID)
    else:
        rest_api_helper.secure_upload(data, fname, constant.USER_ID)


def handle_download_command(param):

    # get essential variable
    target = param[0]
    destination = param[1]

    # download the file
    # the file will be decrpyted by communication helper as this is part of the protocol
    data = rest_api_helper.secure_download(target)

    # write file to the destination
    print("Data: \n" + data)
    open(destination + "/" + target, 'w').write(data)


def run_client():

    command = input(constant.ASK_FOR_COMMAND)
    param = command.split(' ').pop()

    if command.startswith(constant.TRANSACTION_UPLOAD):
        handle_upload_command(param, True)
    elif command.startswith(constant.UPLOAD):
        handle_upload_command(param, False)
    elif command.startswith(constant.DOWNLOAD):
        handle_download_command(param)


if __name__ == '__main__':
    while True:
        run_client()

