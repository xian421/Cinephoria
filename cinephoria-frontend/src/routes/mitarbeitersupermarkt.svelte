<!-- Mitarbeitersupermarkt.svelte -->
<script>
    import { onMount } from 'svelte';
    import { fetchSupermarketitems, addSupermarketItem, updateSupermarketItem } from '../services/api';
    import { authStore } from '../stores/authStore.js';
    import { get } from 'svelte/store';

    let products = [];
    let sortedProducts = [];
    let newItem = { barcode: '', item_name: '', price: '', category: '' };
    let isAdding = false; // Für Ladezustand
    let successMessage = '';
    let errorMessage = '';

    // Zustände für Sortierung
    let sortColumn = '';
    let sortDirection = 'asc'; // 'asc' oder 'desc'

    // Zustände für Modale
    let showAddModal = false;
    let showEditModal = false;
    let editItem = null; // Das aktuelle zu bearbeitende Item

    async function loadProducts() {
        try {
            const data = await fetchSupermarketitems();
            console.log('Loaded Products:', data); // Debugging
            products = data; // Direktes Zuweisen, da data ein Array ist
            sortedProducts = [...products]; // Initial Kopie
        } catch (error) {
            console.error('Fehler beim Laden der Artikel:', error);
            errorMessage = 'Fehler beim Laden der Artikel.';
        }
    }

    onMount(async () => {
        await loadProducts();
    });

    async function handleAddItem() {
        const { barcode, item_name, price, category } = newItem;
        if (!barcode || !item_name || !price || !category) {
            alert('Bitte alle Felder ausfüllen.');
            return;
        }

        const token = get(authStore).token;
        if (isAdding) return; // Verhindert Mehrfachklicks
        isAdding = true;

        try {
            const addedItem = await addSupermarketItem(
                token,
                barcode,
                item_name,
                price,
                category
            );
            console.log('Added Item:', addedItem); // Debugging
          
            // Aktualisiere die Produktliste
            products = [...products, addedItem];
            sortProducts(sortColumn, sortDirection); // Sortiere erneut

            // Setze das Formular zurück
            newItem = { barcode: '', item_name: '', price: '', category: '' };
            successMessage = 'Artikel erfolgreich hinzugefügt!';
            errorMessage = '';
            showAddModal = false; // Schließe das Modal
        } catch (error) {
            console.error('Fehler beim Hinzufügen des Artikels:', error);
            errorMessage = 'Fehler beim Hinzufügen des Artikels.';
            successMessage = '';
        } finally {
            isAdding = false;
        }
    }

    async function handleUpdateItem() {
        const { barcode, item_name, price, category } = editItem;
        if (!barcode || !item_name || !price || !category) {
            alert('Bitte alle Felder ausfüllen.');
            return;
        }

        const token = get(authStore).token;
        try {
            const updatedItem = await updateSupermarketItem(
                token,
                editItem.item_id, // Angenommen, jedes Item hat eine item_id
                barcode,
                item_name,
                price,
                category
            );
            console.log('Updated Item:', updatedItem); // Debugging

            // Aktualisiere die Produktliste
            products = products.map(item => item.item_id === updatedItem.item_id ? updatedItem : item);
            sortProducts(sortColumn, sortDirection); // Sortiere erneut

            successMessage = 'Artikel erfolgreich aktualisiert!';
            errorMessage = '';
            showEditModal = false; // Schließe das Modal
        } catch (error) {
            console.error('Fehler beim Aktualisieren des Artikels:', error);
            errorMessage = 'Fehler beim Aktualisieren des Artikels.';
            successMessage = '';
        }
    }

    function sortProducts(column, direction) {
        if (!column) {
            sortedProducts = [...products];
            return;
        }

        sortedProducts = [...products].sort((a, b) => {
            let aValue = a[column];
            let bValue = b[column];

            // Prüfen, ob die Spalte ein Datum ist
            const isDateColumn = column === 'created_at' || column === 'updated_at';

            if (isDateColumn) {
                const aDate = new Date(aValue);
                const bDate = new Date(bValue);
                return direction === 'asc' ? aDate - bDate : bDate - aDate;
            }

            // Versuche, die Werte als Zahlen zu interpretieren
            const aIsNumeric = !isNaN(parseFloat(aValue)) && isFinite(aValue);
            const bIsNumeric = !isNaN(parseFloat(bValue)) && isFinite(bValue);

            if (aIsNumeric && bIsNumeric) {
                // Sortiere numerisch
                return direction === 'asc'
                    ? parseFloat(aValue) - parseFloat(bValue)
                    : parseFloat(bValue) - parseFloat(aValue);
            }

            // Sortiere alphabetisch, wenn keine Zahlen vorliegen
            aValue = aValue.toString().toLowerCase();
            bValue = bValue.toString().toLowerCase();

            if (aValue < bValue) return direction === 'asc' ? -1 : 1;
            if (aValue > bValue) return direction === 'asc' ? 1 : -1;
            return 0;
        });
    }

    function handleSort(column) {
        if (sortColumn === column) {
            // Toggle die Sortierrichtung
            sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            sortColumn = column;
            sortDirection = 'asc';
        }
        sortProducts(sortColumn, sortDirection);
    }

    function openEditModal(product) {
        editItem = { ...product }; // Erstelle eine Kopie des Produkts
        showEditModal = true;
    }

    function closeModal() {
        showAddModal = false;
        showEditModal = false;
        editItem = null;
    }

    // Hilfsfunktion zur Datumsformatierung
    function formatDate(dateString) {
        const options = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        };
        return new Date(dateString).toLocaleDateString('de-DE', options);
    }
