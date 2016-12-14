from socket import *
import sys
import os
import signal
 
SERVER_NAME = 'localhost'
SERVER_PORT = 1234

def menu():
	while 1:
		#cls on windows, clear on linux
		os.system('clear')
		print('|--------------------------------------|')
		print('|-----------------MENU-----------------|')
		print('|--------------------------------------|')
		print('1 - Login')
		print('0 - exit')

		option = int(input('What do you want to do?\n-> '))

		while option < 0 or option > 1:
			option = int(input('Choose one of the operations above!\n-> '))

		#Login
		if option == 1:
			skt = createSocket()
			login(skt)
			skt.close()

		#Exit
		else:
			break

def usermenu(skt, username):
	flag = 1
	while flag:
		#os.system('clear')
		print('|---------User Menu---------|')
		print('1 - List Unread Messages') #
		print('2 - List Authorized users') #
		print('3 - Send Message') #
		print('4 - List Read Messages') #
		print('5 - Remove Messages') #
		print('6 - Change Password') #
		print('7 - Operator Privileges')
		print('0 - Logout') #

		option = int(input('What do you want to do?\n-> '))

		while option < 0 or option > 7:
			option = int(input('Choose one of the above!\n-> '))

		#Unread Messages
		if option == 1:
			listMail(username, 'UNREAD')
			flag = moreOps(username)
		#Authorized users
		elif option == 2:
			authorized()
			flag = moreOps(username)
		#Send Message
		elif option == 3:
			writeEmail(username)
			flag = moreOps(username)
		#Read Messages
		elif option == 4:
			listMail(username, 'READ')
			flag = moreOps(username)
		#Remove Messages
		elif option == 5:
			listAllMessages(username)
			flag = moreOps(username)
		#Change PW
		elif option == 6:
			changePW(username)
			flag = moreOps(username)
		#operator previleges
		elif option == 7:
			opPrevileges()
			flag = moreOps(username)
		#Exit
		else:
			logout(username)
			flag = 0

def moreOps(username):
	print('\n\n1 - Do something else')
	print('0 - Logout')
	option = int(input('-> '))
	while option < 0 or option > 1:
		option = int(input('-> '))
	if option == 0:
		logout(username)
	else:
		return 1

def login(skt):
	#os.system('clear')
	#change to a prettier solution
	print('|-----Login-----|')
	username = raw_input('Username: ')
	password = raw_input('Password: ')
	skt.send(('L;' + username + ';' + password).encode('utf-8'))
	status = skt.recv(5).decode('utf-8')
	if status == '1':
		os.system('clear')
		print('Sucessefully logged in!\n')
		usermenu(skt, username)
	elif status == '2':
		os.system('clear')
		print('Wrong Password!')
	else:
		os.system('clear')
		print('Wrong Username / User not registered / User Blocked')
		print('Please contact an admin.')

#1
def listMail(username, which):
	skt = createSocket()
	if which == 'UNREAD':
		skt.send(('M;' + username + '; ').encode('utf-8'))
	elif which == 'READ':
		skt.send(('R;' + username + '; ').encode('utf-8'))
	
	sender = []
	subject = []
	sen = ''
	sub = ''

	sen = skt.recv(1024).decode('utf-8')
	processInfo(sen, sender)

	skt.send(('1').encode('utf-8'))###

	sub = skt.recv(2048).decode('utf-8')
	processInfo(sub, subject)
 	skt.close()

 	if sender[0] == 'null' and subject[0] == 'null':
 		print('No ' + which + ' mail to be displayed.')
 		return
 	if sender[0] == 'nullnull' and subject[0] == 'nullnull':
 		print('No ' + which + ' mail to be displayed.')
 		return

	i = 1
	size = len(subject)
	print('#\tFROM:\tSUBJECT:')
	while i <= size:
		print('{}\t'.format(i) + sender[i-1] + '\t' + subject[i-1])
		i += 1
	print('\n\nWhich one would you like to read? (Choose with number, 0 to go back)')
	number = int(input('-> '))
	while number < 0 or number > size:
		number = int(input('-> '))
	if number == 0:
		return
	readMail(username, which, sender[number-1], subject[number-1])

