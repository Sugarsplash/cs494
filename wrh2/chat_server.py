"""
 An IRC server programmed in python
 Note: code has been tested with python version 2.7.9
 Programmed by William Harrington for CS494 Programming Project
"""
import socket  # for socket objects
import select  # for select function
import logging # for logging
import signal  # for signal interrupts
import sys


def broadcast_data (sock, message):
    """Function to broadcast chat messages to all connected clients
   
    This function sends a message to clients connected to the server
    Messages are sent according to the current channel that the sender is in
    This means that only clients whose current channel is the same as
    The sender will receive the message

    :param sock: socket object
    :param message: message to send
    """

    if accounts[sock]['current'] == '':
        return

    #Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock:
            if accounts[socket]['current'] == accounts[sock]['current']:
                # try to send the message, if we can't send socket timed out so log client off
                try :
                    socket.send(message)
                except :
                    logoff(socket)


def privatemsg(sock, msg):
    """Function handles msg command
    which allows user to send private messages

    :param sock: socket object
    :param msg: message to send
    """

    # split the msg string into array of strings
    # then grab the piece at index 1
    user = msg.split()[1]

    # take everything after the user name
    # turn it into msg2send string
    msg2send = msg[5+len(user):]

    # check to see if that username is
    # in the user list
    if user in USER_LIST:

        # go through the accounts
        for key in accounts:

            # find the specified user
            if accounts[key]['username'] == user:

                # try sending the private message
                try:
                    key.send('\n<private message from %s>%s\n' % (accounts[sock]['username'], msg2send))
                    break  # to stop needless iterations

                # otherwise log that socket off
                except:
                    logoff(key)

    # username wasn't in user list
    else:
        sock.send('\nNo such user\n')


def parse_data(sock, message):
    """Function to parse the data received and perform the appropriate action

    This function really only takes care of /PRIVMSG commands
    Everything else is passed on to parse_data2

    :param sock: socket object
    :param message: message to parse
    """

    # received PRIVMSG command 
    if message.find('/PRIVMSG')==0:
        # check to see that we even actually have a message
        if len(accounts[sock]['channels']) == 0:
            sock.send('\nMust join channel to send a message\n')
        else:
            if message[9]:
                broadcast_data(sock, '\n<%s> %s\n' % (accounts[sock]['username'],message[9:])) # we have a message so send it
            else:
                sock.send('\nEmpty message, nothing has been sent\n') # we didn't actually get a message from the user to send, bad user!

    # received a msg command
    elif message.find('/msg') == 0:

        # split message string up to do error checking
        check_msg = message.split()
        print len(check_msg)

        # check to make sure we have a sufficient
        # amount of arguments before we try
        if len(check_msg) >= 3:
            privatemsg(sock, message)
        else:
            sock.send('\nInvalid command\n')

    else:
        # so for simplicity's sake we don't parse the /PRIVMSG command based on white space but everything else we do
        message = message.split()
        parse_data2(sock, message)


def parse_data2(sock, message):
    """Function receives data parsed based on whitespace and takes the appropriate action

    The majority of messages pass through this function
    (the only exception being /PRIVMSG commands)
    Therefore it is very important to server operation

    :param sock: socket object
    :param message: message to dictate action
    """

    # take action based on the length of the message
    if len(message) == 1:

        # received help command
        if message[0] == '/help':
            # general help command, lists all commands
            help(sock, command=None)

        # received who command
        elif message[0] == '/who':
            who(sock)
        
        # received list command
        elif message[0] == '/list':
            list(sock)

        # received exit command
        elif message[0] == '/exit':
            logoff(sock)

        # received nick command
        elif message[0] == '/nick':
            changenick(sock, nick=None)

        # everything else is invalid
        else:
            sock.send('\nInvalid command\n')

    elif len(message) == 2:

        # received help command
        if message[0] == '/help':
            help(sock, message[1])

        # receive a whois command
        elif message[0] == '/whois':
            whois(sock, message[1])

        # received a peek command
        elif message[0] == '/peek':
            peek(sock, message[1])

        # received a join command
        elif message[0] == '/join':
            joinchannel(sock, message[1])

        # received a leave command
        elif message[0] == '/leave':
            leavechannel(sock, message[1])

        # received a current command
        elif message[0] == '/current':
            switchcurrent(sock, message[1])

        # received a nick command
        elif message[0] == '/nick':
            changenick(sock, message[1])

        # everything else is invalid
        else:
            sock.send('\nInvalid command\n')

    # everything else is invalid
    else:
        sock.send('\nInvalid command\n')


