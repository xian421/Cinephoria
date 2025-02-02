// src/services/productService.js

import { fetchSupermarketitems, addSupermarketItem, updateSupermarketItem, fetchPfandOptions } from './api';
import { authStore } from '../stores/authStore.js';
import { get } from 'svelte/store';
import { validateProduct } from '../utils/validation.js';


/**
 * @typedef {Object} Product
 * @property {number} item_id - Die eindeutige ID des Artikels.
 * @property {string} item_name - Der Name des Artikels.
 * @property {string} barcode - Der Barcode des Artikels.
 * @property {string} category - Die Kategorie des Artikels.
 * @property {string|null} description - Die Beschreibung des Artikels.
 * @property {string|null} pfand_id - Die Pfand-ID des Artikels.
 * @property {string|null} pfand_name - Der Name des Pfandartikels.
 * @property {string} price - Der Preis des Artikels (als String, z.B. "3.00").
 * @property {string} created_at - Das Erstellungsdatum des Artikels.
 * @property {string} updated_at - Das Aktualisierungsdatum des Artikels.
 * @property {number|null} amount - Der Pfandbetrag.
 */


/**
 * Lädt alle Produkte vom Server.
 * @returns {Promise<Product[]>} Eine Liste von Produkten.
 * @throws {Error} Wenn das Laden der Produkte fehlschlägt.
 */

export async function loadAllProducts() {
    try {
        const token = get(authStore).token;
        const data = await fetchSupermarketitems(token);
        console.log('fetchSupermarketitems: ' ,data);
        return data.items;
    } catch (error) {
        console.error('Fehler beim Laden der Produkte:', error);
        throw new Error('Fehler beim Laden der Produkte.');
    }
}

/**
 * Lädt alle Pfand-Optionen vom Server.
 * @returns {Promise<Array>} Eine Liste von Pfand-Optionen.
 * @throws {Error} Wenn das Laden der Pfand-Optionen fehlschlägt.
 */
export async function loadPfandOptions() {
    const token = get(authStore).token;
    try {
        const data = await fetchPfandOptions(token);
        return data.pfand_options;
    } catch (error) {
        console.error('Fehler beim Laden der Pfand-Optionen:', error);
        throw new Error('Fehler beim Laden der Pfand-Optionen.');
    }
}

/**
 * Fügt ein neues Produkt hinzu.
 * @param {Object} product - Das Produktobjekt.
 * @param {Array} pfandOptions - Liste der verfügbaren Pfand-Optionen.
 * @returns {Promise<Object>} Das hinzugefügte Produkt.
 * @throws {Error} Wenn die Validierung fehlschlägt oder das Hinzufügen des Produkts fehlschlägt.
 */
export async function addProduct(product, pfandOptions) {
    // Validierung des Produkts
    const validationError = validateProduct(product, pfandOptions);
    if (validationError) {
        throw new Error(validationError);
    }

    const token = get(authStore).token;
    try {
        const addedItem = await addSupermarketItem(
            token,
            product.barcode,
            product.item_name,
            product.price,
            product.category,
            product.pfand_id
        );
        return addedItem.item;
    } catch (error) {
        console.error('Fehler beim Hinzufügen des Produkts:', error);
        throw new Error(error.message || 'Fehler beim Hinzufügen des Produkts.');
    }
}

/**
 * Aktualisiert ein bestehendes Produkt.
 * @param {Object} product - Das zu aktualisierende Produktobjekt.
 * @param {Array} pfandOptions - Liste der verfügbaren Pfand-Optionen.
 * @returns {Promise<Object>} Das aktualisierte Produkt.
 * @throws {Error} Wenn die Validierung fehlschlägt oder das Aktualisieren des Produkts fehlschlägt.
 */
export async function updateProduct(product, pfandOptions) {
    // Validierung des Produkts
    const validationError = validateProduct(product, pfandOptions);
    if (validationError) {
        throw new Error(validationError);
    }

    const token = get(authStore).token;
    try {
        const updatedItem = await updateSupermarketItem(
            token,
            product.item_id,
            product.barcode,
            product.item_name,
            product.price,
            product.category,
            product.pfand_id
        );
        return updatedItem.item;
    } catch (error) {
        console.error('Fehler beim Aktualisieren des Produkts:', error);
        throw new Error(error.message || 'Fehler beim Aktualisieren des Produkts.');
    }
}
