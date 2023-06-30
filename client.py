import os.path
import socket
import sys
import threading, queue, time
import ast
import pyaudio
from pydub import AudioSegment

CHUNK_SIZE = 1024
SAMPLE_WIDTH = 2
CHANNELS = 2
SAMPLE_RATE = 44100
BUFF_SIZE = 65536

stop_event = threading.Event()


class Client:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encode_format = "utf-8"
        #IP e portas para conectar com servidor
        self.server_ip = sys.argv[1]
        self.server_port = int(sys.argv[2])
        #IP e portas utilizadas para ouvir as conexões com os peers
        self.ip_to_accept_peer_connections = sys.argv[3]
        self.port_to_accept_peer_connection = int(sys.argv[4])
        self.files_list = sys.argv[5:] if len(sys.argv) > 4 else []
        self.listen_to_server_thread = threading.Thread
        self.client_table = {}
        self.audio = pyaudio.PyAudio()
        self.queue = queue.Queue(maxsize=2000)

        try:
            #Setando para receber conexões de peers
            self.peer_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.peer_connection_socket.bind((self.ip_to_accept_peer_connections, self.port_to_accept_peer_connection))
            self.peer_connection_socket.listen(1)

            print("Configurado para receber conexões de peers")
        except:
            print("Falha ao iniciar listening socket...")
            sys.exit(1)

    def listen_to_server(self):
        """'Função que fica recebendo dados do servidor'"""
        while True:
            try:
                data = self.client_socket.recv(1024).decode(self.encode_format)
                data = ast.literal_eval(data)
                if not data or data[0] == "desconectado":
                    break

                if data[0] == "lista":
                    self.client_table = data[1]
                    print(f"Nova tabela de clientes: {self.client_table}")

            except Exception as err:
                print(f"Erro ao lidar com a listen to server: {err}")
                break

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            self.listen_to_server_thread(target=self.listen_to_server, daemon=True).start()
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
    
    #Função para lidar com conexão de novos peers
    def handle_peer(self, connection, address):
        """'Função para lidar com conexão de novos peers'"""
        print("Conectado com " + str(address))

        #Primeiro será recebido a porta que deverá ser mandada
        data = connection.recv(1024).decode(self.encode_format)
        port_to_send_file = int(ast.literal_eval(data))
        ip_to_send_file = address[0]

        #Depois será recebido o arquivo que está sendo requisitado
        data = connection.recv(1024).decode(self.encode_format)
        file_chosen = self.files_list[int(ast.literal_eval(data))]

        print("Arquivo escolhido: " + str(file_chosen))

        #A conexão provavelmente está OK, o que precisa ser testado é a função send_file
        self.send_file(file_chosen, ip_to_send_file, port_to_send_file)
        connection.close()

    def send_file(self, filename, ip_to_send, port_to_send):
        """'Função para envio do arquivo'"""
        send_file_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            extension = filename.rsplit(".", 1)[-1]
            audio_infos = AudioSegment.from_file(filename, format=extension)
            raw_data = audio_infos.raw_data
            for i in range(0, len(raw_data), CHUNK_SIZE*10):
                chunk = raw_data[i:i + CHUNK_SIZE*10]
                send_file_socket_udp.sendto(chunk, (ip_to_send, port_to_send))
                time.sleep((CHUNK_SIZE*2)/SAMPLE_RATE)
            send_file_socket_udp.sendto("fim".encode(self.encode_format), (ip_to_send, port_to_send))
        except Exception as err:
            print(f"Erro ao enviar arquivo: {err}")
        finally:
            send_file_socket_udp.close()

    def receive_connections(self):
        """'Função para receber conexão tcp de outros clientes.'"""
        while True:
            new_peer_connection, new_peer_address = self.peer_connection_socket.accept()
            threading.Thread(target=self.handle_peer, args=(new_peer_connection, new_peer_address), daemon=True).start()
            print(f"Conectando com novo peer... {new_peer_address}")

    def get_audio_data(self):
        """'Função que recebes dados e coloca na queue.'"""
        try:
            while True:
                frame, _ = client_socket_to_receive_file.recvfrom(BUFF_SIZE)
                self.queue.put(frame)
        except Exception:
            pass

    def main(self):
        global socket
        global client_socket_to_receive_file
        try:
            self.connect_to_server()
            self.send_packages(str(self.port_to_accept_peer_connection) + "," + ",".join(self.files_list))
            threading.Thread(target=self.receive_connections, args=(), daemon=True).start()
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

                    if peer_to_connect == -1:
                        print("Ok, voltando")
                    elif peer_to_connect < 0 or peer_to_connect >= (len(clients_keys)):
                        print("Não existe esse cliente na lista.\nIgnorando solicitação...")
                    else:
                        peer_addr = clients_keys[peer_to_connect]
                        chosen_user = self.client_table[peer_addr]

                        print("Conectando com " + str(peer_to_connect) + "...")
                        peer_ip = peer_addr[0]
                        peer_port = int(chosen_user[0])

                        #conectar ao peer
                        file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        file_socket.connect((peer_ip, peer_port))
                        
                        #Abrindo para receber resposta
                        port_to_receive = int(input("\nEspecifique a porta que deseja receber o arquivo.\n"))

                        #Pedir arquivo
                        peer_files = chosen_user[1:] #Primeira posição é numero da porta
                        for i in range(len(peer_files)):
                            print(f"{i} - {peer_files[i]}")
                        chosen_file = int(input("Qual arquivo você deseja pedir? ")) - 1

                        #Mandar primeiro porta a ser recebida
                        port_package = str(port_to_receive).encode(self.encode_format)
                        file_socket.send(port_package)

                        #Mandar arquivo requisitado
                        file_package = str(chosen_file).encode(self.encode_format)
                        file_socket.send(file_package)
                        file_socket.close()

                        #configuração para receber arquivo
                        stream = self.audio.open(format=self.audio.get_format_from_width(SAMPLE_WIDTH),
                                 channels=CHANNELS,
                                 rate=SAMPLE_RATE,
                                 output=True,
                                frames_per_buffer=CHUNK_SIZE)
                        
                        client_socket_to_receive_file = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        client_socket_to_receive_file.bind((self.client_socket.getsockname()[0], int(port_to_receive)))
                        threading.Thread(target=self.get_audio_data, args=(), daemon=True).start()
                        time.sleep(2)
                        try:
                            while True:
                                if self.queue.empty(): break
                                data = self.queue.get()
                                stream.write(data)
                        except Exception as err:
                            print(f"Erro ao lidar com recebimento de arquivo: {str(err)}")
                        finally:
                            client_socket_to_receive_file.close()
                            stream.stop_stream()
                            stream.close()

        except Exception as err:
            print(f"A aplicação do cliente foi interrompida: {err}")
        finally:
            pass
            self.audio.terminate()


Client().main()
