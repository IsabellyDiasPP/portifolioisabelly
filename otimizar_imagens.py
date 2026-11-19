from pathlib import Path
from PIL import Image, ImageOps

ORIGEM = Path("IMG")
DESTINO = Path("IMG_otimizado")

def limite(arq):
    n = arq.stem.lower()
    if n.startswith("feed"):   return 500    # mosaico da câmera (aparece pequeno)
    if n == "camera3":         return 1400   # moldura da câmera
    return 1100                              # projetos, habilidades, etc.

def otimizar(arq):
    ext = arq.suffix.lower()
    img = ImageOps.exif_transpose(Image.open(arq))
    lim = limite(arq)
    if img.width > lim:
        img = img.resize((lim, round(img.height * lim / img.width)), Image.LANCZOS)

    saida = DESTINO / arq.relative_to(ORIGEM)
    saida.parent.mkdir(parents=True, exist_ok=True)

    if ext in (".jpg", ".jpeg"):
        img.convert("RGB").save(saida, "JPEG", quality=72, optimize=True, progressive=True)
    else:  # PNG -> WebP (mantém transparência)
        saida = saida.with_suffix(".webp")
        img.save(saida, "WEBP", quality=80, method=6)

    print(f"{arq.name}: {arq.stat().st_size/1024:,.0f} KB -> {saida.stat().st_size/1024:,.0f} KB")

for arq in sorted(ORIGEM.rglob("*")):
    if arq.is_file() and arq.suffix.lower() in {".jpg", ".jpeg", ".png"}:
        try: otimizar(arq)
        except Exception as e: print("Pulei", arq.name, e)