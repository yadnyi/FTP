'''
functions to create :
	get
	put
	ls
	send_file
	receive_file
	sucess_message
	error_message

'''
import socket
#from commands import getstatusoutput
import subprocess
import os
import sys
import constants as const
#from commands import getstatusoutput


class ClientInterface():
	"""Server side operations of local FTP server"""
	curr_dir = "/SERVER_DATA"


	def __init__(self, ftp_client, ftp_socket, address):

		self.ftp_client = ftp_client
		self.ftp_socket = ftp_socket
		self.address = address
		self.main_folder = os.getcwd()

	def ls(self) :
		#it will show the files from current directory
		#TO DO -> send command to os get responce
		result = ""
		result = result.encode()

		try :
			os.chdir(self.main_folder + self.curr_dir)
			result = subprocess.Popen("ls -l " , shell=True, stdout=subprocess.PIPE).stdout.read()
			#print(result.decode())

			print("SUCESS in ls")
		except :
			print("Unable to perform ls")

		#result = getstatusoutput('ls - l ./SERVER_DATA')[1]
		#result = result.encode()
		self.ftp_client.send(result)

	def cd(self, client_request) :
		print(client_request)
		p = client_request.split(" ")[1]

		try :
			if self.curr_dir == "/SERVER_DATA" and p == ".." :
				result = "Cannot change Current directory"
			else :
				os.chdir(self.main_folder + self.curr_dir)
				#print(self.main_folder + self.curr_dir)
				os.chdir(p)
				dir_new = os.getcwd()
				dir_new = dir_new.replace(self.main_folder, '')
				self.curr_dir = dir_new
				#print(self.main_folder)
				#print(dir_new)
				#print(self.curr_dir)
				result = "directory Changed to " + self.curr_dir
		except :
			print( sys.exc_info()[0])
			result = "Cannot change Current directory"
		#print(p)
		#result = "YES"

		result = result.encode()
		self.ftp_client.send(result)


	def mkdir(self, client_request) :
		#print(client_request)
		p = client_request.split(" ")[1]
		directory =self.main_folder + self.curr_dir +"/" + p
		print(directory)
		result = " "
		try :
			if not os.path.exists(directory):
				os.mkdir(directory)
				result = "New directory created : "+ p + " "
		except :
				result = "Failed to create directory"
		#result = "YES"
		result = result.encode()
		self.ftp_client.send(result)

	def cwd(self) :
		responce = self.curr_dir
		responce = responce.encode()
		self.ftp_client.send(responce)


	def get(self, client_request) :
		#get will file to the client
		#TO DO ->
		#check for file exist
		#open file
		#cut file into different parts add header filename and data

		filename = client_request.split(" ")[1]
		filepath = self.main_folder + self.curr_dir+"/" + filename

		exists = os.path.isfile(filepath)
		print(filepath)
		if filename and exists :
			print("Preparing to send file")
			self.send_file(filename, filepath)
			print("File Sent Successfully")
		else :
			err = -1
			err = str(err).encode()
			self.ftp_client.send(err)
			print("Failed to send file")


	def send_file (self,filename, filepath) :

		with open(filepath, 'rb') as file_obj :
			transfer_port = ''


			data = file_obj.read()

			#now we need a port for transfer socket
			try :

				transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				transfer_socket.bind(('', 0))
				transfer_socket.listen(1)
				transfer_port = transfer_socket.getsockname()[1]
			except socket.error as e :
				print(e)
				return

			#now we will send the transfer port details to client
			try :
				print("Sending port to client")
				transfer_port = str(transfer_port).encode()
				self.ftp_client.send(transfer_port)
				ack = self.ftp_client.recv(const.FILEHEADER_SIZE)
				while not ack :
					print("sending port again")
					#transfer_port = str(transfer_port).encode()
					self.ftp_client.send(transfer_port)
					ack = self.ftp_client.recv(const.FILEHEADER_SIZE)
				print("Port address SENT")
				print(ack.decode())

			except socket.error as e :
				print(e)
				return

			while True :
				print("listening on ", transfer_port)
				ftp_transfer_client , address = transfer_socket.accept()
				print("accepted Connection from " , address)

				if ftp_transfer_client :
					byte_sent = 0 #this will count number of bytes sent

					filename_header = self.buffer_header(filename, const.FILENAME_SIZE)

					filesize_header = self.buffer_header(str(len(data)) , const.FILEHEADER_SIZE)

					filetotaldata = filename_header.encode() + filesize_header.encode() + data

					#filetotaldata = filetotaldata.encode()
					while len(filetotaldata) > byte_sent :
						print(byte_sent)
						try :
							byte_sent += ftp_transfer_client.send(filetotaldata[byte_sent :])

						except socket.error as e :
							print(e)
							return

					return


	def buffer_header(self, header, size = 10) :
		header = str(header)

		while len(header) < size :
			header = "0" + header

		return header

	def put(self, args) :
		self.receive_file()



	def receive_file(self) :

		transfer_port = ''
		transfer_port = self.ftp_client.recv(const.BUFFER_SIZE)
		#transfer_port = self.receive_bytes(self.ftp_socket, const.FILEHEADER_SIZE)
		if not transfer_port :
			print("Transfer port not received")
		if transfer_port.decode() == "-1" :
			print("File Not Found : ")
			return
		ack = "YES"
		ack = ack.encode()
		self.ftp_client.send(ack)
		print(transfer_port)


		if transfer_port :
			transfer_port = int(transfer_port)
			#establish a connection between host(server) and client(this)
			ftp_transfer_socket = self.create_socket(self.address[0], transfer_port)

			if ftp_transfer_socket :

				filename_header = self.receive_bytes(ftp_transfer_socket, const.FILENAME_SIZE)
				filename = filename_header.decode()
				filename = filename.translate({ord('0') : ''})

				filesize_header = self.receive_bytes(ftp_transfer_socket, const.FILEHEADER_SIZE)
				file_size = int(filesize_header.decode())

				print("Receiving ", file_size, " Bytes of data")

				file_data = self.receive_bytes(ftp_transfer_socket, file_size)
				filepath = self.main_folder + self.curr_dir + "/" + filename

				transferfile = open(filepath, "wb")
				transferfile.write(file_data)
				transferfile.close()

		else :
			print("no transfer port")


	def receive_bytes(self, ftp_socket, size = None):
		#receives size number of bytes from server

		if ftp_socket and size :
			temp_buffer = ""
			received= b''

			#read input
			while len(temp_buffer) < size :
				temp_buffer = ftp_socket.recv(size)

				if not temp_buffer :
					print("No Bytes Received from server")
				#temp_buffer = temp_buffer.decode()
				print(type(temp_buffer))
				received += temp_buffer[0:]

			return received

		else :
			print("Error : Size or socket not defined")





	def create_socket(self, ip_address, port) :
		try:
			create_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			create_socket.connect((ip_address, port))
			print("Connection to server has been established on port ", port)
		except socket.error as e:
			print("Socket error : ", e )
			return
		return create_socket

	def quit(self):
		S = "Thanks for connection. Bye."
		S = S.encode()
		self.ftp_client.send(S)

		#self.ftp_client.send("Thanks for connection. Bye.")
		self.ftp_client.close()
