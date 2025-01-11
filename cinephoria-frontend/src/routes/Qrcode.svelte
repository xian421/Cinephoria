<!-- src/Qrcode.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import QRCode from 'qrcode';
  
    export let content: string = 'Default QR Content';
    let qrCodeDataUrl: string = '';
    let error: string = '';
  
    onMount(async () => {
      try {
        qrCodeDataUrl = await QRCode.toDataURL(content);
      } catch (err) {
        console.error('QR-Code Generierung fehlgeschlagen:', err);
        error = 'QR-Code konnte nicht generiert werden.';
      }
    });
  </script>
  
  {#if error}
    <p class="error">{error}</p>
  {:else if qrCodeDataUrl}
    <img src="{qrCodeDataUrl}" alt="QR Code" />
  {:else}
    <p>Lade QR-Code...</p>
  {/if}
  
  <style>
    img {
      max-width: 100%;
      height: auto;
    }
    .error {
      color: red;
      font-weight: bold;
    }
  </style>
  