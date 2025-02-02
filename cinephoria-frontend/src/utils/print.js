import { exec } from "child_process";
import fs from "fs";

export function testPrint(scannedItems, total, paymentMethod) {
    // ESC/POS-Reset + CP437 setzen + Quittungstext
    let receiptText = "\x1B\x40" +  // Drucker zurücksetzen
                      "\x1B\x74\x00" + // Zeichensatz auf CP437 setzen
                      "Supermarkt-Quittung\n" +
                      "----------------------\n";

    scannedItems.forEach((item) => {
        receiptText += `${item.name} x${item.quantity}  ${item.totalPrice.toFixed(2)} EUR\n`;
    });

    receiptText += "----------------------\n" +
                   `Gesamt: ${total.toFixed(2)} EUR\n` +
                   `Zahlungsmethode: ${paymentMethod}\n` +
                   "Danke für Ihren Einkauf!\n\n\n" +
                   "\x1D\x56\x42\x03"; // Papier ausgeben

    // Speichere den Text in einer temporären Datei
    fs.writeFileSync("temp_receipt.txt", receiptText, "binary");

    // Drucke die Datei mit lp
    exec(`lp -d supermarkt temp_receipt.txt`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Fehler beim Drucken: ${error.message}`);
            return;
        }
        console.log(`Druck erfolgreich!`, stdout);
    });

    // Datei nach dem Druck löschen
    setTimeout(() => fs.unlinkSync("temp_receipt.txt"), 5000);
}
