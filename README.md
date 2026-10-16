# Music Assistant Alexa Skill als Home-Assistant-Add-on

Dieses Repository verpackt den [Alexa-Skill-Prototyp](https://github.com/alams154/music-assistant-alexa-skill-prototype) als Home-Assistant-Add-on. Zusätzlich läuft Caddy im Add-on: Es stellt Skill und Music-Assistant-Stream über HTTPS bereit und erneuert Let's-Encrypt-Zertifikate automatisch.

Für den [Alexa-Player-Provider von Music Assistant](https://www.music-assistant.io/player-support/alexa/) werden öffentliche DNS-Hostnamen, eine Router-Weiterleitung für TCP 443 und ein Amazon-Developer-Konto benötigt. Der lokale Setup-Zugang bleibt auf Port 5000. Die Anmeldung bei Amazon übernimmt der Nutzer selbst.

Installation und konkrete Konfigurationsfelder: [DOCS.md](music_assistant_alexa/DOCS.md).

Das Add-on verwendet ein veröffentlichtes Upstream-Image mit festem Digest. Bei einem Upstream-Update wird der Digest bewusst geprüft und die Add-on-Version erhöht.
