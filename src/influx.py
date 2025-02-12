from influxdb_client import InfluxDBClient, Point, WritePrecision
import settings
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone, timedelta


def convert_timestamp_to_iso(timestamp_str):
    timestamp_ms = int(timestamp_str)

    # Convert milliseconds to seconds
    timestamp_sec = timestamp_ms / 1000

    dt_utc = datetime.fromtimestamp(timestamp_sec, tz=timezone.utc)

    # Convert to UTC+8
    dt_utc8 = dt_utc.astimezone(timezone(timedelta(hours=8)))

    # Return ISO 8601 formatted string

    return dt_utc8.isoformat()


def influx_write(point):
    # Initialize InfluxDB client
    client = InfluxDBClient(
        url=settings.INFLUX_URL, token=settings.INFLUX_TOKEN, org=settings.INFLUX_ORG
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)
    # Write data to InfluxDB
    write_api.write(
        bucket=settings.INFLUX_BUCKET, org=settings.INFLUX_ORG, record=point
    )

    # Close the client
    client.close()


def create_point(metrics_json, sn, stationId, ts_str):
    ts = convert_timestamp_to_iso(ts_str)
    point_dict = {
        "measurement": "solis",
        "tags": {"sn": sn, "stationId": stationId},
        "fields": metrics_json,
        "time": ts,
    }

    point = Point.from_dict(point_dict, WritePrecision.MS)
    return point
