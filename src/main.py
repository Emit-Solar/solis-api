import collector
import time
from logger import logger
import dashboard
import parse

sns = parse.get_all_sns()

for sn in sns:
    name = parse.get_station_name(sn)
    db = dashboard.generate_dashboard(sn, name)
    err = dashboard.write_dashboard(dashboard)

    if err:
        logger.error(f"Unable to create dashboard for {name}.")
    else:
        logger.info(f"Created dashboard for {name}.")

collector.start_data_collection()

while True:
    time.sleep(5)
