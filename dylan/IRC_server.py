# Dylan Johnson
# CS494
# 6/3/15
# IRC_server

# This is a program for the server of an IRC

# Modules
import select	# Wait for I/O completion
import socket	# Networking interface
import sys	# Command line arguments

# Functions

# This function sends a message to every user in the client's current room
def chat(client, message):
    # Check to see if the client has a username in the server
    if len(user_info[client]['username']) == 0:
	client.send('Please create a username before submitting any '
		'other commands to the server (form: USERNAME <username>)\n')
    elif len(user_info[client]['rooms']) == 0:
	client.send('You need to join a room in order to chat\n')
    else:
	for current_user in connections:
	    # Make sure we don't send to the server or to the client sending
	    if current_user != serv and current_user != client:
		if user_info[current_user]['current'] == \
						user_info[client]['current']:
		    current_user.send(('\n###%s' % user_info[client]['username'])
								 + message)



# This function determines what message the client sent to the server
def decipher(client, info):
    if info[0:6] == 'INROOM':
	specified_room = info[len('INROOM '):]
	INROOM(client, specified_room)
    elif info[0:4] == 'JOIN':
	specified_room = info[len('JOIN '):]
	JOIN(client, specified_room)
    elif info[0:5] == 'LEAVE':
	specified_room = info[len('LEAVE '):]
	LEAVE(client, specified_room)
    elif info[0:6] == 'LOGOUT':
	LOGOUT(client)
    elif info[0:7] == 'PRIVMSG':
	word_array = info.split()
	receiver = word_array[1]
	message = info[(len('PRIVMSG ')+len(receiver + ' ')):]
	PRIVMSG(client, receiver, message)
    elif info[0:5] == 'ROOMS':
	ROOMS(client)
    elif info[0:8] == 'USERNAME':
	name = info[len('USERNAME '):]
	USERNAME(client, name)
    else:# Client is chatting in their current room
	chat(client, info)



# This function displays the names of all the clients in a particular room
def INROOM(client, specified_room):
    # Check to see if the client has a username in the server
    if len(user_info[client]['username']) == 0:
	client.send('Please create a username before submitting any '
		'other commands to the server (form: USERNAME <username>)\n')
    else:
	if len(rooms) == 0:# There are no rooms
	    client.send('There are currently no rooms to look into')
	i = 0
	if specified_room in rooms:# Check rooms
	    i = 1
	    for current_user in connections:# Send usernames in the room
		if current_user != serv:# Don't send to server
		    if specified_room in user_info[current_user]['rooms']:
			client.send(user_info[current_user]['username'])
	if i == 0:# The room was not found
	    client.send('%s does not exist' % current_room)



# This function lets the client join a room, or create a room if the given
# name of the room isn't in the server list. The user can also use this
# function to change their current room
def JOIN(client, specified_room):
    # Check to see if the client has a username in the server
    if len(user_info[client]['username']) == 0:
	client.send('Please create a username before submitting any '
		'other commands to the server (form: USERNAME <username>)\n')
    elif ' ' in specified_room:# Rooms can't have spaces in them
	client.send('Sorry, rooms can not have any spaces in them\n')
    elif specified_room in rooms:
	if specified_room not in user_info[client]['rooms']:
	    user_info[client]['rooms'].append(specified_room)
	user_info[client]['current'] = specified_room
	client.send(('Joined %s') % specified_room)
    else:# Room not found, create room instead
	rooms.append(specified_room)
	user_info[client]['rooms'].append(specified_room)
	user_info[client]['current'] = specified_room
	client.send('Created %s' % specified_room)



