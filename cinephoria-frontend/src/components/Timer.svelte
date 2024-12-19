<!-- src/components/Timer.svelte -->
<script lang="ts">
    import { timeLeft, warning } from '../stores/timerStore';
    import { onDestroy } from 'svelte';

    export let mode: 'navbar' | 'inline' = 'inline'; // Ermöglicht unterschiedliche Darstellungen

    let currentTimeLeft;
    let isWarning;

    // Abonniere die Stores
    const unsubscribeTimeLeft = timeLeft.subscribe(value => {
        currentTimeLeft = value;
       // console.log('Timer Komponente - timeLeft:', currentTimeLeft);
    });

    const unsubscribeWarning = warning.subscribe(value => {
        isWarning = value;
      //  console.log('Timer Komponente - warning:', isWarning);
    });

    // Bereinige die Abonnements beim Zerstören der Komponente
    onDestroy(() => {
        unsubscribeTimeLeft();
        unsubscribeWarning();
    });

    // Funktion zur Formatierung der Zeit
    function formatTime(seconds: number) {
        const min = Math.floor(seconds / 60);
        const sec = seconds % 60;
        return `${min}:${sec < 10 ? '0' : ''}${sec}`;
    }
</script>

{#if currentTimeLeft > 0}
    {#if mode === 'navbar'}
        <div class="timer navbar-timer {isWarning ? 'warning' : ''}">
            <i class="fas fa-clock"></i> {formatTime(currentTimeLeft)}
        </div>
    {:else if mode === 'inline'}
        <p class="reservation-time {isWarning ? 'warning' : ''}">
            Deine Reservierung läuft in <span class="time-highlight">{formatTime(currentTimeLeft)}</span> ab.
        </p>
    {/if}
{/if}

<style>
    .timer {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.3rem 0.6rem;
        background-color: #e74c3c;
        color: #fff;
        border-radius: 8px;
        font-weight: bold;
        animation: fadeIn 0.5s;
        font-size: 0.9rem;
    }

    .warning {
        background-color: #c0392b;
        animation: shake 0.5s;
    }

    .navbar-timer {
        /* Keine absolute Positionierung mehr */
    }

    .reservation-time {
        color: #e74c3c;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }

    .time-highlight {
        color: #c0392b;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes shake {
        0% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        50% { transform: translateX(5px); }
        75% { transform: translateX(-5px); }
        100% { transform: translateX(0); }
    }

    /* Anpassungen für den navbar-Modus */
    :global(.navbar-timer) {
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }

    /* Icon Styling */
    :global(.navbar-timer i) {
        color: #fff;
    }

    /* Responsive Anpassungen */
    @media (max-width: 768px) {
        .timer.navbar-timer {
            margin-left: 0;
            margin-top: 0.5rem;
            width: 100%;
            justify-content: center;
        }

        :global(.navbar-timer i) {
            font-size: 1rem;
        }
    }
</style>
