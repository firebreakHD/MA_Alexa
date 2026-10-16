"""Start the upstream Alexa skill with persistent Home Assistant add-on data."""

import json
import os
import re
import sys
from pathlib import Path


OPTIONS = Path("/data/options.json")
PERSISTENT = Path("/data/.ask")
HOSTNAME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?$")


def fail(message: str) -> None:
    print(f"Music Assistant Alexa: {message}", file=sys.stderr, flush=True)
    raise SystemExit(1)


def main() -> None:
    if not OPTIONS.is_file():
        fail("/data/options.json fehlt; Add-on-Konfiguration prüfen.")
    with OPTIONS.open(encoding="utf-8") as stream:
        options = json.load(stream)

    for key in ("skill_hostname", "app_username", "app_password"):
        if not str(options.get(key, "")).strip():
            fail(f"'{key}' in der Add-on-Konfiguration setzen.")
    for key in ("skill_hostname", "ma_hostname"):
        value = str(options.get(key, "")).strip()
        if value and not HOSTNAME.fullmatch(value):
            fail(f"'{key}' muss ein Hostname ohne Protokoll, Port oder Pfad sein.")

    PERSISTENT.mkdir(parents=True, exist_ok=True)
    PERSISTENT.chmod(0o700)
    root_ask = Path("/root/.ask")
    if root_ask.is_symlink() and root_ask.resolve() != PERSISTENT:
        fail("/root/.ask verweist auf einen unerwarteten Ort.")
    if root_ask.exists() and not root_ask.is_symlink():
        fail("/root/.ask ist bereits ein Verzeichnis; bestehende ASK-Daten nicht überschrieben.")
    if not root_ask.exists():
        root_ask.symlink_to(PERSISTENT, target_is_directory=True)

    mapping = {
        "skill_hostname": "SKILL_HOSTNAME",
        "ma_hostname": "MA_HOSTNAME",
        "app_username": "APP_USERNAME",
        "app_password": "APP_PASSWORD",
        "locale": "LOCALE",
        "aws_region": "AWS_DEFAULT_REGION",
        "ma_api_url": "MA_API_URL",
        "ma_api_token": "MA_API_TOKEN",
        "skill_id": "SKILL_ID",
        "skip_url_validation": "SKIP_URL_VALIDATION",
        "enable_apl": "ENABLE_APL",
    }
    for option, variable in mapping.items():
        value = options.get(option, "")
        os.environ[variable] = str(value).lower() if isinstance(value, bool) else str(value).strip()

    os.environ.update(
        HOME="/root",
        ASK_CREDENTIALS_DIR=str(PERSISTENT),
        DEVICE_MAPPING_PATH="/data/device_players.json",
        PORT="5000",
        DEBUG_PORT="0",
        FLASK_DEBUG="0",
        FLASK_RELOADER="0",
        QUIET_HTTP="1",
    )
    print("Music Assistant Alexa: Skill-Dienst startet auf Port 5000.", flush=True)
    os.execv("/app/venv/bin/python", ["/app/venv/bin/python", "/app/src/app.py"])


if __name__ == "__main__":
    main()
