"""
Reduz o peso das imagens da pasta IMG sem mudar nenhum nome de arquivo.
Nada é sobrescrito: as novas imagens vão para a pasta IMG_otimizado.

Como usar (na pasta do portfólio, onde está o index.html):
    pip install pillow
    python otimizar_imagens.py
Depois confira a pasta IMG_otimizado e, se estiver tudo certo,
troque o conteúdo de IMG pelo dela (guarde uma cópia da IMG original).
"""
from pathlib import Path
from PIL import Image, ImageOps

ORIGEM = Path("IMG")
DESTINO = Path("IMG_otimizado")
EXTS = {".jpg", ".jpeg", ".png"}

LARGURA_FEED = 700      # fotos do mosaico da câmera (aparecem bem pequenas)
LARGURA_GERAL = 1600    # projetos, habilidades, etc.
QUALIDADE_JPG = 80


def otimizar(arq: Path):
    ext = arq.suffix.lower()
    limite = LARGURA_FEED if arq.stem.lower().startswith("feed") else LARGURA_GERAL

    img = Image.open(arq)
    img = ImageOps.exif_transpose(img)  # corrige fotos de celular giradas

    if img.width > limite:
        altura = round(img.height * limite / img.width)
        img = img.resize((limite, altura), Image.LANCZOS)

    saida = DESTINO / arq.relative_to(ORIGEM)
    saida.parent.mkdir(parents=True, exist_ok=True)

    if ext in (".jpg", ".jpeg"):
        img.convert("RGB").save(saida, "JPEG", quality=QUALIDADE_JPG,
                                optimize=True, progressive=True)
    else:
        img.save(saida, "PNG", optimize=True)

    antes = arq.stat().st_size / 1024
    depois = saida.stat().st_size / 1024
    print(f"{arq.name}: {antes:,.0f} KB -> {depois:,.0f} KB")


def main():
    if not ORIGEM.exists():
        print("Pasta IMG não encontrada. Rode o script na pasta do portfólio.")
        return
    for arq in sorted(ORIGEM.rglob("*")):
        if arq.is_file() and arq.suffix.lower() in EXTS:
            try:
                otimizar(arq)
            except Exception as erro:
                print(f"Pulei {arq.name}: {erro}")


if __name__ == "__main__":
    main()
