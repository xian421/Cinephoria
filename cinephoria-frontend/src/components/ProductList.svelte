<!-- src/components/ProductList.svelte -->
<script>
    import { formatDate } from '../utils/dateFormatter.js';
  
    export let products = [];
    export let sortColumn = '';
    export let sortDirection = 'asc';
    export let onSort;
    export let onEdit;
    export let onDelete;  // Neu: Löschen-Event
  </script>
  
  <table class="table">
    <thead>
      <tr>
        <th>Aktion</th>
        <th on:click={() => onSort('item_name')}>
          Name
          {#if sortColumn === 'item_name'}
            <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
          {/if}
        </th>
        <th on:click={() => onSort('price')}>
          Preis
          {#if sortColumn === 'price'}
            <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
          {/if}
        </th>
        <th on:click={() => onSort('barcode')}>
          Barcode
          {#if sortColumn === 'barcode'}
            <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
          {/if}
        </th>
        <th on:click={() => onSort('category')}>
          Kategorie
          {#if sortColumn === 'category'}
            <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
          {/if}
        </th>
        <th on:click={() => onSort('pfand_id')}>
          Pfand
          {#if sortColumn === 'pfand_id'}
            <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
          {/if}
        </th>
        <th on:click={() => onSort('created_at')}>
          Erstellt am
          {#if sortColumn === 'created_at'}
            <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
          {/if}
        </th>
        <th on:click={() => onSort('updated_at')}>
          Aktualisiert am
          {#if sortColumn === 'updated_at'}
            <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
          {/if}
        </th>
      </tr>
    </thead>
    <tbody>
      {#each products as product (product.item_id)}
        <tr>
          <td>
            <span class="edit-icon" on:click={() => onEdit(product)} title="Produkt bearbeiten">✏️</span>
            <span class="delete-icon" on:click={() => onDelete(product.item_id)} title="Produkt löschen">🗑️</span>
          </td>
          <td>{product.item_name}</td>
          <td>{product.price} €</td>
          <td>{product.barcode}</td>
          <td>{product.category}</td>
          <td>{product.pfand_id ? product.pfand_name : 'Nein'}</td>
          <td>{formatDate(product.created_at)}</td>
          <td>{formatDate(product.updated_at)}</td>
        </tr>
      {/each}
    </tbody>
  </table>
  
  <style>
     .table {
        width: 100%; 
        border-collapse: collapse;
        background: #fff;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1); 
        border-radius: 10px;
        margin-bottom: 90px;
    }

    .table thead {
        background-color: #f8f9fa; 
    }

    .table th, .table td {
        padding: 10px; 
        font-size: 0.9rem; 
        white-space: nowrap; 
    }

    .table th {
        text-align: left;
        font-weight: bold;
        color: #333;
        cursor: pointer;
        user-select: none;
    }

    .table th .sort-indicator {
        margin-left: 5px;
        font-size: 0.8rem;
    }

    .table tbody tr {
        border-bottom: 1px solid #ddd; 
    }

    .table tbody tr:last-child {
        border-bottom: none; 
    }

    .table tbody tr:hover {
        background-color: #f1f1f1; 
    }

    .edit-icon {
        cursor: pointer;
        color: #007bff;
        font-size: 1.2rem;
    }

    .edit-icon:hover {
        color: #0056b3;
    }
    .delete-icon {
      cursor: pointer;
      margin-left: 8px;
      color: red;
      font-size: 1.2rem;
    }
    .delete-icon:hover {
      color: darkred;
    }
  </style>
  