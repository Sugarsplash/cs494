# telnet program example
import socket, select, string, sys

def prompt(username) :
    sys.stdout.write("<%s> " % username)
    sys.stdout.flush()

#main function
if __name__ == "__main__":
    
    if(len(sys.argv) < 3) :
        print 'Usage : python chat_client.py hostname port username'
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
    username = sys.argv[3]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
    s.settimeout(2)
    
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print 'Unable to connect'
        sys.exit()

    print 'Connected to remote host.'
    try:
        s.send(username)
    except:
        print 'Unable to send username'
        sys.exit()
    print 'Username authenticated'
    prompt(username)

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
                    sys.stdout.write(data + "\n")
                    prompt(username)
        
            #user entered a message
            else :
                msg = sys.stdin.readline()
                #s.send("<"+username+"> " + msg)
                s.send(msg)
                prompt(username)
