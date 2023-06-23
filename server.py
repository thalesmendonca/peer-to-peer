import socket
import sys
import threading
import ast

client_table = {}


class Server:
    def __init__(self):
        self.encode_format = "utf-8"
        self.server_ip = sys.argv[1]
        self.server_port = int(sys.argv[2])
        self.connections = []
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.server_ip, self.server_port))
            self.server_socket.listen(1)

            print("Servidor pronto para receber conexões...")
        except:
            print("Falha ao iniciar servidor...")
            sys.exit(1)

    def broadcast(self, message):
        for connection in self.connections:
            connection.send(message.encode(self.encode_format))

    def handle_client(self, connection, address):
        while True:
            try:
                data = connection.recv(1024).decode(self.encode_format)
                data = ast.literal_eval(data)
                if not data:
                    break

                if data[0] == "disconnect":
                    client_table.pop(address, None)
                    self.connections.remove(connection)
                    connection.send(str(["desconectado"]).encode(self.encode_format))
                    connection.close()
                    print(f"Cliente desconectado: {address[0]}:{address[1]}")
                    self.broadcast(str(["lista", client_table]))
                    break
                elif data[0] == "lista":
                    connection.send(str(["lista", client_table]).encode(self.encode_format))
                elif data[0] == "peer":
                    client_to_be_server = data[1]
                    client_to_be_client = connection.getpeername()
                    port_to_receive = data[2]
                    file = data[3]
                    for connection in self.connections:
                        if connection.getpeername() == client_to_be_server:
                            client_to_be_server = connection
                    client_to_be_server.send(str(["peer", client_to_be_client, port_to_receive, file])
                                             .encode(self.encode_format))

            except Exception as err:
                print(f"Erro ao lidar com o usuário:{address}")
                break

    def run_server(self):
        while True:
            connection, address = self.server_socket.accept()
            data = connection.recv(1024).decode(self.encode_format)
            print(f"Nova conexão: {address[0]}:{address[1]}")

            if address in client_table:
                print(f"Cliente já cadastrado: {address[0]}:{address[1]}")
                connection.close()
                continue

            self.connections.append(connection)
            client_table[address] = data.split(",")
            self.broadcast(str(["lista", client_table]))
            threading.Thread(target=self.handle_client, args=(connection, address), daemon=True).start()
            print(f"Tabela de clientes atualizada: {client_table}")

    def main(self):
        self.run_server()


Server().main()