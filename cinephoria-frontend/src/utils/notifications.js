//rc/utils/notifications.js
import Swal from 'sweetalert2';

export function showSuccessToast(message) {
    const Toast = Swal.mixin({
        toast: true,
        position: "top-end",
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.onmouseenter = Swal.stopTimer;
            toast.onmouseleave = Swal.resumeTimer;
        }
    });
    Toast.fire({
        icon: "success",
        title: message
    });
}

export function showErrorAlert(message) {
    Swal.fire({
        title: "Fehler",
        text: message || "Ein Fehler ist aufgetreten. Bitte versuche es erneut.",
        icon: "error",
        confirmButtonText: "OK",
    });
}

export function showSuccessAlert(message) {
    Swal.fire({
        title: "Erfolg",
        text: message,
        icon: "success",
        confirmButtonText: "OK",
    });
}
