from socket import *
import sys
import os
import signal
import pickle

SERVER_PORT = 1234

USER_LIST = {}#{'jose': '123', '101': 'abc', 'joao': '123abc'}
USER_BLOCKED = {}
USER_MAIL = {}#{'read': [mail1, mail2], 'unread': [mail3]}
OPERATOR = 'admin'

#email = {'from': user, 'subject': subject, 'body' : body}
#mail = {'UNREAD': [{'from': 'admin', 'subject': 'test', 'body': 'hello there!'}], 'READ': []}

#Each email is a dict where:
#-> 'from' is who sent it, 
#-> 'subject' is the subject
#-> 'body' is the body (the message itself)

def createSocket():
	s = socket(AF_INET, SOCK_STREAM) 
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	s.bind(('', SERVER_PORT))
	s.listen(5)
	print('Socket created!\n')
	return s

#Load UserList
def loadUsers():
	global USER_LIST
	if os.path.isfile('users.irc') and (os.path.getsize('users.irc') > 0):
		with open('users.irc', 'rb') as input:
			USER_LIST = pickle.load(input)
	print('Registered Users:')
	for k, v in USER_LIST.items():
		print(k, v)

#Save the File (when changes are done)
def saveUsers():
	global USER_LIST
	with open('users.irc', 'wb') as file:
		pickle.dump(USER_LIST, file, pickle.HIGHEST_PROTOCOL)

#Load Blocked List
def loadBlocked():
	global USER_BLOCKED
	if os.path.isfile('blocked.irc') and (os.path.getsize('blocked.irc') > 0):
		with open('blocked.irc', 'rb') as input:
			USER_BLOCKED = pickle.load(input)

#Save the File (when changes are done)
def saveBlocked():
	global USER_BLOCKED
	with open('blocked.irc', 'wb') as file:
		pickle.dump(USER_BLOCKED, file, pickle.HIGHEST_PROTOCOL)

#Reads E-mails from file
def loadEmail(username):
	global USER_MAIL
	if os.path.isfile(username + '.irc') and (os.path.getsize(username + '.irc') > 0):
		with open(username + '.irc', 'rb') as input:
			USER_MAIL = pickle.load(input)
	print('Mail from user ' + username + ' loaded.')

#Stores E-mails on file
def storeEmail(username):
	global USER_MAIL
	with open(username + '.irc', 'wb') as file:
		pickle.dump(USER_MAIL, file, pickle.HIGHEST_PROTOCOL)

#"Main" Class
def main():
	skt = createSocket()
	loadUsers()
	loadBlocked()
	while 1:
		client, adress = skt.accept()
		pid = os.fork()
		if pid == 0:
			action(client)
			skt.close()
			sys.exit(0)

#go for login/whatever needed
def action(client):
	operation, username, password = processInfo(client)

	loadUsers()
	loadBlocked()

	if operation == 'L':						#login
		login(client, username, password)
	
	elif operation == 'M':						#LIST_MESS
		emailInfo(client, username, 'UNREAD')
	
	elif operation == 'U':						#LIST_USERS
		listUsers(client, 'authorized')

	elif operation == 'T':						#List Blocked
		listUsers(client, 'banned')				
	
	elif operation == 'S':						#SEND_MESS
		sendEmail(client, username)
	
	elif operation == 'R':						#LIST_READ
		emailInfo(client, username, 'READ')
	
	elif operation == 'A':						#ListAllMessages (used with REMOVE_MES)
		emailInfo(client, username, 'UNREAD')
		emailInfo(client, username, 'READ')

	elif operation == 'D':						#REMOVE_MES
		client.send(('1').encode('utf-8'))
		delMail(client)

	elif operation == 'P':						#CHANGE_PASSW
		changePW(client, username, password)
	
	elif operation == 'E':						#OPER
		operator(client, password)

	elif operation == 'O':						#QUIT
		logout(client, username)
	
	elif operation == 'B':						#Just Getting the body of a certain message
		getBody(client)

	elif operation == 'N':						#Register new user
		register(client, username)

	elif operation == 'G':
		bpUser(client, username, 'ban')

	elif operation == 'H':
		bpUser(client, username, 'pardon')

