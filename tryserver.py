import socket
import threading
from PIL import Image
from io import BytesIO
import io
import rsa.pem
import encryption


class StreamingServer:

    def __init__(self, port):
        # Create a socket object
        self.server_socket = None
        self.server_address = None
        self.__clients_screenshots = {}
        self.__clients = []
        self.__clients_amount = 0
        self.__max_clients = 4
        self.big_screenshot = None
        self.reset_screenshot = None
        self.cords = None
        self.key = b"\xeb\x8d'\xe9\xa1.\x05\x9c\x80]\xce\x073|DC"
        self.iv = b'\x00\x85\xda\xa3gq\x9aC\xbdL\xd0kV"6\xe7'

        # Bind the socket to a specific host and port
        self.host = socket.gethostname()
        self.port = port
        self.server_address = (self.host, self.port)

        self.open_udp_server()

    def open_udp_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(self.server_address)
        print(self.server_address)

    def update_big_screenshot(self, client_address, screenshot):
        try:
            self.big_screenshot.paste(screenshot, self.__clients_screenshots[client_address])
        finally:
            return self.big_screenshot

    def broadcast(self, data):
        for client_address in self.__clients:
            self.server_socket.sendto(data, client_address)

    def handle_data(self):
        """Function to handle the data from client connection and send it back"""

        bio = io.BytesIO()
        image_quality = 10

        while True:
            try:
                # Receive the data from the client
                data, client_address = self.server_socket.recvfrom(65000)
                data = encryption.decrypt_AES(data, self.key, self.iv)
            except:
                continue

            if data == b'Hi':
                self.__clients.append(client_address)
                continue

            if client_address not in self.__clients_screenshots and (not data == b'Hi') and\
                    (not self.__clients_amount >= self.__max_clients):
                x_cords, y_cords = self.cords[self.__clients_amount]
                self.__clients_screenshots[client_address] = (x_cords, y_cords)
                self.__clients_amount += 1
                if client_address not in self.__clients:
                    self.__clients.append(client_address)

            if data == b'Q':
                new_screen = self.update_big_screenshot(client_address, self.reset_screenshot)

            else:
                # Open the screenshot with BytesIO
                screenshot = Image.open(BytesIO(data))

                # Updating the screen
                new_screen = self.update_big_screenshot(client_address, screenshot)

            # Saving the photo to the digital storage
            new_screen.save(bio, "JPEG", quality=image_quality)
            bio.seek(0)

            # Getting the bytes of the photo
            new_screen = bio.getvalue()
            new_screen = encryption.encrypt_AES(new_screen, self.key, self.iv)
            # Restarting the storage
            bio.truncate(0)

            length = len(new_screen)
            if length < 65000:
                # Send back the screenshot
                self.broadcast(new_screen)
                if image_quality < 90 and length < 65000:
                    image_quality += 5
            else:
                image_quality -= 10

    def start(self):
        t = threading.Thread(target=self.handle_data)
        t.start()


class ScreenStreamingServer(StreamingServer):

    def __init__(self):
        super(ScreenStreamingServer, self).__init__(12343)
        self.cords = [(0, 0), (0, 0), (0, 0), (0, 0)]
        self.big_screenshot = Image.new("RGB", (1200, 600), color='black')
        self.reset_screenshot = Image.new("RGB", (1200, 600), color='black')


class CameraStreamingServer(StreamingServer):

    def __init__(self):
        super(CameraStreamingServer, self).__init__(12344)
        self.cords = [(0, 0), (300, 0), (600, 0), (900, 0)]
        self.big_screenshot = Image.new("RGB", (1200, 200), color='black')
        self.reset_screenshot = Image.new("RGB", (300, 200), color='black')


class AudioServer:

    def __init__(self):
        # None objects
        self.server_socket = None
        self.__clients_addresses = []
        self.__clients_amount = 0

        # Bind the socket to a specific host and port
        self.host = socket.gethostname()
        self.port = 12345
        self.server_address = (self.host, self.port)
        print(self.server_address)
        # Open to udp server
        self.open_udp_server()

    def broadcast(self, data, address):
        for client_address in self.__clients_addresses:
            if client_address == address:
                continue
            self.server_socket.sendto(data, client_address)

    def open_udp_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(self.server_address)

    def handle_data(self):
        while True:
            # Receive a chunk of audio data from a client
            data, address = self.server_socket.recvfrom(65000)

            if self.__clients_amount >= 4:
                self.server_socket.sendto(str(len("max capacity")).encode(), address)
                self.server_socket.sendto("max capacity".encode(), address)
                # keep the server going and closing only the 5th client

            if address not in self.__clients_addresses:
                self.__clients_amount += 1
                self.__clients_addresses.append(address)

            # Send the data back to Clients
            self.broadcast(data, address)


class ZoomHostChatWindow:
    def __init__(self):
        self.host = socket.gethostname()
        self.port = 12341
        self.server_address = (self.host, self.port)
        self.clients = []
        self.nicknames = []
        self.sock = None

    def handle_receive(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.server_address)

        self.sock.listen(4)
        print(self.server_address)
        while True:
            client, address = self.sock.accept()

            client.send("NICKNAME".encode('utf-8'))
            nickname = client.recv(1024).decode()

            self.nicknames.append(nickname)
            self.clients.append(client)

            print(f"Name of client:{nickname}")
            self.broadcast(f"{nickname} connected to server!\n".encode('utf-8'))

            thread = threading.Thread(target=self.handle_message, args=(client,))
            thread.start()

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    # handle
    def handle_message(self, client):
        while True:
            try:
                message = client.recv(1024)
                self.broadcast(message)
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                self.nicknames.remove(self.nicknames[index])
                break
