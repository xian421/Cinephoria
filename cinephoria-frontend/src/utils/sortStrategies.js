// src/utils/sortStrategies.js

/**
 * Vergleicht zwei Datumswerte.
 * @param {any} a - Wert A.
 * @param {any} b - Wert B.
 * @param {string} direction - 'asc' oder 'desc'.
 * @returns {number}
 */
export const sortByDate = (a, b, direction) => {
    const aTime = new Date(a).getTime();
    const bTime = new Date(b).getTime();
    return direction === 'asc' ? aTime - bTime : bTime - aTime;
  };
  
  /**
   * Vergleicht zwei numerische Werte.
   * @param {any} a - Wert A.
   * @param {any} b - Wert B.
   * @param {string} direction - 'asc' oder 'desc'.
   * @returns {number}
   */
  export const sortByNumeric = (a, b, direction) => {
    return direction === 'asc'
      ? parseFloat(a) - parseFloat(b)
      : parseFloat(b) - parseFloat(a);
  };
  
  /**
   * Vergleicht zwei Strings alphabetisch.
   * @param {any} a - Wert A.
   * @param {any} b - Wert B.
   * @param {string} direction - 'asc' oder 'desc'.
   * @returns {number}
   */
  export const sortByString = (a, b, direction) => {
    const aStr = a.toString().toLowerCase();
    const bStr = b.toString().toLowerCase();
    if (aStr < bStr) return direction === 'asc' ? -1 : 1;
    if (aStr > bStr) return direction === 'asc' ? 1 : -1;
    return 0;
  };
  