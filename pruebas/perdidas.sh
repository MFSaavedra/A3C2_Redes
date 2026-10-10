#!/bin/sh
# Prueba con pérdidas: envía pruebas/archivo.txt de cliente.py a servidor.py N veces (5 por omisión)
# y revisa que el archivo llegue idéntico y que ambos lados cierren. Se corre con netem activo en lo:
#   sudo tc qdisc add dev lo root netem loss 20.0% delay 0.5s
#   sh pruebas/perdidas.sh [N]
#   sudo tc qdisc del dev lo root netem
# El stderr de cada ejecución (con el modo debug) queda en pruebas/salida/
cd "$(dirname "$0")/.." || exit 1
mkdir -p pruebas/salida
tc qdisc show dev lo | grep -q netem || echo "Aviso: netem no está activo en lo, así que no habrá pérdidas"
: > pruebas/salida/perdidas.txt

for i in $(seq "${1:-5}"); do
    start=$(date +%s)
    timeout 120 python3 servidor.py localhost 8000 > "pruebas/salida/recibido_$i.txt" 2> "pruebas/salida/servidor_$i.log" &
    server_pid=$!
    sleep 0.5
    timeout 120 python3 cliente.py localhost 8000 < pruebas/archivo.txt 2> "pruebas/salida/cliente_$i.log"
    client_status=$?
    wait "$server_pid"
    server_status=$?

    cmp -s pruebas/archivo.txt "pruebas/salida/recibido_$i.txt" && file="íntegro" || file="distinto"
    [ "$client_status" -eq 0 ] && client="cerró" || client="no cerró"
    [ "$server_status" -eq 0 ] && server="cerró" || server="no cerró"
    echo "Ejecución $i ($(( $(date +%s) - start )) s): archivo $file, cliente $client, servidor $server" | tee -a pruebas/salida/perdidas.txt
done
