"""
Collects real-time and historical data for all inverters using threading
"""

from pytz import timezone
import api_requests
import time
import parse
import influx
from datetime import datetime, timedelta
import threading
from logger import logger

semaphore = threading.Semaphore(2)  # Only 2 requests per second


def add_one_day_to_date(date_str):
    """Increase a YYYY-MM-DD date string by one day."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    dt_plus_one_day = dt + timedelta(days=1)
    return dt_plus_one_day.strftime("%Y-%m-%d")


def convert_metrics_to_influx_format(metrics, sn, station_id, name, install_date):
    """Convert metrics: integers to floats & strings to tags, while escaping necessary characters."""
    fields = {}
    tags = {
        "sn": sn,
        "station_id": station_id,
        "name": name,
        "installed_date": install_date,
    }

    for k, v in metrics.items():
        if isinstance(v, int) or isinstance(v, float):
            fields[k] = float(v)  # Convert int to float to prevent type conflicts
        elif isinstance(v, str):
            # Escape spaces in tag values
            tags[k] = v.replace(" ", "\\ ")
    return fields, tags


def fetch_data(sn, station_id, start_date, name, install_date):
    """Fetch historical data first, then switch to real-time mode."""
    today = datetime.today().strftime("%Y-%m-%d")
    date = start_date

    # Check if historical data needs to be fetched
    fetching_historical = date <= today
    logger.info(f"Fetching data for {name} ({sn}) from {start_date} onwards")

    while True:
        # Use today's date in real-time mode
        if not fetching_historical:
            date = datetime.today().strftime("%Y-%m-%d")

        logger.info(f"Fetching data for {name} ({sn}) on {date}")

        day_data = None
        with semaphore:  # Limit concurrent API requests to 2 per second
            day_data = api_requests.get_inverter_day(sn, date)
            time.sleep(0.5)  # Respect API rate limit (2 requests/sec)

        points = []
        if day_data and "data" in day_data:
            for day_metrics in day_data["data"]:
                ts = day_metrics.pop("dataTimestamp", None)
                fields, tags = convert_metrics_to_influx_format(
                    day_metrics, sn, station_id, name, install_date
                )
                if "time" in tags:
                    tags.pop("time")

                if ts:
                    point = influx.create_point(fields, tags, ts)
                    points.append(point)

        if points:
            influx.influx_write(points)

        # If fetching historical data, move to the next day
        if fetching_historical:
            date = add_one_day_to_date(date)

            # If we reach today, switch to real-time mode
            if date >= today:
                fetching_historical = False
                logger.info(
                    f"{name} completed historical data. Switching to real-time mode."
                )

        # In real-time mode, keep fetching the latest data
        else:
            time.sleep(0.5)  # Keep polling in real-time mode


def start_data_collection():
    """Start the process for all inverters: historical first, then real-time."""
    sns = parse.get_all_sns()

    # Batch up inverters to run requests concurrently (while respecting rate limit)
    for sn in sns:
        station_id = parse.get_station_id(sn)
        name = parse.get_station_name(sn)

        install_date_list = parse.get_installation_date(station_id)
        if install_date_list:
            install_date = install_date_list[0]  # First recorded date
        else:
            logger.error(f"Skipping {sn}, no installation date found.")
            continue  # Skip if no install date is found

        print(f"Searching InfluxDB for {name}")
        latest_ts = influx.influx_get_latest_ts(sn)
        if latest_ts:
            print(f"{name} found.")
            start_date = latest_ts.strftime("%Y-%m-%d")
        else:
            start_date = install_date

        logger.info(f"Starting thread {sn} ({name}).")
        thread = threading.Thread(
            target=fetch_data,
            args=(sn, station_id, start_date, name, install_date),
            daemon=True,
        )
        thread.start()
