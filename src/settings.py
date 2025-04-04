import os
import yaml
from dotenv import load_dotenv


def load_config():
    with open(
        os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml"), "r"
    ) as file:
        config = yaml.safe_load(file)
    return config


load_dotenv()
config = load_config()

HOST_URL = config["api"]["host_url"]
CONTENT_TYPE = config["api"]["content_type"]
VERB = config["api"]["verb"]
API_KEYID = os.getenv("SOLIS_KEYID")
API_KEYSECRET = os.getenv("SOLIS_KEYSECRET")

INFLUX_URL = config["db"]["influx_url"]
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = config["db"]["influx_org"]
INFLUX_BUCKET = config["db"]["influx_bucket"]

GRAFANA_URL = config["grafana"]["url"]
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN")
