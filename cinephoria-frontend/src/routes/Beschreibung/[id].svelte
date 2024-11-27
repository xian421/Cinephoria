<script>
    import { page } from '$app/stores';
  
    // Die ID aus den Parametern holen
    $: id = $page.params.id;
  </script>
  
  <h1>Hallo, das ist eine Beschreibung</h1>
  <p>Die ID lautet: {id}</p>
  