# Multi-arch image published by the Alexa skill prototype. Update this digest deliberately.
FROM ghcr.io/alams154/music-assistant-skill@sha256:b1ef33ad0b05b7e0a315535e8141177898be4b6a0401decf43dedf424f0d90f1

ARG BUILD_VERSION=0.1.0
ARG BUILD_ARCH=amd64
LABEL io.hass.version="${BUILD_VERSION}" \
      io.hass.type="app" \
      io.hass.arch="${BUILD_ARCH}"

COPY run.py /app/addon_run.py
COPY patch_upstream.py /app/patch_upstream.py
RUN /app/venv/bin/python /app/patch_upstream.py
EXPOSE 5000
CMD ["/app/venv/bin/python", "/app/addon_run.py"]
