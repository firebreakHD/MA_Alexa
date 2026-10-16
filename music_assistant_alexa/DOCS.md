# Einrichtung

## Voraussetzungen

Der [Music-Assistant-Alexa-Provider](https://www.music-assistant.io/player-support/alexa/) benötigt einen extern erreichbaren Skill-Endpunkt mit gültigem HTTPS-Zertifikat und ein Amazon-Developer-Konto. Für Echo-Geräte ohne Bildschirm muss der Audio-Stream von Music Assistant (normalerweise Port 8097) ebenfalls über HTTPS erreichbar sein. Das Add-on öffnet selbst keine Router-Ports und richtet keinen Reverse-Proxy ein.

## Add-on-Konfiguration

- `skill_hostname`: öffentliche HTTPS-Domain für den Alexa-Skill, **ohne** `https://`, Port oder Pfad.
- `ma_hostname`: öffentliche HTTPS-Domain für den Music-Assistant-Stream, für Echo ohne Bildschirm erforderlich.
- `app_username`, `app_password`: Zugang für Weboberfläche und lokale API. Beide sind erforderlich. Dasselbe Paar später in Music Assistant eintragen.
- `locale`: Sprache der Skill-Interaktion, z. B. `de-DE`.
- `aws_region`: Region für die ASK-CLI, standardmäßig `eu-west-1`.
- `ma_api_url`, `ma_api_token`: optional für Sprachbefehle „nächster/vorheriger Titel“; URL der Music-Assistant-WebSocket-API und gegebenenfalls ein MA-Token.
- `skill_id`: nach der Skill-Erstellung optional eintragen und Add-on neu starten, damit nur der eigene Skill akzeptiert wird.
- `skip_url_validation`, `enable_apl`: optionale Upstream-Funktionen; normalerweise ausgeschaltet lassen.

## Reihenfolge

1. Konfiguration speichern und Add-on starten.
2. `http://HOME-ASSISTANT-IP:5000/setup` im lokalen Netz öffnen. Mit `app_username` und `app_password` anmelden.
3. HTTPS-Reverse-Proxy von `skill_hostname` auf `HOME-ASSISTANT-IP:5000` einrichten. Er muss POST auf `/` durchlassen. Der Proxy sollte die geschützten Verwaltungsseiten nicht ohne weiteren Zugriffsschutz öffentlich anbieten.
4. Für Echo ohne Bildschirm einen zweiten HTTPS-Reverse-Proxy von `ma_hostname` auf den Music-Assistant-Stream-Port 8097 einrichten.
5. In `/setup` die ASK-CLI-Autorisierung und Skill-Erstellung durchführen. Amazon-Anmeldung und Codes selbst eingeben.
6. In Music Assistant den Alexa-Player-Provider aktivieren: Skill-API-Adresse `http://HOME-ASSISTANT-IP:5000`, Add-on-Benutzername und Passwort; anschließend die Amazon-Kontodaten nach der [offiziellen Music-Assistant-Anleitung](https://www.music-assistant.io/player-support/alexa/) eintragen.
7. `/status` prüfen. Ein Echo als Player auswählen und Wiedergabe testen. Falls Sprachbefehle „weiter/zurück“ gewünscht sind, die Zuordnung unter `/devices` vornehmen.

ASK-CLI-Daten liegen unter `/data/.ask`, Echo-Zuordnungen unter `/data/device_players.json`. Diese Daten überstehen Add-on-Neustarts und Updates. Add-on-Backups enthalten diese Daten und sollten geschützt aufbewahrt werden. Zugangsdaten werden nicht ins Git-Repository geschrieben.

Die Upstream-Skill-App ist experimentell. Dieses Repository verpackt sie, ersetzt aber weder Amazons Skill-Dienst noch den nötigen öffentlichen HTTPS-Zugang.
