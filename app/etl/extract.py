import csv 
import io
from typing import Iterable, Dict, Any
from fastapi import UploadFile

async def iter_csv_rows(file: UploadFile) -> Iterable[Dict[str, Any]]:
    content = await file.read()
    text = content.decode("utf-8", errors = "replace")
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        yield row