def help(sock, command):
    """Function processes help command which shows user list of commands
        If command is supplied, specific info about command is sent to client
        
        :param sock: socket object
        :param command: option argument shows specific info for command
        """
    
    if command is None:
        sock.send('\nList of commands\n')
        sock.send('/help -- shows valid commands\n')
        sock.send('/nick <new nickname> -- show/change username\n')
        sock.send('/who -- shows users on server\n')
        sock.send('/list -- shows channels on server\n')
        sock.send('/exit -- logoff\n')
        sock.send('/whois <username> -- info about user\n')
        sock.send('/peek <channel> -- shows users in channel\n')
        sock.send('/join <channel> -- join channel\n')
        sock.send('/leave <channel> -- leave channel\n')
        sock.send('/current <channel> -- change current channel\n')
        sock.send('/msg <user> <message> -- send user private message\n')
        sock.send('/help <command> -- more info on command\n')
    else:
        if command == 'nick':
            sock.send('\nCommand: /nick\n')
            sock.send('Arguments: <new username>\n')
            sock.send('Description: The nick command will' \
                          ' change your username to <new username>\n')
            sock.send('If <new username> is not provided,' \
                          ' current username is echoed\n')
        elif command == 'who':
            sock.send('\nCommand: /who\n')
            sock.send('Arguments: none\n')
            sock.send('Description: The who command will show you all the users on the server\n')

        elif command == 'list':
            sock.send('\nCommand: /list\n')
            sock.send('Arguments: none\n')
            sock.send('Description: The list command will show you a list of the current channels on the server\n')
        
        elif command == 'exit':
            sock.send('\nCommand: /exit\n')
            sock.send('Arguments: none\n')
            sock.send('Description: The exit command will log you off the server\n')
        
        elif command == 'whois':
            sock.send('\nCommand: /whois\n')
            sock.send('Arguments: <username>\n')
            sock.send('Description: The whois command will display basic info about the user specified with <username>\n')
            sock.send('Ex: /whois billy\n')
        
        elif command == 'peek':
            sock.send('\nCommand: /peek\n')
            sock.send('Arguments: <channel>\n')
            sock.send('Description: The peek command will show you a list of users in <channel>\n')
            sock.send('Ex: /peek #channel_one\n')
        
        elif command == 'join':
            sock.send('\nCommand: /join\n')
            sock.send('Arguments: <channel>\n')
            sock.send('Description: The join command will place you in the channel specified with <channel>\n')
            sock.send('If the channel does not exist yet, it will be created\n')
            sock.send('By default the most recent channel you have join becomes your current channel\n')
            sock.send('Channel names must start with # and contain no spaces or other illegal characters\n')
            sock.send('Ex: /join #channel_one\n')
        
        elif command == 'leave':
            sock.send('\nCommand: /leave\n')
            sock.send('Arguments: <channel>\n')
            sock.send('Description: The leave command will take you out of the channel specified by <channel>\n')
            sock.send('You must be in a channel in order to leave it.\n')
            sock.send('If you are the last person in the channel, once you leave it will be deleted\n')
            sock.send('Ex: /leave #channel_one\n')
        
        elif command == 'current':
            sock.send('\nCommand: /current\n')
            sock.send('Arguments: <channel>\n')
            sock.send('Description: The current command will switch your current channel\n')
            sock.send('You must be in the channel specified by <channel>\n')
            sock.send('Ex: /current #channel_one\n')

        elif command == 'msg':
            sock.send('\nCommand: /msg\n')
            sock.send('Arguments: <user>, <message>\n')
            sock.send('Description: Send private message <message> to <user>\n')
            sock.send('Ex: /msg billy hi billybob!\n')
        
        else:
            sock.send('\nSpecified command does not exist.')
            sock.send(' Type /help for list of commands\n')



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

    # channel list is 0 so no channels
    if len(CHANNEL_LIST) == 0:
        sock.send('\nNo channels currently on server\n')
    
    # channel list is not 0 so send the list
    else:
        # prompt the client
        sock.send('\nList of channels on server\n')
        
        # grab the channel list which is an array
        # and turn it a string
        channel_list = ", ".join(CHANNEL_LIST)
        
        # send string off to client
        sock.send('%s' % channel_list)


