// src/utils/dateFormatter.js

/**
 * Formatiert ein Datum nach deutschen Standards.
 * @param {String} dateString - Das Datum als String.
 * @returns {String} - Das formatierte Datum.
 */
export function formatDate(dateString) {
    /** @type {Intl.DateTimeFormatOptions} */
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    };
    return new Date(dateString).toLocaleString('de-DE', options);
}
