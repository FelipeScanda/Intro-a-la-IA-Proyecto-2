# Darle permisos chmod 600 Archivo.sh o usar directamente el comando debajo

#!/bin/bash
curl -L -o ./fruit-image-dataset-22-classes.zip\
  https://www.kaggle.com/api/v1/datasets/download/mdsagorahmed/fruit-image-dataset-22-classes

unzip fruit-image-dataset-22-classes.zip