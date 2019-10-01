#server.py

import socket
import sys
import constants as const
from server_host_interface import ClientInterface
#TODO
'''
get port from user (with checking input)
initialize port
accept connection
listen for inputs from client
send responce
'''

def get_port(client_arguments) :
	#check for arguments is correct or not
	len_arg = len(client_arguments)

	if len_arg == 2 :
		try :
			arg_port = int(client_arguments[1])
		except ValueError as e :
			sys.exit(e)
		return arg_port

	else :
		sys.exit("Argument Exception : Socket parameter is missing or More arguments are given")



def initialize_port(port_id) :
	#initialize port
	try :
		ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#AF_INET refers to the address family ipv4.
			#The SOCK_STREAM means connection oriented TCP protocol.
		ftp_socket.bind(('', port_id)) #binds the ip and port to socket
		ftp_socket.listen(1)
		print("Server is initialized , Listening to port ", port)
		return ftp_socket
	except socket.error as e :
		print("Socket Error ", e)
		sys.exit()
	except IOError as e :
		print("IOError :" , e)
		sys.exit()

def listen_from_client(ftp_socket) :
	'''listen for client connection'''
	while True :
		ftp_client, address = ftp_socket.accept()
		print("Accepted connection From ", address)
		#Now if we comsider multiple clients we  will create a client class
		shi = ClientInterface(ftp_client, ftp_socket, address)

		while True :
			#write code about the I/O to client ans server
			try :
				client_request = ftp_client.recv(const.BUFFER_SIZE)
				client_request = client_request.decode()

				if client_request == '' :
					#print("Aashish")
					continue
				print(	address , " : ", client_request)

				#print(type(client_request))
				client_command = client_request.split(" ")[0]
				#print(client_command)
			except socket.error as e :
				print("Client Disconnected or : ", e)
				break

			#check for correct commands
			if client_command in const.ACCEPTED_COMMANDS :
				if client_command == const.LS :
					#call LS function
					shi.ls()
				'''if client_command == const.GET :
					#call GET function
				if client_command == const.PUT :
					#call PUT function
					'''
				if client_command == const.CD :
					#call CD function
					#print("Aashish")
					shi.cd(client_request)

				if client_command == const.MKDIR :
					#call MKDIR function'''
					shi.mkdir(client_request)
				if client_command == const.CWD :

					shi.cwd()

				if client_command == const.GET :
					shi.get(client_request)

				if client_command == const.PUT :
					shi.put(client_request)







if __name__ == '__main__' :
	port = get_port(sys.argv)
	print(port)
	ftp_socket = initialize_port(port)
	listen_from_client(ftp_socket)
