# CHANGELOG

<a name="unreleased"></a>
## [Unreleased]

### Features
- Hinzufügen und Pflege der `CHANGELOG.md` für zukünftige Releases

### Continuous Integration
- Release-Jon angepasst wür automatische Changelog
---

<a name="v1.0.2"></a>
## [1.0.2] - 2025-11-16

### Features
- Neuer Button `Speichern unter` (#5).
- Überprüfung des Speicherzustands..
- Build als OneDir mittels PyInstaller für schnellere Ausführung (exe + _internals).
- Auslagerung der Config-Datei in den `_internals-Ordner`.
- Automatisches Build & Release über GitHub Actions (#8)
- Anpassungen der README für einfacheres Customizing der App.

### Performance Improvements
- Optimierte Startsequenz durch Umstellung der Build-Struktur von OneFile auf OneDir. (#3)

### Bug Fixes
- Korrekte Abfrage, ob gespeichert werden soll, beim Schließen oder Öffnen einer neuen Datei. (#5)

---

<a name="v1.0.1"></a>
## [1.0.1] - 2025-10-05

### Features
- Kundendaten können nun zusätzlich zur Rechnungsadresse auch eine Objektadresse enthalten (#3).
- Neuer Button zum Kopieren der Rechnungsadresse in die Objektadresse (#3).
- Button zum Erstellen eines neuen Aufmaßes mit Abfrage, ob das aktuelle Dokument gespeichert werden soll (#3).
- Unterstützung für einfache mathematische Operationen innerhalb der Maßzeilen (#3).
- Neue Einstellung zum automatischen Öffnen nach der PDF-Erzeugung (#3).

### Bug Fixes
- Anwendung startet nun im maximierten Fenstermodus auf dem Primärbildschirm. (#3)
- Alle Hinweise und Meldungen werden nun konsistent in Deutsch ausgegeben. (#3)
- Der Import-Button öffnet jetzt korrekt den in den Einstellungen definierten Speicherpfad. (#3)
- Der Reset-Button in den Einstellungen setzt zusätzlich den Dateinamen für die Speicherung zurück. (#3)

---

<a name="v1.0.0"></a>
## [1.0.0] - 2025-07-07

### Features
- Alle erforderlichen Anforderungen wurden erfolgreich umgesetzt.
- Die Software wurde vollständig getestet und ist bereit für den produktiven Einsatz.

### Bug Fixes
- Software getestet und bereit für den produktiven Einsatz

---

[Unreleased]: https://github.com/LuigiFerraioli/FarbenWolf/compare/v1.0.2...HEAD
[v1.0.2]: https://github.com/LuigiFerraioli/FarbenWolf/compare/v1.0.1...v1.0.2
[v1.0.1]: https://github.com/LuigiFerraioli/FarbenWolf/compare/v1.0.0...v1.0.1
