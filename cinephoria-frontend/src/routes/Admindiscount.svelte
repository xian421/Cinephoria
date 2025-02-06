<script>
    import { onMount } from 'svelte';
    // SweetAlert2 NICHT mehr direkt importieren!
    // import Swal from 'sweetalert2';

    // Stattdessen unsere Helferfunktionen aus notifications.js:
    import {
        showErrorAlert,
        showSuccessAlert,
        showConfirmationDialog,
        showCustomAlert
    } from '../utils/notifications.js';

    import {
        fetchDiscounts,
        addDiscount,
        updateDiscount,
        deleteDiscount,
        assignDiscountToSeatType,
        removeDiscountFromSeatType,
        fetchSeatTypesWithDiscounts
    } from '../services/api.js';

    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore.js';
    import { navigate } from 'svelte-routing';

    let discounts = [];
    let seatTypes = [];
    let isLoading = true;
    let error = null;

    // Neue Discount-Daten
    let newDiscountName = '';
    let newDiscountDescription = '';

    // Daten vom Backend laden
    onMount(async () => {
        isLoading = true;
        const token = get(authStore).token;

        try {
            const [fetchedDiscounts, fetchedSeatTypes] = await Promise.all([
                fetchDiscounts(),
                fetchSeatTypesWithDiscounts()
            ]);

            discounts = fetchedDiscounts.discounts;
            seatTypes = fetchedSeatTypes.map(st => ({
                ...st,
                discounts: st.discounts || []
            }));

            isLoading = false;
        } catch (err) {
            console.error('Fehler beim Laden der Discounts oder Sitztypen:', err);
            error = err.message || 'Fehler beim Laden der Daten.';
            isLoading = false;
        }
    });

    // Funktion zum Hinzufügen eines neuen Discounts
    async function handleAddDiscount() {
        const token = get(authStore).token;

        if (!newDiscountName.trim()) {
            showErrorAlert('Bitte geben Sie einen Namen für den Discount ein.');
            return;
        }

        try {
            const result = await addDiscount(token, newDiscountName, newDiscountDescription);
            discounts = [
                ...discounts,
                {
                    discount_id: result.discount_id,
                    name: newDiscountName,
                    description: newDiscountDescription
                }
            ];

            // Felder zurücksetzen
            newDiscountName = '';
            newDiscountDescription = '';
            showSuccessAlert('Der neue Discount wurde hinzugefügt.');
        } catch (err) {
            console.error('Fehler beim Hinzufügen des Discounts:', err);
            showErrorAlert(err.message || 'Fehler beim Hinzufügen des Discounts.');
        }
    }

    // Funktion zum Aktualisieren eines Discounts
    async function handleUpdateDiscount(discount) {
        const token = get(authStore).token;

        if (!discount.name.trim()) {
            showErrorAlert('Bitte geben Sie einen Namen für den Discount ein.');
            return;
        }

        try {
            await updateDiscount(token, discount.discount_id, discount.name, discount.description);
            showSuccessAlert('Der Discount wurde aktualisiert.');
        } catch (err) {
            console.error('Fehler beim Aktualisieren des Discounts:', err);
            showErrorAlert(err.message || 'Fehler beim Aktualisieren des Discounts.');
        }
    }

    // Funktion zum Löschen eines Discounts
    async function handleDeleteDiscount(discount_id) {
        const token = get(authStore).token;

        // Mit eigener Confirm-Dialog-Funktion, wenn du "Ja, löschen" und "Abbrechen" custom willst:
        showCustomAlert(
            'Sind Sie sicher?',
            'Möchten Sie diesen Discount wirklich löschen?',
            'warning',
            'Ja, löschen',
            {
                showCancelButton: true,
                cancelButtonText: 'Abbrechen'
            }
        ).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    await deleteDiscount(token, discount_id);
                    discounts = discounts.filter(d => d.discount_id !== discount_id);

                    // Entferne den Discount aus allen Sitztypen
                    seatTypes = seatTypes.map(seatType => ({
                        ...seatType,
                        discounts: seatType.discounts.filter(d => d.discount_id !== discount_id)
                    }));

                    showSuccessAlert('Der Discount wurde gelöscht.');
                } catch (err) {
                    console.error('Fehler beim Löschen des Discounts:', err);
                    showErrorAlert(err.message || 'Fehler beim Löschen des Discounts.');
                }
            }
        });
    }

    // Funktion zum Zuweisen eines Discounts zu einem Sitztyp
    async function handleAssignDiscount(seatType) {
        const token = get(authStore).token;

        // Hier brauchst du benutzerdefiniertes HTML + preConfirm => showCustomAlert mit Extra-Optionen
        const { value: formValues } = await showCustomAlert(
            `Discount zuweisen: Sitztyp "${seatType.name}"`,
            '', // Du kannst hier optional einen Text reinpacken
            null, // kein Icon => man könnte 'info' nehmen
            'Zuweisen', // Beschriftung des Confirm-Buttons
            {
                html:
                    `<select id="swal-discount-select" class="swal2-select">
                        <option value="" disabled selected>Wähle einen Discount</option>
                        ${
                            discounts
                                .map(d => `<option value="${d.discount_id}">${d.name}</option>`)
                                .join('')
                        }
                    </select>
                    <input id="swal-input1" class="swal2-input" placeholder="Rabattbetrag (EUR)">
                    <input id="swal-input2" class="swal2-input" placeholder="Rabattprozentsatz (%)">`,
                focusConfirm: false,
                preConfirm: () => {
                    const discount_id = document.getElementById('swal-discount-select').value;
                    const discount_amount = document.getElementById('swal-input1').value;
                    const discount_percentage = document.getElementById('swal-input2').value;
                    return { discount_id, discount_amount, discount_percentage };
                },
                showCancelButton: true,
                cancelButtonText: 'Abbrechen'
            }
        );

        if (!formValues) {
            // Abbruch
            return;
        }

        const { discount_id, discount_amount, discount_percentage } = formValues;

        if (!discount_id) {
            showErrorAlert('Bitte wählen Sie einen Discount aus.');
            return;
        }

        if (
            (!discount_amount && !discount_percentage) ||
            (discount_amount && discount_percentage)
        ) {
            showErrorAlert(
                'Bitte geben Sie entweder einen Rabattbetrag oder einen Rabattprozentsatz an.'
            );
            return;
        }

        const selectedDiscount = discounts.find(d => d.discount_id == discount_id);
        if (!selectedDiscount) {
            showErrorAlert('Ungültiger Discount ausgewählt.');
            return;
        }

        try {
            await assignDiscountToSeatType(
                token,
                seatType.seat_type_id,
                selectedDiscount.discount_id,
                discount_amount ? parseFloat(discount_amount) : null,
                discount_percentage ? parseFloat(discount_percentage) : null
            );

            // Aktualisiere Sitztypen-Zuweisungen
            seatTypes = seatTypes.map(st => {
                if (st.seat_type_id === seatType.seat_type_id) {
                    // Überprüfen, ob der Discount bereits zugewiesen ist
                    const existing = st.discounts.find(d => d.discount_id === selectedDiscount.discount_id);
                    if (existing) {
                        // Aktualisiere die vorhandenen Werte
                        return {
                            ...st,
                            discounts: st.discounts.map(d =>
                                d.discount_id === selectedDiscount.discount_id
                                    ? {
                                        ...d,
                                        discount_amount: discount_amount ? parseFloat(discount_amount) : null,
                                        discount_percentage: discount_percentage ? parseFloat(discount_percentage) : null
                                    }
                                    : d
                            )
                        };
                    } else {
                        // Füge den neuen Discount hinzu
                        return {
                            ...st,
                            discounts: [
                                ...st.discounts,
                                {
                                    discount_id: selectedDiscount.discount_id,
                                    name: selectedDiscount.name,
                                    description: selectedDiscount.description,
                                    discount_amount: discount_amount ? parseFloat(discount_amount) : null,
                                    discount_percentage: discount_percentage ? parseFloat(discount_percentage) : null
                                }
                            ]
                        };
                    }
                }
                return st;
            });

            showSuccessAlert('Der Discount wurde dem Sitztyp zugewiesen.');
        } catch (err) {
            console.error('Fehler beim Zuweisen des Discounts:', err);
            showErrorAlert(err.message || 'Fehler beim Zuweisen des Discounts.');
        }
    }

    // Funktion zum Entfernen eines Discounts von einem Sitztyp
    async function handleRemoveDiscount(seatType, discount) {
        const token = get(authStore).token;

        showCustomAlert(
            'Sind Sie sicher?',
            `Möchten Sie den Discount "${discount.name}" von Sitztyp "${seatType.name}" entfernen?`,
            'warning',
            'Ja, entfernen',
            {
                showCancelButton: true,
                cancelButtonText: 'Abbrechen'
            }
        ).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    await removeDiscountFromSeatType(token, seatType.seat_type_id, discount.discount_id);

                    // Aktualisiere die Sitztypen-Zuweisungen
                    seatTypes = seatTypes.map(st => {
                        if (st.seat_type_id === seatType.seat_type_id) {
                            return {
                                ...st,
                                discounts: st.discounts.filter(d => d.discount_id !== discount.discount_id)
                            };
                        }
                        return st;
                    });

                    showSuccessAlert('Der Discount wurde vom Sitztyp entfernt.');
                } catch (err) {
                    console.error('Fehler beim Entfernen des Discounts:', err);
                    showErrorAlert(err.message || 'Fehler beim Entfernen des Discounts.');
                }
            }
        });
    }

    function goBack() {
        navigate('/admin'); // Passe den Pfad entsprechend an
    }
