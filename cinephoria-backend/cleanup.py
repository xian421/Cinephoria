# cleanup.py
import psycopg2
import os
import logging

# Konfiguriere das Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Holen der Datenbank-URL aus den Umgebungsvariablen
DATABASE_URL = os.getenv('DATABASE_URL')


def cleanup_inactive_carts():
   logging.info("Macht gerade nichts weil auskommentiert!")
#     try:
#         with psycopg2.connect(DATABASE_URL) as conn:
#             with conn.cursor() as cursor:

#                 cursor.execute("""
#                     SELECT max(reserved_until), user_id
#                     FROM user_cart_items
#                     GROUP BY user_id
#                                """)
#                 for row in cursor.fetchall():
#                     logging.info(row)
#                     User_id = row[0]
#                     reversed_until = row[0]

#                 # Löschen von user_cart_items, deren Reservierungszeit abgelaufen ist
#                 cursor.execute("""
#                     DELETE FROM user_cart_items
#                     WHERE reserved_until < NOW()
#                 """)
#                 logging.info("Abgelaufene user_cart_items wurden gelöscht.")

#                 # Löschen von guest_cart_items, deren Reservierungszeit abgelaufen ist
#                 cursor.execute("""
#                     DELETE FROM guest_cart_items
#                     WHERE reserved_until < NOW()
#                 """)
#                 logging.info("Abgelaufene guest_cart_items wurden gelöscht.")

#                 # Löschen von leeren user_carts
#                 cursor.execute("""
#                     DELETE FROM user_carts
#                     WHERE user_id NOT IN (SELECT DISTINCT user_id FROM user_cart_items)
#                 """)
#                 logging.info("Leere user_carts wurden gelöscht.")

#                 # Löschen von leeren guest_carts
#                 cursor.execute("""
#                     DELETE FROM guest_carts
#                     WHERE guest_id NOT IN (SELECT DISTINCT guest_id FROM guest_cart_items)
#                 """)
#                 logging.info("Leere guest_carts wurden gelöscht.")

#                 conn.commit()
#         logging.info("Bereinigung der inaktiven Warenkörbe abgeschlossen.")
#     except Exception as e:
#         logging.error(f"Fehler beim Bereinigen der inaktiven Warenkörbe: {e}")

if __name__ == '__main__':
    cleanup_inactive_carts()
