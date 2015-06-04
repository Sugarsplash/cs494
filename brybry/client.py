# telnet program example
import socket, select, string, sys

def prompt():
    sys.stdout.write('<You> ')
    sys.stdout.flush()

#main function
if __name__ == "__main__":
    #Check args supplied by user
    if(len(sys.argv) < 4) :
        #Wrong number of args, display usage and exit
        print 'Usage : python2 client.py hostname port username'
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
    username = sys.argv[3]

    #Create TCP socket connection and set timeout
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print 'Unable to connect'
        sys.exit()

    print 'Connected to remote host.'
    
    #log on with username supplied
    try:
        s.send(username)
    except:
        #username was not able to log in
        print 'Unable to log in with credentials provided.'
        sys.exit()
    print 'Log in success. Join a room to begin chat.'
    
    while 1:
        socket_list = [sys.stdin, s]

        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print '\nDisconnected from chat server'
                    sys.exit()
                else :
                    #print data
                    sys.stdout.write(data)
                    prompt()

            #user entered a message
            else :
                msg = sys.stdin.readline()
                s.send(msg)
                prompt()
