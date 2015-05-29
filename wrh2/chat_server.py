"""
 An IRC server programmed in python
 Note: code has been tested with python version 2.7.9
 Programmed by William Harrington for CS494 Programming Project
"""
import socket  # for socket objects
import select  # for select function
import logging # for logging

def broadcast_data (sock, message):
    """Function to broadcast chat messages to all connected clients
    :param sock: socket object
    :param message: message to send
    """

    #Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            # try to send the message, if we can't send socket timed out so log client off
            try :
                socket.send(message)
            except :
                logoff(socket)

def parse_data(sock, message):
    """Function to parse the data received and perform the appropriate action
    :param sock: socket object
    :param message: message to parse
    """
    if message.find('/who')==0:
        logging.info('%s requested user list' % accounts[sock]['username'])
        logging.info('%s' % USER_LIST)
        
    elif message.find('/join')==0:
        if message[6]:
            logging.info(('%s user wants to join ' + message[6:]) % accounts[sock]['username'])
            joinchannel(sock, message[6:])
        else:
            logging.info('%s sent invalid command' % accounts[sock]['username'])
    elif message.find('/exit')==0:
        logoff(sock)
    elif message.find('/leave')==0:
        if message[7]:
            logging.info(('%s sent request to leave' + message[7:]) % accounts[sock]['username'])
        else:
            logging.info('%s user sent invalid command' % accounts[sock]['username'])
    elif message.find('/PRIVMSG')==0:
        if message[9]:
            broadcast_data(sock, "\n" + "<" + accounts[sock]['username'] + "> " + message[9:])
    else:
        logging.info('%s sent invalid command' % accounts[sock]['username'])
        sock.send("\n" + "INVALID COMMAND NIGGUH")

def joinchannel(sock, channel):
    """Function joins user to channel
    :param sock: socket object
    :param channel: channel name
    """
    # look for the channel name in the channel list
    for channels in CHANNEL_LIST:
        # if the channel is in the list
        if channel:
            accounts[sock]['channels'].append(channel) # add channel to user's channels
            accounts[sock]['current'] = channel        # make channel the user's current channel
            sock.send(("\n" + "Joined %s") % channel)  # tell the user their in the channel now
        else:
            CHANNEL_LIST.append(channel)               # create channel by adding it to the channel list
            accounts[sock]['channels'].append(channel) # add channel to user's channels
            accounts[sock]['current'] = channel        # make channel the user's current channel
            sock.send(("\n" + "Joined %s") % channel)  # tell the user their in the channel now
    logging.info('Channel list: %s' % CHANNEL_LIST)    # for the server log


def logoff(sock):
    """Function logs a client off the server
    :param sock: socket object:
    """
    broadcast_data(sock, "\n" + "%s has gone offline" % accounts[sock]['username']) #tell everyone what is going on
    logging.info('%s is offline' % accounts[sock]['username']) #for the server log
    USER_LIST.remove(accounts[sock]['username']) #remove client from user list
    sock.close() #close the socket
    CONNECTION_LIST.remove(sock) #remove socket from connection list

if __name__ == "__main__":
    """Main function
    """

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
    accounts = {}        # keep track of user information
    USER_LIST = []       # list to keep track of usernames
    CONNECTION_LIST = [] # list to keep track of socket descriptors
    CHANNEL_LIST = []    # array to keep track of channels
    RECV_BUFFER = 4096   # Receive buffer, Advisable to keep it as an exponent of 2
    PORT = 6667          # Server port number
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP socket
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT)) #bind socket
    server_socket.listen(10) #start listening, backlog of 10
    
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
    
    #information that might be useful to clients
    logging.info("Chat server started. Client should connect to " + socket.gethostbyname(socket.gethostname()) + " " + str(PORT))

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
        
        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd) #Add to connection list

                #create an account, in the account dictionary
                accounts[sockfd]={
                    'username': '',
                    'key': '',
                    'channels': '',
                    'current': ''
                }

                #get the client's username
                while 1:
                    name = sockfd.recv(RECV_BUFFER).strip()
                    if name in USER_LIST:
                        print "Username already in use"
                    else:
                        accounts[sockfd]['username']=name
                        break
                USER_LIST.append(accounts[sockfd]['username']) #Add to user list
                logging.info('Client (%s, %s) connected' % addr) #log some information
                logging.info('Client is know as %s, added to the user list' % accounts[sockfd]['username']) #log some information
                broadcast_data(sockfd, "%s entered room\n" % accounts[sockfd]['username']) #tell everyone someone has arrived
            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER).strip()
                    if data:
                        parse_data(sock,data)

                except:
                    logoff(sock)
                    continue

server_socket.close()
