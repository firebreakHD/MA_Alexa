"""Run the Alexa skill and its automatic HTTPS proxy in one HA add-on."""

import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


OPTIONS = Path("/data/options.json")
PERSISTENT = Path("/data/.ask")
CADDY_DIR = Path("/data/caddy")
HOST_LABEL = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


def fail(message: str) -> None:
    print(f"Music Assistant Alexa: {message}", file=sys.stderr, flush=True)
    raise SystemExit(1)


def hostname(value: object, name: str, required: bool = False) -> str:
    host = str(value or "").strip().lower()
    if not host:
        if required:
            fail(f"'{name}' in der Add-on-Konfiguration setzen.")
        return ""
    labels = host.split(".")
    if len(host) > 253 or len(labels) < 2 or any(not HOST_LABEL.fullmatch(label) for label in labels):
        fail(f"'{name}' muss ein öffentlicher Hostname ohne Protokoll, Port oder Pfad sein.")
    return host


def stream_target(value: object) -> str:
    target = str(value or "").strip()
    if not target:
        fail("Für 'ma_hostname' auch 'ma_stream_upstream' setzen, z. B. http://192.168.1.184:8097.")
    if any(ch.isspace() or ch in "{}\\\"'" for ch in target):
        fail("'ma_stream_upstream' enthält unerlaubte Zeichen.")
    parsed = urllib.parse.urlsplit(target)
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        fail("'ma_stream_upstream' muss eine interne http(s)-Adresse ohne Zugangsdaten oder Pfad sein.")
    try:
        port = parsed.port
    except ValueError:
        fail("Ungültiger Port in 'ma_stream_upstream'.")
    if not port or not 1 <= port <= 65535:
        fail("'ma_stream_upstream' braucht einen gültigen Port, normalerweise 8097.")
    return target.rstrip("/")


def persist_ask_credentials() -> None:
    PERSISTENT.mkdir(parents=True, exist_ok=True)
    PERSISTENT.chmod(0o700)
    root_ask = Path("/root/.ask")
    if root_ask.is_symlink() and root_ask.resolve() != PERSISTENT:
        fail("/root/.ask verweist auf einen unerwarteten Ort.")
    if root_ask.exists() and not root_ask.is_symlink():
        fail("/root/.ask ist bereits ein Verzeichnis; bestehende ASK-Daten nicht überschrieben.")
    if not root_ask.exists():
        root_ask.symlink_to(PERSISTENT, target_is_directory=True)


def caddyfile(skill_host: str, ma_host: str, ma_target: str, email: str) -> str:
    lines = ["{", "    acme_ca https://acme-v02.api.letsencrypt.org/directory", "    admin localhost:2019"]
    if email:
        lines.append(f"    email {email}")
    tls = ["    tls {", "        issuer acme {", "            disable_http_challenge", "        }", "    }"]
    lines.extend(["}", "", f"{skill_host} {{", *tls, "    reverse_proxy 127.0.0.1:5000", "}"])
    if ma_host:
        lines.extend(["", f"{ma_host} {{", *tls, f"    reverse_proxy {ma_target}", "}"])
    return "\n".join(lines) + "\n"


def update_ddnss(key: str, hosts: list[str]) -> None:
    params = urllib.parse.urlencode({"key": key, "host": ",".join(hosts)})
    request = urllib.request.Request(
        f"https://ip4.ddnss.de/upd.php?{params}",
        headers={"User-Agent": "MA-Alexa-Addon/0.2.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.status != 200:
                raise RuntimeError("unexpected HTTP status")
            response.read(1024)
        print("Music Assistant Alexa: ddnss.de-IPv4-Update angefragt.", flush=True)
    except (urllib.error.URLError, TimeoutError, RuntimeError):
        # The request URL contains the host key. Never print the exception or URL.
        print("Music Assistant Alexa: ddnss.de-Update fehlgeschlagen; neuer Versuch später.", file=sys.stderr, flush=True)


def ddnss_worker(key: str, hosts: list[str], stop: threading.Event) -> None:
    while not stop.is_set():
        update_ddnss(key, hosts)
        stop.wait(600)


def run_processes(env: dict[str, str], config: Path, ddnss_key: str, hosts: list[str]) -> int:
    stop = threading.Event()
    unexpected_exit = False
    children: list[subprocess.Popen] = []

    def request_stop(_signum: int, _frame: object) -> None:
        stop.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    if ddnss_key:
        thread = threading.Thread(target=ddnss_worker, args=(ddnss_key, hosts, stop), daemon=True)
        thread.start()

    try:
        children.append(subprocess.Popen(["/app/venv/bin/python", "/app/src/app.py"], env=env))
        children.append(subprocess.Popen(["/usr/local/bin/caddy", "run", "--config", str(config), "--adapter", "caddyfile"], env=env))
        print("Music Assistant Alexa: Skill auf Port 5000; HTTPS-Proxy auf 443 gestartet.", flush=True)
        while not stop.is_set():
            for child in children:
                if child.poll() is not None:
                    print(f"Music Assistant Alexa: Dienst beendet (Code {child.returncode}).", file=sys.stderr, flush=True)
                    unexpected_exit = True
                    stop.set()
                    break
            if not stop.is_set():
                time.sleep(0.5)
    finally:
        stop.set()
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
    # A service ending on its own must make the add-on fail, even when it exits 0.
    return 1 if unexpected_exit or any(child.returncode not in (0, -signal.SIGTERM) for child in children) else 0


def main() -> int:
    if not OPTIONS.is_file():
        fail("/data/options.json fehlt; Add-on-Konfiguration prüfen.")
    with OPTIONS.open(encoding="utf-8") as stream:
        options = json.load(stream)

    skill_host = hostname(options.get("skill_hostname"), "skill_hostname", required=True)
    ma_host = hostname(options.get("ma_hostname"), "ma_hostname")
    if ma_host and ma_host == skill_host:
        fail("'skill_hostname' und 'ma_hostname' müssen verschieden sein.")
    ma_target = stream_target(options.get("ma_stream_upstream")) if ma_host else ""
    for key in ("app_username", "app_password"):
        if not str(options.get(key, "")).strip():
            fail(f"'{key}' in der Add-on-Konfiguration setzen.")
    email = str(options.get("acme_email", "")).strip()
    if email and ("@" not in email or any(ch.isspace() or ch in "{}\"'\\" for ch in email)):
        fail("'acme_email' muss eine gültige E-Mail-Adresse sein.")

    persist_ask_credentials()
    CADDY_DIR.mkdir(parents=True, exist_ok=True)
    CADDY_DIR.chmod(0o700)
    config = CADDY_DIR / "Caddyfile"
    config.write_text(caddyfile(skill_host, ma_host, ma_target, email), encoding="utf-8")

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
    env = os.environ.copy()
    for option, variable in mapping.items():
        value = options.get(option, "")
        env[variable] = str(value).lower() if isinstance(value, bool) else str(value).strip()
    env.update(
        HOME="/root",
        ASK_CREDENTIALS_DIR=str(PERSISTENT),
        DEVICE_MAPPING_PATH="/data/device_players.json",
        PORT="5000",
        DEBUG_PORT="0",
        FLASK_DEBUG="0",
        FLASK_RELOADER="0",
        QUIET_HTTP="1",
        XDG_DATA_HOME=str(CADDY_DIR / "data"),
        XDG_CONFIG_HOME=str(CADDY_DIR / "config"),
    )
    ddnss_key = str(options.get("ddnss_host_key", "")).strip()
    return run_processes(env, config, ddnss_key, [host for host in (skill_host, ma_host) if host])


if __name__ == "__main__":
    raise SystemExit(main())
