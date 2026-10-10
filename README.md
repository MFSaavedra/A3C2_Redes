# CC4303 — Actividad 3: sockets orientados a conexión con Stop & Wait

Actividad 3 del curso **Redes (CC4303)**, DCC — Universidad de Chile.
El objetivo es implementar un TCP simplificado: la clase `SocketTCP`, un socket orientado
a conexión que entrega los datos de forma confiable usando Stop & Wait, y un cliente y un
servidor que la usan para enviar un archivo.

**Restricción:** `SocketTCP` debe enviar todo por sockets UDP, así que el handshake, los
ACK, los timeouts y el cierre de conexión están implementados a mano. Solo se usa la
librería estándar de Python.

Integrantes: María Moya G., M. Fernando Saavedra.

## Ejecución

Primero se inicia el servidor, que queda esperando en `accept`, y luego el cliente:

```bash
python3 servidor.py localhost 8000 > recibido.txt
python3 cliente.py localhost 8000 < archivo.txt
```

El cliente envía el archivo como un solo mensaje y cierra la conexión. El servidor escribe
lo recibido en la salida estándar y sus mensajes de estado en stderr, así que
`recibido.txt` queda idéntico al original. Un tercer argumento opcional fija el `buff_size`
de cada `recv` (1024 por omisión), lo que permite probar archivos más largos que el
buffer: `python3 servidor.py localhost 8000 10`.

Las pérdidas se simulan con `netem` sobre loopback. Como afecta a todo el tráfico de `lo`,
hay que quitarlo al terminar:

```bash
sudo tc qdisc add dev lo root netem loss 20.0% delay 0.5s
sudo tc qdisc del dev lo root netem
```

El modo debug se controla con la constante `DEBUG` al inicio de `SocketTCP.py` (activado
por defecto). Imprime en stderr cada timeout, reenvío y segmento descartado, así que solo
muestra algo cuando hay pérdidas.

## Archivos

- **`SocketTCP.py`** — la clase `SocketTCP`: formato de segmento, handshake, `send` y
  `recv` con Stop & Wait, y cierre de conexión.
- **`cliente.py`** — lee un archivo desde la entrada estándar y lo envía al servidor.
- **`servidor.py`** — acepta una conexión, recibe el archivo y lo escribe en la salida
  estándar.
- **`Informe/`** — informe LaTeX de la actividad (`main.tex`). Los diagramas están en
  `Informe/img/` como fuentes `.dot` y se regeneran con `render.sh`.

## Implementación

- **Segmento:** header fijo de 5 bytes (1 byte con los flags ACK, SYN y FIN, y 4 bytes de
  número de secuencia) seguido de a lo más 16 bytes de datos. El socket UDP siempre lee
  con un buffer de 21 bytes, independiente del `buff_size` de `recv`.
- **Handshake:** `connect` elige un número de secuencia inicial aleatorio entre 0 y 100.
  `accept` responde desde un `SocketTCP` nuevo, en un puerto que elige el sistema, y el
  cliente aprende esa dirección del SYN+ACK. Ambos lados reenvían su segmento tras cada
  timeout; si se pierde el último ACK, `accept` toma como confirmación el primer segmento
  de datos o un FIN.
- **Stop & Wait:** timeout fijo de 2 s, mayor que el RTT de ~1 s que produce
  `netem delay 0.5s` en loopback. `send` envía primero el largo del mensaje y luego trozos
  de 16 bytes, reenviando cada uno hasta recibir su ACK. `recv` guarda entre llamadas los
  bytes que faltan del mensaje y el excedente que no cupo en `buff_size`; los segmentos
  duplicados se descartan y se vuelven a confirmar.
- **Cierre:** `close` reenvía el FIN tras cada timeout y se rinde al tercero. Al recibir
  el FIN+ACK envía el ACK final 3 veces, separadas por un timeout, por lo que el cliente
  demora unos segundos en terminar. `recv_close` responde con FIN+ACK y espera ese ACK
  hasta 3 timeouts. Cuando llega el FIN, `recv` retorna `b""`.
