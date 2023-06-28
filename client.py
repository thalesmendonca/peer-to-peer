import os.path
import socket
import sys
import threading
import ast
# import pyaudio
# from pydub import AudioSegment
import select

CHUNK_SIZE = 1024
SAMPLE_WIDTH = 2
CHANNELS = 2
SAMPLE_RATE = 44100


class Client:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Socket utilizada para conectar com peer
        self.file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encode_format = "utf-8"
        #IP e portas para conectar com servidor
        self.server_ip = sys.argv[1]
        self.server_port = int(sys.argv[2])
        #IP e portas utilizadas para ouvir as conexões com os peers
        self.peer_connection_ip = sys.argv[3]
        self.peer_connection_port = int(sys.argv[4])
        self.files_list = sys.argv[5:] if len(sys.argv) > 4 else []
        self.listen_thread = threading.Thread
        self.client_table = {}
        # self.audio = pyaudio.PyAudio()

        try:
            #Setando para receber conexões de peers
            self.peer_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Configuração para modo não bloqueante
            self.peer_connection_socket.setblocking(0)
            self.peer_connection_socket.bind((self.peer_connection_ip, self.peer_connection_port))
            self.peer_connection_socket.listen(1)

            print("Configurado para receber conexões de peers")
        except:
            print("Falha ao iniciar listening socket...")
            sys.exit(1)

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
                    client_socket_to_send_file = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket_to_send_file.connect((data[1], int(data[2])))
                    self.send_file(data[3], client_socket_to_send_file)

            except Exception as err:
                print(f"Erro ao lidar com a listen to server: {err}")
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

    def open_server_to_receive_file(self, port):

        stream = self.audio.open(format=self.audio.get_format_from_width(SAMPLE_WIDTH),
                                 channels=CHANNELS,
                                 rate=SAMPLE_RATE,
                                 output=True)
        client_socket_to_receive_file = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket_to_receive_file.bind((self.client_socket.getsockname()[0], int(port)))
        client_socket_to_receive_file.listen(1)

        remetente, address = client_socket_to_receive_file.accept()
        try:
            while True:
                data = remetente.recv(CHUNK_SIZE)
                if not data:
                    break

                stream.write(data)
        except Exception as err:
            print(f"Erro ao lidar com recebimento de arquivo: {str(err)}")

        finally:
            remetente.close()
            stream.stop_stream()
            stream.close()

    def send_file(self, filename, connection):
        try:
            pass
            # size = os.path.getsize(filename)
            # print(f"Tamanho total do arquivo: {size}")
            # times = 1
            # extension = filename.rsplit(".", 1)[-1]
            # audio_infos = AudioSegment.from_file(filename, format=extension)
            # raw_data = audio_infos.raw_data
            # for i in range(0, len(raw_data), CHUNK_SIZE):
            #     chunk = raw_data[i:i + CHUNK_SIZE]
            #     connection.send(chunk)
            #     print("{:.2f}% enviado".format((CHUNK_SIZE * times * 100) / size))
            #     times = times + 1
        except Exception as err:
            print(f"Erro ao enviar arquivo: {err}")
        finally:
            connection.close()
    
    #Função para lidar com conexão de novos peers
    def handle_peer(self, connection, address):
        print("Conectado com " + str(address))
        pass



    def main(self):
        try:
            self.connect_to_server()
            self.send_packages(str(self.peer_connection_port) + "," + ",".join(self.files_list))
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
                    clients_keys = list(self.client_table.keys())
                    print(f"{0} - nenhum")
                    for i, cliente in enumerate(self.client_table.keys()):
                        if cliente == self.client_socket.getsockname(): continue
                        print(f"{i+1} - {cliente}")
                    
                    peer_to_connect = int(input("Qual peer você deseja se conectar? ")) - 1

                    if peer_to_connect < 0 or peer_to_connect >= (len(clients_keys)):
                        print("Não existe esse cliente na lista.\nIgnorando solicitação...")
                    else:
                        peer_addr = clients_keys[peer_to_connect]
                        chosen_user = self.client_table[peer_addr]
                        print("Conectando com " + str(peer_to_connect) + "...")
                        peer_ip = peer_addr[0]
                        peer_port = int(chosen_user[0])

                        #Criar nova socket para se conectar ao peer
                        self.file_socket.connect((peer_ip, peer_port))

                        #Pedir e receber arquivo


                        

                        
                        
                        

                elif choice == "0":
                    print("\nDeseja solicitar um arquivo a qual cliente?\n")
                    clients_keys = list(self.client_table.keys())
                    for i, cliente in enumerate(self.client_table.keys()):
                        if cliente == self.client_socket.getsockname(): continue
                        print(f"{i} - {cliente}")

                    client_to_connect = int(input())
                    if client_to_connect < 0 or client_to_connect >= (len(clients_keys)-1):
                        print("Não existe esse cliente na lista.\nIgnorando solicitação...")
                    else:
                        client_to_connect = {
                            clients_keys[client_to_connect]:
                                self.client_table[clients_keys[client_to_connect]]
                        }
                        print("\nQual arquivo deseja receber?\n")
                        client_keys = list(client_to_connect.keys())
                        client_files = client_to_connect[client_keys[0]]
                        for i, file in enumerate(client_files):
                            print(f"{i} - {file}")
                        file_to_receive = int(input())
                        if file_to_receive < 0 or file_to_receive >= len(client_files):
                            print("Não existe esse arquivo na lista.\nIgnorando solicitação...")
                        else:
                            client_addr = client_keys[0]
                            file_to_receive = client_files[file_to_receive]
                            port_to_receive = input("\nEspecifique a porta que deseja receber o arquivo.\n")
                            self.send_packages(["peer", client_addr, port_to_receive, file_to_receive])
                            self.open_server_to_receive_file(port_to_receive)
                
                #Como é utilizado a configuração não bloqueante, 
                # é necessário fazer desse modo para verificar se há uma nova conexão de peer
                available_socket, _, _ = select.select([self.peer_connection_socket], [], [], 0.5)

                for socket in available_socket:
                    new_peer_connection, new_peer_address = socket.accept()
                    threading.Thread(target=self.handle_peer, args=(new_peer_connection, new_peer_address), daemon=True).start()
                    print(f"Conectando com novo peer... {new_peer_address}")

        except Exception as err:
            print(f"A aplicação do cliente foi interrompida: {err}")
        finally:
            pass
            #self.audio.terminate()


Client().main()
