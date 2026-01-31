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

class RawTripRow(BaseModel):
    tripduration: Optional[str] = None
    starttime: Optional[str] = None
    stoptime: Optional[str] = None

    start_station_id: Optional[str] = Field(default=None, alias="start station id")
    start_station_name: Optional[str] = Field(default=None, alias="start station name")
    start_station_latitude: Optional[str] = Field(default=None, alias="start station latitude")
    start_station_longitude: Optional[str] = Field(default=None, alias="start station longitude")

    end_station_id: Optional[str] = Field(default=None, alias="end station id")
    end_station_name: Optional[str] = Field(default=None, alias="end station name")
    end_station_latitude: Optional[str] = Field(default=None, alias="end station latitude")
    end_station_longitude: Optional[str] = Field(default=None, alias="end station longitude")

    bikeid: Optional[str] = None
    usertype: Optional[str] = None
    birth_year: Optional[str] = Field(default=None, alias="birth year")
    gender: Optional[str] = None

    @field_validator("*", mode="before")
    @classmethod
    def blank_to_none(cls, v):
        return _to_none_if_blank(v)
    
class StagedTrip(BaseModel):
    tripduration_seconds: int
    started_at: datetime
    stopped_at: datetime

    start_station_id: Optional[int] = None
    start_station_name: Optional[str] = None
    start_lat: Optional[float] = None
    start_lng: Optional[float] = None

    end_station_id: Optional[int] = None
    end_station_name: Optional[str] = None
    end_lat: Optional[float] = None
    end_lng: Optional[float] = None

    bike_id: Optional[int] = None
    usertype: UserType = "Unknown"
    birth_year: Optional[int] = None
    gender: Optional[int] = None

    start_date: str
    start_hour: int

    dq_flags: dict = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def build_from_row(cls, data):
        raw = data

        dq: dict = {}

        if not raw.get("starttime") or not raw.get("stoptime"):
            raise ValueError("Missing starttime or stoptime.")
        started = _parse_dt(raw["starttime"])
        stopped = _parse_dt(raw["stopptime"])

        if stopped < started:
            dq["time_inversion"] = True

        computed = int((stopped-started).total_seconds())
        if computed < 0:
            dq["negative_duration_computed"] = True
            computed = abs(computed)

        provider_dur = None
        if raw.get("tripduration"):
            try:
                provider_dur = int(float(raw["tripduration"]))
            except Exception:
                dq["bad_tripduration_format"] = True

        if provider_dur is not None:
            if abs(provider_dur - computed) > 300:  # 5 minutes diff
                dq["duration_mismatch"] = {"provider": provider_dur, "computed": computed}
                    
            if provider_dur > 24 * 3600:
                dq["provider_duration_gt_24h"] = provider_dur

        duration_seconds = computed
        if duration_seconds == 0:
            dq["zero_duration"] = True

        def to_int(v):
            if v is None:
                return None
            try:
                return int(float(v))
            except Exception:
                return None
        
        def to_float(v):
            if v is None:
                return None
            try:
                return float(v)
            except Exception:
                return None
            
        start_lat = to_float(raw.get("start station latitude"))
        start_lng = to_float(raw.get("start station longitude"))
        end_lat = to_float(raw.get("end station latitude"))
        end_lng = to_float(raw.get("end station longitude"))

        def valid_latling(lat, lng):
            if lat is None or lng is None:
                return False
            return -90 <= lat <= 90 and -180 <= lng <= 180
        
        if start_lat is not None and start_lng is not None and not valid_latlng(start_lat, start_lng):
            dq["bad_start_geo"] = True
            start_lat, start_lng = None, None

        if end_lat is not None and end_lng is not None and not valid_latlng(end_lat, end_lng):
            dq["bad_end_geo"] = True
            end_lat, end_lng = None, None

        ut = raw.get("usertype")
        if ut is None:
            usertype = "Unknown"
        else:
            ut2 = ut.strip().lower()
            if ut2 == "subscriber":
                usertype = "subscriber"
            elif ut2 == "customer":
                usertype = "customer"
            else:
                dq["unknown_usertype"] = ut
                usertype = "Unknown"
        
        by = to_int(raw.get("birth year"))
        if by is not None:
            if by < 1900 or by > datetime.now(timezone.utc).year:
                dq["bad_birth_year"] = by
                by = None

        gender = to_int(raw.get("gender"))
        if gender is not None and gender not in (0, 1, 2):
            dq["bad_gender_code"] = gender
            gender = None      

        start_date = started.date().isoformat()
        start_hour = started.hour

        return {
            "tripduration_seconds": duration_seconds,
            "started_at": started,
            "stopped_at": stopped,

            "start_station_id": to_int(raw.get("start station id")),
            "start_station_name": raw.get("start station name"),
            "start_lat": start_lat,
            "start_lng": start_lng,

            "end_station_id": to_int(raw.get("end station id")),
            "end_station_name": raw.get("end station name"),
            "end_lat": end_lat,
            "end_lng": end_lng,

            "bike_id": to_int(raw.get("bikeid")),
            "usertype": usertype,
            "birth_year": by,
            "gender": gender,

            "start_date": start_date,
            "start_hour": start_hour,

            "dq_flags": dq,
        }