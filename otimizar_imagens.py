"""
Reduz o peso das imagens da pasta IMG sem mudar nenhum nome de arquivo.
Nada é sobrescrito: tudo vai para a pasta IMG_otimizado (já completa,
com vídeo, PDFs e demais arquivos copiados).

Como usar (na pasta do portfólio, onde está o index.html):
    pip install pillow
    python otimizar_imagens.py
Depois confira a pasta IMG_otimizado e, se estiver tudo certo,
troque a IMG por ela (guarde uma cópia da IMG original).
"""
import shutil
from pathlib import Path
from PIL import Image, ImageOps

ORIGEM = Path("IMG")
DESTINO = Path("IMG_otimizado")
EXTS = {".jpg", ".jpeg", ".png"}

LARGURA_FEED = 700      # fotos do mosaico da câmera (aparecem bem pequenas)
LARGURA_GERAL = 1600    # projetos, habilidades, etc.
QUALIDADE_JPG = 80


def otimizar(arq: Path, saida: Path):
    ext = arq.suffix.lower()
    limite = LARGURA_FEED if arq.stem.lower().startswith("feed") else LARGURA_GERAL

    img = Image.open(arq)
    img = ImageOps.exif_transpose(img)  # corrige fotos de celular giradas

    if img.width > limite:
        altura = round(img.height * limite / img.width)
        img = img.resize((limite, altura), Image.LANCZOS)

    if ext in (".jpg", ".jpeg"):
        img.convert("RGB").save(saida, "JPEG", quality=QUALIDADE_JPG,
                                optimize=True, progressive=True)
    else:
        # PNG: mantém a transparência (a câmera precisa dela)
        if img.mode not in ("RGB", "RGBA", "L", "LA", "P"):
            img = img.convert("RGBA")
        img.save(saida, "PNG", optimize=True)

    antes = arq.stat().st_size
    depois = saida.stat().st_size

    # se não ficou menor, mantém o original
    if depois >= antes:
        shutil.copy2(arq, saida)
        print(f"{arq.name}: {antes/1024:,.0f} KB (mantido, já estava leve)")
    else:
        print(f"{arq.name}: {antes/1024:,.0f} KB -> {depois/1024:,.0f} KB")


def main():
    if not ORIGEM.exists():
        print("Pasta IMG não encontrada. Rode o script na pasta do portfólio.")
        return

    total_antes = total_depois = 0

    for arq in sorted(ORIGEM.rglob("*")):
        if not arq.is_file():
            continue

        saida = DESTINO / arq.relative_to(ORIGEM)
        saida.parent.mkdir(parents=True, exist_ok=True)

        try:
            if arq.suffix.lower() in EXTS:
                otimizar(arq, saida)
            else:
                shutil.copy2(arq, saida)  # vídeo, PDF, svg etc.: só copia
                print(f"{arq.name}: copiado sem alterar")
        except Exception as erro:
            shutil.copy2(arq, saida)      # na dúvida, copia o original
            print(f"{arq.name}: erro ({erro}), original copiado")

        total_antes += arq.stat().st_size
        total_depois += saida.stat().st_size

    print(f"\nTOTAL: {total_antes/1e6:,.1f} MB -> {total_depois/1e6:,.1f} MB")


if __name__ == "__main__":
    main()