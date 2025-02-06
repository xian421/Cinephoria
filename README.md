# Cinephoria

> **Hinweis:** _!!! Noch anpassen !!!_

## Projektübersicht

### Repositories

- [Repository 1](https://github.com/xian421/Cinephoria)


## Libraries

### Backend

In der Datei **requirements.txt** sind folgende Python-Bibliotheken definiert:

- **flask**  
  Ein leichtgewichtiges Web-Framework, das für den Aufbau von Webanwendungen und APIs genutzt wird.
- **flask-cors**  
  Ermöglicht Cross-Origin Resource Sharing (CORS) in Flask-Anwendungen, sodass z. B. das Frontend auf das Backend zugreifen kann.
- **gunicorn**  
  Ein WSGI HTTP-Server, der oft in der Produktion verwendet wird, um Flask-Anwendungen performant bereitzustellen.
- **requests**  
  Eine benutzerfreundliche HTTP-Bibliothek, die das Senden von HTTP-Anfragen erleichtert.
- **psycopg2-binary**  
  Ein PostgreSQL-Adapter für Python, der die Kommunikation mit PostgreSQL-Datenbanken ermöglicht.
- **pyjwt**  
  Eine Bibliothek zur Erzeugung und Verifizierung von JSON Web Tokens (JWTs) für Authentifizierungs- und Autorisierungszwecke.
- **pytest**  
  Ein weit verbreitetes Test-Framework für Python, das das Schreiben und Ausführen von Tests vereinfacht.
- **pytest-cov**  
  Ein Plugin für pytest, das Code Coverage während der Testausführung misst und dokumentiert.

---

### Frontend

In der **package.json** findest du zwei Gruppen von Abhängigkeiten:

#### Produktivabhängigkeiten (dependencies)

- **@fortawesome/fontawesome-free**  
  Eine Icon-Bibliothek, die dir eine große Auswahl an Icons zur Verfügung stellt.
- **date-fns**  
  Eine Utility-Bibliothek zur einfachen Manipulation und Formatierung von Datums- und Zeitangaben.
- **qr-scanner**  
  Eine Bibliothek, die es ermöglicht, QR-Codes über die Kamera zu scannen und auszuwerten.
- **qrcode**  
  Dient zur Generierung von QR-Codes.
- **svelte-select**  
  Eine ansprechende Dropdown-/Auswahl-Komponente, die speziell für Svelte entwickelt wurde.
- **svelte-spa-router**  
  Ein Router für Single Page Applications (SPAs) in Svelte, der das Navigieren zwischen den verschiedenen Ansichten ermöglicht.
- **sweetalert2**  
  Bietet schöne, erweiterbare Dialoge und Alerts für Benutzerinteraktionen.

#### Entwicklungsabhängigkeiten (devDependencies)

- **@sveltejs/vite-plugin-svelte**  
  Ein Plugin, das die Integration von Svelte in den Vite-Build-Prozess ermöglicht.
- **svelte**  
  Das Svelte-Framework (Version 5), das für die Erstellung reaktiver Benutzeroberflächen verwendet wird.
- **svelte-routing**  
  Eine zusätzliche Routing-Lösung für Svelte-Anwendungen, die während der Entwicklung nützlich sein kann.
- **vite**  
  Ein modernes Build-Tool und Entwicklungsserver, das vor allem für schnelle Entwicklungszyklen und Hot Module Replacement (HMR) geschätzt wird.

---

## Installation

1. **Bibliotheken installieren:**  
   Stelle sicher, dass du die erforderlichen Bibliotheken installiert hast (z. B. via `pip install -r requirements.txt` für das Backend und `npm install` bzw. `yarn` für das Frontend).

2. **Repository klonen:**  
   ```bash
   git clone https://github.com/xian421/Cinephoria
