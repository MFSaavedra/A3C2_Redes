import socket
import sys
 
print('Creando socket - Servidor UDP')
new_socket_adress = ('localhost', 8000)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(new_socket_adress)
print(f"Servidor escuchando en {new_socket_adress[0]}:{new_socket_adress[1]}")
buffer_size = 1024

try:
    while True:
        data, client_address = server_socket.recvfrom(buffer_size)
        if not data:
            break
        sys.stdout.write(data.decode('utf-8', errors='ignore'))
        sys.stdout.flush()

except KeyboardInterrupt:
    print("\nServidor detenido por el usuario.")
finally:
    server_socket.close()