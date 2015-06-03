# Tcp Chat server

import socket, select

#Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message, shout = None):
    if shout:
        for socket in CONNECTION_LIST:
            if socket != server_socket and socket != sock :
                for every in user[sock]['rooms']:
                    if every in user[socket]['rooms']:
                        try :
                            socket.send(message)
                        except :
                            # broken socket connection may be, chat client pressed ctrl+c for example
                            print "OH, he gettin removed and shit."
                            socket.close()
                            CONNECTION_LIST.remove(socket)
    else:
        #Do not send the message to master socket and the client who has send us the message
        for socket in CONNECTION_LIST:
            if socket != server_socket and socket != sock :
                if user[socket]['current'] == user[sock]['current']:
                    try :
                        socket.send(message)
                    except :
                        # broken socket connection may be, chat client pressed ctrl+c for example
                        print "OH, he gettin removed and shit."
                        socket.close()
                        CONNECTION_LIST.remove(socket)


def command_tree (sock, data):

    if data.find('logout')!= -1:
        logout(sock)
    elif data.find('create')!= -1:
        command_list = data.split()
        del command_list[0]
        create_room(sock, command_list)
    elif data.find('rooms')!= -1:
        list_rooms(sock)
    elif data.find('join')!= -1:
        command_list = data.split()
        del command_list[0]
        join_room(sock, command_list)
    elif data.find('leave')!= -1:
        leave_room(sock, data)
    elif data.find('lurk')!= -1:
        lurk(sock, data)
    elif data.find('where')!= -1:
        where(sock)
    elif data.find('shout')!= -1:
        command_list = data.split()
        del command_list[0]
        message = '<' + str(user[sock]['username']) + '> ' + ' '.join(command_list) + '\n'
        shout = 'shouting'
        broadcast_data(sock, message, shout)


def logout (sock):
    print 'loggin out broseph'
    broadcast_data(sock, "\n" + user[sock]['username'] + " has gone offline\n") #tell everyone what is going on
    USER_LIST.remove(user[sock]['username']) #remove client from user list
    sock.close() #close the socket
    CONNECTION_LIST.remove(sock) #remove socket from connection list


def create_room(sock, data):

   for i in range(len(data)):
        if data[i] in ROOM_LIST:
            break
        else:
            ROOM_LIST.append(data[i])
            if not user[sock]['rooms']:
                args = []
                args.append(data[i])
                join_room(sock, args)

def list_rooms(sock):
    room_str = ', '.join(ROOM_LIST) + '\n'
    sock.send(room_str)

def join_room(sock,data):

    for i in range(len(data)):
        if data[i] in ROOM_LIST:
            user[sock]['rooms'].append(data[i])
        else: 
            ROOM_LIST.append(data[i])
            user[sock]['rooms'].append(data[i])

        if not user[sock]['current']:
            user[sock]['current'] = data[i]

        sock.send("\n" + "Joined %s" % data[i])

def leave_room(sock, data):

    command_list = data.split()
    del command_list[0]
    print command_list
    for i in range(len(command_list)):
        if command_list[i] in user[sock]['rooms']:
            user[sock]['rooms'].remove(command_list[i])
            sock.send("\n" + "Left %s" % command_list[i])
            if command_list[i] == user[sock]['current']:
                user[sock]['current'] = ''
                sock.send("\n" + "No room currently selected")

def lurk(sock, data):

    command_list = data.split()
    del command_list[0]
    for key in user:
            if command_list:
                if command_list[0] in user[key]['rooms']:
                    sock.send(user[key]['username'] + "\n")
            else:
                sock.send('feed the baby\n')

def where(sock):

    sock.send(user[sock]['current'] + "\n")






if __name__ == "__main__":


    user = {} #A dict to track usernames and rooms for each connection
    CONNECTION_LIST = []    # List to keep track of socket descriptors
    USER_LIST = []          # List of usernames
    ROOM_LIST = []          # List of rooms
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)

    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)

    print "Chat server started on port " + str(PORT)

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)      #add connection to list
                #Create a user entry for new connection
                user[sockfd]={
                    'username': '',
                    'rooms': [],
                    'current': ''
                }

                #attempt to log user in with supplied username
                
                credential = sockfd.recv(RECV_BUFFER).strip()
                #Check to see if username desired is already in use.
                if credential in USER_LIST:
                    error_mesg = 'Username taken.\n'
                    print error_mesg
                    sockfd.send(error_mesg)
                    sockfd.close()
                    CONNECTION_LIST.remove(sockfd)
                    break
                        
                else: #set username and append to list of users
                    user[sockfd]['username']=credential
                    USER_LIST.append(user[sockfd]['username'])
                    print "Client", addr, "logged in as", credential,"\n"
                    broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)
                    break



               

            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                data = sock.recv(RECV_BUFFER).strip()
                if data:
                    if data.find(':')!= -1:
                        command_tree(sock, data)
                    else:
                        print data
                        broadcast_data(sock, "\r" + '<' + str(user[sock]['username']) + '> ' + data + '\n')

    server_socket.close()
