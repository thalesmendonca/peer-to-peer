import socket
import sys

client_table = {}


class Server():
    def __init__(self):
        self.encode_format = "utf-8"
        self.server_ip = sys.argv[1]
        self.server_port = int(sys.argv[2])
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.server_ip, self.server_port))
            self.server_socket.listen(1)

            print("Servidor pronto para receber conexões...")
        except:
            print("Falha ao iniciar servidor...")
            sys.exit(1)

    def handle_client(self, connection, address):
        print(f"Nova conexão: {address[0]}:{address[1]}")

        while True:
            try:
                data = connection.recv(1024).decode()
                if not data:
                    break

                if data == "disconnect":
                    client_table.pop(address, None)
                    connection.close()
                    print(f"Cliente desconectado: {address[0]}:{address[1]}")
                    break

                if address in client_table:
                    print(f"Cliente já cadastrado: {address[0]}:{address[1]}")
                else:
                    client_table[address] = data.split(",")
                    print(f"Tabela de clientes atualizada: {client_table}")
            except:
                continue

    def run_server(self):
        while True:
            connection, address = self.server_socket.accept()
            self.handle_client(connection, address)

    def main(self):
        self.run_server()


Server().main()
