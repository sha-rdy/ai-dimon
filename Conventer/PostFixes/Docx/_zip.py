from __future__ import annotations

import os
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from zipfile import ZIP_DEFLATED, ZipFile

class DocxZipWorkspace:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._tmpdir = Path(mkdtemp())
        self._tmp_zip = path.with_suffix(path.suffix + ".tmp")
        self._dirty = False

    def __enter__(self) -> "DocxZipWorkspace":
        with ZipFile(self._path, "r") as z:
            z.extractall(self._tmpdir)
        return self
    @property
    def tmpdir(self) -> Path:
        """Папка, куда распакован DOCX. Править файлы только здесь."""
        return self._tmpdir
    
    def mark_dirty(self) -> None:
        self._dirty = True

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is None and self._dirty:
                with ZipFile(self._tmp_zip, "w", ZIP_DEFLATED) as zout:
                    for f in sorted(self._tmpdir.rglob("*")):
                        if f.is_file():
                            zout.write(f, str(f.relative_to(self._tmpdir)))
                os.replace(self._tmp_zip, self._path)
        finally:
            rmtree(self._tmpdir, ignore_errors=True)
            if self._tmp_zip.exists():
                self._tmp_zip.unlink(missing_ok=True)

def open_docx_zip(path: Path) -> DocxZipWorkspace:
    return DocxZipWorkspace(path)