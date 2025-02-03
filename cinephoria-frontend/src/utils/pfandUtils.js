// src/utils/pfandUtils.js

// Minimalistische Icons – hier die SVG-Codes als Konstanten

// Eine einfache Flasche: Körper und Hals
export const normalBottleSVG = `
  <svg viewBox="0 0 48 48" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
    <!-- Flasche -->
    <rect x="18" y="10" width="12" height="24" fill="#4CAF50" rx="3" ry="3"/>
    <rect x="21" y="4" width="6" height="6" fill="#4CAF50"/>
  </svg>
`;

// Eine Kiste, dargestellt als mehrere Flaschen innerhalb eines Rahmens
export const crateSVG = `
  <svg viewBox="0 0 48 48" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
    <!-- Rahmen der Kiste -->
    <rect x="2" y="2" width="44" height="44" fill="none" stroke="#795548" stroke-width="2"/>
    <!-- Drei Flaschen in einer Reihe -->
    <rect x="6" y="8" width="10" height="20" fill="#4CAF50" rx="2" ry="2"/>
    <rect x="19" y="8" width="10" height="20" fill="#4CAF50" rx="2" ry="2"/>
    <rect x="32" y="8" width="10" height="20" fill="#4CAF50" rx="2" ry="2"/>
  </svg>
`;

// Eine Glasflasche: Nur Umriss in Blau
export const glassBottleSVG = `
  <svg viewBox="0 0 48 48" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
    <!-- Glasflasche -->
    <rect x="18" y="10" width="12" height="24" fill="none" stroke="#2196F3" stroke-width="2" rx="3" ry="3"/>
    <rect x="21" y="4" width="6" height="6" fill="none" stroke="#2196F3" stroke-width="2"/>
  </svg>
`;

// Ein Cinephoria-Becher: Ein Becher, in dessen Mitte ein "C" steht
export const cinephoriaCupSVG = `
  <svg viewBox="0 0 48 48" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
    <!-- Becherform -->
    <path d="M12,14 Q24,4 36,14 L36,30 Q24,38 12,30 Z" fill="#E91E63" stroke="#880E4F" stroke-width="2"/>
    <!-- Buchstabe C in der Mitte -->
    <text x="24" y="24" text-anchor="middle" fill="white" font-size="12" font-family="Arial" dy=".3em">C</text>
  </svg>
`;

const pfandIcons = {
  "Flasche": normalBottleSVG,
  "Kiste": crateSVG,
  "Glasflasche": glassBottleSVG,
  "Cinephoria-Becher": cinephoriaCupSVG,
};

/**
 * Gibt das passende SVG-Icon für einen Pfandnamen zurück.
 * Falls kein Icon gefunden wird, gibt es einen Fallback zurück.
 * @param {string} pfandName 
 * @returns {string} SVG-Code
 */
export function getPfandSVG(pfandName) {
  return pfandIcons[pfandName] || `
    <svg viewBox="0 0 48 48" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
      <circle cx="24" cy="24" r="20" fill="#ccc" />
      <text x="50%" y="55%" fill="#333" font-size="10" text-anchor="middle" font-family="sans-serif">
        Pfand
      </text>
    </svg>
  `;
}

/**
 * Formatiert den Bon als Text.
 * @param {Object} bon 
 * @returns {string}
 */
export function formatBon(bon) {
  let bonText = "Pfandautomat Bon\n";
  bonText += "--------------------------\n";
  bonText += "Artikel:\n";
  bonText += bon.items.map(item => `${item.pfand_name} x${item.quantity}`).join('\n') + '\n';
  bonText += "--------------------------\n";
  bonText += `Summe: ${bon.summe} €\n`;
  bonText += "Danke fuer deinen Einkauf!\n";
  bonText += `${bon.datum}\n`;
  return bonText;
}
