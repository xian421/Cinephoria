# Cinephoria

Cinephoria ist ein Kinoticketreservierungssystem, bestehend aus einem Backend (Flask-basierte REST API) und einem Frontend (Svelte-basierte Single Page Application).

---

## Projektübersicht

**Repository:**  
https://github.com/xian421/Cinephoria

---

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

### 1. Repository klonen

Öffne ein Terminal und führe folgende Befehle aus:

git clone https://github.com/xian421/Cinephoria.git  
cd Cinephoria

### 2. Backend installieren

#### a) Virtuelle Umgebung erstellen und aktivieren

Auf macOS/Linux:
  
  python3 -m venv venv  
  source venv/bin/activate

Auf Windows:
  
  python -m venv venv  
  venv\Scripts\activate

#### b) Abhängigkeiten installieren

  cd cinephoria_backend  
  pip install -r requirements.txt  
  cd ..

#### c) Umgebungsvariablen setzen

Setze in deinem Terminal die notwendigen Umgebungsvariablen:

Für Windows (PowerShell):

  $env:SECRET_KEY="dein_geheimer_schluessel"  
  $env:TMDB_BEARER_TOKEN="hier_bearer_token_von_TMDB"  
  $env:DATABASE_URL="postgres://benutzer:passwort@localhost:5432/deinedatenbank"  
  $env:PAYPAL_CLIENT_ID="deine_paypal_client_id"  
  $env:PAYPAL_CLIENT_SECRET="dein_paypal_client_secret"


#### d) Datenbank einrichten

- Stelle sicher, dass PostgreSQL installiert ist.
- Erstelle die erforderliche Datenbank mit den Tabellen unten.


#### e) Backend starten

Starte die Flask‑App:

  python -m cinephoria_backend.app

### 3. Frontend installieren

Wechsle in das Frontend-Verzeichnis und installiere die npm‑Abhängigkeiten:

  cd cinephoria-frontend  
  npm install

### 4. Frontend ausführen

Starte den Entwicklungsserver:

  npm run dev

