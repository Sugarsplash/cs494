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
            if accounts[socket]['current'] == accounts[sock]['current']:
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
    # received PRIVMSG command, check for this first because the other commands are parsed based on white space while this one is not
    if message.find('/PRIVMSG')==0:
        # check to see that we even actually have a message
        if len(accounts[sock]['channels']) == 0:
            sock.send("\n" + "Must join channel to send a message" + "\n")
        else:
            if message[9]:
                broadcast_data(sock, "\n" + "<" + accounts[sock]['username'] + "> " + message[9:]) # we have a message so send it
            else:
                sock.send("\n" + "Empty message, nothing has been sent") # we didn't actually get a message from the user to send, bad user!
    else:
        # so for simplicity's sake we don't parse the /PRIVMSG command based on white space but everything else we do
        message = message.split()
        parse_data2(sock, message)

def parse_data2(sock, message):
    """Function receives data parsed based on whitespace and takes the appropriate action

    :param sock: socket object
    :param message: message to dictate action
    """
    # take action based on the length of the message
    if len(message) == 1:

        # received who command
        if message[0] == '/who':
            logging.info('%s requested user list' % accounts[sock]['username'])
            logging.info('Current user list: %s' % USER_LIST)
            who(sock)
        
        # received list command
        if message[0] == '/list':
            logging.info('%s requested list of channels' % accounts[sock]['username'])
            logging.info('Current list of channels: %s' % CHANNEL_LIST)
            list(sock)

        # received exit command
        if message[0] == '/exit':
            logoff(sock) # log user off

    elif len(message) == 2:

        # receive a whois command
        if message[0] == '/whois':
            whois(sock, message[1])

        # received a peek command
        if message[0] == '/peek':
            peek(sock, message[1])

        # received a join command
        if message[0] == '/join':
            logging.info(('%s user wants to join ' + message[1]) % accounts[sock]['username']) # log info for server
            joinchannel(sock, message[1])                                                      # try to put user in channel
        
        # received a leave command
        if message[0] == '/leave':
            logging.info(('%s sent request to leave' + message[1]) % accounts[sock]['username']) # log info for server
            leavechannel(sock, message[1])                                                       # try to take user out of channel

        # received a current command
        if message[0] == '/current':
            switchcurrent(sock, message[1])

    # everything else is...well invalid bitches~!
    else:
        logging.info('%s sent invalid command' % accounts[sock]['username'])
        sock.send("\n" + "INVALID COMMAND NIGGUH")

def who(sock):
    """Function processes who command which shows user other users connected to server

    :param sock: socket object
    """

    sock.send('\nUsers currently connected to server\n') # prompt
    user_list = ", ".join(USER_LIST)                     # make string out of USER_LIST array
    sock.send('%s' % user_list)                          # send string

def list(sock):
    """Function processes list command which shows user list of channels on server
    If no channels are currently on the server then the user is prompted
    Otherwise, each channel in CHANNEL_LIST is sent to the user

    :param sock: socket object
    """

    # send user list of channels
    if len(CHANNEL_LIST) == 0:
        sock.send('\nNo channels currently on server\ntype /join and then a channel name to create one!\n')
    else:
        sock.send('\nList of channels on server\n')
        channel_list = ", ".join(CHANNEL_LIST)
        sock.send('%s' % channel_list)

def logoff(sock):
    """Function processes exit command which logs a client off the server

    :param sock: socket object
    """
    broadcast_data(sock, "\n" + "%s has gone offline" % accounts[sock]['username']) #tell everyone what is going on
    
    # Remove user from all the channels that they are currently in
    for i in range(len(accounts[sock]['channels'])):
        leavechannel(sock,accounts[sock]['channels'][i])
              
    logging.info('%s is offline' % accounts[sock]['username']) #for the server log
    USER_LIST.remove(accounts[sock]['username']) #remove client from user list
    sock.close() #close the socket
    CONNECTION_LIST.remove(sock) #remove socket from connection list

def whois(sock, username):
    """Function processes a whois command which reveals information about a specific username

    :param sock: socket object
    :param username: user to look up
    """

    if username in USER_LIST:
        for key in accounts:
            if accounts[key]['username'] == username:
                socket = key
                break
        sock.send('\nUser: %s [%s]' % (username, accounts[socket]['ip']))
        if len(accounts[socket]['channels']) > 0:
            channel_list = ",".join(accounts[socket]['channels'])
            sock.send('\nChannels: %s\n' % channel_list)
        else:
            sock.send('\n%s is currently not in any channels' % username)
    else:
        sock.send('\n%s not currently connected to server' % username)

