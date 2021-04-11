# LikeUber

<img src="https://img.shields.io/badge/python-3.9.2-blue" />
<img src="https://img.shields.io/badge/docstyle-Google Docstrings-success" />

## Inhaltsverzeichnis:

- [**Benutzung**](https://github.com/julianYaman/dhbw-telegram-bot#Benutzung)
- [**Einführung**](https://github.com/julianYaman/dhbw-telegram-bot#Einführung)
- [**Installation**](https://github.com/julianYaman/dhbw-telegram-bot#Installation)
- [**Konfiguration**](https://github.com/julianYaman/dhbw-telegram-bot#Konfiguration)
- [**Hinweise**](https://github.com/julianYaman/dhbw-telegram-bot#Hinweise)
- [**Mitwirkende**](https://github.com/julianYaman/dhbw-telegram-bot#Mitwirkende)
- [**Kontakt**](https://github.com/julianYaman/dhbw-telegram-bot#Kontakt)

## Benutzung
```sh
python main.py 
```

## Einführung

In dieser Arbeit soll der Prototyp einer Mitfahrzentrale konzipiert und technisch umgesetzt werden. 
Die Mitfahrzentrale soll von den Anwendern ausschließlich ̈uber Telegram bedient werden konnen, eine Administration kann serverseitig ̈uber eine Konfigurationsdatei im Format JSON erfolgen. Fur die Anwender sollen allumfängliche Funktionen zur Nutzung der Mitfahrzentrale implementiert werden

## Installation

Um den Bot zu nutzen, sollte man dieses Repository klonen oder als ZIP von GitHub 
herunterladen und auf dem eigenen PC/Server speichern.

Es empfiehlt sich für einen dauerhaften Betrieb des Bots (24/7), diesen auf einem Server zu starten.

Nun wird die Bibliothek [**python-telegram-bot**](https://github.com/python-telegram-bot/python-telegram-bot) benötigt
und muss installiert werden.

```sh
pip install python-telegram-bot --upgrade
```

## Konfiguration

Im Ordner *data* befindet sich die Datei `example.bot.json`.
Diese sollte in `bot.json` umbenannt werden und wird den Token für den Bot beinhalten.

Einen Telegram Bot und einen dazugehörigen Token erhält man über den offiziellen Bot [**BotFather**](https://t.me/botfather). 

Eine Einführung zu Telegram Bots und wie der *BotFather* genutzt wird, 
kann auf der [**Hilfeseite für Bots von Telegram**](https://core.telegram.org/bots) gefunden werden.

Sobald man einen Token erhalten hat, setzt man diesen in den Placeholder in der `bot.json` im Ordner *data* ein.

```json
{
  "token": "my-token"
}
```

## Hinweise
Es sollte darauf geachtet werden, dass in den Speicherfiles `location.json` und `users.json` leere Arrays enthalten sind,
**bevor man den Bot zum ersten Mal startet**.

## Mitwirkende

- Julian Yaman
- Gary Lude
- Niklas Leinz
- Lars Strölin
- Moritz Gärtner

## Kontakt

Durch folgende Kanäle kann Kontakt aufgenommen werden
- **[E-Mail](mailto:mail@yaman.pro)** - mail@yaman.pro
<hr>
Made remotely with ❤️ (and partly on Arch Linux)
