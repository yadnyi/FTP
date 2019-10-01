from cmd import Cmd
from sys import exit
from os import system
import constants as const
import socket

class ftp_client(Cmd):
	"""docstring for ftp_client"""
	host_ip = ''
	host_port = 0
	ftp_socket = ''

	prompt = "ftp> "
	download_folder = "./CLIENT_DATA"

	def store_details(self, ftp_soc, ip_address, port = 0) :

		self.ftp_socket = ftp_soc
		self.host_ip = ip_address
		self.host_port = port

	def do_ls(self, args) :
		response = self.run_command(const.LS)

		print(response)

	def do_cd(self, args) :
		print(args)
		print(type(args))
		response = self.run_command(const.CD + " " + args)
		print(response)

	def do_mkdir(self, args):
		response = self.run_command(const.MKDIR + " " + args)
		print(response)

	def do_cwd(self, args) :
		response = self.run_command(const.CWD)
		print(response)

	def do_get(self, args) :
		#send command to server
		command = const.GET + " " + args
		command = command.encode()
		self.ftp_socket.send(command)
		#wait for receiving file
		self.receive_file()

	def do_put(self, args) :
		command = const.PUT + " " + args
		command = command.encode()
		self.ftp_socket.send(command)
		filename = args.split("/")[-1]
		self.send_file(filename, args)

	def do_mget(self, args) :
		#command = const.MGET + " " + args
		#command = command.encode()
		#self.ftp_socket.send(command)
		self.receive_multiple_files(args)

	def do_mput(self, args) :
		self.send_multiple_files(args)

	def do_clear(self, args):
		system("clear")
		return

	def do_quit(self, args):
		response = self.run_command(const.QUIT)
		self.ftp_socket.close()
		exit(response)

	def run_command(self, command) :
		command = command.encode()
		self.ftp_socket.send(command)
		res = self.ftp_socket.recv(const.BUFFER_SIZE)
		res= res.decode()
		return res

	def receive_file(self) :

		transfer_port = ''
		transfer_port = self.ftp_socket.recv(const.BUFFER_SIZE)
		#transfer_port = self.receive_bytes(self.ftp_socket, const.FILEHEADER_SIZE)
		if not transfer_port :
			print("Transfer port not received")
		if transfer_port.decode() == "-1" :
			print("File Not Found : ")
			return
		ack = "YES"
		ack = ack.encode()
		self.ftp_socket.send(ack)
		print(transfer_port)


		if transfer_port :
			transfer_port = int(transfer_port)
			#establish a connection between host(server) and client(this)
			ftp_transfer_socket = self.create_socket(self.host_ip, transfer_port)

			if ftp_transfer_socket :

				filename_header = self.receive_bytes(ftp_transfer_socket, const.FILENAME_SIZE)
				filename = filename_header.decode()
				filename = filename.translate({ord('0') : ''})

				filesize_header = self.receive_bytes(ftp_transfer_socket, const.FILEHEADER_SIZE)
				file_size = int(filesize_header.decode())

				print("Receiving ", file_size, " Bytes of data")

				file_data = self.receive_bytes(ftp_transfer_socket, file_size)
				filepath = self.download_folder + "/" + filename

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
				self.ftp_socket.send(transfer_port)
				ack = self.ftp_socket.recv(const.FILEHEADER_SIZE)
				while not ack :
					print("sending port again")
					#transfer_port = str(transfer_port).encode()
					self.ftp_socket.send(transfer_port)
					ack = self.ftp_socket.recv(const.FILEHEADER_SIZE)
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

	def receive_multiple_files(self, args) :
		if len(args) < 1 :
			print("help")

		filenames = args.split(' ')
		if len(filenames) < 1 :
			print("help")
			return

		for i in range(len(filenames)) :
			command = const.GET + " " + filenames[i]
			command = command.encode()
			self.ftp_socket.send(command)
			#wait for receiving file
			self.receive_file()

	def send_multiple_files(self, args) :
		if len(args) < 1 :
			print("help")
		filenames = args.split(' ')
		if len(filenames) < 1 :
			print(help)

		for i in range(len(filenames)) :
			file = filenames[i]
			command = const.PUT + " " + file
			command = command.encode()
			self.ftp_socket.send(command)
			filename = file.split("/")[-1]
			self.send_file(filename, file)


    ######## Describesthe commands ##########
	def help_get(self):
		self.print_help_method("get", "Download file from host", "get <file>")
		return

	def help_put(self):
		self.print_help_method("put", "Upload file from host", "put <file>")
		return

	def help_ls(self):
		self.print_help_method("ls", "List files on the host", "ls")

	def help_clear(self):
		self.print_help_method("clear", "Clear the terminal", "clear")

	def help_quit(self):
		self.print_help_method("quit", "Quits the interface", "quit")


	def print_help_method(self, command, description, example):
		msg = "\nCommand: %s" \
              "\n========================================" \
              "\n  -Description: %s" \
              "\n  -Example: %s" % (command, description, example)
		print (msg)
