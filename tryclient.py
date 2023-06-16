import pickle
import socket
import sys
import threading
from io import BytesIO
import cv2
import pyaudio
import rsa
from PIL import ImageGrab, Image, ImageTk, JpegImagePlugin, ImageDraw, ImageFont
import io
import time
from pynput.mouse import Controller
from abc import ABC

import encryption


class Client(ABC):

    def __init__(self, name, ip_address):
        self.host = ip_address
        self.port = None
        self.server_address = None
        self.name = name

    def connect_udp_socket(self):
        # Open a socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return

    def send_message(self, data):
        """Gets encoded data to send"""
        self.server_socket.sendto(data, self.server_address)
        return

    def exit_window(self):
        sys.exit()


class StreamingClient(Client):

    def __init__(self, name, ip_address):
        super().__init__(name, ip_address)
        self.__stream_on = False
        self.root = None
        self.app_image = None
        self.label = None
        self.server_socket = None
        self.window = None
        self.func = None
        self.aes_key_iv = None
        self.rsa_public_key = None
        self.font = ImageFont.truetype("arial.ttf", 36)
        self.font_color = (255, 255, 255)
        self.text_pos = (5, 3)
        self.overlay_color = (0, 0, 0, 128)
        self.overlay_size = self.font.getsize(self.name)
        self.overlay_size = tuple(value + 10 for value in self.overlay_size)
        self.overlay = Image.new('RGBA', self.overlay_size, self.overlay_color)
        self.overlay_pos = (0, 0)

        self.cursor = Image.open("cursor.png").resize((28, 28))
        self.my_cursor = Controller()

        # Connect to udp server
        self.connect_udp_socket()

    def send_screenshot(self):
        """Function to send the screenshot"""

        self.aes_key_iv = encryption.create_AES_key_iv()
        previous_screenshot = None
        bio = io.BytesIO()
        image_quality = 10

        self.send_message("Hi".encode())
        rsa_public_key_bytes, server_address = self.server_socket.recvfrom(4096)
        self.rsa_public_key = rsa.PublicKey.load_pkcs1(rsa_public_key_bytes, format='PEM')
        keys = pickle.dumps(self.aes_key_iv)
        encrypted_keys = encryption.encrypt_rsa(keys, self.rsa_public_key)
        self.send_message(encrypted_keys)


        while True:
            print(f"")
            if self.__stream_on:
                # Take a screenshot of the monitor or the camera
                screenshot = self.get_frame()
                if previous_screenshot == screenshot:
                    continue

                # Saving the photo to the digital storage
                screenshot.save(bio, "JPEG", quality=image_quality)
                bio.seek(0)

                # Getting the bytes of the photo
                screenshot = bio.getvalue()
                screenshot = encryption.encrypt_AES(screenshot, self.aes_key_iv[0], self.aes_key_iv[1])
                # Restarting the storage
                bio.truncate(0)

                length = len(screenshot)
                if length < 65000:
                    # Sending the screenshot
                    self.send_message(screenshot)
                    if image_quality < 90 and length < 65000:
                        image_quality += 5
                else:
                    image_quality -= 10
                previous_screenshot = screenshot

    def receive_screenshot(self):
        """Function to receive and display the screenshot"""
        previous_img = None

        while True:
            try:
                # Receive the screenshot from the server
                screenshot_bytes, server_address = self.server_socket.recvfrom(65000)
                screenshot_bytes = encryption.decrypt_AES(screenshot_bytes, self.aes_key_iv[0], self.aes_key_iv[1])

                # Create a PhotoImage object from the received data
                screenshot = Image.open(BytesIO(screenshot_bytes))
                img = ImageTk.PhotoImage(screenshot)

                # Update the label with the new screenshot
                if not previous_img == img:
                    self.update_label(self.label, img)
                previous_img = img
            except:
                continue

    def update_label(self, label, img):
        """updating label with given image"""
        if type(img) == JpegImagePlugin.JpegImageFile:
            img = ImageTk.PhotoImage(img)

        label.configure(image=img)
        label.update()
        return

    def start(self, label):
        # Setting the label to update
        self.label = label

        # Send screenshots to the server
        threading.Thread(target=self.send_screenshot).start()
        time.sleep(1 / 3)
        threading.Thread(target=self.receive_screenshot).start()
        return

    def start_stream(self):
        self.__stream_on = True
        return

    def stop_stream(self):
        self.__stream_on = False
        self.send_message("Q".encode())
        return

    def get_frame(self):
        pass

    def confirm_close(self):
        self.send_message("Q".encode())
        self.__stream_on = False
        self.server_socket.close()
        sys.exit()


class ScreenShareClient(StreamingClient):

    def __init__(self, name, ip_address):
        super(ScreenShareClient, self).__init__(name, ip_address)
        self.port = 12343
        self.server_address = (self.host, self.port)

    def get_frame(self):
        frame = ImageGrab.grab()

        # Drawing a mouse on the screen
        frame = frame.convert("RGBA")
        frame.alpha_composite(self.cursor, dest=self.my_cursor.position)
        frame = frame.convert("RGB")

        # Resizing the photo
        frame = frame.resize((1200, 600))

        frame.paste(self.overlay, self.overlay_pos, self.overlay)

        draw_tool = ImageDraw.Draw(frame)
        draw_tool.text(self.text_pos, self.name, font=self.font, fill=self.font_color)

        return frame


