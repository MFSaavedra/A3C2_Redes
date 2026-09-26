import socket
import random

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
    def parse_segment(segment: bytes):
        flags = segment[0]               
        seq   = int.from_bytes(segment[1:2], "big")
        return {"ACK": bool(flags & 0x01), "SYN": bool(flags & 0x02), "FIN": bool(flags & 0x04), "seq": seq, "payload": segment[2:]}
        

    @staticmethod
    def create_segment(seq: int, flags: str, payload: bytes=b""):
        flags_byte = 0
        if "ACK" in flags: flags_byte |= 0x01
        if "SYN" in flags: flags_byte |= 0x02
        if "FIN" in flags: flags_byte |= 0x04

        header = bytes([flags_byte]) + seq.to_bytes(2, 'big')
        return header + payload


    def bind(self, address):
        self.socket.bind(address)
        self.local_address = address
        self.is_bound = True

    def connect(self, address):
        self.remote_address = address
        self.seq_num = random.randint(0, 100)
    def accept()

    def send(message):
        self.socket.send()

    def recv(buff_size)

    def close(self):
        self.socket.close()
    def recv_close()