# Einrichtung

Dieses Add-on startet den Music-Assistant-Alexa-Skill und einen Caddy-HTTPS-Proxy. Caddy beschafft und erneuert gültige Let's-Encrypt-Zertifikate automatisch. Das bereits installierte Home-Assistant-Let's-Encrypt-Add-on wird dafür nicht verändert oder benötigt: Es ist derzeit nur für `mpwohnen.ddnss.de` konfiguriert und erneuert Zertifikate nicht selbstständig.

## Voraussetzungen

- Eine öffentlich erreichbare DNS-Adresse für Skill und Musikstream, z. B. `mpwohnen.ddnss.de`. Ein zweiter Hostname ist nicht nötig. Wenn gewünscht, kann der Stream auch einen eigenen Hostnamen erhalten.
- Router-Portweiterleitung **TCP 443 → Home-Assistant-Server 192.168.1.184**, sofern dieser Port nicht schon ein anderer Dienst belegt. Caddy verwendet die TLS-ALPN-Prüfung auf Port 443; Port 80 wird für dieses Add-on nicht benötigt. Kein Port 5000 oder 8097 ins Internet weiterleiten.
- Für die automatische ddnss.de-IP-Aktualisierung den **Host-Key** im Add-on-Feld `ddnss_host_key` hinterlegen. Wenn ddnss.de bereits anderweitig aktualisiert wird, dieses Feld leer lassen.
- Ein Amazon-Developer-Konto und der [Alexa-Player-Provider](https://www.music-assistant.io/player-support/alexa/) in Music Assistant.

## Add-on-Konfiguration

- `skill_hostname`: öffentlicher Skill-Hostname, ohne `https://`, Port oder Pfad.
- `ma_hostname`: für den gemeinsamen Hostnamen denselben Wert wie bei `skill_hostname` eintragen. Dann werden nur die Music-Assistant-Stream-Pfade an Port 8097 weitergeleitet. Für Echo ohne Bildschirm nötig.
- `ma_stream_upstream`: interne Stream-Adresse von Music Assistant, normalerweise `http://192.168.1.184:8097`. Nur zusammen mit `ma_hostname` nötig.
- `app_username`, `app_password`: eigener Zugang für Setup und lokale Skill-API. Dasselbe Paar später in Music Assistant eintragen.
- `acme_email`: E-Mail für Let's Encrypt; optional, aber empfohlen.
- `ddnss_host_key`: optionaler ddnss.de-Host-Key. Nicht in Chat, Screenshots oder Git teilen.
- `locale`: Alexa-Sprache, z. B. `de-DE`.
- `aws_region`: ASK-CLI-Region, normalerweise `eu-west-1`.
- `ma_api_url`, `ma_api_token`: optional für „nächster/vorheriger Titel“.
- `skill_id`: nach der Skill-Erstellung optional eintragen, um nur den eigenen Skill zu akzeptieren.
- `skip_url_validation`, `enable_apl`: normalerweise ausgeschaltet lassen.

## Ablauf

1. Einen ddnss.de-Hostnamen bereitstellen. Falls `mpwohnen.ddnss.de` schon für einen anderen öffentlichen Dienst verwendet wird, dessen bisherige Weiterleitung berücksichtigen.
2. Add-on-Felder ausfüllen. In **Netzwerk** Host-Port 443 aktivieren und kontrollieren, dass er nicht schon durch ein anderes Add-on belegt ist. Port 5000 nur im lokalen Netz nutzen.
3. Router TCP 443 an den Home-Assistant-Server weiterleiten. Add-on starten; Caddy schreibt Zertifikate dauerhaft unter `/data/caddy/`. Zertifikatsausstellung im Add-on-Protokoll prüfen.
4. Lokal `http://192.168.1.184:5000/setup` öffnen, mit Add-on-Benutzername/-Passwort anmelden und die ASK-CLI-/Amazon-Schritte selbst durchführen. Amazon-Passwort und Codes werden nicht von Codex eingegeben.
5. Im Alexa Developer Portal **Endpoint → HTTPS → Default Region** auf `https://SKILL_HOSTNAME/` setzen. Zertifikatstyp: vertrauenswürdiges Zertifikat einer Zertifizierungsstelle. Speichern und Modell bauen.
6. In Music Assistant den Alexa-Player-Provider einrichten. Skill-API-Adresse: `http://192.168.1.184:5000`; Benutzername und Passwort wie im Add-on. Die übrigen Amazon-Schritte stehen in der [offiziellen Anleitung](https://www.music-assistant.io/player-support/alexa/).
7. Über `/status` am lokalen Port 5000 prüfen und mit einem Echo Wiedergabe testen. Erst nach echtem HTTPS-Test den Endpunkt im Developer Portal als fertig betrachten.

ASK-CLI-Daten liegen unter `/data/.ask`, Echo-Zuordnungen unter `/data/device_players.json`, Caddy-Daten unter `/data/caddy/`. Diese Pfade bleiben bei Add-on-Neustarts und Updates bestehen. Backups enthalten sensible Daten und müssen geschützt werden.

Das Add-on kann keine Router-Ports oder ddnss.de-Hostnamen selbst anlegen. Bei Carrier-Grade-NAT oder bereits belegtem Port 443 ist ein anderer öffentlich erreichbarer HTTPS-Proxy erforderlich.