#Info Processing (getting username/password from client)
def processInfo(client):
	operation = ''
	username = ''
	password = ''

	aux = client.recv(32).decode('utf-8')
	operation = aux[0]
	i = 2
	while 1:
		if aux[i] != ';':
			username += aux[i]
			i += 1
		else:
			break
	
	for c in aux[i + 1:]:
		password += c

	return operation, username, password

#Info Processing 2(converting multiple info into lists)
def processInfo2(string, output):
	i = 0
	size = len(string)
	aux  = ''
	while i < size:
		if string[i] != ',':
			aux += string[i]
		elif string[i] == ',':
			output.append(aux)
			aux = ''
		if i == size -1:
			output.append(aux)
		i += 1

#login stuff
def login(client, username, password):
	global USER_LIST

	if username in USER_LIST.keys():
		if USER_LIST[username] == password:
			client.send(('1').encode('utf-8'))
			print('User successfully connected!')
			print('id: ' + username, 'pw: ' + password)
		else:
			client.send(('2').encode('utf-8'))
			print('Wrong Password! Try again?')
	else:
		client.send(('0').encode('utf-8'))

#Get the Senders and Subjects
def emailInfo(client, username, which):
	global USER_MAIL
	mails = {}#{'UNREAD': [{'from': 'admin', 'subject': 'test', 'body': 'hello there!'}], 'READ': []}
	loadEmail(username)
	senders = ''
	subjects = ''

	size = len(USER_MAIL[which])
	if size == 0:
		client.send(('null').encode('utf-8'))
		client.recv(5).decode('utf-8')
		client.send(('null').encode('utf-8'))
		return
	#from
	i = 0
	while i < size:
		senders += USER_MAIL[which][i]['from']
		if i != size -1:
			senders += ','
		i += 1
	#Subjects
	i = 0
	while i < size:
		subjects += USER_MAIL[which][i]['subject']
		if i != size -1:
			subjects += ','
		i += 1

	client.send((senders).encode('utf-8'))

	client.recv(5).decode('utf-8') ###

	client.send((subjects).encode('utf-8'))

#sends the email body to the user
def getBody(client):
	global USER_MAIL
	info = []
	client.send(('1').encode('utf-8'))
	aux = client.recv(1024).decode('utf-8')
	processInfo2(aux, info)
	username = info[0]	
	which = info[1]
	sender = info[2]
	subject = info[3]

	loadEmail(username)
	
	size = len(USER_MAIL[which])
	i = 0
	while i < size:
		if USER_MAIL[which][i]['subject'] == subject:
			if USER_MAIL[which][i]['from'] == sender:
				client.send((USER_MAIL[which][i]['body']))
				readMail(USER_MAIL[which][i], username, which)
				break

#marks the mail as read (only if needed)
def readMail(mail, username, which):
	global USER_MAIL
	if which == 'UNREAD':
		loadEmail(username)
		USER_MAIL['READ'].append(mail)
		USER_MAIL['UNREAD'].remove(mail)
		storeEmail(username)

#Send the authorized users list
def listUsers(client, which):
	global USER_LIST
	global USER_BLOCKED
	
	if which == 'authorized':
		users = USER_LIST.keys()
	elif which == 'banned':
		users = USER_BLOCKED.keys()

	number = len(users)

	if number == 0:
		client.send(('null').encode('utf-8'))
		return

	info = ''
	while number != 0:
		info += users[number-1]
		if number > 1:
			info += ','
		number -= 1
	client.send((info).encode('utf-8'))