def readMail(username, which, sender, subject):
	skt = createSocket()
	skt.send(('B; ; ').encode('utf-8')) #action
	#print(username + ' ' + which + ' ' + sender + ' ' + subject)
	skt.recv(5).decode('utf-8')

	skt.send((username + ',' + which + ',' + sender + ',' + subject).encode('utf-8')) #1
	body = skt.recv(4096).decode('utf-8')
	skt.close()

	#Print Mail
	print('From: ' + sender)
	print('Subject: ' + subject)
	print('\n')
	print(body)
	raw_input('\n\nPress "Enter" to leave')

def processInfo(string, output):
	i = 0
	size = len(string)
	aux = ''
	if size == 0:
		return

	while i < size:
		if string[i] != ',':
			aux += string[i]
		elif string[i] == ',':
			output.append(aux)
			aux = ''
		if i == size - 1:
			output.append(aux)

		i += 1

#2
def authorized():
	os.system('clear')
	print('|-----List of Authorized Users-----|')

	skt = createSocket()
	skt.send(('U; ; '))
	users = skt.recv(1024).decode('utf-8')
	print(users)

#3
def writeEmail(username):
	sendTo = ''
	subject = ''
	message = ''
	skt = createSocket()
	skt.send(('S;' + username + '; ').encode('utf-8'))

	#select users
	print('\nWho do you want to send this message to?')
	print('in case of multiple users, separate them with "," (comma). ex: "a,b,c,d"')
	sendTo = raw_input('-> ')

	#subject of the message
	print('\nWhat is the subject of this message?')
	subject = raw_input('-> ')

	#message
	print('\nMessage body:')
	message = raw_input('-> ')

	#send users
	skt.send((sendTo).encode('utf-8'))

	status = skt.recv(5).decode('utf-8')
	if status == '1':
		skt.send((subject).encode('utf-8'))
		status = skt.recv(5).decode('utf-8')
		if status == '1':
			skt.send((message).encode('utf-8'))
			status = skt.recv(5).decode('utf-8')
			if status == '1':
				print('Mail Successfully sent!')
			else:
				print('Error Sending message')
		else:
			print('Error sending subject')
	else:
		print('Error sending users')
	skt.close()

#4
#made on #1

#5
def listAllMessages(username):
	sender = ''
	subject = ''
	senders = []
	senders1 = []
	subjects = []
	subjects1 = []

	skt = createSocket()
	skt.send(('A;' + username + '; '))

	#UNREAD
	sender = skt.recv(1024).decode('utf-8')
	processInfo(sender, senders)

	skt.send(('1').encode('utf-8'))

	subject = skt.recv(2048).decode('utf-8')
	processInfo(subject, subjects)

	sizeU = len(subjects)
	#just to intercalate send with recv
	#skt.send(('').encode('utf-8'))

	#READ
	sender = skt.recv(1024).decode('utf-8')
	processInfo(sender, senders1)
	
	skt.send(('1').encode('utf-8'))

	subject = skt.recv(2048).decode('utf-8')
	processInfo(subject, subjects1)
	skt.close()

	subjects += subjects1
	senders += senders1

	size = len(subjects)
	i = 1
	flag = 0

	print('#\tFROM:\tSUBJECT:')
	while i <= size:
		if senders[i-1] == 'null' and subjects[i-1] == 'null':
			i+=1
			flag += 1
			continue

		print('{}\t'.format(i-flag) + senders[i-1] + '\t' + subjects[i-1])
		i += 1

	print('Which mail do you want to delete? (Press 0 to go back)')
	number = int(input('-> '))
	while number < 0 or number > size:
		number = int(input('-> '))
	if number == 0:
		return

	if number + flag > 0 and number + flag <= sizeU:
		deleteMail(username, 'UNREAD', senders[number+flag-1], subjects[number+flag-1])

	elif number + flag > sizeU and number + flag <= size:
		deleteMail(username, 'READ', senders[number+flag-1], subjects[number+flag-1])

