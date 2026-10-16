"""Redact Home Assistant option secrets in the pinned upstream image logs."""

from pathlib import Path


source = Path("/app/src/app.py")
old = "secret_keys = {'APP_USERNAME', 'APP_PASSWORD'}"
new = (
    "secret_keys = {'APP_USERNAME', 'APP_PASSWORD', 'MA_API_TOKEN', "
    "'app_username', 'app_password', 'ma_api_token'}"
)
content = source.read_text(encoding="utf-8")
if content.count(old) != 1:
    raise RuntimeError("Upstream app.py changed; verify secret redaction before building")
source.write_text(content.replace(old, new), encoding="utf-8")
