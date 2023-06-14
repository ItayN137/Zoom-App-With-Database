from tkinter.messagebox import askyesno
import tkinter.scrolledtext
import customtkinter
import tkinter
from PIL import Image
import socket
import sys
import threading
import tryclient
import tryserver
from customtkinter import CTkScrollbar


class ZoomClient:

    def __init__(self, username, ip_address):
        self._USERNAME = username
        self._IP = ip_address
        self._IS_MUTED = True
        self._IS_CAMERA = False
        self._IS_SCREEN_SHARING = False
        self._WIDTH = 1500
        self._HEIGHT = 920
        self.root = None
        self.lower_frame = None
        self.upper_frame = None
        self.label = None
        self.app_image = None
        self.microphone_button = None
        self.camera_button = None
        self.share_screen_button = None
        self.window = None
        self.camera_display_label = None
        self.screen_display_label = None
        self.text_area = None
        self.input_area = None
        self.chat_label = None
        self.send_button = None
        self.appearance_mode_option_menu = None
        self.emoji1 = None
        self.emoji2 = None
        self.emoji3 = None
        self.emoji4 = None
        self.emoji5 = None
        self.muted_mic_image = customtkinter.CTkImage(light_image=Image.open("mute_microphone.png"),
                                                      dark_image=Image.open("mute_microphone.png"),
                                                      size=(20, 20))

        self.unmuted_mic_image = customtkinter.CTkImage(light_image=Image.open("microphone.png"),
                                                        dark_image=Image.open("microphone.png"),
                                                        size=(20, 20))

        self.camera_on = customtkinter.CTkImage(light_image=Image.open("video_camera.png"),
                                                dark_image=Image.open("video_camera.png"),
                                                size=(20, 20))

        self.camera_off = customtkinter.CTkImage(light_image=Image.open("no_video_camera.png"),
                                                 dark_image=Image.open("no_video_camera.png"),
                                                 size=(20, 20))

        self.share_screen_on_photo = customtkinter.CTkImage(light_image=Image.open("screen_share_on.png"),
                                                            dark_image=Image.open("screen_share_on.png"),
                                                            size=(20, 20))

        self.share_screen_off_photo = customtkinter.CTkImage(light_image=Image.open("screen_share_off.png"),
                                                             dark_image=Image.open("screen_share_off.png"),
                                                             size=(20, 20))

        self.screen_default_photo = customtkinter.CTkImage(light_image=Image.open("black_screen.png"),
                                                           dark_image=Image.open("black_screen.png"),
                                                           size=(1200, 600))

        self.camera_default_photo = customtkinter.CTkImage(light_image=Image.open("black_screen.png"),
                                                           dark_image=Image.open("black_screen.png"),
                                                           size=(1200, 200))
        self.send_photo = customtkinter.CTkImage(light_image=Image.open("send.png"),
                                                 dark_image=Image.open("send.png"),
                                                 size=(20, 20))

        self.audio_client = tryclient.MicrophoneAudioClient(ip_address)
        self.screen_share_client = tryclient.ScreenShareClient(self._USERNAME, ip_address)
        self.camera_client = tryclient.CameraClient(self._USERNAME, ip_address)
        self.chat_client = None

        threading.Thread(target=self.handle_new_client).start()

    def handle_new_client(self):
        self.root = customtkinter.CTk()
        self.root.geometry(f"{self._WIDTH}x{self._HEIGHT}")
        self.root.title("PyMeetings")

        self.app_image = tkinter.PhotoImage(file="zoom.png")
        self.root.iconphoto(False, self.app_image)

        self.label = customtkinter.CTkLabel(master=self.root, text="PyMeetings",
                                            font=("Arial", 30))
        self.label.pack(pady=6, padx=5)

        self.camera_display_label = customtkinter.CTkLabel(master=self.root, image=self.camera_default_photo, text="")
        self.camera_display_label.place(relx=0.41, rely=0.16, anchor=tkinter.CENTER)

        self.screen_display_label = customtkinter.CTkLabel(master=self.root, image=self.screen_default_photo, text="")
        self.screen_display_label.place(relx=0.41, rely=0.6, anchor=tkinter.CENTER)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.root, width=25, height=35, bg='grey')
        self.text_area.place(relx=0.9, rely=0.5, anchor=tkinter.CENTER)
        self.text_area.config(state='disabled')

        self.input_area = tkinter.Text(self.root, width=25, height=3)
        self.input_area.place(relx=0.9, rely=0.85, anchor=tkinter.CENTER)

        self.chat_label = customtkinter.CTkLabel(master=self.root, text="Chat",
                                            font=("Arial", 50))
        self.chat_label.place(relx=0.9, rely=0.15, anchor=tkinter.CENTER)

        self.appearance_mode_option_menu = customtkinter.CTkOptionMenu(self.root,
                                                                       values=["Light", "Dark"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_option_menu.place(relx=0.9, rely=0.05, anchor=tkinter.CENTER)

        self.emoji1 = customtkinter.CTkButton(master=self.root,
                                              text="👋",
                                              font=("Ariel", 15, "bold"), width=10, height=10,
                                              command=lambda: self.handle_emoji("👋"))
        self.emoji1.place(relx=0.84, rely=0.9, anchor=tkinter.CENTER)

        self.emoji2 = customtkinter.CTkButton(master=self.root,
                                              text="🎤",
                                              font=("Ariel", 15, "bold"), width=10, height=10,
                                              command=lambda: self.handle_emoji("🎤"))
        self.emoji2.place(relx=0.87, rely=0.9, anchor=tkinter.CENTER)

        self.emoji3 = customtkinter.CTkButton(master=self.root,
                                              text="📷",
                                              font=("Ariel", 15, "bold"), width=10, height=10,
                                              command=lambda: self.handle_emoji("📷"))
        self.emoji3.place(relx=0.9, rely=0.9, anchor=tkinter.CENTER)

        self.emoji4 = customtkinter.CTkButton(master=self.root,
                                              text="💻",
                                              font=("Ariel", 15, "bold"), width=10, height=10,
                                              command=lambda: self.handle_emoji("💻"))
        self.emoji4.place(relx=0.93, rely=0.9, anchor=tkinter.CENTER)

        self.emoji5 = customtkinter.CTkButton(master=self.root,
                                              text="💡",
                                              font=("Ariel", 15, "bold"), width=10, height=10,
                                              command=lambda: self.handle_emoji("💡"))
        self.emoji5.place(relx=0.96, rely=0.9, anchor=tkinter.CENTER)

        self.lower_frame = customtkinter.CTkFrame(master=self.root, width=400, height=50)
        self.lower_frame.pack(ipadx=400, ipady=4, side="bottom")

        self.microphone_button = customtkinter.CTkButton(master=self.lower_frame, image=self.muted_mic_image,
                                                         text="Unmute",
                                                         font=("Ariel", 15, "bold"), width=10, height=10,
                                                         command=self.handle_mic)
        self.microphone_button.pack(pady=10, padx=10, side="left", anchor=tkinter.CENTER)

        self.camera_button = customtkinter.CTkButton(master=self.lower_frame, image=self.camera_off,
                                                     text="Turn On",
                                                     font=("Ariel", 15, "bold"), width=10, height=10,
                                                     command=self.handle_camera)
        self.camera_button.pack(pady=10, padx=10, side="left", anchor=tkinter.CENTER)

        self.share_screen_button = customtkinter.CTkButton(master=self.lower_frame, image=self.share_screen_off_photo,
                                                           text="Share Screen",
                                                           font=("Ariel", 15, "bold"), width=10, height=10,
                                                           command=self.handle_share_screen)
        self.share_screen_button.pack(pady=10, padx=10, side="left", anchor=tkinter.CENTER)

        self.send_button = customtkinter.CTkButton(master=self.lower_frame, image=self.send_photo,
                                                   text="Send",
                                                   font=("Ariel", 15, "bold"), width=10, height=10,
                                                   command=self.handle_send)
        self.send_button.pack(pady=10, padx=10, side="right", anchor=tkinter.CENTER)

        self.chat_client = tryclient.ChatWindow(self._USERNAME, self._IP, self.input_area, self.text_area)

        self.chat_client.start()
        self.audio_client.start()
        self.screen_share_client.start(self.screen_display_label)
        self.camera_client.start(self.camera_display_label)

        self.root.protocol("WM_DELETE_WINDOW", self.confirm_close)
        self.root.mainloop()

    def confirm_close(self):
        if askyesno(title='Exit', message='Close Window?'):
            self.screen_share_client.confirm_close()
            self.screen_share_client.exit_window()
            self.audio_client.stop_mic()
            self.audio_client.exit_window()
            self.camera_client.confirm_close()
            self.camera_client.exit_window()
            sys.exit()

    def change_appearance_mode_event(self, mode):
        customtkinter.set_appearance_mode(mode)
        return

    def handle_emoji(self, emoji):
        if self.input_area.get('1.0', 'end-1c') == "":
            data = f"{self._USERNAME}: {emoji}\n"
            self.input_area.delete('1.0', 'end')
            self.chat_client.send_data(data)
        else:
            self.input_area.insert('end', emoji)
        return

    def handle_mic(self):
        """
        handle the press of the button. changes the button to mute or un-mute text and image and also provides
        the audio share between clients
        :return:
        """
        if self._IS_MUTED:
            self._IS_MUTED = False
            self.microphone_button.configure(image=self.unmuted_mic_image, text="Mute",
                                             font=("Ariel", 15, "bold"), width=10, height=10)
            self.audio_client.start_mic()

        else:
            self._IS_MUTED = True
            self.microphone_button.configure(image=self.muted_mic_image,
                                             text="Unmute",
                                             font=("Ariel", 15, "bold"), width=10, height=10)
            self.audio_client.stop_mic()
        return

    def handle_camera(self):
        """
        handle the press of the button. changes the button to camera on or off with text and image and also provides
        the camera share between clients
        :return:
        """
        if not self._IS_CAMERA:
            self._IS_CAMERA = True
            self.camera_button.configure(image=self.camera_on,
                                         text="Turn Off",
                                         font=("Ariel", 15, "bold"), width=10, height=10)
            self.camera_client.start_stream()

        else:
            self._IS_CAMERA = False
            self.camera_button.configure(image=self.camera_off,
                                         text="Turn On",
                                         font=("Ariel", 15, "bold"), width=10, height=10)
            self.camera_client.stop_stream()

        return

    def handle_share_screen(self):
        """
        handle the press of the button. changes the button to share screen on or off with text and image and also
        provides the screen share between clients
        :return:
        """
        if not self._IS_SCREEN_SHARING:
            self._IS_SCREEN_SHARING = True
            self.share_screen_button.configure(image=self.share_screen_on_photo,
                                               text="Stop Sharing",
                                               font=("Ariel", 15, "bold"), width=10, height=10)
            self.screen_share_client.start_stream()
        else:
            self._IS_SCREEN_SHARING = False
            self.share_screen_button.configure(image=self.share_screen_off_photo,
                                               text="Share Screen",
                                               font=("Ariel", 15, "bold"), width=10, height=10)
            self.screen_share_client.stop_stream()
        return

    def handle_send(self):
        data = None
        if not self.input_area.get('1.0', 'end-1c') == "":
            data = f"{self._USERNAME}: {self.input_area.get('1.0', 'end')}"
            self.input_area.delete('1.0', 'end')
        self.chat_client.send_data(data)


class HostZoomClient(ZoomClient):

    def __init__(self, name, ip):
        threading.Thread(target=tryserver.AudioServer().handle_data).start()
        threading.Thread(target=tryserver.ScreenStreamingServer().handle_data).start()
        threading.Thread(target=tryserver.CameraStreamingServer().handle_data).start()
        threading.Thread(target=tryserver.ZoomHostChatWindow().handle_receive).start()

        super().__init__(name, ip)


def main():
    client = HostZoomClient("Itay Navon", socket.gethostname())


if __name__ == '__main__':
    main()
