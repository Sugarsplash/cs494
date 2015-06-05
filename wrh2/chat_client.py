"""
 An IRC Client programmed in python
 Note: code has been tested with python version 2.7.9
 Programmed by William Harrington for CS494 Programming Project
"""

import socket   # for socket objects
import select   # for select function
import signal   # for signal interrupt
import sys      # for handling command line arguments

def prompt() :
    """Function creates a user prompt

    :param username: the user's name
    """

    sys.stdout.write("->") # prompt user
    sys.stdout.flush()     # flush buffer


def signal_handler(signal, frame):
    """Function handles signal interrupt (CTRL-C)
    
    :param signal: signal caught
    :param frame: current stack frame
    """
    s.send('/exit')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    """Main function

    """
    
    # user supplied the wrong amount of arguments
    if(len(sys.argv) < 4):
        # show proper usage and exit program
        print 'Usage : python chat_client.py hostname port username'
        sys.exit()

    host = sys.argv[1]      # get the IRC server address
    port = int(sys.argv[2]) # get the IRC server  port number
    username = sys.argv[3]  # get the user's name

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create TCP Socket
    s.settimeout(2)                                       # set timeout to 2 seconds
    
    # connect to remote host
    try:
        s.connect((host, port))
    except:
        print 'Unable to connect'
        sys.exit()

    print 'Connected to IRC server'

    # send user's name to server
    try:
        s.send(username)
    except:
        # bad username, exit program
        print 'Unable to authenticate username'
        sys.exit()
    print 'Username authenticated'
    prompt()

    while 1:
        socket_list = [sys.stdin, s]
        
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
        
        #try:
        for sock in read_sockets:
        #incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data:
                    print '\nDisconnected from chat server'
                    sys.exit()
                else:
                    sys.stdout.write('%s\n' % data)
                    prompt()
        
            #user entered a message
            else :
                msg = sys.stdin.readline()
                s.send(msg)
                prompt()
            
