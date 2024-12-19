// src/utils/getInitials.js
export function getInitials(vorname, nachname) {
    const vorInitial = vorname ? vorname.charAt(0).toUpperCase() : '';
    const nachInitial = nachname ? nachname.charAt(0).toUpperCase() : '';
    return `${vorInitial}${nachInitial}`;
}
