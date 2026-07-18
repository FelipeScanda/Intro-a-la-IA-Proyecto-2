from pathlib import Path
import random
import shutil
import re


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Carpeta que contiene:
# ripe apple/, unripe apple/, ripe banana/, etc.
SOURCE_DIR = Path("./Ripe & Unripe Fruits")

# Carpeta donde se creará el dataset organizado
OUTPUT_DIR = Path("dataset")

# Proporciones de la división
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Permite obtener siempre la misma división
RANDOM_SEED = 42

# Formatos de imagen aceptados
VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp"
}


# ============================================================
# VALIDACIONES INICIALES
# ============================================================

if not SOURCE_DIR.exists():
    raise FileNotFoundError(
        f"No se encontró la carpeta de origen: {SOURCE_DIR.resolve()}"
    )

if round(TRAIN_RATIO + VAL_RATIO + TEST_RATIO, 10) != 1.0:
    raise ValueError(
        "Las proporciones de train, val y test deben sumar 1."
    )

random.seed(RANDOM_SEED)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_clase(nombre_carpeta: str) -> str | None:
    """
    Determina si una carpeta corresponde a frutas maduras
    o inmaduras.

    Ejemplos:
        'ripe apple'     -> 'ripe'
        'unripe apple'   -> 'unripe'
        'ripe banana'    -> 'ripe'
        'unripe mango'   -> 'unripe'
    """

    nombre = nombre_carpeta.strip().lower()

    # Es importante revisar primero "unripe"
    # porque contiene la palabra "ripe".
    if nombre.startswith("unripe"):
        return "unripe"

    if nombre.startswith("ripe"):
        return "ripe"

    return None


def limpiar_nombre(texto: str) -> str:
    """
    Convierte un nombre en uno seguro para utilizarlo
    como parte del nombre de un archivo.

    Ejemplo:
        'ripe apple' -> 'ripe_apple'
    """

    texto = texto.strip().lower()
    texto = re.sub(r"\s+", "_", texto)
    texto = re.sub(r"[^a-z0-9_-]", "", texto)

    return texto


def dividir_imagenes(imagenes: list[Path]):
    """
    Mezcla y divide una lista de imágenes en:
    entrenamiento, validación y prueba.
    """

    imagenes = imagenes.copy()
    random.shuffle(imagenes)

    total = len(imagenes)

    cantidad_train = int(total * TRAIN_RATIO)
    cantidad_val = int(total * VAL_RATIO)

    train = imagenes[:cantidad_train]

    val = imagenes[
        cantidad_train:
        cantidad_train + cantidad_val
    ]

    test = imagenes[
        cantidad_train + cantidad_val:
    ]

    return {
        "train": train,
        "val": val,
        "test": test
    }


# ============================================================
# CREAR CARPETAS DE SALIDA
# ============================================================

for split in ["train", "val", "test"]:
    for clase in ["ripe", "unripe"]:
        carpeta_destino = OUTPUT_DIR / split / clase
        carpeta_destino.mkdir(parents=True, exist_ok=True)


# ============================================================
# PROCESAR CADA CARPETA DE FRUTA
# ============================================================

resumen = {
    "train": {
        "ripe": 0,
        "unripe": 0
    },
    "val": {
        "ripe": 0,
        "unripe": 0
    },
    "test": {
        "ripe": 0,
        "unripe": 0
    }
}

carpetas_ignoradas = []

for carpeta_fruta in sorted(SOURCE_DIR.iterdir()):

    # Ignorar archivos que estén directamente en SOURCE_DIR
    if not carpeta_fruta.is_dir():
        continue

    clase = obtener_clase(carpeta_fruta.name)

    if clase is None:
        carpetas_ignoradas.append(carpeta_fruta.name)
        continue

    imagenes = [
        archivo
        for archivo in carpeta_fruta.iterdir()
        if archivo.is_file()
        and archivo.suffix.lower() in VALID_EXTENSIONS
    ]

    if len(imagenes) == 0:
        print(
            f"Advertencia: la carpeta '{carpeta_fruta.name}' "
            "no contiene imágenes válidas."
        )
        continue

    divisiones = dividir_imagenes(imagenes)

    nombre_carpeta_limpio = limpiar_nombre(carpeta_fruta.name)

    for split, archivos in divisiones.items():

        carpeta_destino = OUTPUT_DIR / split / clase

        for indice, archivo in enumerate(archivos, start=1):

            # Se cambia el nombre para evitar colisiones.
            #
            # Por ejemplo, probablemente existen:
            # ripe apple/1.jpg
            # ripe banana/1.jpg
            #
            # Si ambas se copiasen como "1.jpg", una podría
            # sobrescribir a la otra.
            nuevo_nombre = (
                f"{nombre_carpeta_limpio}_"
                f"{indice:05d}"
                f"{archivo.suffix.lower()}"
            )

            destino = carpeta_destino / nuevo_nombre

            # Copia la imagen sin eliminar la original
            shutil.copy2(archivo, destino)

            resumen[split][clase] += 1

    print(f"\nCarpeta procesada: {carpeta_fruta.name}")
    print(f"Clase asignada: {clase}")
    print(f"Total: {len(imagenes)}")
    print(f"Train: {len(divisiones['train'])}")
    print(f"Val: {len(divisiones['val'])}")
    print(f"Test: {len(divisiones['test'])}")


# ============================================================
# MOSTRAR RESUMEN FINAL
# ============================================================

print("\n" + "=" * 50)
print("RESUMEN FINAL")
print("=" * 50)

for split in ["train", "val", "test"]:
    ripe = resumen[split]["ripe"]
    unripe = resumen[split]["unripe"]
    total = ripe + unripe

    print(f"\n{split.upper()}")
    print(f"  Ripe:   {ripe}")
    print(f"  Unripe: {unripe}")
    print(f"  Total:  {total}")

if carpetas_ignoradas:
    print("\nCarpetas ignoradas porque no comienzan con ripe o unripe:")

    for nombre in carpetas_ignoradas:
        print(f"  - {nombre}")

print(f"\nDataset creado en: {OUTPUT_DIR.resolve()}")