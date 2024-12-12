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

    main {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-family: Arial, sans-serif;
        padding: 20px;
    }

    h1, h2 {
        margin-bottom: 20px;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        max-width: 1000px;
        margin-bottom: 20px;
    }

    th, td {
        text-align: left;
        padding: 12px;
        border-bottom: 1px solid #ddd;
    }

    th {
        background-color: #4CAF50;
        color: white;
    }

    input[type="text"], textarea, select, input[type="number"] {
        padding: 8px;
        margin-right: 10px;
        width: 100%;
        box-sizing: border-box;
    }

    button {
        padding: 10px 20px;
        font-size: 14px;
        cursor: pointer;
        border: none;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        transition: background-color 0.3s;
        margin: 5px;
    }

    button:hover {
        background-color: #45a049;
    }

    .form-section {
        width: 100%;
        max-width: 800px;
        margin-bottom: 40px;
    }

    .form-section h2 {
        margin-bottom: 15px;
    }

    .discount-list {
        width: 100%;
        max-width: 1000px;
    }

    .assign-section {
        margin-top: 20px;
    }

    .assign-section table {
        margin-top: 10px;
    }

    /* Responsive Design */
    @media (max-width: 800px) {
        table, .form-section, .discount-list {
            width: 100%;
        }

        th, td {
            padding: 8px;
        }

        button {
            padding: 8px 16px;
            font-size: 12px;
        }
    }

    /* Icon Styling */
    .icon-display {
        display: flex;
        align-items: center;
    }

    .icon-display i {
        margin-right: 8px;
        font-size: 18px;
    }

    /* Fehler- und Erfolgsnachrichten */
    .error {
        color: red;
    }

    .success {
        color: green;
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
