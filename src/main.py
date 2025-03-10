import collector
import time
from logger import logger
import dashboard
import parse

sns = parse.get_all_sns()
for sn in sns:
    name = parse.get_station_name(sn)
    db = dashboard.generate_dashboard(sn, name)
    err = dashboard.write_dashboard(db)

    if err:
        logger.error(
            "Unable to create dashboard.",
            extra={"tags": {"sn": sn, "name": name, "err": err}},
        )
    else:
        logger.info(
            "Created dashboard.",
            extra={"tags": {"sn": sn, "name": name}},
        )

collector.start_data_collection()

while True:
    time.sleep(5)
