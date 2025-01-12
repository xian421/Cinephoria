<script>
    let ticket = {
        movie: 'Inception',
        time: '20:00 Uhr',
        seat: 'Reihe 5, Platz 12',
        date: '11. Januar 2025',
    };
</script>

<style>
    .kino-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        background: linear-gradient(135deg, #1e3c72, #2a5298); /* Dunkles Kino-Design */
        color: #fff;
        font-family: 'Verdana', sans-serif;
    }

    .ticket {
        width: 350px;
        background: #222;
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
    }

    .ticket h2 {
        font-size: 1.8rem;
        margin-bottom: 10px;
        color: #ffcc00;
    }

    .ticket p {
        font-size: 1.2rem;
        margin: 5px 0;
    }

    .ticket .seat {
        margin-top: 15px;
        font-size: 1.5rem;
        font-weight: bold;
        color: #4caf50;
    }
</style>

<div class="kino-container">
    <div class="ticket">
        <h2>{ticket.movie}</h2>
        <p>{ticket.date}</p>
        <p>{ticket.time}</p>
        <p class="seat">{ticket.seat}</p>
    </div>
</div>
