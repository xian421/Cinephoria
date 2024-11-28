<script>
    import { navigate } from "svelte-routing";
  </script>
  
  <div>
    <h1>Zugriff verweigert</h1>
    <p>Du hast keine Berechtigung, diese Seite zu sehen.</p>
    <button on:click={() => navigate("/")}>Zurück zur Startseite</button>
  </div>
  
  <style>
    div {
      text-align: center;
      margin-top: 50px;
    }
  
    button {
      padding: 10px 20px;
      background-color: #3498db;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }
  
    button:hover {
      background-color: #2980b9;
    }
  </style>
  