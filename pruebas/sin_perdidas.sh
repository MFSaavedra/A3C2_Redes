#!/bin/sh
# Prueba sin pérdidas: Tests 1-3 del enunciado, Test 4 (buff_size < message_length) y cierre.
#   sh pruebas/sin_perdidas.sh
# La salida de cada lado queda también en pruebas/salida/
cd "$(dirname "$0")/.." || exit 1
mkdir -p pruebas/salida
tc qdisc show dev lo | grep -q netem && echo "Aviso: netem está activo en lo y esta prueba es sin pérdidas"

python3 pruebas/server_test.py > pruebas/salida/servidor_sin_perdidas.txt 2>&1 &
sleep 0.5
python3 pruebas/client_test.py > pruebas/salida/cliente_sin_perdidas.txt 2>&1
wait

echo "--- servidor"; cat pruebas/salida/servidor_sin_perdidas.txt
echo "--- cliente"; cat pruebas/salida/cliente_sin_perdidas.txt
