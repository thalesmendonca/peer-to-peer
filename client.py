import socket
import sys


class Client:

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
            raise Exception("Erro ao conectar-se ao servidor...")

    def receive_packages(self):
        try:
            package = self.client_socket.recv(1024).decode(self.encode_format)
            print(f"Mensagem do servidor: {package}")

        except:
            raise Exception("Erro ao receber mensagem...")

    def send_packages(self, package):
        try:
            encoded_package = package.encode(self.encode_format)
            if package == "lista":
                self.client_socket.send(encoded_package)
                self.receive_packages()
            else:
                self.client_socket.send(encoded_package)
        except:
            raise Exception("Erro ao enviar mensagem ao servidor.")

    def disconnect(self):
        self.client_socket.send("disconnect".encode(self.encode_format))
        self.client_socket.close()

    def main(self):
        try:
            self.connect_to_server()
            self.send_packages(",".join(self.files_list))
            while True:
                message = input()
                if message == "disconnect":
                    self.disconnect()
                    break
                self.send_packages(message)
        except Exception as err:
            print(f"A aplicação do cliente foi interrompida: {err}")


Client().main()