Der Entwicklungsserver startet und zeigt dir in der Konsole die URL (z. B. http://localhost:3000) an.

---

## Tests ausführen

Führe die Tests aus, um sicherzustellen, dass alles funktioniert:

  pytest --cov=. --cov-report=term-missing

---

## Deployment

### Backend

- Für das Deployment in der Produktion wird empfohlen, Gunicorn zusammen mit einem Reverse-Proxy (z. B. Nginx) zu verwenden.
- Das Projekt enthält auch einen Procfile für Heroku.

### Frontend

- Baue das Frontend mit Vite:

  npm run build

Die erzeugten Dateien können dann auf einem statischen Server oder über einen Cloud-Service (z. B. Vercel, Netlify) bereitgestellt werden.

---

## Contributing

Beiträge sind willkommen! Bitte erstelle Pull-Requests und bespreche größere Änderungen im Voraus.

---


## Anhang: Tabellen-Struktur

Anhang: Datenbankschema
Im Folgenden findest du eine Übersicht der wichtigsten Tabellen der Datenbank. Diese Informationen wurden mit dem Befehl \d <tablename> aus der PostgreSQL-Shell generiert.

Alle Tabellen:
\d screens
 \d seat_types
 \d cinema
 \d showtimes
 \d booking_seats
 \d seats
 \d user_cart_items
 \d user_carts
 \d discounts
 \d user_points
 \d users
 \d guest_cart_items
 \d guest_carts
 \d points_transactions
 \d seat_type_discounts
 \d rewards
 \d supermarkt_pfand
 \d supermarkt_items
 \d bookings
(19 Zeilen)


cinephoria-backend::DATABASE=>  \d screens
                                               Tabelle ╗public.screens½
   Spalte   |             Typ             | Sortierfolge | NULL erlaubt? |                Vorgabewert
------------+-----------------------------+--------------+---------------+--------------------------------------------
 screen_id  | integer                     |              | not null      | nextval('screens_screen_id_seq'::regclass)
 cinema_id  | integer                     |              | not null      |
 name       | character varying(50)       |              | not null      |
 capacity   | integer                     |              | not null      |
 type       | character varying(20)       |              |               |
 created_at | timestamp without time zone |              |               | now()
 updated_at | timestamp without time zone |              |               | now()
Indexe:
    "screens_pkey" PRIMARY KEY, btree (screen_id)
Fremdschl³ssel-Constraints:
    "screens_cinema_id_fkey" FOREIGN KEY (cinema_id) REFERENCES cinema(cinema_id)
Fremdschl³sselverweise von:
    TABLE "seats" CONSTRAINT "seats_screen_id_fkey" FOREIGN KEY (screen_id) REFERENCES screens(screen_id)
    TABLE "showtimes" CONSTRAINT "showtimes_screen_id_fkey" FOREIGN KEY (screen_id) REFERENCES screens(screen_id)
Trigger:
    set_updated_at BEFORE UPDATE ON screens FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()


cinephoria-backend::DATABASE=>  \d seat_types
                                              Tabelle ╗public.seat_types½
    Spalte    |          Typ          | Sortierfolge | NULL erlaubt? |                   Vorgabewert
--------------+-----------------------+--------------+---------------+--------------------------------------------------
 seat_type_id | integer               |              | not null      | nextval('seat_types_seat_type_id_seq'::regclass)
 name         | character varying(50) |              | not null      |
 price        | numeric(10,2)         |              | not null      |
 color        | character varying(20) |              |               |
 icon         | character varying(50) |              |               |
Indexe:
    "seat_types_pkey" PRIMARY KEY, btree (seat_type_id)
Fremdschl³sselverweise von:
    TABLE "seat_type_discounts" CONSTRAINT "seat_type_discounts_seat_type_id_fkey" FOREIGN KEY (seat_type_id) REFERENCES seat_types(seat_type_id) ON DELETE CASCADE
    TABLE "seats" CONSTRAINT "seats_seat_type_id_fkey" FOREIGN KEY (seat_type_id) REFERENCES seat_types(seat_type_id) ON DELETE CASCADE


cinephoria-backend::DATABASE=>  \d cinema
                                                 Tabelle ╗public.cinema½
     Spalte     |             Typ             | Sortierfolge | NULL erlaubt? |                Vorgabewert
----------------+-----------------------------+--------------+---------------+-------------------------------------------
 cinema_id      | integer                     |              | not null      | nextval('cinema_cinema_id_seq'::regclass)
 name           | character varying(255)      |              | not null      |
 location       | character varying(255)      |              | not null      |
 contact_number | character varying(20)       |              |               |
 created_at     | timestamp without time zone |              |               | now()
 updated_at     | timestamp without time zone |              |               | now()
Indexe:
    "cinema_pkey" PRIMARY KEY, btree (cinema_id)
Fremdschl³sselverweise von:
    TABLE "screens" CONSTRAINT "screens_cinema_id_fkey" FOREIGN KEY (cinema_id) REFERENCES cinema(cinema_id)


cinephoria-backend::DATABASE=>  \d showtimes
                                                Tabelle ╗public.showtimes½
   Spalte    |             Typ             | Sortierfolge | NULL erlaubt? |                  Vorgabewert
-------------+-----------------------------+--------------+---------------+------------------------------------------------
 showtime_id | integer                     |              | not null      | nextval('showtimes_showtime_id_seq'::regclass)
 movie_id    | integer                     |              | not null      |
 screen_id   | integer                     |              | not null      |
 start_time  | timestamp without time zone |              | not null      |
 end_time    | timestamp without time zone |              |               |
 created_at  | timestamp without time zone |              |               | now()
Indexe:
    "showtimes_pkey" PRIMARY KEY, btree (showtime_id)
Fremdschl³ssel-Constraints:
    "showtimes_screen_id_fkey" FOREIGN KEY (screen_id) REFERENCES screens(screen_id)
Fremdschl³sselverweise von:
    TABLE "booking_seats" CONSTRAINT "booking_seats_showtime_id_fkey" FOREIGN KEY (showtime_id) REFERENCES showtimes(showtime_id) ON DELETE CASCADE
    TABLE "guest_cart_items" CONSTRAINT "guest_cart_items_showtime_id_fkey" FOREIGN KEY (showtime_id) REFERENCES showtimes(showtime_id)
    TABLE "user_cart_items" CONSTRAINT "user_cart_items_showtime_id_fkey" FOREIGN KEY (showtime_id) REFERENCES showtimes(showtime_id)


cinephoria-backend::DATABASE=>  \d booking_seats
                                                       Tabelle ╗public.booking_seats½
        Spalte         |             Typ             | Sortierfolge | NULL erlaubt? |                      Vorgabewert
-----------------------+-----------------------------+--------------+---------------+--------------------------------------------------------
 booking_seat_id       | integer                     |              | not null      | nextval('booking_seats_booking_seat_id_seq'::regclass)
 booking_id            | integer                     |              |               |
 seat_id               | integer                     |              |               |
 price                 | numeric(10,2)               |              |               |
 created_at            | timestamp without time zone |              |               | CURRENT_TIMESTAMP
 showtime_id           | integer                     |              |               |
 seat_type_discount_id | integer                     |              |               |
Indexe:
    "booking_seats_pkey" PRIMARY KEY, btree (booking_seat_id)
    "booking_seats_booking_id_seat_id_key" UNIQUE CONSTRAINT, btree (booking_id, seat_id)
Fremdschl³ssel-Constraints:
    "booking_seats_booking_id_fkey" FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE
    "booking_seats_seat_id_fkey" FOREIGN KEY (seat_id) REFERENCES seats(seat_id) ON DELETE CASCADE
    "booking_seats_showtime_id_fkey" FOREIGN KEY (showtime_id) REFERENCES showtimes(showtime_id) ON DELETE CASCADE
    "fk_booking_seats_seat_type_discount" FOREIGN KEY (seat_type_discount_id) REFERENCES seat_type_discounts(seat_type_discount_id) ON DELETE SET NULL


cinephoria-backend::DATABASE=>  \d seats
                                               Tabelle ╗public.seats½
    Spalte    |             Typ             | Sortierfolge | NULL erlaubt? |              Vorgabewert
--------------+-----------------------------+--------------+---------------+----------------------------------------
 seat_id      | integer                     |              | not null      | nextval('seats_seat_id_seq'::regclass)
 screen_id    | integer                     |              | not null      |
 row          | character(1)                |              | not null      |
 number       | integer                     |              | not null      |
 created_at   | timestamp without time zone |              |               | now()
 seat_type_id | integer                     |              | not null      | 1
Indexe:
    "seats_pkey" PRIMARY KEY, btree (seat_id)
    "unique_screen_row_number" UNIQUE CONSTRAINT, btree (screen_id, "row", number)
Fremdschl³ssel-Constraints:
    "seats_screen_id_fkey" FOREIGN KEY (screen_id) REFERENCES screens(screen_id)
    "seats_seat_type_id_fkey" FOREIGN KEY (seat_type_id) REFERENCES seat_types(seat_type_id) ON DELETE CASCADE
Fremdschl³sselverweise von:
    TABLE "booking_seats" CONSTRAINT "booking_seats_seat_id_fkey" FOREIGN KEY (seat_id) REFERENCES seats(seat_id) ON DELETE CASCADE
    TABLE "user_cart_items" CONSTRAINT "fk_seat" FOREIGN KEY (seat_id) REFERENCES seats(seat_id) ON DELETE CASCADE
    TABLE "guest_cart_items" CONSTRAINT "guest_cart_items_seat_id_fkey" FOREIGN KEY (seat_id) REFERENCES seats(seat_id) ON DELETE CASCADE


cinephoria-backend::DATABASE=>  \d user_cart_items
                                                      Tabelle ╗public.user_cart_items½
        Spalte         |             Typ             | Sortierfolge | NULL erlaubt? |                      Vorgabewert
-----------------------+-----------------------------+--------------+---------------+-------------------------------------------------------
 cart_item_id          | integer                     |              | not null      | nextval('user_cart_items_cart_item_id_seq'::regclass)
 user_id               | integer                     |              | not null      |
 seat_id               | integer                     |              | not null      |
 price                 | numeric(10,2)               |              | not null      |
 added_at              | timestamp without time zone |              |               | CURRENT_TIMESTAMP
 reserved_until        | timestamp without time zone |              |               |
 showtime_id           | integer                     |              | not null      |
 seat_type_discount_id | integer                     |              |               |
Indexe:
    "user_cart_items_pkey" PRIMARY KEY, btree (cart_item_id)
    "user_cart_showtime_seat_unique" UNIQUE CONSTRAINT, btree (showtime_id, seat_id)
Fremdschl³ssel-Constraints:
    "fk_seat" FOREIGN KEY (seat_id) REFERENCES seats(seat_id) ON DELETE CASCADE
    "fk_seat_type_discount" FOREIGN KEY (seat_type_discount_id) REFERENCES seat_type_discounts(seat_type_discount_id) ON DELETE SET NULL
    "fk_user_cart" FOREIGN KEY (user_id) REFERENCES user_carts(user_id) ON DELETE CASCADE
    "user_cart_items_showtime_id_fkey" FOREIGN KEY (showtime_id) REFERENCES showtimes(showtime_id)


cinephoria-backend::DATABASE=>  \d user_carts
                                 Tabelle ╗public.user_carts½
   Spalte    |             Typ             | Sortierfolge | NULL erlaubt? |    Vorgabewert
-------------+-----------------------------+--------------+---------------+-------------------
 user_id     | integer                     |              | not null      |
 created_at  | timestamp without time zone |              |               | CURRENT_TIMESTAMP
 valid_until | timestamp without time zone |              |               |
Indexe:
    "user_carts_pkey" PRIMARY KEY, btree (user_id)
Fremdschl³ssel-Constraints:
    "fk_user" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
Fremdschl³sselverweise von:
    TABLE "user_cart_items" CONSTRAINT "fk_user_cart" FOREIGN KEY (user_id) REFERENCES user_carts(user_id) ON DELETE CASCADE


cinephoria-backend::DATABASE=>  \d discounts
                                             Tabelle ╗public.discounts½
   Spalte    |          Typ          | Sortierfolge | NULL erlaubt? |                  Vorgabewert
-------------+-----------------------+--------------+---------------+------------------------------------------------
 discount_id | integer               |              | not null      | nextval('discounts_discount_id_seq'::regclass)
 name        | character varying(50) |              | not null      |
 description | text                  |              |               |
Indexe:
    "discounts_pkey" PRIMARY KEY, btree (discount_id)
Fremdschl³sselverweise von:
    TABLE "seat_type_discounts" CONSTRAINT "seat_type_discounts_discount_id_fkey" FOREIGN KEY (discount_id) REFERENCES discounts(discount_id) ON DELETE CASCADE


cinephoria-backend::DATABASE=>  \d user_points
                                 Tabelle ╗public.user_points½
    Spalte    |             Typ             | Sortierfolge | NULL erlaubt? |    Vorgabewert
--------------+-----------------------------+--------------+---------------+-------------------
 user_id      | integer                     |              | not null      |
 points       | integer                     |              | not null      | 0
 last_updated | timestamp without time zone |              | not null      | CURRENT_TIMESTAMP
Indexe:
    "user_points_pkey" PRIMARY KEY, btree (user_id)
Fremdschl³ssel-Constraints:
    "user_points_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE


cinephoria-backend::DATABASE=>  \d users
                                            Tabelle ╗public.users½
    Spalte     |          Typ           | Sortierfolge | NULL erlaubt? |             Vorgabewert
---------------+------------------------+--------------+---------------+--------------------------------------
 id            | integer                |              | not null      | nextval('users_id_seq'::regclass)
 email         | text                   |              | not null      |
 password      | text                   |              | not null      |
 vorname       | character varying(255) |              |               |
 nachname      | character varying(255) |              |               |
 role          | character varying(50)  |              |               | 'Standard'::character varying
 profile_image | character varying(255) |              |               | 'default.png'::character varying
 nickname      | character varying(255) |              |               | 'DefaultNickname'::character varying
Indexe:
    "users_pkey" PRIMARY KEY, btree (id)
    "users_email_key" UNIQUE CONSTRAINT, btree (email)
Fremdschl³sselverweise von:
    TABLE "bookings" CONSTRAINT "bookings_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    TABLE "user_carts" CONSTRAINT "fk_user" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    TABLE "points_transactions" CONSTRAINT "points_transactions_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    TABLE "user_points" CONSTRAINT "user_points_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
Trigger:
    after_user_insert AFTER INSERT ON users FOR EACH ROW EXECUTE FUNCTION create_user_points()


cinephoria-backend::DATABASE=>  \d guest_cart_items
                                                      Tabelle ╗public.guest_cart_items½
        Spalte         |             Typ             | Sortierfolge | NULL erlaubt? |                      Vorgabewert
-----------------------+-----------------------------+--------------+---------------+--------------------------------------------------------
 cart_item_id          | integer                     |              | not null      | nextval('guest_cart_items_cart_item_id_seq'::regclass)
 guest_id              | text                        |              | not null      |
 seat_id               | integer                     |              | not null      |
 price                 | numeric(10,2)               |              | not null      |
 added_at              | timestamp without time zone |              |               | CURRENT_TIMESTAMP
 reserved_until        | timestamp without time zone |              | not null      |
 showtime_id           | integer                     |              | not null      |
 seat_type_discount_id | integer                     |              |               |
Indexe:
    "guest_cart_items_pkey" PRIMARY KEY, btree (cart_item_id)
    "guest_cart_showtime_seat_unique" UNIQUE CONSTRAINT, btree (showtime_id, seat_id)
Fremdschl³ssel-Constraints:
    "fk_guest_seat_type_discount" FOREIGN KEY (seat_type_discount_id) REFERENCES seat_type_discounts(seat_type_discount_id) ON DELETE SET NULL
    "guest_cart_items_guest_id_fkey" FOREIGN KEY (guest_id) REFERENCES guest_carts(guest_id) ON DELETE CASCADE
    "guest_cart_items_seat_id_fkey" FOREIGN KEY (seat_id) REFERENCES seats(seat_id) ON DELETE CASCADE
    "guest_cart_items_showtime_id_fkey" FOREIGN KEY (showtime_id) REFERENCES showtimes(showtime_id)


cinephoria-backend::DATABASE=>  \d guest_carts
                                 Tabelle ╗public.guest_carts½
   Spalte    |             Typ             | Sortierfolge | NULL erlaubt? |    Vorgabewert
-------------+-----------------------------+--------------+---------------+-------------------
 guest_id    | text                        |              | not null      |
 created_at  | timestamp without time zone |              |               | CURRENT_TIMESTAMP
 valid_until | timestamp without time zone |              |               |
Indexe:
    "guest_carts_pkey" PRIMARY KEY, btree (guest_id)
Fremdschl³sselverweise von:
    TABLE "guest_cart_items" CONSTRAINT "guest_cart_items_guest_id_fkey" FOREIGN KEY (guest_id) REFERENCES guest_carts(guest_id) ON DELETE CASCADE


cinephoria-backend::DATABASE=>  \d points_transactions
                                                   Tabelle ╗public.points_transactions½
     Spalte     |             Typ             | Sortierfolge | NULL erlaubt? |                         Vorgabewert
----------------+-----------------------------+--------------+---------------+-------------------------------------------------------------
 transaction_id | integer                     |              | not null      | nextval('points_transactions_transaction_id_seq'::regclass)
 user_id        | integer                     |              | not null      |
 points_change  | integer                     |              | not null      |
 description    | character varying(255)      |              |               |
 timestamp      | timestamp without time zone |              | not null      | CURRENT_TIMESTAMP
 reward_id      | integer                     |              |               |
Indexe:
    "points_transactions_pkey" PRIMARY KEY, btree (transaction_id)
    "idx_points_transactions_reward_id" btree (reward_id)
Fremdschl³ssel-Constraints:
    "points_transactions_reward_id_fkey" FOREIGN KEY (reward_id) REFERENCES rewards(reward_id) ON DELETE SET NULL
    "points_transactions_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE


cinephoria-backend::DATABASE=>  \d seat_type_discounts
                                          Tabelle ╗public.seat_type_discounts½
        Spalte         |      Typ      | Sortierfolge | NULL erlaubt? |                   Vorgabewert
-----------------------+---------------+--------------+---------------+-------------------------------------------------
 seat_type_id          | integer       |              | not null      |
 discount_id           | integer       |              | not null      |
 discount_amount       | numeric(10,2) |              |               |
 discount_percentage   | numeric(5,2)  |              |               |
 seat_type_discount_id | integer       |              | not null      | nextval('seat_type_discounts_id_seq'::regclass)
Indexe:
    "seat_type_discounts_pkey" PRIMARY KEY, btree (seat_type_discount_id)
    "unique_seat_type_discount" UNIQUE CONSTRAINT, btree (seat_type_id, discount_id)
Fremdschl³ssel-Constraints:
    "seat_type_discounts_discount_id_fkey" FOREIGN KEY (discount_id) REFERENCES discounts(discount_id) ON DELETE CASCADE
    "seat_type_discounts_seat_type_id_fkey" FOREIGN KEY (seat_type_id) REFERENCES seat_types(seat_type_id) ON DELETE CASCADE
Fremdschl³sselverweise von:
    TABLE "booking_seats" CONSTRAINT "fk_booking_seats_seat_type_discount" FOREIGN KEY (seat_type_discount_id) REFERENCES seat_type_discounts(seat_type_discount_id) ON DELETE SET NULL
    TABLE "guest_cart_items" CONSTRAINT "fk_guest_seat_type_discount" FOREIGN KEY (seat_type_discount_id) REFERENCES seat_type_discounts(seat_type_discount_id) ON DELETE SET NULL
    TABLE "user_cart_items" CONSTRAINT "fk_seat_type_discount" FOREIGN KEY (seat_type_discount_id) REFERENCES seat_type_discounts(seat_type_discount_id) ON DELETE SET NULL


cinephoria-backend::DATABASE=>  \d rewards
                                         Tabelle ╗public.rewards½
   Spalte    |          Typ           | Sortierfolge | NULL erlaubt? |             Vorgabewert
-------------+------------------------+--------------+---------------+-------------------------------------
 reward_id   | integer                |              | not null      | nextval('rewards_id_seq'::regclass)
 title       | character varying(255) |              | not null      |
 points      | integer                |              | not null      |
 description | text                   |              |               |
 image       | character varying(255) |              |               |
Indexe:
    "rewards_pkey" PRIMARY KEY, btree (reward_id)
Fremdschl³sselverweise von:
    TABLE "points_transactions" CONSTRAINT "points_transactions_reward_id_fkey" FOREIGN KEY (reward_id) REFERENCES rewards(reward_id) ON DELETE SET NULL


cinephoria-backend::DATABASE=>  \d supermarkt_pfand
                                            Tabelle ╗public.supermarkt_pfand½
   Spalte    |          Typ          | Sortierfolge | NULL erlaubt? |                    Vorgabewert
-------------+-----------------------+--------------+---------------+----------------------------------------------------
 pfand_id    | integer               |              | not null      | nextval('supermarkt_pfand_pfand_id_seq'::regclass)
 amount      | numeric(10,2)         |              | not null      |
 name        | character varying(50) |              | not null      |
 description | text                  |              |               |
Indexe:
    "supermarkt_pfand_pkey" PRIMARY KEY, btree (pfand_id)
Fremdschl³sselverweise von:
    TABLE "supermarkt_items" CONSTRAINT "fk_pfand" FOREIGN KEY (pfand_id) REFERENCES supermarkt_pfand(pfand_id) ON DELETE SET NULL


cinephoria-backend::DATABASE=>  \d supermarkt_items
                                              Tabelle ╗public.supermarkt_items½
   Spalte   |             Typ             | Sortierfolge | NULL erlaubt? |                    Vorgabewert
------------+-----------------------------+--------------+---------------+---------------------------------------------------
 item_id    | integer                     |              | not null      | nextval('supermarkt_items_item_id_seq'::regclass)
 barcode    | character varying(50)       |              | not null      |
 item_name  | character varying(100)      |              | not null      |
 price      | numeric(10,2)               |              | not null      |
 category   | character varying(50)       |              |               |
 created_at | timestamp without time zone |              |               | CURRENT_TIMESTAMP
 updated_at | timestamp without time zone |              |               | CURRENT_TIMESTAMP
 pfand_id   | integer                     |              |               |
Indexe:
    "supermarkt_items_pkey" PRIMARY KEY, btree (item_id)
    "supermarkt_items_barcode_key" UNIQUE CONSTRAINT, btree (barcode)
Fremdschl³ssel-Constraints:
    "fk_pfand" FOREIGN KEY (pfand_id) REFERENCES supermarkt_pfand(pfand_id) ON DELETE SET NULL
Trigger:
    set_updated_at_supermarkt_items BEFORE UPDATE ON supermarkt_items FOR EACH ROW EXECUTE FUNCTION update_supermarkt_items_updated_at()


cinephoria-backend::DATABASE=>  \d bookings
                                                  Tabelle ╗public.bookings½
     Spalte      |             Typ             | Sortierfolge | NULL erlaubt? |                 Vorgabewert
-----------------+-----------------------------+--------------+---------------+----------------------------------------------
 booking_id      | integer                     |              | not null      | nextval('bookings_booking_id_seq'::regclass)
 user_id         | integer                     |              |               |
 booking_time    | timestamp without time zone |              |               | CURRENT_TIMESTAMP
 payment_status  | character varying(50)       |              |               | 'completed'::character varying
 total_amount    | numeric(10,2)               |              | not null      |
 created_at      | timestamp without time zone |              |               | CURRENT_TIMESTAMP
 paypal_order_id | character varying(255)      |              |               |
 email           | character varying(255)      |              |               |
 nachname        | character varying(255)      |              |               |
 vorname         | character varying(255)      |              |               |
 qr_token        | character varying(255)      |              |               |
 qr_seite        | character varying(255)      |              |               |
Indexe:
    "bookings_pkey" PRIMARY KEY, btree (booking_id)
    "bookings_qr_seite_key" UNIQUE CONSTRAINT, btree (qr_seite)
    "bookings_qr_token_key" UNIQUE CONSTRAINT, btree (qr_token)
Fremdschl³ssel-Constraints:
    "bookings_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
Fremdschl³sselverweise von:
    TABLE "booking_seats" CONSTRAINT "booking_seats_booking_id_fkey" FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE
