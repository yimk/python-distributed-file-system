# host
LOCALHOST = "localhost"
DIRECTORY_SERVER_HOST = LOCALHOST
AUTHENTICATION_SERVER_HOST = LOCALHOST
LOCK_SERVER_HOST = LOCALHOST

FILE_SERVER_HOST = {}
FILE_SERVER_HOST['0'] = LOCALHOST
FILE_SERVER_HOST['1'] = LOCALHOST
FILE_SERVER_HOST['2'] = LOCALHOST
FILE_SERVER_HOST['3'] = LOCALHOST

# port
DIRECTORY_SERVER_PORT = "5001"
AUTHENTICATION_SERVER_PORT = "5002"
LOCK_SERVER_PORT = "5003"

FILE_SERVER_PORT = {}
FILE_SERVER_PORT['0'] = "6001"
FILE_SERVER_PORT['1'] = "6002"
FILE_SERVER_PORT['2'] = "6003"
FILE_SERVER_PORT['3'] = "6004"

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
LOCK = "lock"
UNLOCK = "unlock"
EDIT = "edit"

# gui properties
UPLOAD_PARAM = " <upload-file-path> \n"
DOWNLOAD_PARAM = " <download-file-name>\n"
LOCK_PARAM = " <file-name>\n"
UNLOCK_PARAM = " <file-name>\n"
EDIT_PARAM = " <file-name>\n"

ASK_FOR_COMMAND = "Please enter one of the following:\n\n" + \
                  UPLOAD + UPLOAD_PARAM + \
                  TRANSACTION_UPLOAD + UPLOAD_PARAM + \
                  DOWNLOAD + DOWNLOAD_PARAM + \
                  EDIT + EDIT_PARAM + \
                  LOCK + LOCK_PARAM + \
                  UNLOCK + UNLOCK_PARAM

# protocol
DIRECTORY_SERVER_UPLOAD_DESTINATION_ASSIGNING_REQUEST = "http://{}:{}/user/upload-assign".format(LOCALHOST, DIRECTORY_SERVER_PORT)
DIRECTORY_SERVER_DOWNLOAD_DESTINATION_ASSIGNING_REQUEST = "http://{}:{}/user/download-assign".format(LOCALHOST, DIRECTORY_SERVER_PORT)
AUTHENTICATION_SERVER_GET_TICKET_REQUEST = "http://{}:{}/user/authenticate".format(AUTHENTICATION_SERVER_HOST, AUTHENTICATION_SERVER_PORT)
# AUTHENTICATION_SERVER_DOWNLOAD_DESTINATION_ASSIGNING_REQUEST = "http://{}:{}/user/download-assign".format(AUTHENTICATION_SERVER_HOST, AUTHENTICATION_SERVER_PORT)
LOCK_REQUEST = 'http://{}/user/lock'.format(LOCK_SERVER_HOST, LOCK_SERVER_HOST)
UNLOCK_REQUEST = 'http://{}/user/unlock'.format(LOCK_SERVER_HOST, LOCK_SERVER_HOST)
ISLOCK_REQUEST = 'http://{}/user/islocked'.format(LOCK_SERVER_HOST, LOCK_SERVER_HOST)
UPLOAD_FILE_REQUEST = 'http://{}/user/upload'
DOWNLOAD_FILE_REQUEST = 'http://{}/user/download'


# PUBLIC KEYS
DIRECTORY_SERVER_PUBLIC_KEY = "4ThisIsARandomlyGenAESpublicKey4"
AUTHENTICATION_SERVER_PUBLIC_KEY = "4ThisIsARandomlyGenAESpublicKey4"
LOCK_SERVER_PUBLIC_KEY = "4ThisIsARandomlyGenAESpublicKey4"

CLIENT_PUBLIC_KEY = {}
CLIENT_PUBLIC_KEY['0'] = ("4ThisIsARandomlyGenAESpublicKey4")
CLIENT_PUBLIC_KEY['1'] = ("4ThisIsARandomlyGenAESpublicKey4")
CLIENT_PUBLIC_KEY['2'] = ("4ThisIsARandomlyGenAESpublicKey4")
CLIENT_PUBLIC_KEY['3'] = ("4ThisIsARandomlyGenAESpublicKey4")

FILE_SERVER_PUBLIC_KEY = {}
FILE_SERVER_PUBLIC_KEY['0'] = ("4ThisIsARandomlyGenAESpublicKey4")
FILE_SERVER_PUBLIC_KEY['1'] = ("4ThisIsARandomlyGenAESpublicKey4")
FILE_SERVER_PUBLIC_KEY['2'] = ("4ThisIsARandomlyGenAESpublicKey4")
FILE_SERVER_PUBLIC_KEY['3'] = ("4ThisIsARandomlyGenAESpublicKey4")

# PRIVATE KEY
DIRECTORY_SERVER_PRIVATE_KEY = "4ThisIsARandomlyGenAESpublicKey4"
AUTHENTICATION_SERVER_PRIVATE_KEY = "4ThisIsARandomlyGenAESpublicKey4"
LOCK_SERVER_PRIVATE_KEY = "4ThisIsARandomlyGenAESpublicKey4"

CLIENT_PRIVATE_KEY = {}
CLIENT_PRIVATE_KEY['0'] = ("4ThisIsARandomlyGenAESPRIVATEKey4")
CLIENT_PRIVATE_KEY['1'] = ("4ThisIsARandomlyGenAESPRIVATEKey4")
CLIENT_PRIVATE_KEY['2'] = ("4ThisIsARandomlyGenAESPRIVATEKey4")
CLIENT_PRIVATE_KEY['3'] = ("4ThisIsARandomlyGenAESPRIVATEKey4")

FILE_SERVER_PRIVATE_KEY = {}
FILE_SERVER_PRIVATE_KEY['0'] = ("4ThisIsARandomlyGenAESPRIVATEKey4")
FILE_SERVER_PRIVATE_KEY['1'] = ("4ThisIsARandomlyGenAESPRIVATEKey4")
FILE_SERVER_PRIVATE_KEY['2'] = ("4ThisIsARandomlyGenAESPRIVATEKey4")
FILE_SERVER_PRIVATE_KEY['3'] = ("4ThisIsARandomlyGenAESPRIVATEKey4")

