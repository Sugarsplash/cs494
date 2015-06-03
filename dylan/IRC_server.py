# Dylan Johnson
# CS494
# 6/3/15
# IRC_server

# This is a program for the server of an IRC

# Modules
import select	# Wait for I/O completion
import socket	# Networking interface

# Functions

# This function determines what message the client sent to the server
def decipher(client, info):
    if info[0:6] == 'INROOM':
	specified_room = info[len('INROOM'):]
	INROOM(client, specified_room)
    elif info[0:4] == 'JOIN':
	specified_room = info[len('JOIN'):]
	JOIN(client, specified_room)
    elif info[0:5] == 'LEAVE':
	specified_room = info[len('LEAVE'):]
	LEAVE(client, specified_room)
    elif info[0:6] == 'LOGOUT':
	LOGOUT(client)
    elif info[0:7] == 'PRIVMSG':
	word_array = info.split()
	receiver = word_array[1]
	message = info[(len('PRIVMSG')+len(receiver)):]
	PRIVMSG(client, receiver, message)
    elif info[0:7] == 'ROOMMSG':
	word_array = info.split()
	specified_room = word_array[1]
	message = info[(len('ROOMMSG')+len(specified_room)):]
	ROOMMSG(client, message)
    elif info[0:5] == 'ROOMS':
	ROOMS(client)
    else:# User entered an invalid command
	client.send('Invalid command, refer to README for list of commands')



# This function displays the names of all the clients in a particular room
def INROOM(client, specified_room):
    if len(rooms) == 0:# There are no rooms
	client.send('There are currently no rooms to look into')
    i = 0
    for current_room in rooms:# Check rooms
	if current_room == specified_room:# Room found
	    for check in user_info:# Send usernames in the room
		if current_room in user_info[client]['rooms']:
		    client.send(user_info[client]['username'])
	    i = 1
    if i == 0:# The room was not found
	client.send('%s does not exist' % current_room)



# This function lets the client join a room, or create a room if the given
# name of the room isn't in the list of current rooms
def JOIN(client, specified_room):
    if specified_room in rooms:
	user_info[client]['rooms'].append(specified_room)
	user_info[client]['current'] = specified_room
	client.send(('Successfully joined %s') % specified_room)
    else:# Room not found, create room instead
	rooms.append(specified_room)
	user_info[client]['rooms'].append(specified_room)
	user_info[client]['current'] = specified_room
	client.send('Created %s' % specified_room)



# This function lets the client leave any room they have previously joined
def LEAVE(client, specified_room):
    if specified_room in user_info[client]['rooms']:
	# If the room the client leaves is the room they're currently in,
	# make sure to change their current room to no current room
	if specified_room == user_info[client]['current']:
	    user_info[client]['current'] = ''
	user_info[client]['rooms'].remove(specified_room)
    else:# Client hasn't joined this room
	client.send('You need to join %s before you can try to leave it'
							% specified_room)



# This function causes the client to exit the server
def LOGOUT(client):
    # Remove the user from any rooms previously joined
    for i in range(len(user_info[client]['rooms'])):
	LEAVE(client, user_info[client]['rooms'][i])
    usernames.remove(user_info[client]['username'])# Remove client username
    client.close()		# Close client connection
    connections.remove(client)	# Remove client socket from connections



# This function allows a client to send a private message to another client
def PRIVMSG(client, receiver, message):
    if receiver in usernames:
	for current_socket in connections:
	    if current_socket == receiver:
		current_socket.send(message)
    else:# Username not in server list
	client.send('The given username "%s" was not found' % receiver)



def ROOMMSG(client, specified_room, message):
    if specified_room in user_info[client]['rooms']:
	for current_socket in connections:
	    if specified_room in user_info[current_socket]['rooms']:
		current_socket.send(message)
    else:# Client hasn't joined this room to send the message
	client.send('You need to join %s before you can send a message to it'
							% specified_room)



# This function displays all the rooms currently in the server
def ROOMS(client):
   if len(rooms) == 0:# Check if there are rooms on the server
	client.send('There are no rooms on the server')
   else:
	client.send('Rooms in the server: ')
	for current_room in rooms:
	    client.send('%s, ' %  current_room)



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

while 1:
    # Check if any input sockets are ready (output and exception not used)
    input_ready, output_dummy, exception_dummy = select.select(
							connections, [], [])

    for client in input_ready:
	if client == serv:# Incoming connection
	    clientfd = serv.accept()
	    connections.append(clientfd)
	    # Set up for acquiring details of user information
	    user_info[clientfd]={
		'username': '',
		'rooms': [],
		'current': ''		# Keep track of which room client is in
	    }
	    # Make sure that the username sent isn't already in the server
	    name = clientfd.recv(2048).strip()
	    if name in usernames:
		client.send('%s in use, log in with another username' % name)
		LOGOUT(client)
	    elif ' ' in name:
		client.send('Please do not use spaces in your username')
		LOGOUT(client)
	    else:
		user_info[clientfd]['username'] = name
		usernames.append(name)
	else:# Incoming message
	    try:
		info = client.recv(2048).strip()
		if info:
		    decipher(info)		# Interpret message
	    except:
		LOGOUT(client)
		continue
	

serv.close()

