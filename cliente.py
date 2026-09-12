import socket
 
print('Creando socket - Cliente UDP')
 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = ('localhost', 8000)
file_path = input("Ingrese la ruta del archivo a enviar: ")

try:
    with open(file_path, 'rb') as file:
        file_data = file.read()
    chunk_size = 16
    print(f"... Mandando el archivo: {file_path}")
    for i in range(0, len(file_data), chunk_size):
        chunk = file_data[i:i+chunk_size]
        client_socket.sendto(chunk, address)

    print("... Archivo enviado")

except Exception as e:
    print(f"Error al enviar el archivo: {e}")
finally:
    client_socket.close()