document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('btn-start');
    const nextBtn = document.getElementById('btn-next');
    const realBtn = document.getElementById('btn-real');
    const fakeBtn = document.getElementById('btn-fake');
    const gameArea = document.getElementById('game-area');
    const instructions = document.getElementById('instructions');
    const roundInfo = document.getElementById('round-info');
    const flowerImg = document.getElementById('flower-img');
    const resultP = document.getElementById('result');
    const scoreP = document.getElementById('score');

    let currentRound = 0;
    let totalRounds = 10;
    let score = 0;

    startBtn.addEventListener('click', () => {
        startBtn.style.display = 'none';
        instructions.style.display = 'none';
        gameArea.style.display = 'block';
        loadNextRound();
    });

    nextBtn.addEventListener('click', () => {
        nextBtn.style.display = 'none';
        realBtn.disabled = false;
        fakeBtn.disabled = false;
        resultP.textContent = '';
        loadNextRound();
    });

    realBtn.addEventListener('click', () => handleGuess('real'));
    fakeBtn.addEventListener('click', () => handleGuess('fake'));

    function loadNextRound() {
        fetch('/next_round')
            .then(response => response.json())
            .then(data => {
                if (data.game_over) {
                    gameArea.innerHTML = `<p>Game Over! Final Score: ${data.score} / ${data.total}</p>`;
                    return;
                }
                currentRound = data.round;
                roundInfo.textContent = `Round ${currentRound} of ${totalRounds}`;
                flowerImg.src = data.img_url + '?' + new Date().getTime(); // Cache bust
                realBtn.disabled = false;
                fakeBtn.disabled = false;
            });
    }

    function handleGuess(guess) {
        realBtn.disabled = true;
        fakeBtn.disabled = true;
        fetch('/guess', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({guess: guess})
        })
            .then(response => response.json())
            .then(data => {
                resultP.textContent = data.result;
                score = data.score;
                scoreP.textContent = `Score: ${score} / ${totalRounds}`;
                if (currentRound < totalRounds) {
                    nextBtn.style.display = 'block';
                } else {
                    nextBtn.style.display = 'none';
                    setTimeout(() => {
                        gameArea.innerHTML = `<p>Game Over! Final Score: ${score} / ${totalRounds}</p>`;
                    }, 2000);
                }
            });
    }
});