#!/bin/bash

# convertimos a png
mogrify -format png *.jpg *.jpeg

mkdir thumbs
mogrify -resize 120x120 -background transparent -gravity center -path thumbs -extent 120x120  -quality 75 *


# pasamos todo a 640 de ancho, altura proporcional
mogrify -resize 640x  *



# borramos los restos
rm *.jpg *.jpeg

# redimensionamos el thumb
mogrify -resize 120x120 -background transparent -gravity center -extent 120x120  -quality 75  thumb.png
