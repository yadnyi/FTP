import socket
import sys
from client_interface import ftp_client


def getserveraddress(user_arg) :

	len_arg = len(user_arg)

	if len_arg == 3 :
		try :
			ip = user_arg[1]
			port = int(user_arg[2])
			return ip, port
		except ValueError as e :
			sys.exit("Arguments ERROR " + e)

	else :
		sys.exit("Arguments ERROR : HELP -> client.py ip_address port")


def get_ftp_socket(ip, port) :
	try :
		ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ftp_socket.connect((ip , port))
		print("Successfully Connected to ", ip ,":", port)
	except socket.error as e :
		print("Socket Error :" , e)
		sys.exit()

	return ftp_socket


def handle_client_request(ftp_socket, ip, port) :
	#create a ftp_client object
	ftp_client_object = ftp_client()
	ftp_client_object.store_details(ftp_socket, ip , port)
	ftp_client_object.cmdloop()


if __name__ == '__main__' :
	ip, port = getserveraddress(sys.argv) #inputs from user
	#print(ip)
	#print(port)
	ftp_socket = get_ftp_socket(ip, port)
	handle_client_request(ftp_socket, ip, port)
