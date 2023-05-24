import socket
import sys


class Client():

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encode_format = "utf-8"
        self.server_ip = sys.argv[1]
        self.server_port = int(sys.argv[2])
        self.files_list = sys.argv[3:] if len(sys.argv) > 2 else []

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            print("Conectado ao servidor...")

        except:
            print("Erro ao conectar-se ao servidor...")

    def receive_packages(self):
        try:
            package = self.client_socket.recv(1024).decode(self.encode_format)
            print(f"Mensagem do servidor: {package}")

        except:
            print("Erro ao receber mensagem...")

    def send_packages(self, package):
        self.client_socket.send(package)

    def disconnect(self):
        self.client_socket.send("disconnect".encode())
        self.client_socket.close()

    def main(self):
        self.connect_to_server()
        encoded_files_list = ",".join(self.files_list).encode(self.encode_format)
        self.send_packages(encoded_files_list)

        #self.disconnect()


Client().main()
