// src/services/pfandService.js
import { get } from 'svelte/store';
import { authStore } from '../stores/authStore.js';
import { fetchProductByBarcode } from '../services/api';

/**
 * Scannt einen Barcode und gibt das verarbeitete Pfand-Item zurück.
 * @param {string} barcode 
 * @returns {Promise<Object>} { pfand_id, pfand_name, amount }
 * @throws {Error} falls der Artikel nicht gefunden wird oder keinen Pfand hat.
 */
export async function scanPfandItem(barcode) {
  const token = get(authStore).token;
  const product = await fetchProductByBarcode(token, barcode);
  if (!product) {
    throw new Error('Artikel nicht gefunden.');
  }
  if (product.pfand_id && product.amount) {
    const amount = parseFloat(product.amount);
    if (isNaN(amount)) {
      throw new Error('Ungültiger Pfandbetrag.');
    }
    return {
      pfand_id: product.pfand_id,
      pfand_name: product.pfand_name,
      amount,
    };
  }
  throw new Error('Artikel ohne Pfand.');
}

/**
 * Fügt einen gescannten Pfand-Artikel zur Liste hinzu oder erhöht die Menge.
 * @param {Array} currentItems 
 * @param {Object} newItem 
 * @returns {Array} aktualisierte Liste
 */
export function addOrUpdatePfandItem(currentItems, newItem) {
  const index = currentItems.findIndex(item => item.pfand_id === newItem.pfand_id);
  if (index !== -1) {
    return currentItems.map((item, i) =>
      i === index ? { ...item, quantity: item.quantity + 1 } : item
    );
  } else {
    return [
      ...currentItems,
      {
        ...newItem,
        quantity: 1,
      },
    ];
  }
}

/**
 * Berechnet die Gesamtsumme der Pfandartikel.
 * @param {Array} pfandItems 
 * @returns {number}
 */
export function calculateTotalPfand(pfandItems) {
  return pfandItems.reduce(
    (sum, item) => sum + item.quantity * item.amount,
    0
  );
}
