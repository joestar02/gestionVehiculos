import os
import logging
import uuid
from typing import Optional, Tuple
from werkzeug.utils import secure_filename
from app.utils.exceptions import UploadError

logger = logging.getLogger(__name__)


def parse_money(value: Optional[str]) -> Optional[float]:
    """Parse a monetary input string into float, accepting commas and dots.

    Returns None for empty/None input. Raises ValueError for invalid format.
    """
    if not value:
        return None
    s = value.strip().replace(' ', '')
    # if both dot and comma present, assume dot is thousands and comma decimal
    if '.' in s and ',' in s:
        s = s.replace('.', '').replace(',', '.')
    else:
        s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        raise ValueError(f'Formato de precio inválido: {value}')


def save_uploaded_file(file_storage, upload_dir: str, allowed_ext: set, max_bytes: int) -> Tuple[str, int]:
    """Validate and save an uploaded file.

    Returns tuple (relative_path, size_bytes).
    Raises UploadError on validation failure.
    """
    if not file_storage or not getattr(file_storage, 'filename', None):
        err_id = uuid.uuid4().hex[:8]
        logger.error('[%s] No file provided for upload', err_id)
        raise UploadError(f'No se proporcionó archivo (id={err_id})')

    filename = secure_filename(file_storage.filename)
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext not in allowed_ext:
        err_id = uuid.uuid4().hex[:8]
        logger.error('[%s] Disallowed extension: %s', err_id, ext)
        raise UploadError(f'Tipo de archivo no permitido (id={err_id})')

    # Determine size safely
    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > max_bytes:
        err_id = uuid.uuid4().hex[:8]
        logger.error('[%s] File too large: %d bytes (max %d)', err_id, size, max_bytes)
        raise UploadError(f'El fichero excede el tamaño máximo permitido (id={err_id})')

    os.makedirs(upload_dir, exist_ok=True)
    # create unique filename
    base = os.path.splitext(filename)[0]
    unique_name = f"{base}_{os.urandom(8).hex()}{ext}"
    save_path = os.path.join(upload_dir, unique_name)
    file_storage.save(save_path)
    logger.info('Saved uploaded file to %s (%d bytes)', save_path, size)

    # return relative path (under static) and size
    rel_path = os.path.join('uploads', os.path.basename(upload_dir), unique_name).replace('\\', '/')
    return rel_path, size
