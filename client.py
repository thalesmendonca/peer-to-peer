import socket
import sys
import threading
import ast
import re


class Client:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encode_format = "utf-8"
        self.server_ip = sys.argv[1]
        self.server_port = int(sys.argv[2])
        self.files_list = sys.argv[3:] if len(sys.argv) > 2 else []
        self.listen_thread = threading.Thread
        self.client_table = {}
        self.connections = {}

    def listen_to_server(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode(self.encode_format)
                data = ast.literal_eval(data)
                if not data or data[0] == "desconectado":
                    break

                if data[0] == "lista":
                    self.client_table = data[1]
                    print(f"Nova tabela de clientes: {self.client_table}")
                elif data[0] == "peer":
                    print("Tem gente querendo conexão com você")

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
            encoded_package = str(package).encode(self.encode_format)
            self.client_socket.send(encoded_package)
        except:
            raise Exception("Erro ao enviar mensagem ao servidor.")

    def disconnect(self):
        self.client_socket.send(str(["disconnect"]).encode(self.encode_format))
    
    def listen_to_new_peer_connections(self):
        print("Ouvindo por conexões de peers")

        #Lidar com novas tentativas de conexão a esse cliente, análogo a lógica do servidor
        while True:
            connection, address = self.server_socket.accept()
            data = connection.recv(1024).decode(self.encode_format)
            print(f"Nova conexão: {address[0]}:{address[1]}")

            self.connections.append(connection)
            threading.Thread(target=self.handle_new_peer, args=(connection, address), daemon=True).start()
    
    def handle_new_peer(self, connection, address):
        while True:
            try:
                data = connection.recv(1024).decode(self.encode_format)
                data = ast.literal_eval(data)
                if not data:
                    break

                if data[0] == "disconnect":
                    self.connections.remove(connection)
                    connection.send(str(["desconectado"]).encode(self.encode_format))
                    connection.close()
                    break
                elif data[0] == "arquivo":
                    #Mandar minha lista de arquivos para ser escolhido pelo peer
                    connection.send(str(["lista", self.files_list]).encode(self.encode_format))
                elif re.search("[0-9]", data[0]) != None:
                    chosenFile = data[0]
                    if chosenFile > 0 and chosenFile < len(self.files_list):
                        pass
                        #Aqui fazer lógica para enviar arquivo pedido

            except Exception as err:
                print(f"Erro ao lidar com o peer")
                break

    def main(self):
        try:
            #Thread para conexão com servidor:
            self.connect_to_server()
            self.send_packages(",".join(self.files_list))

            #Iniciar thread para ouvir por novas conexões de peer
            threading.Thread(target=self.listen_to_new_peer_connections, args=(), daemon=True).start()

            while True:
                choice = input(
                    "\nO que deseja fazer?\n"
                    "1 - desconectar\n"
                    "2 - solicitar lista\n"
                    "3 - solicitar arquivo a um cliente\n"
                )

                if choice == "1":
                    self.disconnect()
                    break
                elif choice == "2":
                    self.send_packages(["lista"])
                elif choice == "3":
                    print("\nDeseja solicitar um arquivo a qual cliente?\n")
                    clients_keys = list(self.client_table.keys())
                    for i, cliente in enumerate(self.client_table.keys()):
                        print(f"{i} - {cliente}")

                    client_to_connect = int(input())
                    if client_to_connect < 0 or client_to_connect >= len(clients_keys):
                        print("Não existe esse cliente na lista.\nIgnorando solicitação...")
                    else:
                        
                        client_to_connect = {
                            clients_keys[client_to_connect]:
                                self.client_table[clients_keys[client_to_connect]]
                        }
                        self.client_socket.connect((clients_keys[0][0], clients_keys[0][1]))
                        # print("\nQual arquivo deseja receber?\n")
                        # client_keys = list(client_to_connect.keys())
                        # client_files = client_to_connect[client_keys[0]]
                        # for i, file in enumerate(client_files):
                        #     print(f"{i} - {file}")
                        # file_to_receive = int(input())
                        # if file_to_receive < 0 or file_to_receive >= len(client_files):
                        #     print("Não existe esse arquivo na lista.\nIgnorando solicitação...")
                        # else:
                        #     client_addr = client_keys[0]
                        #     file_to_receive = client_files[file_to_receive]
                        #     port_to_receive = input("\nEspecifique a porta que deseja receber o arquivo.\n")
                        #     self.send_packages(["peer", client_addr, port_to_receive, file_to_receive])
            
            

        except Exception as err:
            print(f"A aplicação do cliente foi interrompida: {err}")


Client().main()
