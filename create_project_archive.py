#!/usr/bin/env python3
"""
create_project_archive.py

Genera un archivo ZIP en la raíz del repositorio con el nombre
<project_name>-YYYYMMDDHHMMSS.zip incluyendo todo el proyecto excepto:
 - caches: __pycache__, .pytest_cache, .mypy_cache
 - entornos virtuales: .venv, venv
 - metadatos de control de versiones y builds: .git, build, dist
 - carpetas de IDE: .vscode, .idea

Uso:
    python create_project_archive.py

El archivo resultante se crea en la misma carpeta donde está este script.
"""
from __future__ import annotations

import zipfile
from datetime import datetime
from pathlib import Path
import sys


EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
    "node_modules",
    "build",
    "dist",
}

EXCLUDE_EXTS = {".pyc", ".pyo", ".egg-info"}


def should_exclude(path: Path, root: Path, archive_name: str) -> bool:
    """Decide si `path` debe excluirse del archive.
    path: absoluta
    root: carpeta raíz del proyecto
    """
    try:
        rel = path.relative_to(root)
    except Exception:
        return True

    # No incluir el archivo de salida si existe en la carpeta
    if rel.as_posix() == archive_name:
        return True

    # Excluir por extensión
    if path.suffix in EXCLUDE_EXTS:
        return True

    # Excluir si alguna parte del path está en EXCLUDE_DIRS
    for part in rel.parts:
        if part in EXCLUDE_DIRS:
            return True

    return False


def create_archive():
    root = Path(__file__).resolve().parent
    project_name = root.name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_filename = f"{project_name}-{timestamp}.zip"

    archive_path = root / archive_filename

    print(f"Creando archivo: {archive_path}")

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in root.rglob("*"):
            if p.is_dir():
                continue

            if should_exclude(p, root, archive_filename):
                # print(f"Excluyendo: {p}")
                continue

            arcname = p.relative_to(root).as_posix()
            zf.write(p, arcname)

    print(f"Archivo creado: {archive_path}")
    return archive_path


def main() -> int:
    try:
        archive = create_archive()
        print("Hecho.")
        print(f"Tamaño: {archive.stat().st_size} bytes")
        return 0
    except Exception as e:
        print("Error al crear el archivo:", e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
