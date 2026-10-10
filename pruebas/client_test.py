# Contraparte de server_test.py: Tests 1-3 del enunciado, Test 4 y el cierre
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import SocketTCP

address = ("localhost", 8000)

# CLIENT
client_socketTCP = SocketTCP.SocketTCP()
client_socketTCP.connect(address)
# test 1
message = "Mensje de len=16".encode()
client_socketTCP.send(message)
# test 2
message = "Mensaje de largo 19".encode()
client_socketTCP.send(message)
# test 3
message = "Mensaje de largo 19".encode()
client_socketTCP.send(message)
# test 4
message = "Mensaje de largo 42, recibido en 2 mitades".encode()
client_socketTCP.send(message)

client_socketTCP.close()
print("Conexión cerrada")
