from sqlalchemy import (
    MetaData, Table, Column, String, Integer, Float, DateTime, Boolean, Text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

metadata = MetaData()

etl_runs = Table(
    "etl_runs",
    metadata,
    Column("run_id", String, primary_key=True),

    Column("source_file", String, nullable=True),
    Column("started_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("finished_at", DateTime(timezone=True), nullable=True),
    Column("status", String, nullable=False, default="running"),
    Column("rows_received", Integer, nullable=False, default=0),
    Column("rows_loaded", Integer, nullable=False, default=0),
    Column("rows_failed", Integer, nullable=False, default=0),
    Column("error_sample", JSONB, nullable=False, server_default="[]"),
)

raw_mobility_trips = Table(
    "raw_mobility_trips",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("run_id", String, nullable=False, index=True),
    Column("tripduration", Text),
    Column("starttime", Text),
    Column("stoptime", Text),
    Column("start_station_id", Text),
    Column("start_station_name", Text),
    Column("start_station_latitude", Text),
    Column("start_station_longitude", Text),
    Column("end_station_id", Text),
    Column("end_station_name", Text),
    Column("end_station_latitude", Text),
    Column("end_station_longitude", Text),
    Column("bikeid", Text),
    Column("usertype", Text),
    Column("birth_year", Text),
    Column("gender", Text),
    Column("ingested_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)

stg_mobility_trips = Table(
    "stg_mobility_trips",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("run_id", String, nullable=False, index=True),

    Column("tripduration_seconds", Integer, nullable=False),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("stopped_at", DateTime(timezone=True), nullable=False),

    Column("start_station_id", Integer, nullable=True),
    Column("start_station_name", String, nullable=True),
    Column("start_lat", Float, nullable=True),
    Column("start_lng", Float, nullable=True),

    Column("end_station_id", Integer, nullable=True),
    Column("end_station_name", String, nullable=True),
    Column("end_lat", Float, nullable=True),
    Column("end_lng", Float, Float, nullable=True),
    Column("bike_id", Integer, nullable=True),

    Column("usertype", String, nullable=True),
    Column("birth_year", Integer, nullable=True),
    Column("gender", Integer, nullable=True),  


    Column("start_date", String, nullable=False), 
    Column("start_hour", Integer, nullable=False),

    Column("dq_flags", JSONB, nullable=False, server_default="{}"),
    Column("loaded_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)