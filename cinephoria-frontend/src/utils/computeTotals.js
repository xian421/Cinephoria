// src/utils/computeTotals.js

const TAX_RATE = 0.19;

/**
 * Berechnet die Zwischensumme, MwSt. und Gesamtbetrag.
 * @param {Array} scannedItems - Liste der gescannten Artikel.
 * @param {Number} discount - Rabatt in Euro.
 * @returns {Object} - { subtotal, tax, total }
 */
export function computeTotals(scannedItems, discount = 0) {
    const subtotal = scannedItems.reduce((acc, item) => acc + (item.price * item.quantity), 0);
    const tax = subtotal * TAX_RATE;
    const total = subtotal + pfandTotal(scannedItems) - discount;
    return { subtotal, tax, total };
}

/**
 * Berechnet die Gesamtsumme der Pfandbeträge.
 * @param {Array} scannedItems - Liste der gescannten Artikel.
 * @returns {Number} - Gesamtsumme der Pfandbeträge.
 */
export function pfandTotal(scannedItems) {
    return scannedItems.reduce((acc, item) => acc + (item.pfandPrice * item.quantity), 0);
}