def joinchannel(sock, channel):
    """Function processes join command which joins user to channel

    :param sock: socket object
    :param channel: channel name
    """
    if channel in CHANNEL_LIST:
        accounts[sock]['channels'].append(channel) # add channel to user's channels
        accounts[sock]['current'] = channel        # make channel the user's current channel
        sock.send(("\n" + "Joined %s") % channel)
        broadcast_data(sock, ('\n%s joined %s\n') % (accounts[sock]['username'], channel)) #tell everyone someone has arrived
    else:
        CHANNEL_LIST.append(channel)               # create channel by adding it to the channel list
        accounts[sock]['channels'].append(channel) # add channel to user's channels
        accounts[sock]['current'] = channel        # make channel the user's current channel
        sock.send(("\n" + "Joined %s") % channel)
        broadcast_data(sock, ('\n' + '%s joined %s' + '\n') % (accounts[sock]['username'], channel)) #tell everyone someone has arrived
    logging.info('Channel list: %s' % CHANNEL_LIST)# for the server log

def leavechannel(sock, channel):
    """Function processes exit command which removes user from channel

    :param sock: socket object
    :param channel: channel to leave
    """
    #print accounts[sock]

    # check to see if user is even in that channel
    if channel in accounts[sock]['channels']:
        
        # tell channel that user is leaving
        broadcast_data(sock, ('\n%s left %s\n') % (accounts[sock]['username'], channel))

        # user has the channel in their channel list, check to see if its their current channel
        if accounts[sock]['current'] == channel:
            accounts[sock]['current'] = ''         # reset current channel
        accounts[sock]['channels'].remove(channel) # remove channel from user's channel list
        logging.info('%s left %s' % (accounts[sock]['username'], channel))
        sock.send(("\n" + "You left %s") % channel)

    else:
        sock.send("\n" + "Channel not in channel list" + "\n" + "Must be in a channel to leave")

def peek(sock, channel):
    """Function processes peek command which shows user who is in a specific channel

    :param sock: socket object
    :param channel: channel to check
    """

    # No channels yet
    if len(CHANNEL_LIST) == 0:
        sock.send("\n" + "No channels currently on server" + "\n" + "type /join and then a channel name to create one!")
    # We have channels to peek at
    else:
        # check if channel is in the list
        if channel in CHANNEL_LIST:
            # it is so tell the user who is in there
            sock.send("\nUsers in %s\n" % channel)
            for key in accounts:
                if channel in accounts[key]['channels']:
                    sock.send(accounts[key]['username'] + "\n")
        # uh oh channel not in the list
        else:
            sock.send("Channel not in channel list")

def switchcurrent(sock, channel):
    """Function processes a current command which allows a user to switch current channel

    :param sock: socket object
    :param channel: channel to switch to
    """

    # as long as they are in that channel
    if channel in accounts[sock]['channels']:
        accounts[sock]['current'] = channel # switch current channel
    else:
        sock.send('\nCurrently not in %s\nMust be in channel to make it current channel\n' % channel)

if __name__ == "__main__":
    """Main function

    """
    
    # for logging information on the server
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

    accounts = {}        # keep track of user information
    USER_LIST = []       # list to keep track of usernames
    CONNECTION_LIST = [] # list to keep track of socket descriptors
    CHANNEL_LIST = []    # array to keep track of channels
    RECV_BUFFER = 4096   # Receive buffer, Advisable to keep it as an exponent of 2
    PORT = 6667          # Server port number
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # create TCP socket
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # set socket options
    server_socket.bind(("0.0.0.0", PORT))                                # bind socket
    server_socket.listen(10)                                             # start listening, backlog of 10
    
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
                    'ip': '',
                    'key': '',
                    'channels': [],
                    'current': ''
                }

                accounts[sockfd]['ip'] = addr[0] # store IP address

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
                
            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER).strip()
                    if data:
                        if data.find('/')==0:
                            parse_data(sock, data)
                        else:
                            parse_data(sock, "/PRIVMSG " + data)

                except:
                    logoff(sock)
                    continue

server_socket.close()