def logoff(sock):
    """Function processes exit command which logs a client off the server
        
    First this function tells everyone what is going on
    Second it removes the client from each channel they are in
    Third it removes user from list
    Fourth it closes the socket and removes it from connection list

    :param sock: socket object
    """
    
    # tell everyone that someone is leaving
    broadcast_data(sock, '\n%s has gone offline' % accounts[sock]['username'])
    
    # Remove user from all the channels that they are currently in
    for i in range(len(accounts[sock]['channels'])):
        leavechannel(sock,accounts[sock]['channels'][i])

    # for the server log
    logging.info('%s is offline' % accounts[sock]['username'])

    # check to see if we even had a user name
    if len(accounts[sock]['username']) > 0:
        # remove client from user list
        USER_LIST.remove(accounts[sock]['username'])
    
    # close the socket
    sock.close()
    
    # remove socket from connection list
    CONNECTION_LIST.remove(sock)


def whois(sock, username):
    """Function processes a whois command
    which reveals info about a specific username

    :param sock: socket object
    :param username: user to look up
    """

    socket = 0

    # check to see if username exists
    if username in USER_LIST:

        # it does so lets find the socket
        # that is associated with that username
        for key in accounts:
            if accounts[key]['username'] == username:
                socket = key  # store socket object
                break  # break out of for loop
    
        # send client some info on this socket
        sock.send('\nUser: %s [%s]' % (username, accounts[socket]['ip']))
        
        # check to see if this socket is in any channels
        if len(accounts[socket]['channels']) > 0:
            # grab the array of channels
            # associated with the socket
            # and turn it into a string
            channel_list = ",".join(accounts[socket]['channels'])
            
            # send client the channels
            sock.send('\nChannels: %s\n' % channel_list)
                
        # socket is not in any channels
        else:
            sock.send('\n%s is currently not in any channels' % username)

    # username doesn't exist
    else:
        sock.send('\n%s not currently connected to server' % username)


