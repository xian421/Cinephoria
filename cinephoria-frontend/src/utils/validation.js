// src/utils/validation.js

/**
 * Validiert ein Produktobjekt.
 * @param {Object} item - Das Produktobjekt.
 * @param {Array} pfandOptions - Liste der verfügbaren Pfandoptionen.
 * @returns {String|null} - Gibt einen Fehlerstring zurück oder null, wenn keine Fehler vorliegen.
 */
export function validateProduct(item, pfandOptions) {
    const { barcode, item_name, price, category, pfand_id } = item;
    
    if (!barcode || !item_name || !price || !category) {
        return 'Bitte alle Felder ausfüllen.';
    }
    
    if (pfand_id && !pfandOptions.some(p => p.pfand_id === parseInt(pfand_id))) {
        return 'Bitte wähle eine gültige Pfandoption.';
    }
    
    return null;
}
