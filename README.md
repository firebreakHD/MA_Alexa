# Music Assistant Alexa Skill als Home-Assistant-Add-on

Dieses Repository verpackt den [Alexa-Skill-Prototyp](https://github.com/alams154/music-assistant-alexa-skill-prototype) als Home-Assistant-Add-on. Es startet den Skill-Dienst für den [Alexa-Player-Provider von Music Assistant](https://www.music-assistant.io/player-support/alexa/). Die eigentliche Skill-Anmeldung und Geräteverknüpfung erfolgen über dessen Setup-Oberfläche.

**Wichtig:** Der Alexa-Provider ist experimentell. Amazon muss den Skill über eine öffentlich erreichbare HTTPS-Adresse ansprechen können. Für Echo-Geräte ohne Bildschirm muss auch der Music-Assistant-Stream über öffentliches HTTPS erreichbar sein. Das Add-on allein stellt weder Domain noch Zertifikat oder Amazon-Konto bereit.

## Installation

1. Dieses GitHub-Repository im Home Assistant Add-on Store als eigenes Repository hinzufügen.
2. **Music Assistant Alexa Skill** installieren.
3. In der Add-on-Konfiguration `skill_hostname`, `app_username` und `app_password` setzen. Für Echo ohne Bildschirm außerdem `ma_hostname` setzen. Die Hostnamen sind reine Hostnamen, ohne `https://` oder Pfad.
4. Add-on starten und in einem Browser `http://HOME-ASSISTANT-IP:5000/setup` öffnen. Die Oberfläche ist mit den konfigurierten Zugangsdaten geschützt.
5. Einen HTTPS-Reverse-Proxy für `skill_hostname` auf den Host-Port 5000 einrichten. Für Echo ohne Bildschirm auch den Music-Assistant-Stream-Port 8097 unter `ma_hostname` per HTTPS bereitstellen. Nur den dafür nötigen Verkehr öffentlich freigeben.
6. `/setup` im Skill-Dienst durchlaufen und den Alexa-Player-Provider in Music Assistant gemäß [offizieller Anleitung](https://www.music-assistant.io/player-support/alexa/) hinzufügen. Dort die lokale Skill-Adresse `http://HOME-ASSISTANT-IP:5000` sowie denselben Benutzernamen und dasselbe Passwort verwenden.

Weitere Details und Optionen: [DOCS.md](music_assistant_alexa/DOCS.md).

Das Add-on verwendet das veröffentlichte Upstream-Image mit festem Digest. Upstream-Quellcode wird nicht hier dupliziert. Bei einem Upstream-Update muss der Digest bewusst geprüft und die Add-on-Version erhöht werden.
