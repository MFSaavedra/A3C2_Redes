import sys
import SocketTCP

# Uso: python3 cliente.py <host> <puerto> < archivo
# Envía todo lo que llega por la entrada estándar como un solo mensaje y luego cierra la conexión.
# Los mensajes de estado van a stderr

if len(sys.argv) != 3:
    sys.exit("Uso: python3 cliente.py <host> <puerto> < archivo")

address = (sys.argv[1], int(sys.argv[2]))
file_data = sys.stdin.buffer.read()  # bytes crudos: el archivo no tiene por qué ser texto

client_socketTCP = SocketTCP.SocketTCP()
client_socketTCP.connect(address)
print(f"Conectado a {address[0]}:{address[1]}, enviando {len(file_data)} bytes", file=sys.stderr)
client_socketTCP.send(file_data)
client_socketTCP.close()
print("Archivo enviado y conexión cerrada", file=sys.stderr)
