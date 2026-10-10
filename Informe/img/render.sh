#!/bin/sh
# Genera el PDF de cada diagrama .dot de esta carpeta. Las posiciones van fijas en puntos
# (neato -n2) y la fuente es la del informe, Latin Modern: viene con TeX, pero fontconfig
# no la ve, así que se le pasa una configuración que agrega esa carpeta.
cd "$(dirname "$0")" || exit 1
conf=$(mktemp)
trap 'rm -f "$conf"' EXIT
printf '<fontconfig><include ignore_missing="yes">/etc/fonts/fonts.conf</include><dir>%s</dir></fontconfig>\n' \
    "$(dirname "$(kpsewhich lmroman10-regular.otf)")" > "$conf"
for dot in *.dot; do
    FONTCONFIG_FILE=$conf neato -n2 -Tpdf "$dot" -o "${dot%.dot}.pdf" || exit 1
done