class CameraClient(StreamingClient):

    def __init__(self, name, ip_address, x_res=1280, y_res=720):
        super(CameraClient, self).__init__(name, ip_address)
        self.port = 12344
        self.server_address = (self.host, self.port)
        self.__x_res = x_res
        self.__y_res = y_res
        self.__camera = cv2.VideoCapture(0)
        self.__configure()
        self.font = ImageFont.truetype("arial.ttf", 15)  # Specify the desired font file
        self.overlay_size = self.font.getsize(self.name)
        self.overlay_size = tuple(value + 6 for value in self.overlay_size)
        self.overlay = Image.new('RGBA', self.overlay_size, self.overlay_color)

    def __configure(self):
        self.__camera.set(3, self.__x_res)
        self.__camera.set(4, self.__y_res)

    def get_frame(self):
        # Get the screenshot from webcam
        ret, frame = self.__camera.read()

        # Convert screenshot to PIL image
        rgb_frame = frame[:, :, ::-1]
        pil_image = Image.fromarray(rgb_frame)

        # Resizing the photo
        pil_image = pil_image.resize((300, 200))

        pil_image.paste(self.overlay, self.overlay_pos, self.overlay)

        draw_tool = ImageDraw.Draw(pil_image)
        draw_tool.text(self.text_pos, self.name, font=self.font, fill=self.font_color)

        return pil_image


class AudioClient(Client):

    def __init__(self, ip_address, name=None):
        super().__init__(name, ip_address)
        self.server_socket = None
        self.stream = None
        self.__muted = True
        self.aes_key_iv = None
        self.rsa_public_key = None

        # Private Parameters
        self._chunk = 1024
        self._format = pyaudio.paInt16
        self._channels = 1
        self._rate = 44100

        self.port = 12345
        self.server_address = (self.host, self.port)

        # Connect to udp server
        self.connect_udp_socket()

        # Create a PyAudio object
        self.audio = pyaudio.PyAudio()

        # Create a PyAudio stream for playback
        self.stream = self.audio.open(format=self._format, channels=self._channels,
                                      rate=self._rate, input=True, frames_per_buffer=self._chunk)

        self.speaker = self.audio.open(format=self._format, channels=self._channels,
                                       rate=self._rate, output=True)

    def recv_data(self):
        while True:
            try:
                # Receive a chunk of audio data from a client
                data, address = self.server_socket.recvfrom(65000)
                data = encryption.decrypt_AES(data, self.aes_key_iv[0], self.aes_key_iv[1])

                # Play back audio data
                self.speaker.write(data)
            except:
                continue

    def send_data(self):

        self.aes_key_iv = encryption.create_AES_key_iv()
        self.send_message("Hi".encode())
        rsa_public_key_bytes, server_address = self.server_socket.recvfrom(4096)
        self.rsa_public_key = rsa.PublicKey.load_pkcs1(rsa_public_key_bytes, format='PEM')
        keys = pickle.dumps(self.aes_key_iv)
        encrypted_keys = encryption.encrypt_rsa(keys, self.rsa_public_key)
        self.send_message(encrypted_keys)

        # Loop forever and send audio data to the server
        while True:
            print(f"")
            if not self.__muted:
                # Read a chunk of audio data from the microphone
                data = self.get_audio_data()

                data = encryption.encrypt_AES(data, self.aes_key_iv[0], self.aes_key_iv[1])
                # Send the audio data to the server
                self.send_message(data)

    def start(self):
        threading.Thread(target=self.send_data).start()
        time.sleep(1 / 3)
        threading.Thread(target=self.recv_data).start()
        return

    def start_mic(self):
        self.__muted = False
        return

    def stop_mic(self):
        self.__muted = True
        return

    def get_audio_data(self):
        pass


class MicrophoneAudioClient(AudioClient):

    def __init__(self, ip_address):
        super(MicrophoneAudioClient, self).__init__(ip_address)
        self._rate = 16000

    def get_audio_data(self):
        return self.stream.read(self._chunk)


class ChatWindow():
    def __init__(self, client_name, address, input_area, text_area):
        self._CLIENT_NAME = client_name
        self.input_area = input_area
        self.text_area = text_area
        self._IP = address
        self._PORT = 12341
        self.server_address = (self._IP, self._PORT)
        self.sock = None
        self.running = True
        self.aes_key_iv = None
        self.rsa_public_key = None
        self.aes_sent = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)

    def send_data(self, data):
        data = encryption.encrypt_AES(data.encode('utf-8'), self.aes_key_iv[0], self.aes_key_iv[1])
        self.sock.send(data)
        return

    def send_message(self, data):
        self.sock.send(data)
        return

    def start(self):
        threading.Thread(target=self.handle_receive).start()
        return

    def handle_receive(self):
        while self.running:
            try:
                message = self.sock.recv(4096)
                if self.aes_sent:
                    message = encryption.decrypt_AES(message, self.aes_key_iv[0], self.aes_key_iv[1]).decode('utf-8')
                if message == 'NICKNAME':
                    self.sock.send(encryption.encrypt_AES(self._CLIENT_NAME.encode(), self.aes_key_iv[0], self.aes_key_iv[1]))
                else:
                    if not self.aes_sent:
                        self.aes_key_iv = encryption.create_AES_key_iv()
                        rsa_public_key_bytes = message
                        self.rsa_public_key = rsa.PublicKey.load_pkcs1(rsa_public_key_bytes, format='PEM')
                        keys = pickle.dumps(self.aes_key_iv)
                        encrypted_keys = encryption.encrypt_rsa(keys, self.rsa_public_key)
                        self.send_message(encrypted_keys)
                        print('aes sent')
                        self.aes_sent = True
                        continue

                    self.text_area.config(state="normal")
                    self.text_area.insert('end', message)
                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')

            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break
