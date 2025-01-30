// src/stores/productStore.js
import { writable } from 'svelte/store';

/**
 * Store für die Produktliste.
 */
export const productsStore = writable([]);

/**
 * Funktion zum Aktualisieren der Produktliste.
 * @param {Array} newProducts - Neue Liste von Produkten.
 */
export function setProducts(newProducts) {
    productsStore.set(newProducts);
}

/**
 * Funktion zum Hinzufügen eines neuen Produkts.
 * @param {Object} product - Das hinzuzufügende Produkt.
 */
export function addProductToStore(product) {
    productsStore.update(products => [...products, product]);
}

/**
 * Funktion zum Aktualisieren eines bestehenden Produkts.
 * @param {Object} updatedProduct - Das aktualisierte Produkt.
 */
export function updateProductInStore(updatedProduct) {
    productsStore.update(products => 
        products.map(product => 
            product.item_id === updatedProduct.item_id ? updatedProduct : product
        )
    );
}
