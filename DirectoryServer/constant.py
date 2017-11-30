
# host
LOCALHOST = "localhost"
DIRECTORY_SERVER_HOST = LOCALHOST
AUTHENTICATION_SERVER_HOST = LOCALHOST

# port
DIRECTORY_SERVER_PORT = "5001"
AUTHENTICATION_SERVER_PORT = "5002"

# mongo db configuration
MONGO_HEADING = "mongodb://"
MONGO_SERVER = LOCALHOST
MONGO_PORT = "27017"

# security configuration
USER_ID = "1"
PUBLIC_KEY = "4ThisIsARandomlyGenAESpublicKey4"
PRIVATE_KEY = "notsoez2HackThis"

# user input command
UPLOAD = "upload"
DOWNLOAD = "download"
TRANSACTION_UPLOAD = "upload-transaction"

# gui properties
UPLOAD_PARAM = " <upload-file-path> \n"
DOWNLOAD_PARAM = " <download-file-name> <destination-path> \n"
ASK_FOR_COMMAND = "Please enter one of the following:\n\n" + UPLOAD + UPLOAD_PARAM + TRANSACTION_UPLOAD + UPLOAD_PARAM + DOWNLOAD + DOWNLOAD_PARAM

# protocol
DIRECTORY_SERVER_UPLOAD_DESTINATION_ASSIGNING_REQUEST = "http://{}:{}/user/upload-assign".format(LOCALHOST, DIRECTORY_SERVER_PORT)
DIRECTORY_SERVER_DOWNLOAD_DESTINATION_ASSIGNING_REQUEST = "http://{}:{}/user/download-assign".format(LOCALHOST, DIRECTORY_SERVER_PORT)
DIRECTORY_SERVER_PUBLIC_KEY = "4ThisIsARandomlyGenAESpublicKey4"

AUTHENTICATION_SERVER_GET_TICKET_REQUEST = "http://{}:{}/user/get-ticket".format(AUTHENTICATION_SERVER_HOST, AUTHENTICATION_SERVER_PORT)
# AUTHENTICATION_SERVER_DOWNLOAD_DESTINATION_ASSIGNING_REQUEST = "http://{}:{}/user/download-assign".format(AUTHENTICATION_SERVER_HOST, AUTHENTICATION_SERVER_PORT)
