import socket
import sys
import SocketTCP

print('Creando socket - Servidor UDP')
new_socket_adress = ('localhost', 8000)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(new_socket_adress)
print(f"Servidor escuchando en {new_socket_adress[0]}:{new_socket_adress[1]}", flush=True)
buffer_size = SocketTCP.BUFFER_SIZE

try:
    while True:
        data, client_address = server_socket.recvfrom(buffer_size)
        if not data:
            break
        payload = SocketTCP.SocketTCP.parse_segment(data)["payload"]
        # bytes crudos: decodificar cada trozo por separado corta los caracteres de 2+ bytes (ñ, tildes)
        sys.stdout.buffer.write(payload)
        sys.stdout.buffer.flush()

except KeyboardInterrupt:
    print("\nServidor detenido por el usuario.")
finally:
    server_socket.close()