# Distributed File System (Python)

## Client Service

The client provides the following services:

  - Upload: Upload files and distribute(replicate) the target file across the distributed file system
  - Download: Download the file from the distributed file system
  - Lock: Lock the file
  - Unlock the file
  - Edit: 
    - The file will be first be locked by the client
    - No other person but client can access the file
    - Client will then download the file and display it to user
    - Client will ask user to enter the new data of the file
    - Client will upload the new data(edit the file)
    - Client will then unlock the file
          
 ## Security Service
 
 - The security service follows the keberos pattern
 - When client starts, it will first check if it is signed up(on the distributed file system).
 - If not, it will register itself. It will generate a private key and public key pair. 
     - Private Key: Client will keep the private key. 
     - Public Key: Client will encrypt it with the authentication server's public key and send the encrypted public key to client. This ensures man-in-middle will not be able to pretend to be the auth server.
     In here, we assume the client must know authentication server's public key to register.
 - The authentication server will keep the public key of the client and assign client an user_id.
 - When client trying to acccess file_server, lock_serve or directory server, it will:
    - send the encrypted address of the target server to the authentication server(encrypted by it's public key)
    - authentication server will then decrypt it and if it works, it will send back a temporary public key and temporary private key to the client.
    - temporary public key will be used by the client(client be need to decrypt it with it's private key as it is encrypted by authentication server with it's public key)
    - temporary private key will be used by the target server(target server be need to decrypt it with it's private key as it is encrypted by authentication server with it's public key)
    - when the client and target server are transferring sensitive information. They will encrypt the data with the temporary key first
    - This ensures man-in-middle will not be able to pretend to be the target server and steal sensitive information, especially when the client is trying to  transfer data to file server

## Directory Service
  - Uploading: when user upload a file, it will first communicate with the directory server. The directory server will returns back the address of the assigned file server and the file code of the file. 
  The file will be stored as file code in the file server. This makes the system scalable.
  
  - Downloading: when user wants to download the file, it will communicate with the directory server. The directory server will returns back the address of the assigned file server and the file code of the file.
  The client will then download the file from one of the file server available.
  
## Replication
  - When client is uploading the file. Instead of uploading the file to one file server, we will distribute the replications of the file across the system.(In here, every file server will have a copy)
  This makes the system fault tolerant, e.g when one file server crash, client will be able to get the file from another file server.
  - There are two options when we do replication:
    1. client upload the file to one of the file server and the file server distributes it
    2. client send the copy of the file to a number of file server
  - I choose 2, as we can have unlimited number of client and always have limited number of file server. By doing that, we minimize the traffic between the servers.

## Locking
- The Locking server enables client to lock a file in a given file server. When the file is locked, no person but the client who lock the file can access the file. The client will also be the only person that are able to unlock the file.

## Caching
I implemented caching in
  - File Server: The file server will keep the data of maximum of 50 files in the memory. This optimise the speed of for the file server to read the file.
  - Client: The client will keep the directories of maximum of 50 files in the memory. This reduces the traffic of the system as client do not have to communicate with the directory server as much as before.
  
  
# Run the application without docker

1. Ensure Mongodb is installed in the machine
2. Run the start-service-without-docker.sh file, it
    
    - install dependency
    - start mongodb
    - run all the servers
    
    bash ./start-service-without-docker.sh file
    
    
3. Run Client in test mode
    
    python Client/client.py test-mode
   
   The test mode does the following:
   
    1. Upload a log file to distributed file system. You will now be able to tmp_0, tmp_1 .. folders, you will be able to see that the files are created under these directory
    
    2. Download the file again from the DFS and store it in tmp_download_client directory
    3. Edit the file, it will
        - lock the target file
        - display the target file data and ask you to enter new data.
        - NOW! Do Not enter it. Try to start another client with the same command: python Client/client.py test-mode
        - You will see that client2 will not be able to upload the file as it is locked. Do not terminate client2, as it will reupload the file automatically after five minutes
        - Go back to client1 and enter the updated data
        - Job done
        - Wait for client 2 and you will be able see that it will upload the file again under the same scenerio after five minutes
    4. Download the file.
    
 4. Run Client in free-to-go mode, you can create as many client as you want
    
      python Client/client.py 
    
     
    
    

  
  
