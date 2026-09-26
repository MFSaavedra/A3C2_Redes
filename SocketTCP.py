import socket
import random

# Formato del segmento: [flags: 1 byte][seq: 4 bytes, big-endian][datos: 0 a 16 bytes]
ACK_BIT = 0x01
SYN_BIT = 0x02
FIN_BIT = 0x04
SEQ_SIZE = 4
HEADER_SIZE = 1 + SEQ_SIZE
MAX_PAYLOAD = 16                         # máximo de datos por segmento (enunciado)
BUFFER_SIZE = HEADER_SIZE + MAX_PAYLOAD  # buffer fijo del socket UDP interno

class SocketTCP:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.remote_address = None
        self.local_address = None
        self.seq_num = 0
        self.ack_num = 0
        self.is_connected = False
        self.is_bound = False
        self.timeout = 1

    @staticmethod
    def parse_segment(segment: bytes) -> dict:
        flags = segment[0]
        return {"ACK": bool(flags & ACK_BIT),
                "SYN": bool(flags & SYN_BIT),
                "FIN": bool(flags & FIN_BIT),
                "seq": int.from_bytes(segment[1:HEADER_SIZE], "big"),
                "payload": segment[HEADER_SIZE:]}

    @staticmethod
    def create_segment(segment: dict) -> bytes:
        # Inversa de parse_segment; las llaves que falten valen False, 0 o b""
        flags_byte = 0
        if segment.get("ACK"): flags_byte |= ACK_BIT
        if segment.get("SYN"): flags_byte |= SYN_BIT
        if segment.get("FIN"): flags_byte |= FIN_BIT

        header = bytes([flags_byte]) + segment.get("seq", 0).to_bytes(SEQ_SIZE, "big")
        return header + segment.get("payload", b"")

    def bind(self, address):
        self.socket.bind(address)
        self.local_address = address
        self.is_bound = True

    def connect(self, address):
        self.remote_address = address
        self.seq_num = random.randint(0, 100)

    def accept(self):
        raise NotImplementedError  # paso 4

    def send(self, message):
        raise NotImplementedError  # paso 5

    def recv(self, buff_size):
        raise NotImplementedError  # paso 5

    def close(self):
        self.socket.close()

    def recv_close(self):
        raise NotImplementedError  # paso 6