# This function lets the client leave any room they have previously joined
def LEAVE(client, specified_room):
    # Check to see if the client has a username in the server
    if len(user_info[client]['username']) == 0:
	client.send('Please create a username before submitting any '
		'other commands to the server (form: USERNAME <username>)\n')
    elif specified_room in user_info[client]['rooms']:
	# If the room the client leaves is the room they're currently in,
	# make sure to change their current room to no current room
	if specified_room == user_info[client]['current']:
	    user_info[client]['current'] = ''
	user_info[client]['rooms'].remove(specified_room)
    else:# Client hasn't joined this room
	client.send('You need to join %s before you can try to leave it\n'
							% specified_room)



# This function causes the client to exit the server
def LOGOUT(client):
    # Check to see if the client has a username in the server
    if len(user_info[client]['username']) == 0:
	client.send('Please create a username before submitting any '
		'other commands to the server (form: USERNAME <username>)\n')
    # Remove the user from any rooms previously joined
    else:
	if len(user_info[client]['rooms']) != 0:
	    for current_room in rooms:
		if current_room in user_info[client]['rooms']:
		    LEAVE(client, current_room)
	if user_info[client]['username'] != '':# Remove client username
	    usernames.remove(user_info[client]['username'])
	client.close()		# Close client connection
	connections.remove(client)	# Remove client socket from connections



# This function allows a client to send a private message to another client
def PRIVMSG(client, receiver, message):
    # Check to see if the client has a username in the server
    if len(user_info[client]['username']) == 0:
	client.send('Please create a username before submitting any '
		'other commands to the server (form: USERNAME <username>)\n')
    elif receiver in usernames:
	for current_user in connections:
	    if current_user != serv:# Don't send to server
		if user_info[current_user]['username'] == receiver:
		    current_user.send(('%s ' % user_info[client]['username'])
								 + message)
    else:# Username not in server list
	client.send('The given username "%s" was not found\n' % receiver)



# This function displays all the rooms currently in the server
def ROOMS(client):
    # Check to see if the client has a username in the server
    if len(user_info[client]['username']) == 0:
	client.send('Please create a username before submitting any '
		'other commands to the server (form: USERNAME <username>)\n')
    elif len(rooms) == 0:# Check if there are rooms on the server
	client.send('There are no rooms on the server\n')
    else:
	client.send('Rooms in the server: ')
	for current_room in rooms:
	    client.send('%s' %  current_room)



# This function allows a client to create or change their username
def USERNAME(client, name):
	if name in usernames:
	    client.send('The name "%s" is already in use, please try '
						'another username' % name)
	elif len(name) == 0:
	    client.send('Your username can not be empty\n')
	elif ' ' in name:
	    client.send('Please do not use spaces in your username\n')
	else:
	    if user_info[client]['username'] != '':
		usernames.remove(user_info[client]['username'])
	    user_info[client]['username'] = name
	    usernames.append(name)
	    client.send('Your username is now: %s' % name)
    



###############################################################################

# Main program
connections = []	# Monitor all socket connections
port = 50000		# Port number
rooms = []		# Array of rooms
usernames = []		# Monitor list of usernames
user_info = {}		# Required for obtaining details in user information

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create socket
# set socket options here
serv.bind(("0.0.0.0", port))	# bind the socket
serv.listen(5)			# listen for clients

# The server needs to be added as one of the connections
connections.append(serv)
running = 1;

while running:
    # Check if any input sockets are ready (output and exception not used)
    input_ready, output_dummy, exception_dummy = select.select(
							connections, [], [])

    for client in input_ready:
	if client == serv:# Incoming connection
	    clientfd, address = serv.accept()
	    connections.append(clientfd)
	    # Set up for acquiring details of user information
	    user_info[clientfd]={
		'username': '',
		'rooms': [],
		'current': ''		# Keep track of which room client is in
	    }
	elif client == sys.stdin:
	    # Close the server if any input is entered
	    junk = sys.stdin.readline()
	    running = 0
	    serv.close()
	    sys.exit()
	else:# Incoming message
	    try:
		info = client.recv(2048)
		if info:
		    decipher(client, info)		# Interpret message
	    except:
		LOGOUT(client)
		continue
	

serv.close()