</script>

<style>
    .title {
        font-size: 2.5rem;
        margin-bottom: 30px;
        font-weight: bold;
        margin-top: 0;
    }

    /* Container-Stil für die gesamte Seite */
    .container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        margin: 0 auto;
        width: 100%;
        max-width: 1200px;
        height: auto; /* Anpassung der Höhe */
        font-family: 'Arial', sans-serif;
        color: #333;
        position: relative; /* Für den Add-Button */
    }

    /* Header mit Titel und Add-Button */
    .header {
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }

    /* Add-Button */
    .add-button {
        padding: 10px 20px;
        font-size: 1rem;
        background-color: #28a745;
        color: #fff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
        transition: background-color 0.3s;
    }

    .add-button:hover {
        background-color: #218838;
    }

    /* Wrapper für die Tabelle, um horizontales Scrollen zu ermöglichen */
    .table-wrapper {
        width: 100%;
        overflow-x: auto; /* Horizontales Scrollen bei schmalen Bildschirmen */
    }

    /* Tabelle */
    .table {
        width: 100%; /* Nutzt die gesamte Breite */
        max-width: 1500px; /* Begrenzung der maximalen Breite */
        min-width: 700px; /* Mindestbreite der Tabelle */
        border-collapse: collapse;
        background: #fff;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1); /* Leichter Schatten für mehr Tiefe */
        border-radius: 10px;
        margin-bottom: 90px;
    }

    /* Tabellenkopf */
    .table thead {
        background-color: #f8f9fa; /* Heller Hintergrund für den Kopfbereich */
    }

    .table th {
        padding: 20px;
        text-align: left;
        font-weight: bold;
        font-size: 1.2rem; /* Größere Schriftgröße */
        color: #333;
        cursor: pointer;
        user-select: none;
        white-space: nowrap; /* Verhindert Zeilenumbrüche in Kopfzellen */
    }

    /* Sortierindikatoren (Pfeile) */
    .table th .sort-indicator {
        margin-left: 10px;
        font-size: 0.8rem;
    }

    /* Tabellenzellen */
    .table td {
        padding: 20px;
        font-size: 1.1rem; /* Angenehme Lesbarkeit */
        color: #555;
        white-space: nowrap; /* Verhindert Zeilenumbrüche in Zellen */
    }

    /* Tabellenreihen */
    .table tbody tr {
        border-bottom: 1px solid #ddd; /* Leichte Abgrenzung der Zeilen */
    }

    .table tbody tr:last-child {
        border-bottom: none; /* Kein Rand unter der letzten Zeile */
    }

    /* Hover-Effekt für Tabellenreihen */
    .table tbody tr:hover {
        background-color: #f1f1f1; /* Heller Hintergrund beim Überfahren */
    }

    /* Bearbeitungs-Icon */
    .edit-icon {
        cursor: pointer;
        color: #007bff;
        font-size: 1.2rem;
    }

    .edit-icon:hover {
        color: #0056b3;
    }

    /* Modal-Stile */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }

    .modal {
        background: #fff;
        padding: 30px;
        border-radius: 10px;
        width: 90%;
        max-width: 500px;
        position: relative;
    }

    .modal h2 {
        margin-top: 0;
    }

    .close-button {
        position: absolute;
        top: 15px;
        right: 20px;
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
    }

    /* Formular-Container */
    .form-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }

    /* Formularfelder */
    .form-container label {
        font-size: 1rem;
        font-weight: bold;
    }

    .form-container input {
        padding: 10px;
        font-size: 1rem;
        border: 1px solid #ddd;
        border-radius: 5px;
    }

    /* Button-Stil */
    .form-container button {
        padding: 10px;
        font-size: 1rem;
        background-color: #007bff;
        color: #fff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
        transition: background-color 0.3s;
    }

    .form-container button:hover {
        background-color: #0056b3;
    }

    /* Erfolg- und Fehlermeldungen */
    .success {
        color: green;
        margin-bottom: 10px;
    }

    .error {
        color: red;
        margin-bottom: 10px;
    }
