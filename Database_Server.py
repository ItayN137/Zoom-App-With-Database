import socket
import sqlite3
import threading


class Database_Server:

    def __init__(self, ip_address, port):
        self.host = ip_address
        self.port = port
        self.server_address = (self.host, self.port)
        self.conn = None

    def build_connection_to_db(self):
        # Build the database file + the control tool of it
        db_connection = sqlite3.connect("servers.db")
        db_cursor = db_connection.cursor()
        return db_connection, db_cursor

    def handle_request(self, client_socket, request):
        response = None
        try:
            db_connection, db_cursor = self.build_connection_to_db()
            #print("outside the if statements")
            if request.lower().startswith("select"):
                request_clear = request.split(";")
                db_cursor.execute(request_clear[0])
                result = db_cursor.fetchall()
                print(f"result: {result}")
                stored_password = result[0][0]
                print(f"password found: {stored_password}")
                print(f"request password: {request_clear[1]}")
                if stored_password == request_clear[1]:
                    response = f"Authentication successful"
                else:
                    response = "Exception"
            elif request.lower().startswith("insert"):
                try:
                    print(request)
                    db_cursor.execute(request)
                    print("hi")
                    db_connection.commit()
                    response = "Authentication successful"
                except:
                    response = "Exception1"
        except:
            response = "Exception2"
        #print(response)
        client_socket.sendall(response.encode())
        return

    def handle_client(self, client_socket):
        request = None
        while True:
            request = client_socket.recv(1024).decode()
            if not request:
                break
            print("Received request:", request)

            self.handle_request(client_socket, request)

    def start_server(self):
        self.build_data_base()

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(self.server_address)
        server_socket.listen()
        print("Server started, listening for connections...")

        while True:
            client_socket, client_address = server_socket.accept()
            print("Client connected:", client_address)

            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

            # client_socket.close()

    def build_data_base(self):
        db_connection, db_cursor = self.build_connection_to_db()
        db_cursor.execute("""CREATE TABLE IF NOT EXISTS servers (
                                    ip int,
                                    password VARCHAR(255) NOT NULL
                                )""")

        # Running the command
        db_connection.commit()


s = Database_Server(socket.gethostname(), 56789)
s.start_server()