#sends Emails
def sendEmail(client, username):
	global USER_LIST
	sendTo = []	#List of users to send the message to
	user = ''
	users = ''
	users = client.recv(100).decode('utf-8')
	size = len(users)
	i = 0
	while i < size:
		if users[i] != ',' and users[i] != ' ':
			user += users[i]
		elif users[i] == ',':
			sendTo.append(user)

			user = ''
		if i == size - 1:
			sendTo.append(user)
		i += 1

	client.send(('1').encode('utf-8'))
	subject = client.recv(50).decode('utf-8')

	client.send(('1').encode('utf-8'))
	body = client.recv(2048).decode('utf-8')

	client.send(('1').encode('utf-8'))

	i = 0
	size = len(sendTo)
	while i < size:
		print('Mail received!')
		writeEmail(username, sendTo[i], subject, body)
		i += 1

#Writes the email on each user file
def writeEmail(username, receiver, subject, body):
	global USER_LIST
	global USER_MAIL
	print(username)
	if receiver in USER_LIST.keys():
		new_mail ={'from': username, 'subject': subject, 'body': body}
		loadEmail(receiver)
		USER_MAIL['UNREAD'].append(new_mail)
		storeEmail(receiver)

#deletes a specific email
def delMail(client):
	global USER_MAIL
	info = []
	aux = client.recv(1024).decode('utf-8')
	processInfo2(aux, info)
	username = info[0]	
	which = info[1]
	sender = info[2]
	subject = info[3]

	loadEmail(username)

	size = len(USER_MAIL[which])
	i = 0
	while i < size:
		if USER_MAIL[which][i]['subject'] == subject:
			if USER_MAIL[which][i]['from'] == sender:
				USER_MAIL[which].remove(USER_MAIL[which][i])
				print('Mail Deleted.')
				client.send(('1').encode('utf-8'))
				storeEmail(username)
				break

#Change Password
def changePW(client, username, password):
	global USER_LIST
	if username in USER_LIST:
		USER_LIST[username] = password
		client.send(('1').encode('utf-8'))
		print('Password for user ' + username + ', now is: ' + password)
		saveUsers()
	else:
		client.send(('0').encode('utf-8'))

#Operator Privileges
def operator(client, password):
	global OPERATOR
	if password == OPERATOR:
		client.send(('1').encode('utf-8'))
	else:
		client.send(('0').encode('utf-8'))

def bpUser(client, username, action):
	global USER_LIST
	global USER_BLOCKED

	if action == 'ban':
		password = USER_LIST[username]
		USER_BLOCKED[username] = password
		del USER_LIST[username]

	elif action == 'pardon':
		password = USER_BLOCKED[username]
		USER_LIST[username] = password
		del USER_BLOCKED[username]
	client.send(('1').encode('utf-8'))

	print('User banned/pardoned')

	saveUsers()
	saveBlocked()

#Reg new user
def register(client, username):
	global USER_LIST
	global USER_BLOCKED
	global USER_MAIL
	while 1:
		if username not in USER_LIST.keys() and username not in USER_BLOCKED.keys():
			client.send(('1').encode('utf-8'))
			break

		else:
			client.send(('0').encode('utf-8'))
			username = client.recv(15).decode('utf-8')

	password = client.recv(50).decode('utf-8')

	USER_LIST[username] = password

	saveUsers()

	client.send(('1').encode('utf-8'))

	#just give a default mail when a new user is created
	USER_MAIL = {'UNREAD': [{'from': 'admin', 'subject': 'test', 'body': 'hello there!'}], 'READ': []}

	storeEmail(username)

#client LogOut
def logout(client, username):
	print('User ' + username + ' logged out!')
	client.send(('1').encode('utf-8'))

def signal_handler(signal, frame):
	print(' pressed, exiting now')
	sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal_handler)
	main()
	#in order to create a "new" email file, run the command below with the first parameter being 
	#the name of the new user
	#storeEmail('101', {'UNREAD': [{'from': 'admin', 'subject': 'test', 'body': 'hello there!'}], 'READ': []})
