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
        self.is_connected = False
        self.is_bound = False
        self.timeout = 1
        self.remaining_bytes = 0
        self.pending_buffer = b""
        self.expected_seq = 0

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
        self.local_address = self.socket.getsockname()  # dirección real: con puerto 0 el SO elige uno
        self.is_bound = True

    # Handshake con un solo contador: SYN lleva x, SYN+ACK x+1 y ACK x+2; ambos lados guardan x+2
    def connect(self, address):
        self.remote_address = address
        self.seq_num = random.randint(0, 100)
        self.socket.settimeout(self.timeout)
        syn_segment = self.create_segment({"SYN": True, "seq": self.seq_num})
        self.socket.sendto(syn_segment, self.remote_address)

        while not self.is_connected:
            try:
                data, addr = self.socket.recvfrom(BUFFER_SIZE)
                parsed = self.parse_segment(data)

                if parsed["SYN"] and parsed["ACK"] and parsed["seq"] == self.seq_num + 1:
                    self.remote_address = addr  # el SYN+ACK viene del socket nuevo que creó accept
                    self.seq_num += 2
                    ack_segment = self.create_segment({"ACK": True, "seq": self.seq_num})
                    self.socket.sendto(ack_segment, self.remote_address)
                    self.is_connected = True
            except socket.timeout:
                self.socket.sendto(syn_segment, self.remote_address)

    def accept(self):
        while True:
            data, addr = self.socket.recvfrom(BUFFER_SIZE)
            parsed = self.parse_segment(data)

            if parsed["SYN"]:
                new_socket = SocketTCP()
                new_socket.bind((self.local_address[0], 0))
                new_socket.remote_address = addr
                new_socket.seq_num = parsed["seq"] + 1
                new_socket.socket.settimeout(self.timeout)
                syn_ack = new_socket.create_segment({"SYN": True, "ACK": True, "seq": new_socket.seq_num})
                new_socket.socket.sendto(syn_ack, new_socket.remote_address)

                while True:
                    try:
                        data, _ = new_socket.socket.recvfrom(BUFFER_SIZE)
                        parsed = new_socket.parse_segment(data)

                        if parsed["ACK"] and parsed["seq"] == new_socket.seq_num + 1:
                            new_socket.seq_num += 1
                            new_socket.is_connected = True
                            return new_socket, new_socket.local_address
                    except socket.timeout:
                        new_socket.socket.sendto(syn_ack, new_socket.remote_address)

    def send(self, message):
        self.socket.settimeout(self.timeout)
        message_length = len(message)
        len_payload = message_length.to_bytes(4, "big")
        len_segment = self.create_segment({"seq": self.seq_num, "payload": len_payload})

        expected_ack = self.seq_num + len(len_payload)
        ack_received = False
        while not ack_received:
            try:
                self.socket.sendto(len_segment, self.remote_address)
                data, addr = self.socket.recvfrom(BUFFER_SIZE)
                parsed = self.parse_segment(data)

                if parsed and parsed["ACK"] and parsed["seq"] == expected_ack:
                    ack_received = True
                    self.seq_num = expected_ack
            except socket.timeout:
                continue

        offset = 0
        while offset < message_length:
            chunk = message[offset:offset + MAX_PAYLOAD]
            segment = self.create_segment({"seq": self.seq_num, "payload": chunk})
            expected_ack = self.seq_num + len(chunk)
            ack_received = False

            while not ack_received:
                try:
                    self.socket.sendto(segment, self.remote_address)
                    data, addr = self.socket.recvfrom(BUFFER_SIZE)
                    parsed = self.parse_segment(data)

                    if parsed and parsed["ACK"] and parsed["seq"] == expected_ack:
                        ack_received = True
                        self.seq_num = expected_ack
                        offset += len(chunk)
                except socket.timeout:
                    continue

    def recv(self, buff_size):
        self.socket.settimeout(self.timeout)
        received_data = b""

        if self.pending_buffer:
            if len(self.pending_buffer) >= buff_size:
                received_data = self.pending_buffer[:buff_size]
                self.pending_buffer = self.pending_buffer[buff_size:]
                return received_data
            else:
                received_data += self.pending_buffer
                self.pending_buffer = b""

        if self.remaining_bytes == 0:
            while True:
                try:
                    data, addr = self.socket.recvfrom(BUFFER_SIZE)
                    parsed = self.parse_segment(data)

                    if parsed and not parsed["ACK"] and not parsed["SYN"] and not parsed["FIN"]:
                        message_length = int.from_bytes(parsed["payload"], "big")
                        self.remaining_bytes = message_length
                        self.expected_seq = parsed["seq"] + len(parsed["payload"])
                        ack_segment = self.create_segment({"ACK": True, "seq": self.expected_seq})
                        self.socket.sendto(ack_segment, addr)
                        break
                except socket.timeout:
                    continue

        bytes_to_receive = min(buff_size - len(received_data), self.remaining_bytes)
        bytes_collected = 0
        while bytes_collected < bytes_to_receive:
            try:
                data, addr = self.socket.recvfrom(BUFFER_SIZE)
                parsed = self.parse_segment(data)

                if parsed and not parsed["ACK"] and not parsed["SYN"] and not parsed["FIN"]:
                    payload = parsed["payload"]
                    if parsed["seq"] == self.expected_seq:
                        received_data += payload
                        bytes_collected += len(payload)
                        self.remaining_bytes -= len(payload)
                        self.expected_seq += len(payload)
                        ack_segment = self.create_segment({"ACK": True, "seq": self.expected_seq})
                        self.socket.sendto(ack_segment, addr)
                    elif parsed["seq"] < self.expected_seq:
                        ack_segment = self.create_segment({"ACK": True, "seq": self.expected_seq})
                        self.socket.sendto(ack_segment, addr)

            except socket.timeout:
                continue

        if len(received_data) > buff_size:
            self.pending_buffer = received_data[buff_size:]
            self.remaining_bytes += len(self.pending_buffer)
            return received_data[:buff_size]

        return received_data
    
    def close(self):
        self.socket.close()

    def recv_close(self):
        raise NotImplementedError  # paso 6