def joinchannel(sock, channel):
    """Function processes join command which joins user to channel

    :param sock: socket object
    :param channel: channel name
    """
    
    user = accounts[sock]['username']
    
    if channel in CHANNEL_LIST:
        # add channel to user's channels
        accounts[sock]['channels'].append(channel)
        
        # make channel the user's current channel
        accounts[sock]['current'] = channel
        
        # notify client
        sock.send('\nJoined %s\n' % channel)
        
        # tell everyone someone has arrived
        broadcast_data(sock, ('\n%s joined %s\n') % (user, channel))
    
    else:
        # make sure channel starts with # character
        if channel.find('#') == 0:
            # create channel by adding it to the channel list
            CHANNEL_LIST.append(channel)
            
            # add channel to user's channels
            accounts[sock]['channels'].append(channel)
            
            # make channel the user's current channel
            accounts[sock]['current'] = channel
            
            # notify client
            sock.send('\nJoined %s' % channel)
            
            # tell everyone someone has arrived
            broadcast_data(sock, ('\n%s joined %s\n') % (user, channel))
            
            
            # for the server logs
            logging.info('New channel: %s' % channel)
            logging.info('Updated channel list: %s' % CHANNEL_LIST)
        
        # invalid channel name, no bueno
        else:
            sock.send('\nInvalid channel name\n')
            sock.send('\nSee /help join\n')

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
        sock.send('\nYou left %s\n' % channel)

        # check to see if we should remove
        # from the channel list
        count = 0
        for key in accounts:
            if channel in accounts[key]['channels']:
                count += 1
        if count == 0:
            CHANNEL_LIST.remove(channel)
            logging.info('%s removed from channel list' % channel)
            logging.info('Updated channel list: %s' % CHANNEL_LIST)

    else:
        sock.send('\nNot in channel\nMust be in a channel to leave\n')


def peek(sock, channel):
    """Function processes peek command which shows user who is in a specific channel

    :param sock: socket object
    :param channel: channel to check
    """

    users_in_channel = []
    
    # No channels yet
    if len(CHANNEL_LIST) == 0:
        sock.send('\nNo channels currently on server\n')

    # We have channels to peek at
    else:
        # check if channel is in the list
        if channel in CHANNEL_LIST:
            
            # it is so tell the user who is in there
            sock.send("\nUsers in %s\n" % channel)
            
            # go through the accounts
            for key in accounts:
                # if channel listed in account, store it in array
                if channel in accounts[key]['channels']:
                    users_in_channel.append(accounts[key]['username'])
        
            # turn array into string
            users_in_channel = ", ".join(users_in_channel)

            # send info to client who requested it
            sock.send('%s' % users_in_channel)

        # uh oh channel not in the list
        else:
            sock.send('\nChannel not in channel list\n')

def switchcurrent(sock, channel):
    """Function processes a current command which allows a user to switch current channel

    :param sock: socket object
    :param channel: channel to switch to
    """

    # as long as they are in that channel
    if channel in accounts[sock]['channels']:
        accounts[sock]['current'] = channel # switch current channel
    else:
        sock.send('\nCurrently not in %s\nMust be in channel\n' % channel)


def changenick(sock, nick):
    """Function processes a nick command
    which changes the user's username

    :param sock: socket object
    :param nick: new username
    """

    # echo back username
    if nick is None:
        sock.send('\nCurrent username: %s\n' % accounts[sock]['username'])
        return

    if nick in USER_LIST:
        if nick == accounts[sock]['username']:
            sock.send('\nThats already your username\n')
        else:
            sock.send('\nUsername already in use\n')
    else:
        old = accounts[sock]['username']

        # remove the old username
        USER_LIST.remove(old)

        # set new username
        accounts[sock]['username'] = nick

        # update the USER_LIST
        USER_LIST.append(accounts[sock]['username'])

        # tell the user about the change
        broadcast_data(sock, '\n%s is now know as %s' % (old,accounts[sock]['username']))


def signal_handler(signal, frame):
    """Function handles signal interrupt (CTRL-C)
        
    :param signal: signal caught
    :param frame: current stack frame
    """

    for connection in CONNECTION_LIST:
        if connection != server_socket:
            logoff(connection)
    server_socket.close()
    
    logging.info('Server shutting down')
    sys.exit(0)


# initialize signal handler
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    """Main function

    """
    
    # for logging information on the server
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

    accounts = {}        # keep track of user information
    USER_LIST = []       # list to keep track of usernames
    CONNECTION_LIST = [] # list to keep track of socket descriptors
    CHANNEL_LIST = []    # array to keep track of channels
    RECV_BUFFER = 4096   # Receive buffer
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
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])
        
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
                name = sockfd.recv(RECV_BUFFER).strip()

                accounts[sockfd]['username']=name
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
