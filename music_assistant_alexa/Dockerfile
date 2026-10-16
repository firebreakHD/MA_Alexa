# Multi-arch images. Update digests deliberately after checking both architectures.
FROM caddy:2.11.4-alpine@sha256:6aeddd44c3078b0f9a35206472a11420648a79c184603ef95957d0a20044cb2b AS caddy

FROM ghcr.io/alams154/music-assistant-skill@sha256:b1ef33ad0b05b7e0a315535e8141177898be4b6a0401decf43dedf424f0d90f1

ARG BUILD_VERSION=0.2.1
ARG BUILD_ARCH=amd64
LABEL io.hass.version="${BUILD_VERSION}" \
      io.hass.type="app" \
      io.hass.arch="${BUILD_ARCH}"

COPY run.py /app/addon_run.py
COPY patch_upstream.py /app/patch_upstream.py
COPY --from=caddy /usr/bin/caddy /usr/local/bin/caddy
RUN /app/venv/bin/python /app/patch_upstream.py
EXPOSE 5000 443
CMD ["/app/venv/bin/python", "/app/addon_run.py"]
