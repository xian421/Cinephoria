// src/utils/notifications.js
import Swal from 'sweetalert2';

// Definiere eine zentrale SweetAlert2-Mixin-Konfiguration für Dark Mode
const SwalDark = Swal.mixin({
    customClass: {
        popup: 'custom-swal2-popup',
        title: 'custom-swal2-title',
        confirmButton: 'custom-swal2-confirm',
        cancelButton: 'custom-swal2-cancel',
        footer: 'custom-swal2-footer',
    },
    buttonsStyling: false, // Verhindert, dass SweetAlert2 eigene Stile für Buttons anwendet
    showClass: {
        popup: 'swal2-show',
    },
    hideClass: {
        popup: 'swal2-hide',
    }
});

/**
 * Zeigt eine benutzerdefinierte Benachrichtigung an und führt eine Aktion beim Bestätigen aus.
 * @param {string} title - Der Titel der Benachrichtigung.
 * @param {string} text - Der Text der Benachrichtigung.
 * @param {string} icon - Das Symbol der Benachrichtigung (z.B. 'info', 'success', 'error', 'warning').
 * @param {object} options - Zusätzliche Optionen für SweetAlert2 (optional).
 * @param {Function} onConfirm - Eine Callback-Funktion, die beim Bestätigen ausgeführt wird (optional).
 * @returns {Promise<import('sweetalert2').SweetAlertResult>} - Das Ergebnis der SweetAlert2-Instanz.
 */
export function showCustomAlert(title, text, icon, confirmButton = "Okay", options = {}, onConfirm = null) {
    return SwalDark.fire({
        title: title,
        text: text,
        icon: icon,
        confirmButtonText: confirmButton, // Standard-Text für den Bestätigungsbutton
        ...options,
    }).then((result) => {
        if (result.isConfirmed && typeof onConfirm === 'function') {
            onConfirm();
        }
        return result;
    });
}

/**
 * Zeigt einen Erfolgstoast in der oberen rechten Ecke an.
 * @param {string} message - Die Nachricht, die angezeigt werden soll.
 */
export function showSuccessToast(message) {
    const Toast = SwalDark.mixin({
        toast: true,
        position: "top-end",
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer);
            toast.addEventListener('mouseleave', Swal.resumeTimer);
        }
    });
    Toast.fire({
        icon: "success",
        title: message
    });
}

/**
 * Zeigt eine Fehlermeldung an.
 * @param {string} message - Die Fehlermeldung, die angezeigt werden soll.
 * @returns {Promise<import('sweetalert2').SweetAlertResult>} - Das Ergebnis der SweetAlert2-Instanz.
 */
export function showErrorAlert(message) {
    return SwalDark.fire({
        title: "Fehler",
        text: message || "Ein Fehler ist aufgetreten. Bitte versuche es erneut.",
        icon: "error",
        confirmButtonText: "OK",
    });
}

/**
 * Zeigt eine Erfolgsmeldung an.
 * @param {string} message - Die Erfolgsmeldung, die angezeigt werden soll.
 * @returns {Promise<import('sweetalert2').SweetAlertResult>} - Das Ergebnis der SweetAlert2-Instanz.
 */
export function showSuccessAlert(message) {
    return SwalDark.fire({
        title: "Erfolg",
        text: message,
        icon: "success",
        confirmButtonText: "OK",
        timer: 1000,
    });
}

/**
 * Zeigt einen Bestätigungsdialog an.
 * @param {string} title - Der Titel des Dialogs.
 * @param {string} text - Der Text des Dialogs.
 * @returns {Promise<import('sweetalert2').SweetAlertResult>} - Das Ergebnis der SweetAlert2-Instanz.
 */
export function showConfirmationDialog(title, text) {
    return SwalDark.fire({
        title: title,
        text: text,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Ja',
        cancelButtonText: 'Nein',
    });
}

/**
 * Zeigt eine Warnmeldung an.
 * @param {string} title - Der Titel der Warnung.
 * @param {string} text - Der Text der Warnung.
 * @param {number} timer - Die Dauer der Anzeige in Millisekunden (optional).
 * @returns {Promise<import('sweetalert2').SweetAlertResult>} - Das Ergebnis der SweetAlert2-Instanz.
 */
export function showWarningAlert(title, text, timer = 3000) {
    return SwalDark.fire({
        title: title,
        text: text,
        icon: 'warning',
        timer: timer,
        showConfirmButton: false,
    });
}
