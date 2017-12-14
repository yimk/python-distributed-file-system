
# install essential lib
pip install -r requirements.txt
# run mongodb
mongod &

# start authentication server
python AuthenticationServer/server.py &

# start directory server
python DirectoryServer/server.py &

# start locking server
python LockingServer/server.py &

# start all file servers
python FileServer/server.py 0 &
python FileServer/server.py 1 &
python FileServer/server.py 2 &
python FileServer/server.py 3 