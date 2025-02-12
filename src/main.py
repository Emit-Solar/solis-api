import api_requests
import pytz
import time
import math
import parse
import influx
from datetime import datetime, timedelta
from tqdm import tqdm  # ✅ Import tqdm for the progress bar


def add_one_day_to_date(date_str):
    """Increase a YYYY-MM-DD date string by one day."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    dt_plus_one_day = dt + timedelta(days=1)
    return dt_plus_one_day.strftime("%Y-%m-%d")


# Main loop to process inverter data
while True:
    sns = parse.get_all_sns()  # Get all serial numbers
    for sn in sns:
        station_id = parse.get_station_id(sn)
        install_date_list = parse.get_installation_date(station_id)
        name = parse.get_station_name(sn)
        if not install_date_list:
            continue  # Skip if no install date is found

        start_date = install_date_list[0]  # First recorded date
        today = datetime.today().strftime("%Y-%m-%d")  # Today's date

        # Calculate total days to process
        total_days = (
            datetime.strptime(today, "%Y-%m-%d")
            - datetime.strptime(start_date, "%Y-%m-%d")
        ).days

        # Create a progress bar for this inverter
        with tqdm(
            total=total_days, desc=f"Processing station: {name}", unit="day"
        ) as pbar:
            date = start_date
            while date <= today:
                day_data = api_requests.get_inverter_day(sn, date)
                time.sleep(1)  # Prevent API rate limits

                points = []
                if day_data and "data" in day_data:
                    for day_metrics in day_data["data"]:
                        ts = day_metrics.pop(
                            "dataTimestamp", None
                        )  # Remove timestamp from metrics

                        # Convert all integers to floats to prevent type conflicts
                        day_metrics = {
                            k: float(v) if isinstance(v, int) else v
                            for k, v in day_metrics.items()
                        }

                        if ts:
                            point = influx.create_point(day_metrics, sn, station_id, ts)
                            points.append(point)

                # ✅ Write points to InfluxDB
                influx.influx_write(points)

                # Move to the next day
                date = add_one_day_to_date(date)

                # Update progress bar
                pbar.update(1)

