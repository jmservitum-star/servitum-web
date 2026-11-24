#!/usr/bin/env python3
"""Externaliza imágenes base64 del HTML de Servitum sin alterar contenido ni diseño."""
from pathlib import Path
import base64
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "index.html"
DEST = ROOT / "assets" / "imagenes"
PATTERN = re.compile(r"data:image/(webp|png|jpeg|svg\+xml);base64,([A-Za-z0-9+/=]+)")
EXT = {"webp": "webp", "png": "png", "jpeg": "jpg", "svg+xml": "svg"}

def main():
    html = PAGE.read_text(encoding="utf-8")
    matches = list(PATTERN.finditer(html))
    if not matches:
        print("Sin imágenes incrustadas: no se necesita conversión.")
        return
    if len(matches) < 300:
        raise RuntimeError(f"Solo se detectaron {len(matches)} imágenes; abortando por seguridad.")
    DEST.mkdir(parents=True, exist_ok=True)
    unique = {}
    def externalize(match):
        kind, encoded = match.groups()
        raw = base64.b64decode(encoded, validate=True)
        digest = hashlib.sha256(raw).hexdigest()[:20]
        name = f"{digest}.{EXT[kind]}"
        path = DEST / name
        if path.exists() and path.read_bytes() != raw:
            raise RuntimeError("Colisión de imagen; no se modifica la página")
        if not path.exists():
            path.write_bytes(raw)
        unique[name] = len(raw)
        return "assets/imagenes/" + name
    result = PATTERN.sub(externalize, html)
    if PATTERN.search(result):
        raise RuntimeError("Quedaron imágenes incrustadas sin convertir")
    for name in unique:
        if not (DEST / name).is_file():
            raise RuntimeError("Archivo de imagen faltante: " + name)
    if len(result) >= len(html) // 2:
        raise RuntimeError("La reducción del HTML no alcanzó el umbral esperado")
    PAGE.write_text(result, encoding="utf-8")
    print(f"Imágenes: {len(matches)} referencias, {len(unique)} archivos únicos.")
    print(f"HTML: {len(html):,} -> {len(result):,} caracteres.")
    print("Conservados los enlaces, productos, textos, estilos y scripts originales.")

if __name__ == "__main__":
    main()
