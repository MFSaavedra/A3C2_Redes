import sys
import SocketTCP

# Uso: python3 servidor.py <host> <puerto> [buff_size]
# Recibe un archivo de un cliente y lo escribe en la salida estándar. Los mensajes de estado van a
# stderr, así que `python3 servidor.py localhost 8000 > recibido.txt` deja solo el archivo.
# buff_size (1024 por omisión) es el tamaño de cada recv: con un archivo de 2n bytes y buff_size n se
# prueba que recv entrega el mensaje en partes

if len(sys.argv) not in (3, 4):
    sys.exit("Uso: python3 servidor.py <host> <puerto> [buff_size]")

address = (sys.argv[1], int(sys.argv[2]))
buff_size = int(sys.argv[3]) if len(sys.argv) == 4 else 1024

server_socketTCP = SocketTCP.SocketTCP()
server_socketTCP.bind(address)
print(f"Servidor escuchando en {address[0]}:{address[1]}", file=sys.stderr)
connection_socketTCP, new_address = server_socketTCP.accept()
print(f"Conexión aceptada, atendida en {new_address[0]}:{new_address[1]}", file=sys.stderr)

# recv retorna b"" cuando llega el FIN del cliente, como un socket TCP cuando se cierra la conexión.
# Se escriben bytes crudos: un recv puede cortar un carácter de 2+ bytes (ñ, tildes)
received = 0
while data := connection_socketTCP.recv(buff_size):
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()
    received += len(data)

connection_socketTCP.recv_close()
server_socketTCP.close()
print(f"Recibidos {received} bytes, conexión cerrada", file=sys.stderr)