</script>


<style>
    /* Basis-Layout */
    main {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 40px;
        max-width: 1200px;
        margin: 0 auto;
        color: #fff;
        font-family: 'Roboto', sans-serif;
    }

    /* Überschriften */
     h2 {
        color: #2ecc71;
        text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
        margin-bottom: 40px;
        font-size: 2rem;
        animation: glow 2s infinite alternate;
    }

    @keyframes glow {
      from {
        text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
      }
      to {
        text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
      }
    }

    /* Tabellen */
    table {
        width: 100%;
        max-width: 900px;
        border-collapse: collapse;
        margin: 20px 0;
        background: rgba(0,0,0,0.4);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        color: #fff;
        text-align: center;
    }

    th, td {
        padding: 20px;
        text-align: center;
        border-bottom: 1px solid #2ecc71;
        font-size: 1rem;
        vertical-align: middle;
        text-shadow: 0 0 5px #2ecc71;
    }

    th {
        background-color: #000;
        font-size: 1.1rem;
        color: #2ecc71;
        border-bottom: 2px solid #2ecc71;
        text-transform: uppercase;
    }

    td {
        background-color: rgba(42, 42, 42, 0.7);
    }

    td:last-child {
        text-align: center;
    }

    /* Eingabefelder */
    input, select, textarea {
        width: 100%;
        padding: 12px;
        border: 1px solid #2ecc71;
        border-radius: 8px;
        font-size: 1rem;
        background: rgba(0,0,0,0.5);
        color: #2ecc71;
        margin-top: 5px;
        box-shadow: inset 0 0 10px #2ecc71;
        transition: box-shadow 0.3s, border-color 0.3s;
    }

    input:focus, select:focus, textarea:focus {
        border-color: #27ae60;
        box-shadow: 0 0 15px #27ae60;
        outline: none;
    }

    /* Buttons */
    button {
        background: #2ecc71;
        color: #000;
        padding: 12px 20px;
        font-size: 1rem;
        border: none;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        font-weight: bold;
        text-shadow: 0 0 10px #000;
    }

    button:hover {
        background: #27ae60;
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 0 15px #27ae60;
    }

    /* Sektionen */
    .discount-list, .assign-section {
        width: 100%;
        max-width: 1200px;
        margin-bottom: 40px;
    }

    /* Delete Button */
    .delete-button {
        padding: 10px 20px;
        font-size: 1rem;
        cursor: pointer;
        border: none;
        background-color: #e74c3c;
        color: white;
        border-radius: 10px;
        transition: background-color 0.3s ease, transform 0.3s ease;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
    }

    .delete-button:hover {
        background-color: #c0392b !important;
        transform: translateY(-3px) !important;
    }

    /* Icons */
    .fas {
        margin-right: 5px;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem;
        }

        h2 {
            font-size: 1.5rem;
        }

        table {
            font-size: 0.9rem;
        }

        button {
            font-size: 0.9rem;
            padding: 10px 15px;
        }

        .discount-list, .assign-section {
            max-width: 100%;
        }
    }

    /* Nachrichten */
    .error {
        color: #e74c3c;
        font-weight: bold;
        margin-bottom: 20px;
        text-shadow: 0 0 10px #e74c3c;
    }
