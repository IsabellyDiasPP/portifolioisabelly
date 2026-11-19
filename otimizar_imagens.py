"""
Otimiza as imagens da pasta IMG sem mudar nenhum nome de arquivo.
Nada é sobrescrito: o resultado vai para a pasta IMG_otimizado.

Uso (na pasta do portfólio, onde está o index.html):
    pip install pillow
    python otimizar_imagens.py

Novidades desta versão:
  - fotos do mosaico (feed*) em 420 px, qualidade 70
  - CAMERA3 também sai em WebP com transparência (muito mais leve)
  - nunca grava um arquivo maior que o original
"""
import shutil
from pathlib import Path
from PIL import Image, ImageOps

ORIGEM = Path("IMG")
DESTINO = Path("IMG_otimizado")
EXTS = {".jpg", ".jpeg", ".png"}

LARGURA_FEED = 420      # mosaico da câmera (aparece com ~175 px)
LARGURA_CAMERA = 1400   # imagem da câmera (máx. ~960 px na tela)
LARGURA_GERAL = 1200    # projetos, habilidades, etc.

QUALIDADE_FEED = 70
QUALIDADE_GERAL = 80
QUALIDADE_WEBP = 85


def limite_para(arq: Path):
    nome = arq.stem.lower()
    if nome.startswith("feed"):
        return LARGURA_FEED, QUALIDADE_FEED
    if nome.startswith("camera"):
        return LARGURA_CAMERA, QUALIDADE_GERAL
    return LARGURA_GERAL, QUALIDADE_GERAL


def otimizar(arq: Path):
    ext = arq.suffix.lower()
    limite, qualidade = limite_para(arq)

    img = Image.open(arq)
    img = ImageOps.exif_transpose(img)  # corrige fotos de celular giradas

    if img.width > limite:
        altura = round(img.height * limite / img.width)
        img = img.resize((limite, altura), Image.LANCZOS)

    saida = DESTINO / arq.relative_to(ORIGEM)
    saida.parent.mkdir(parents=True, exist_ok=True)

    if ext in (".jpg", ".jpeg"):
        img.convert("RGB").save(saida, "JPEG", quality=qualidade,
                                optimize=True, progressive=True)
    else:
        img.save(saida, "PNG", optimize=True)

    # nunca deixa o arquivo "otimizado" maior que o original
    if saida.stat().st_size >= arq.stat().st_size:
        shutil.copy2(arq, saida)

    # câmera: gera também a versão WebP com transparência
    if arq.stem.lower().startswith("camera") and ext == ".png":
        webp = saida.with_suffix(".webp")
        img.convert("RGBA").save(webp, "WEBP", quality=QUALIDADE_WEBP, method=6)
        print(f"   + {webp.name}: {webp.stat().st_size / 1024:,.0f} KB")

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