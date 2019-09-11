#server.py

import socket
import sys

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




if __name__ == '__main__' :
	port = get_port(sys.argv)
	print(port)
	ftp_socket = initialize_port(port)
	listen_from_client(ftp_socket)