</style>

<div class="container">
    <div class="header">
        <h1 class="title">Alle Artikel in der Datenbank</h1>
        <button class="add-button" on:click={() => showAddModal = true}>Produkt hinzufügen</button>
    </div>

    {#if successMessage}
        <div class="success">{successMessage}</div>
    {/if}
    {#if errorMessage}
        <div class="error">{errorMessage}</div>
    {/if}

    <div class="table-wrapper">
        <table class="table">
            <thead>
                <tr>
                    <th>Aktion</th> <!-- Neue Spalte für den Bearbeitungsstift -->
                    <th on:click={() => handleSort('item_name')}>
                        Name
                        {#if sortColumn === 'item_name'}
                            <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
                        {/if}
                    </th>
                    <th on:click={() => handleSort('price')}>
                        Preis
                        {#if sortColumn === 'price'}
                            <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
                        {/if}
                    </th>
                    <th on:click={() => handleSort('barcode')}>
                        Barcode
                        {#if sortColumn === 'barcode'}
                            <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
                        {/if}
                    </th>
                    <th on:click={() => handleSort('category')}>
                        Kategorie
                        {#if sortColumn === 'category'}
                            <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
                        {/if}
                    </th>
                    <th on:click={() => handleSort('created_at')}>
                        Erstellt am
                        {#if sortColumn === 'created_at'}
                            <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
                        {/if}
                    </th>
                    <th on:click={() => handleSort('updated_at')}>
                        Aktualisiert am
                        {#if sortColumn === 'updated_at'}
                            <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
                        {/if}
                    </th>
                </tr>
            </thead>
            <tbody>
                {#each sortedProducts as product (product.item_id)}
                    <tr>
                        <td>
                            <span class="edit-icon" on:click={() => openEditModal(product)}>✏️</span>
                        </td>
                        <td>{product.item_name}</td>
                        <td>{product.price} €</td>
                        <td>{product.barcode}</td>
                        <td>{product.category}</td>
                        <td>{formatDate(product.created_at)}</td>
                        <td>{formatDate(product.updated_at)}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>

    {#if showAddModal}
        <div class="modal-overlay" on:click|self={closeModal}>
            <div class="modal">
                <button class="close-button" on:click={closeModal}>×</button>
                <h2>Neues Produkt hinzufügen</h2>
                <div class="form-container">
                    <label for="barcode">Barcode:</label>
                    <input id="barcode" type="text" bind:value={newItem.barcode} />

                    <label for="item_name">Name:</label>
                    <input id="item_name" type="text" bind:value={newItem.item_name} />

                    <label for="price">Preis (€):</label>
                    <input id="price" type="number" step="0.01" bind:value={newItem.price} />

                    <label for="category">Kategorie:</label>
                    <input id="category" type="text" bind:value={newItem.category} />

                    <button on:click={handleAddItem} disabled={isAdding}>
                        {isAdding ? 'Hinzufügen...' : 'Hinzufügen'}
                    </button>
                </div>
            </div>
        </div>
    {/if}

    {#if showEditModal && editItem}
        <div class="modal-overlay" on:click|self={closeModal}>
            <div class="modal">
                <button class="close-button" on:click={closeModal}>×</button>
                <h2>Produkt bearbeiten</h2>
                <div class="form-container">
                    <label for="edit_barcode">Barcode:</label>
                    <input id="edit_barcode" type="text" bind:value={editItem.barcode} />

                    <label for="edit_item_name">Name:</label>
                    <input id="edit_item_name" type="text" bind:value={editItem.item_name} />

                    <label for="edit_price">Preis (€):</label>
                    <input id="edit_price" type="number" step="0.01" bind:value={editItem.price} />

                    <label for="edit_category">Kategorie:</label>
                    <input id="edit_category" type="text" bind:value={editItem.category} />

                    <button on:click={handleUpdateItem}>
                        Aktualisieren
                    </button>
                </div>
            </div>
        </div>
    {/if}
</div>
