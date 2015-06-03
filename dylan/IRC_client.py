# Dylan Johnson
# CS494
# 6/3/15
# IRC_client

# This is a program for the client of an IRC

# Modules
import select	# Wait for I/O completion
import socket	# Networking interface
import string	# Useful for message displays
import sys	# Command line arguments (i.e. argv)

# User should supply the name of the program followed by the hostname (name of
# the server), the port number, and then their username.
# USAGE:	IRC_client.py <HOST> <PORT> <USERNAME>
# EXAMPLE:	IRC_client.py ubuntu 1.2.3.4 my_username

# Check if the user gave the correct number of arguments
if len(sys.argv) < 4:
    print "USAGE: IRC_client.py <HOST> <PORT> <USERNAME>";
    sys.exit(0)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	# Create socket

host = sys.argv[1]	# IRC server address
port = int(sys.argv[2])	# IRC server port number
username = sys.argv[3]	# Name of the user

s.settimeout(3)		# This is needed for checking to see if the connection
			# is still established (check if server is running)

# Connect to the server
try:
    s.connect((host, port))
except:
    print 'Could not connect to server'
    sys.exit()

# Now that we're connected, make sure that the server can accept the username
try:
    s.send(username)
except:
    # Username has unsupported characters
    print 'Server can not process the username: %s' % username
    sys.exit()

# Give the user a basic prompt interface
sys.stdout.write("IRC-SERVER: ")
sys.stdout.flush()	# Make sure to flush the buffer

# The user is connected and can now pass in messages to the server. The server
# will interpret the messages and determine which action the user wants to
# take. These actions include 
while 1:
    # Create a list of input objects containing server socket and the
    # standard input
    input_objects = [s, sys.stdin]

    # Check if any input sockets are ready (output and exception not used)
    input_ready, output_dummy, exception_dummy = select.select(
							input_objects, [], [])

    # Check where the socket came from
    for current_socket in input_ready:
	if current_socket == s:# Socket received from server
	    info = current_socket.recv(2048)
	    if not info:# Server disconnected
		print 'Disconnected from server'
		sys.exit()
	    else:# Display information received from server
		sys.stdout.write("IRC-SERVER: " + info + "\n")
		sys.stdout.flush()

	else:# Socket received from user
	    user_message = sys.stdin.readline()
	    s.send(user_message)
	    sys.stdout.write("IRC-SERVER: ")
	    sys.stdout.flush()

