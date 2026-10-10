# Tests 1-3 del apartado "Test send y recv" del enunciado, más un Test 4 (recv con buff_size menor
# que message_length) y el cierre. Se corre junto a client_test.py con: sh pruebas/sin_perdidas.sh
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import SocketTCP

address = ("localhost", 8000)

# SERVER
server_socketTCP = SocketTCP.SocketTCP()
server_socketTCP.bind(address)
connection_socketTCP, new_address = server_socketTCP.accept()

# test 1
buff_size = 16
full_message = connection_socketTCP.recv(buff_size)
print("Test 1 received:", full_message)
if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
else: print("Test 1: Failed")

# test 2
buff_size = 19
full_message = connection_socketTCP.recv(buff_size)
print("Test 2 received:", full_message)
if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
else: print("Test 2: Failed")

# test 3
buff_size = 14
message_part_1 = connection_socketTCP.recv(buff_size)
message_part_2 = connection_socketTCP.recv(buff_size)
print("Test 3 received:", message_part_1 + message_part_2)
if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): print("Test 3: Passed")
else: print("Test 3: Failed")

# test 4: mensaje de 2n = 42 bytes leído con dos recv(n), con n = 21 (no es múltiplo de 16)
buff_size = 21
message_part_1 = connection_socketTCP.recv(buff_size)
message_part_2 = connection_socketTCP.recv(buff_size)
print("Test 4 received part 1:", message_part_1, f"({len(message_part_1)} bytes)")
print("Test 4 received part 2:", message_part_2, f"({len(message_part_2)} bytes)")
if (message_part_1 + message_part_2) == "Mensaje de largo 42, recibido en 2 mitades".encode(): print("Test 4: Passed")
else: print("Test 4: Failed")

connection_socketTCP.recv_close()
print("Conexión cerrada")
