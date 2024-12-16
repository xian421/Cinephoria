<script>
    import { onMount } from 'svelte';
    import Swal from 'sweetalert2';
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

            // Debugging: Logge die empfangenen Daten
            console.log('Fetched Discounts:', fetchedDiscounts);
            console.log('Fetched Seat Types:', fetchedSeatTypes);

            discounts = fetchedDiscounts.discounts;
            seatTypes = fetchedSeatTypes.map(st => ({
                ...st,
                discounts: st.discounts || []
            }));

            console.log('Processed Seat Types:', seatTypes);

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
            Swal.fire({
                title: 'Fehler',
                text: 'Bitte geben Sie einen Namen für den Discount ein.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
            return;
        }

        try {
            const result = await addDiscount(token, newDiscountName, newDiscountDescription);
            discounts = [...discounts, {
                discount_id: result.discount_id,
                name: newDiscountName,
                description: newDiscountDescription
            }];
            console.log('Added Discount:', result);

            // Felder zurücksetzen
            newDiscountName = '';
            newDiscountDescription = '';
            Swal.fire({
                title: 'Erfolgreich',
                text: 'Der neue Discount wurde hinzugefügt.',
                icon: 'success',
                confirmButtonText: 'OK',
            });
        } catch (err) {
            console.error('Fehler beim Hinzufügen des Discounts:', err);
            Swal.fire({
                title: 'Fehler',
                text: err.message || 'Fehler beim Hinzufügen des Discounts.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
        }
    }

    // Funktion zum Aktualisieren eines Discounts
    async function handleUpdateDiscount(discount) {
        const token = get(authStore).token;

        if (!discount.name.trim()) {
            Swal.fire({
                title: 'Fehler',
                text: 'Bitte geben Sie einen Namen für den Discount ein.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
            return;
        }

        try {
            await updateDiscount(token, discount.discount_id, discount.name, discount.description);
            console.log('Updated Discount:', discount);

            Swal.fire({
                title: 'Erfolgreich',
                text: 'Der Discount wurde aktualisiert.',
                icon: 'success',
                confirmButtonText: 'OK',
            });
        } catch (err) {
            console.error('Fehler beim Aktualisieren des Discounts:', err);
            Swal.fire({
                title: 'Fehler',
                text: err.message || 'Fehler beim Aktualisieren des Discounts.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
        }
    }

    // Funktion zum Löschen eines Discounts
    async function handleDeleteDiscount(discount_id) {
        const token = get(authStore).token;

        Swal.fire({
            title: 'Sind Sie sicher?',
            text: 'Möchten Sie diesen Discount wirklich löschen?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Ja, löschen',
            cancelButtonText: 'Abbrechen',
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    await deleteDiscount(token, discount_id);
                    discounts = discounts.filter(d => d.discount_id !== discount_id);
                    // Entferne den Discount aus allen Sitztypen
                    seatTypes = seatTypes.map(seatType => ({
                        ...seatType,
                        discounts: seatType.discounts.filter(d => d.discount_id !== discount_id)
                    }));
                    console.log('Deleted Discount ID:', discount_id);

                    Swal.fire({
                        title: 'Gelöscht',
                        text: 'Der Discount wurde gelöscht.',
                        icon: 'success',
                        confirmButtonText: 'OK',
                    });
                } catch (err) {
                    console.error('Fehler beim Löschen des Discounts:', err);
                    Swal.fire({
                        title: 'Fehler',
                        text: err.message || 'Fehler beim Löschen des Discounts.',
                        icon: 'error',
                        confirmButtonText: 'OK',
                    });
                }
            }
        });
    }

    // Funktion zum Zuweisen eines Discounts zu einem Sitztyp
    async function handleAssignDiscount(seatType, discount) {
        const token = get(authStore).token;

        // Dialog zur Eingabe von Rabattbetrag oder -prozentsatz
        const { value: formValues } = await Swal.fire({
            title: `Discount zuweisen: Sitztyp "${seatType.name}"`,
            html:
                `<select id="swal-discount-select" class="swal2-select">
                    <option value="" disabled selected>Wähle einen Discount</option>
                    ${discounts.map(d => `<option value="${d.discount_id}">${d.name}</option>`).join('')}
                </select>
                 <input id="swal-input1" class="swal2-input" placeholder="Rabattbetrag (EUR)">
                 <input id="swal-input2" class="swal2-input" placeholder="Rabattprozentsatz (%)">`,
            focusConfirm: false,
            preConfirm: () => {
                const discount_id = document.getElementById('swal-discount-select').value;
                const discount_amount = document.getElementById('swal-input1').value;
                const discount_percentage = document.getElementById('swal-input2').value;
                return { discount_id, discount_amount, discount_percentage };
            }
        });

        if (formValues) {
            const { discount_id, discount_amount, discount_percentage } = formValues;

            if (!discount_id) {
                Swal.fire({
                    title: 'Fehler',
                    text: 'Bitte wählen Sie einen Discount aus.',
                    icon: 'error',
                    confirmButtonText: 'OK',
                });
                return;
            }

            if ((!discount_amount && !discount_percentage) ||
                (discount_amount && discount_percentage)) {
                Swal.fire({
                    title: 'Fehler',
                    text: 'Bitte geben Sie entweder einen Rabattbetrag oder einen Rabattprozentsatz an.',
                    icon: 'error',
                    confirmButtonText: 'OK',
                });
                return;
            }

            const selectedDiscount = discounts.find(d => d.discount_id == discount_id);
            if (!selectedDiscount) {
                Swal.fire({
                    title: 'Fehler',
                    text: 'Ungültiger Discount ausgewählt.',
                    icon: 'error',
                    confirmButtonText: 'OK',
                });
                return;
            }

            try {
                await assignDiscountToSeatType(token, seatType.seat_type_id, selectedDiscount.discount_id,
                    discount_amount ? parseFloat(discount_amount) : null,
                    discount_percentage ? parseFloat(discount_percentage) : null
                );

                // Aktualisiere die Sitztypen-Zuweisungen
                seatTypes = seatTypes.map(st => {
                    if (st.seat_type_id === seatType.seat_type_id) {
                        // Überprüfen, ob der Discount bereits zugewiesen ist
                        const existing = st.discounts.find(d => d.discount_id === selectedDiscount.discount_id);
                        if (existing) {
                            // Aktualisiere die vorhandenen Werte
                            return {
                                ...st,
                                discounts: st.discounts.map(d => d.discount_id === selectedDiscount.discount_id ? {
                                    ...d,
                                    discount_amount: discount_amount ? parseFloat(discount_amount) : null,
                                    discount_percentage: discount_percentage ? parseFloat(discount_percentage) : null
                                } : d)
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

                console.log(`Assigned Discount ID ${selectedDiscount.discount_id} to Seat Type ID ${seatType.seat_type_id}`);

                Swal.fire({
                    title: 'Erfolgreich',
                    text: 'Der Discount wurde dem Sitztyp zugewiesen.',
                    icon: 'success',
                    confirmButtonText: 'OK',
                });
            } catch (err) {
                console.error('Fehler beim Zuweisen des Discounts:', err);
                Swal.fire({
                    title: 'Fehler',
                    text: err.message || 'Fehler beim Zuweisen des Discounts.',
                    icon: 'error',
                    confirmButtonText: 'OK',
                });
            }
        }
    }

    // Funktion zum Entfernen eines Discounts von einem Sitztyp
    async function handleRemoveDiscount(seatType, discount) {
        const token = get(authStore).token;

        Swal.fire({
            title: 'Sind Sie sicher?',
            text: `Möchten Sie den Discount "${discount.name}" von Sitztyp "${seatType.name}" entfernen?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Ja, entfernen',
            cancelButtonText: 'Abbrechen',
        }).then(async (result) => {
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
                    console.log(`Removed Discount ID ${discount.discount_id} from Seat Type ID ${seatType.seat_type_id}`);

                    Swal.fire({
                        title: 'Entfernt',
                        text: 'Der Discount wurde vom Sitztyp entfernt.',
                        icon: 'success',
                        confirmButtonText: 'OK',
                    });
                } catch (err) {
                    console.error('Fehler beim Entfernen des Discounts:', err);
                    Swal.fire({
                        title: 'Fehler',
                        text: err.message || 'Fehler beim Entfernen des Discounts.',
                        icon: 'error',
                        confirmButtonText: 'OK',
                    });
                }
            }
        });
    }
</script>

<style>
   @import "@fortawesome/fontawesome-free/css/all.min.css";

/* Basis-Layout */
main {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-family: 'Roboto', sans-serif;
    padding: 30px;
    background: linear-gradient(120deg, #f0f9ff, #cfefff);
    border-radius: 10px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

/* Überschriften */
h1, h2 {
    text-align: center;
    margin-bottom: 20px;
}

h1 {
    font-size: 2.8rem;
    color: #34495e;
    margin-bottom: 15px;
    border-bottom: 4px solid #3498db;
    display: inline-block;
    padding-bottom: 10px;
}

h2 {
    font-size: 2rem;
    color: #2c3e50;
}

/* Tabellen */
table {
    width: 100%;
    max-width: 900px;
    border-collapse: collapse;
    margin: 20px 0;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

th, td {
    padding: 20px;
    text-align: left;
    border-bottom: 1px solid #ddd;
    font-size: 1rem;
    vertical-align: middle;
}

th {
    background-color: #2c3e50;
    color: #ffffff;
    text-transform: uppercase;
    font-weight: bold;
}

td {
    color: #555;
    background-color: #ffffff;
}

td:last-child {
    text-align: center;
}

/* Eingabefelder */
input, select, textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 1rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

input:focus, select:focus, textarea:focus {
    border-color: #3498db;
    box-shadow: 0 2px 10px rgba(52, 152, 219, 0.3);
    outline: none;
}

/* Buttons */
button {
    background: linear-gradient(45deg, #3498db, #1abc9c);
    color: white;
    padding: 12px 20px;
    font-size: 1rem;
    border: none;
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

button:hover {
    background: linear-gradient(45deg, #2980b9, #16a085);
    transform: translateY(-3px);
}

/* Sektionen */
.form-section {
    display: flex;
    flex-direction: column;
    gap: 20px;
    width: 100%;
    max-width: 800px;
    background-color: #ffffff;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    margin-bottom: 30px;
    animation: fadeIn 0.5s ease-out;
}

.form-section h2 {
    font-size: 1.8rem;
    color: #34495e;
}

/* Icon-Auswahl */
.icon-container {
    display: flex;
    align-items: center;
    gap: 10px;
}

.icon-background {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background-color: var(--bg-color, #3498db);
    position: relative;
    cursor: pointer;
    transition: transform 0.3s ease, background-color 0.3s ease;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

.icon-background input[type="color"] {
    opacity: 0;
    position: absolute;
    width: 100%;
    height: 100%;
    cursor: pointer;
}

.icon-background:hover {
    transform: scale(1.2);
    background-color: #1abc9c;
}

.icon-background i {
    color: white;
    font-size: 1.5rem;
}

/* Nachrichten */
.success-message, .error-message {
    font-size: 1rem;
    padding: 10px 15px;
    border-radius: 8px;
    margin: 20px 0;
    text-align: center;
    font-weight: bold;
}

.success-message {
    color: #27ae60;
    background-color: #dff0d8;
}

.error-message {
    color: #c0392b;
    background-color: #f8d7da;
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

    .form-section {
        padding: 20px;
    }
}

/* Animationen */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.delete-button {
    padding: 10px 20px;
    font-size: 1rem;
    cursor: pointer;
    border: none;
    background-color: #e74c3c;
    color: white;
    border-radius: 25px;
    transition: background-color 0.3s ease, transform 0.3s ease;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.delete-button:hover {
    background-color: #c0392b;
    transform: translateY(-3px);
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
                                <button on:click={() => handleDeleteDiscount(discount.discount_id)}>
                                    <i class="fas fa-trash-alt"></i> Löschen
                                </button>
                                

                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>

        <!-- Formular zum Hinzufügen eines neuen Discounts -->
        <div class="form-section">
            <h2>Neuen Discount erstellen</h2>
            <form on:submit|preventDefault={handleAddDiscount}>
                <div>
                    <label for="discount-name">Name:</label>
                    <input id="discount-name" type="text" bind:value={newDiscountName} required />
                </div>
                <div>
                    <label for="discount-description">Beschreibung:</label>
                    <textarea id="discount-description" bind:value={newDiscountDescription}></textarea>
                </div>
                <button type="submit">Discount hinzufügen</button>
            </form>
        </div>

        <!-- Zuweisung von Discounts zu Sitztypen -->
        <div class="assign-section">
            <h2>Discounts zu Sitztypen zuweisen</h2>
            <table>
                <thead>
                    <tr>
                        <th>Sitztyp</th>
                        <th>Discount</th>
                        <th>Rabattbetrag (€)</th>
                        <th>Rabattprozentsatz (%)</th>
                        <th>Aktionen</th>
                    </tr>
                </thead>
                <tbody>
                    {#each seatTypes as seatType}
                        {#if seatType.discounts.length > 0}
                            {#each seatType.discounts as seatDiscount}
                                <tr>
                                    <td>{seatType.name}</td>
                                    <td>{seatDiscount.name}</td>
                                    <td>{seatDiscount.discount_amount !== null ? seatDiscount.discount_amount.toFixed(2) : '-'}</td>
                                    <td>{seatDiscount.discount_percentage !== null ? seatDiscount.discount_percentage.toFixed(2) : '-'}</td>
                                    <td>
                                        <button on:click={() => handleRemoveDiscount(seatType, seatDiscount)}>
                                            <i class="fas fa-minus-circle"></i> Entfernen
                                        </button>
                                    </td>
                                </tr>
                            {/each}
                        {/if}
                        {#if seatType.discounts.length === 0}
                            <tr>
                                <td>{seatType.name}</td>
                                <td colspan="3">Keine Discounts zugewiesen</td>
                                <td>
                                    <button on:click={() => handleAssignDiscount(seatType, null)}>
                                        <i class="fas fa-plus-circle"></i> Zuweisen
                                    </button>
                                </td>
                            </tr>
                        {/if}
                        <tr>
                            <td colspan="5">
                                <button on:click={() => handleAssignDiscount(seatType, null)}>
                                    <i class="fas fa-plus-circle"></i> Discount zuweisen
                                </button>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    {/if}
</main>