</style>

<main>
    <h1>Verwaltung von Discounts</h1>

    {#if isLoading}
        <p>Lade Discounts...</p>
    {:else if error}
        <p class="error">{error}</p>
    {:else}
        <!-- Liste der bestehenden Discounts -->
        <div class="discount-list">
            <h2>Bestehende Discounts</h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Beschreibung</th>
                        <th>Aktionen</th>
                    </tr>
                </thead>
                <tbody>
                    {#each discounts as discount}
                        <tr>
                            <td>
                                <input
                                    type="text"
                                    bind:value={discount.name}
                                />
                            </td>
                            <td>
                                <textarea
                                    bind:value={discount.description}
                                ></textarea>
                            </td>
                            <td>
                                <button on:click={() => handleUpdateDiscount(discount)}>
                                    <i class="fas fa-save"></i> Speichern
                                </button>
                                <button class="delete-button" on:click={() => handleDeleteDiscount(discount.discount_id)}>
                                    <i class="fas fa-trash-alt"></i> Löschen
                                </button>
                            </td>
                        </tr>
                    {/each}
                    <!-- Extra Zeile zum Hinzufügen eines neuen Discounts -->
                    <tr>
                        <td>
                            <input
                                type="text"
                                placeholder="Neuer Discount-Name"
                                bind:value={newDiscountName}
                            />
                        </td>
                        <td>
                            <textarea
                                placeholder="Neue Beschreibung"
                                bind:value={newDiscountDescription}
                            ></textarea>
                        </td>
                        <td>
                            <button on:click={handleAddDiscount}>
                                <i class="fas fa-plus-circle"></i> Hinzufügen
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Zuweisung von Discounts zu Sitztypen -->
        <div class="assign-section">
            <h2>Discounts zu Sitztypen zuweisen</h2>

            {#each seatTypes as seatType}
                <div class="seat-type-table">
                    <h3>Sitztyp: {seatType.name}</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Discount</th>
                                <th>Wert</th>
                                <th>Aktionen</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#if seatType.discounts.length > 0}
                                {#each seatType.discounts as seatDiscount}
                                    <tr>
                                        <td>{seatDiscount.name}</td>
                                        <td>
                                            {#if seatDiscount.discount_amount}
                                                <strong>{seatDiscount.discount_amount.toFixed(2)} €</strong>
                                            {:else if seatDiscount.discount_percentage}
                                                <strong>{seatDiscount.discount_percentage.toFixed(2)} %</strong>
                                            {:else}
                                                -
                                            {/if}
                                        </td>
                                        <td>
                                            <button class="delete-button" on:click={() => handleRemoveDiscount(seatType, seatDiscount)}>
                                                <i class="fas fa-minus-circle"></i> Entfernen
                                            </button>
                                        </td>
                                    </tr>
                                {/each}
                            {:else}
                                <tr>
                                    <td colspan="3" class="no-discounts">Keine Discounts zugewiesen</td>
                                </tr>
                            {/if}
                            <!-- Zuweisungsbutton -->
                            <tr>
                                <td colspan="3">
                                    <button on:click={() => handleAssignDiscount(seatType, null)}>
                                        <i class="fas fa-plus"></i> Discount zuweisen
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            {/each}
        </div>
    {/if}

    <button class="back-button" on:click={goBack}>Zurück zum Adminbereich</button>
</main>
