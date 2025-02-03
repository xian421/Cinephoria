// src/utils/computeTotals.js
const TAX_RATE = 0.19;

/**
 * Berechnet Zwischensumme, Pfand, MwSt und Gesamtbetrag.
 * Gibt zusätzlich den Bruttobetrag (gross) zurück, um z. B. Rabattvalidierung zu ermöglichen.
 *
 * @param {Array} scannedItems - Liste der gescannten Artikel.
 * @param {Number} discount - Rabatt in Euro.
 * @returns {Object} - { subtotal, pfand, tax, total, gross }
 */
export function computeTotals(scannedItems, discount = 0) {
  // Summe der Artikelpreise (ohne Pfand)
  const itemsSum = scannedItems.reduce((acc, item) => acc + (item.price * item.quantity), 0);
  // Summe aller Pfandbeträge
  const pfand = scannedItems.reduce((acc, item) => acc + (item.pfandPrice * item.quantity), 0);
  // Bruttosumme (alle Angaben bereits inkl. MwSt)
  const gross = itemsSum + pfand;
  // Rabatt darf nicht den Bruttobetrag übersteigen
  const validDiscount = Math.min(discount, gross);
  // Endbetrag abzüglich Rabatt, niemals negativ
  const total = Math.max(0, gross - validDiscount);
  const tax = total * TAX_RATE;
 
  return { subtotal: itemsSum, pfand, tax, total, gross };
}
