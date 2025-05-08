import socket
import threading
import json

class TetrisNetwork:
    def __init__(self, mode, ip, port, on_event=None, on_connect=None):
        self.mode = mode  # 'host' or 'join'
        self.ip = ip
        self.port = port
        self.sock = None
        self.conn = None
        self.running = False
        self.on_event = on_event  # callback for received events
        self.on_connect = on_connect  # callback for connection established
        self.thread = None

    def start(self):
        if self.mode == 'host':
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.ip, self.port))
            self.sock.listen(1)
            print(f"[TetrisNetwork] Waiting for connection on {self.ip}:{self.port}...")
            threading.Thread(target=self._accept_and_start, daemon=True).start()
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"[TetrisNetwork] Connecting to {self.ip}:{self.port}...")
            threading.Thread(target=self._connect_and_start, daemon=True).start()

    def _accept_and_start(self):
        self.conn, addr = self.sock.accept()
        print(f"[TetrisNetwork] Connected by {addr}")
        self.running = True
        if self.on_connect:
            self.on_connect()
        self.thread = threading.Thread(target=self.listen, daemon=True)
        self.thread.start()

    def _connect_and_start(self):
        try:
            self.sock.connect((self.ip, self.port))
            self.conn = self.sock
            self.running = True
            if self.on_connect:
                self.on_connect()
            self.thread = threading.Thread(target=self.listen, daemon=True)
            self.thread.start()
        except Exception as e:
            print(f"[TetrisNetwork] Connection error: {e}")

    def listen(self):
        while self.running:
            try:
                data = self.conn.recv(1024)
                if not data:
                    break
                msg = data.decode('utf-8')
                try:
                    event = json.loads(msg)
                    if self.on_event:
                        self.on_event(event)
                except Exception as e:
                    print(f"[TetrisNetwork] Error decoding event: {e}")
            except Exception as e:
                print(f"[TetrisNetwork] Network error: {e}")
                break
        self.running = False

    def send_event(self, event):
        try:
            msg = json.dumps(event).encode('utf-8')
            self.conn.sendall(msg)
        except Exception as e:
            print(f"[TetrisNetwork] Send error: {e}")

    def close(self):
        self.running = False
        try:
            if self.conn:
                self.conn.close()
            if self.sock and self.sock != self.conn:
                self.sock.close()
        except Exception:
            pass