def deleteMail(username, which, sender, subject):
	skt = createSocket()
	skt.send('D; ; ')
	skt.recv(5).decode('utf-8')

	skt.send((username + ',' + which + ',' + sender + ',' + subject).encode('utf-8'))
	status = skt.recv(5).decode('utf-8')
	if status == '1':
		print('Mail Deleted!')

#6
def changePW(username):
	#os.system('clear')
	print('|---------Change PassWord---------|')
	new_password = raw_input('New Password: ')

	skt = createSocket()
	skt.send(('P;' + username + ';' + new_password).encode('utf-8'))
	status = skt.recv(5).decode('utf-8')
	skt.close()
	if status == '1':
		os.system('clear')
		print('Password Successfully Changed!')
	else:
		print('Error Changing Password!')

#7
def opPrevileges():
	print('|------Operator Priveleges------|')
	print('Please insert Operator Password:')
	password = raw_input('-> ')

	skt = createSocket()
	skt.send(('E; ;' + password).encode('utf-8'))

	status = skt.recv(5).decode('utf-8')
	skt.close()
	if status == '1':
		opMenu()
	else:
		print('Wrong Password.')

def opMenu():
	print('|-----Operator Menu-----|')
	print('1 - Ban User')
	print('2 - Pardon User')
	print('3 - Register New User')
	print('0 - Go back')

	print('\nWhat do you want to do?')
	option = int(input('-> '))
	while option < 0 or option > 3:
		option = int(input('-> '))

	if option == 1:
		bpUser('ban')

	elif option == 2:
		bpUser('pardon')

	elif option == 3:
		register()

def register():
	username = ''
	password = ''
	skt = createSocket()

	print('Choose your Username:')
	username = raw_input('-> ')

	skt.send(('N;' + username + '; '))
	status = skt.recv(5).decode('utf-8')

	while 1:
		if len(username) < 9 and status == '1':
			break
		username = raw_input('-> ')
		skt.send((username).encode('utf-8'))
		status = skt.recv(5).decode('utf-8')

	print('Choose your Password:')
	password = raw_input('-> ')

	skt.send((password).encode('utf-8'))

	status = skt.recv(5).decode('utf-8')
	if status == '1':
		print('New User created, now you can login!')

def bpUser(op):
	user = ''
	users = []
	skt = createSocket()
	if op == 'ban':
		skt.send(('U; ; ').encode('utf-8'))
		print('List of authorized users:')
	elif op == 'pardon':
		skt.send(('T; ; '))
		print('List of banned users:')

	user = skt.recv(1024).decode('utf-8')

	if user == 'null':
		print('There are no users to be displayed. Going Back to User Menu!')
		raw_input('Press "ENTER" to leave')
		skt.close()
		return
	skt.close()
	processInfo(user, users)

	size = len(users)
	i = 1

	if size != 0:
		while i <= size:
			print('{}\t'.format(i) + users[i-1])
			i += 1


	print('which user should be banned/pardoned? (0 to go back)')
	number = int(input('-> '))
	while number < 0 or number > size:
		number = int(input('-> '))

	if number == 0:
		return

	skt = createSocket()
	
	if op == 'ban':
		skt.send(('G;' + users[number-1] + '; ').encode('utf-8'))
		status = skt.recv(5).decode('utf-8')
		if status == '1':
			print('User ' + users[number-1] + ' successfully banned')

	elif op == 'pardon':
		skt.send(('H;' + users[number-1] + '; ').encode('utf-8'))
		status = skt.recv(5).decode('utf-8')
		if status == '1':
			print('User ' + users[number-1] + ' successfully pardoned')
	skt.close()

#8
def logout(username):
	skt = createSocket()
	skt.send(('O;' + username + '; ').encode('utf-8'))
	status = skt.recv(5).decode('utf-8')
	skt.close()
	if status == '1':
		print('User logged out Successfully!')
	else:
		print('Error logging out!')

def createSocket():
	s = socket(AF_INET, SOCK_STREAM)
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	s.connect((SERVER_NAME, SERVER_PORT))
	#print('Socket created!\n')
	return s

def signal_handler(signal, frame):
	print(' pressed, exiting now')
	sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal_handler)
	menu()
