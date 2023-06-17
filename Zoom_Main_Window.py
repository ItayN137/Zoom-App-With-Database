import sys
import threading
from tkinter.messagebox import askyesno
import sqlite3
import customtkinter
import tkinter
import socket
import encryption
from Zoom_Client import ZoomClient, HostZoomClient
import multiprocessing


class Zoom_Main_Window:

    def __init__(self, database_address, database_port):
        self.root = None
        self.frame = None
        self.label = None
        self.entry1 = None
        self.entry2 = None
        self.entry3 = None
        self.create_button = None
        self.join_button = None
        self.__meeting_id = None
        self.__meeting_password = None
        self.__username = None
        self.host = database_address
        self.port = database_port
        self.server_address = (self.host, self.port)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)

        multiprocessing.Process(target=self.handle_zoom_window).start()

    def build_connection_to_db(self):
        # Build the database file + the control tool of it
        db_connection = sqlite3.connect("servers.db")
        db_cursor = db_connection.cursor()
        return db_connection, db_cursor

    def handle_zoom_window(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")

        self.root = customtkinter.CTk()
        self.root.geometry("300x400")
        self.root.title("Itay's Zoom Application")

        self.app_image = tkinter.PhotoImage(file="zoom.png")
        self.root.iconphoto(False, self.app_image)

        self.label = customtkinter.CTkLabel(master=self.root, text="Itay's Zoom Application", font=("Arial", 25))
        self.label.pack(pady=12, padx=10)

        self.frame = customtkinter.CTkFrame(master=self.root)
        self.frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.entry1 = customtkinter.CTkEntry(master=self.frame, placeholder_text="Username")
        self.entry1.pack(pady=12, padx=10)

        self.entry2 = customtkinter.CTkEntry(master=self.frame, placeholder_text="Meeting ID")
        self.entry2.pack(pady=12, padx=10)

        self.entry3 = customtkinter.CTkEntry(master=self.frame, placeholder_text="Password")
        self.entry3.pack(pady=12, padx=10)

        self.create_button = customtkinter.CTkButton(master=self.frame, text="Create New Meeting",
                                                     command=self.handle_new_host_client)
        self.create_button.pack(pady=12, padx=10)

        self.join_button = customtkinter.CTkButton(master=self.frame, text="Join Meeting",
                                                   command=self.handle_new_client)
        self.join_button.pack(pady=12, padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.confirm_close)
        self.root.mainloop()

    def handle_new_client(self):
        self.__username = self.entry1.get()
        self.__meeting_id = self.entry2.get()
        self.__meeting_password = self.entry3.get()

        if not self.validate_entry(self.__username, self.__meeting_id, self.__meeting_password):
            if self.check_db(self.__meeting_id, self.__meeting_password):
                self.root.destroy()
                threading.Thread(target=ZoomClient, args=(self.__username, self.__meeting_id)).start()
            else:
                self.create_top_level("try again!")
                return
        else:
            self.create_top_level("One or more fields are empty, try again!")
        return

    def handle_new_host_client(self):
        self.__username = self.entry1.get()
        self.__meeting_id = self.entry2.get()
        self.__meeting_password = self.entry3.get()

        if not self.validate_entry(self.__username, self.__meeting_id, self.__meeting_password):
            if self.insert_db(self.__meeting_id, self.__meeting_password):
                self.root.destroy()
                threading.Thread(target=HostZoomClient, args=(self.__username, self.__meeting_id)).start()
            else:
                self.create_top_level("Error")
        else:
            self.create_top_level("One or more fields are empty, try again!")
        return

    def validate_entry(self, *args):
        for arg in args:
            if arg == "":
                return True
        return False

    def check_db(self, ip, password):
        encrypted_password = encryption.encrypt_MD5(password)
        db_connection, db_cursor = self.build_connection_to_db()
        request = f"SELECT password FROM servers WHERE ip='{ip}';{encrypted_password}"
        self.client_socket.sendall(request.encode())

        response = self.client_socket.recv(1024).decode()
        return response == "Authentication successful"

    def insert_db(self, ip, password):
        db_connection, db_cursor = self.build_connection_to_db()
        encrypted_password = encryption.encrypt_MD5(password)
        request = f"INSERT INTO servers (ip, password) VALUES ('{ip}', '{encrypted_password}')"
        self.client_socket.sendall(request.encode())

        response = self.client_socket.recv(1024).decode()
        print(response)
        return response == "Authentication successful"

    def create_top_level(self, text):
        top_level = customtkinter.CTkToplevel()
        top_level.geometry("500x50")
        top_level.title("Itay's Zoom Application")
        top_level.iconphoto(False, self.app_image)
        label = customtkinter.CTkLabel(master=top_level, text=text, font=("Ariel", 20, "bold"), width=10, height=10)
        label.pack(pady=10, padx=10, anchor=tkinter.CENTER)

    def confirm_close(self):
        if askyesno(title='Exit', message='Close Window?'):
            sys.exit()


def main():
    zoom1 = Zoom_Main_Window(socket.gethostname(), 56789)


if __name__ == '__main__':
    main()
