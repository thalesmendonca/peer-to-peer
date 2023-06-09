import socket
import sys
import threading
import ast

client_table = {}


class Client:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encode_format = "utf-8"
        self.server_ip = sys.argv[1]
        self.server_port = int(sys.argv[2])
        self.files_list = sys.argv[3:] if len(sys.argv) > 2 else []
        self.listen_thread = threading.Thread

    def listen_to_server(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode(self.encode_format)
                data = ast.literal_eval(data)
                if not data:
                    break

                print(f"Mensagem do servidor: {data}")
                if data[0] == "lista":
                    client_table = data[1]
                    print(f"Nova tabela de clientes: {client_table}")
            except:
                print("Erro ao lidar com a listen to server")
                break

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            self.listen_thread(target=self.listen_to_server, daemon=True).start()
            print("Conectado ao servidor...")

        except:
            raise Exception("Erro ao conectar-se ao servidor...")

    def send_packages(self, package):
        try:
            encoded_package = package.encode(self.encode_format)
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
