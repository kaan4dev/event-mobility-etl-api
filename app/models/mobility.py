from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Literal, Any

from pydantic import BaseModel, Field, field_validator, model_validator

UserType = Literal["Subsriber", "Customer", "Unknown"]

def _to_none_if_blank(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    return v

def _parse_dt(value: str) -> datetime:
    value = value.strip()
    fmts = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.replace(tzinfo = timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized datetime format: {value!r}")