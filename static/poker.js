// JavaScript สำหรับเกม Poker

// สถานะเกม
let gameState = {
    sessionId: null,
    pot: 0,
    currentBet: 0,
    gameStage: "pre_flop",
    communityCards: [],
    players: [],
    currentPlayer: "",
    winner: null,
    aiMode: 0,
    betAmount: 10,
    soundEnabled: true,
    betHistory: [],
    handDescriptions: {
        'high_card': 'High Card',
        'pair': 'Pair',
        'two_pair': 'Two Pair',
        'three_of_a_kind': 'Three of a Kind',
        'straight': 'Straight',
        'flush': 'Flush',
        'full_house': 'Full House',
        'four_of_a_kind': 'Four of a Kind',
        'straight_flush': 'Straight Flush',
        'royal_flush': 'Royal Flush'
    },
    sounds: {
        deal: null,
        chip: null,
        fold: null,
        check: null,
        win: null,
        lose: null
    }
};

// Initialize the game
function initGame() {
    // Generate session ID
    gameState.sessionId = generateSessionId();
    
    // Set AI mode from URL parameters if provided
    const urlParams = new URLSearchParams(window.location.search);
    const aiParam = urlParams.get('ai');
    if (aiParam !== null) {
        gameState.aiMode = parseInt(aiParam);
        aiModeSelect.value = aiParam;
    }
    
    // Start a new game
    startNewGame();
    
    // Load game statistics
    loadGameStats();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize sounds
    loadSounds();
}

// Load sound effects
function loadSounds() {
    if (typeof Audio !== 'undefined') {
        gameState.sounds.deal = new Audio('/static/sounds/card_deal.mp3');
        gameState.sounds.chip = new Audio('/static/sounds/chip.mp3');
        gameState.sounds.fold = new Audio('/static/sounds/fold.mp3');
        gameState.sounds.check = new Audio('/static/sounds/check.mp3');
        gameState.sounds.win = new Audio('/static/sounds/win.mp3');
        gameState.sounds.lose = new Audio('/static/sounds/lose.mp3');
    }
    
    // Add sound toggle button if it exists
    const soundToggle = document.getElementById('sound-toggle');
    if (soundToggle) {
        soundToggle.addEventListener('click', toggleSound);
    }
}

// Toggle sound on/off
function toggleSound() {
    gameState.soundEnabled = !gameState.soundEnabled;
    const soundToggle = document.getElementById('sound-toggle');
    if (soundToggle) {
        soundToggle.textContent = gameState.soundEnabled ? '🔊' : '🔇';
    }
}

// Play a sound if sound is enabled
function playSound(soundName) {
    if (gameState.soundEnabled && gameState.sounds[soundName]) {
        gameState.sounds[soundName].currentTime = 0;
        gameState.sounds[soundName].play().catch(e => console.log("Error playing sound:", e));
    }
}

// Start a new poker game
function startNewGame() {
    // Clear the UI
    communityCardsDiv.innerHTML = '';
    playerHandDiv.innerHTML = '';
    aiHandDiv.innerHTML = '';
    
    // Reset the bet slider container
    betSliderContainer.style.display = 'none';
    
    // Clear bet history
    gameState.betHistory = [];
    
    // Send request to start a new game
    fetch('/api/new_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: gameState.sessionId,
            ai_mode: gameState.aiMode,
            game_type: 'Poker'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error starting new game:', data.error);
            return;
        }
        
        // Update game state
        updateGameState(data);
        
        // Reset winner overlay
        winnerOverlay.classList.remove('active');
        
        // Play deal sound after a short delay
        setTimeout(() => {
            playSound('deal');
        }, 500);
    })
    .catch(error => {
        console.error('Error starting new game:', error);
    });
}

// Update the player's hand
function updatePlayerHand() {
    playerHandDiv.innerHTML = '';
    
    const player = gameState.players.find(p => p.name === 'Player');
    if (player && player.hand) {
        player.hand.forEach((card, index) => {
            const cardElement = document.createElement('div');
            cardElement.className = `card ${card.suit}`;
            cardElement.innerHTML = `
                <div class="rank">${card.rank}</div>
                <div class="suit">${SUIT_SYMBOLS[card.suit]}</div>
                <div class="center-symbol">${SUIT_SYMBOLS[card.suit]}</div>
            `;
            
            // Add animation class with delay based on index
            cardElement.style.animationDelay = `${index * 0.2}s`;
            cardElement.classList.add('deal-animation');
            
            playerHandDiv.appendChild(cardElement);
        });
    }
}

// Update the AI's hand
function updateAIHand() {
    aiHandDiv.innerHTML = '';
    
    const ai = gameState.players.find(p => p.name === 'AI');
    if (ai) {
        // If showdown or game over with winner, show AI cards
        if (gameState.gameStage === 'showdown' || gameState.winner) {
            ai.hand.forEach((card, index) => {
                const cardElement = document.createElement('div');
                cardElement.className = `card ${card.suit}`;
                cardElement.innerHTML = `
                    <div class="rank">${card.rank}</div>
                    <div class="suit">${SUIT_SYMBOLS[card.suit]}</div>
                    <div class="center-symbol">${SUIT_SYMBOLS[card.suit]}</div>
                `;
                
                // Add animation class with delay
                cardElement.style.animationDelay = `${index * 0.2}s`;
                cardElement.classList.add('deal-animation');
                
                aiHandDiv.appendChild(cardElement);
            });
        } else {
            // If not showdown, show back of cards
            for (let i = 0; i < 2; i++) {
                const cardElement = document.createElement('div');
                cardElement.className = 'card back';
                
                // Add animation class with delay
                cardElement.style.animationDelay = `${i * 0.2}s`;
                cardElement.classList.add('deal-animation');
                
                aiHandDiv.appendChild(cardElement);
            }
        }
    }
}

// Update the community cards
function updateCommunityCards() {
    communityCardsDiv.innerHTML = '';
    
    if (gameState.communityCards && gameState.communityCards.length > 0) {
        gameState.communityCards.forEach((card, index) => {
            const cardElement = document.createElement('div');
            cardElement.className = `card ${card.suit}`;
            cardElement.innerHTML = `
                <div class="rank">${card.rank}</div>
                <div class="suit">${SUIT_SYMBOLS[card.suit]}</div>
                <div class="center-symbol">${SUIT_SYMBOLS[card.suit]}</div>
            `;
            
            // Add animation class with delay based on index
            cardElement.style.animationDelay = `${index * 0.2}s`;
            cardElement.classList.add('deal-animation');
            
            communityCardsDiv.appendChild(cardElement);
        });
    }
}

// Show the game result
function showGameResult() {
    if (gameState.winner) {
        winnerText.textContent = `${gameState.winner} Wins!`;
        
        // Play appropriate sound
        if (gameState.winner === 'Player') {
            playSound('win');
        } else {
            playSound('lose');
        }
        
        // Find the player or AI object
        const winningPlayer = gameState.players.find(p => p.name === gameState.winner);
        
        // Show hand description if available
        if (winningPlayer && winningPlayer.best_hand_name) {
            const handName = gameState.handDescriptions[winningPlayer.best_hand_name] || winningPlayer.best_hand_name;
            handDescription.textContent = `Winning Hand: ${handName}`;
            handDescription.classList.add('animate-text');
        } else {
            handDescription.textContent = '';
        }
        
        winnerOverlay.classList.add('active');
    }
}

// Handle player actions
function handlePlayerAction(action, betAmount = 0) {
    // Add to bet history
    const player = gameState.players.find(p => p.name === 'Player');
    
    if (player) {
        gameState.betHistory.push({
            player: 'Player',
            action: action,
            amount: action === 'raise' || action === 'call' ? betAmount : 0,
            gameStage: gameState.gameStage
        });
    }
    
    // Play corresponding sound
    switch(action) {
        case 'fold':
            playSound('fold');
            break;
        case 'check':
            playSound('check');
            break;
        case 'call':
        case 'raise':
            playSound('chip');
            break;
    }
    
    // Send action to server
    fetch('/api/poker_action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: gameState.sessionId,
            action: action,
            bet_amount: betAmount
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error processing action:', data.error);
            return;
        }
        
        // Update game state
        updateGameState(data);
    })
    .catch(error => {
        console.error('Error processing action:', error);
    });
}

// AI move function
function aiMove() {
    // If it's not AI's turn, return
    if (gameState.currentPlayer !== 'AI') return;
    
    // Simulate thinking time for AI
    setTimeout(() => {
        // If the AI makes a betting action, play the chip sound
        const aiAction = gameState.nextAIAction || 'check';
        
        // Add to bet history
        const ai = gameState.players.find(p => p.name === 'AI');
        if (ai) {
            gameState.betHistory.push({
                player: 'AI',
                action: aiAction,
                amount: aiAction === 'raise' || aiAction === 'call' ? (gameState.currentBet - ai.current_bet) : 0,
                gameStage: gameState.gameStage
            });
        }
        
        // Play sound based on action
        switch(aiAction) {
            case 'fold':
                playSound('fold');
                break;
            case 'check':
                playSound('check');
                break;
            case 'call':
            case 'raise':
                playSound('chip');
                break;
        }
        
        // Send AI action to server
        fetch('/api/poker_action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: gameState.sessionId,
                action: aiAction,
                bet_amount: gameState.nextAIBet || 0
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error processing AI action:', data.error);
                return;
            }
            
            // Update game state
            updateGameState(data);
        })
        .catch(error => {
            console.error('Error processing AI action:', error);
        });
    }, 1500);  // AI thinking time
}

// Update the UI based on current game state
function updateUI() {
    // Update pot
    potText.textContent = `Pot: $${gameState.pot}`;
    
    // Update game stage
    const stageNames = {
        "pre_flop": "Pre-Flop",
        "flop": "Flop",
        "turn": "Turn",
        "river": "River",
        "showdown": "Showdown"
    };
    gameStageText.textContent = stageNames[gameState.gameStage] || gameState.gameStage;
    
    // Update player information
    const player = gameState.players.find(p => p.name === 'Player');
    const ai = gameState.players.find(p => p.name === 'AI');
    
    if (player) {
        playerInfoText.textContent = `Player: $${player.chips} ${player.current_bet > 0 ? `(Bet: $${player.current_bet})` : ''}`;
    }
    
    if (ai) {
        aiInfoText.textContent = `AI: $${ai.chips} ${ai.current_bet > 0 ? `(Bet: $${ai.current_bet})` : ''}`;
    }
    
    // Update community cards
    updateCommunityCards();
    
    // Update player hand
    updatePlayerHand();
    
    // Update AI hand (face down unless showdown)
    updateAIHand();
    
    // Update action buttons
    updateActionButtons();
    
    // Update bet slider
    updateBetSlider(player ? player.chips : 0);
    
    // Update bet history
    updateBetHistory();
    
    // Update AI thinking indicator
    updateAIThinking();
}

// Update AI thinking indicator
function updateAIThinking() {
    const aiThinking = document.getElementById('ai-thinking');
    if (!aiThinking) return;
    
    if (gameState.currentPlayer === 'AI' && !gameState.winner && gameState.gameStage !== 'showdown') {
        aiThinking.classList.add('active');
    } else {
        aiThinking.classList.remove('active');
    }
}

// Update the bet history display
function updateBetHistory() {
    const betHistoryDiv = document.getElementById('bet-history');
    if (!betHistoryDiv) return;
    
    // Clear previous history
    betHistoryDiv.innerHTML = '';
    
    // No need to show anything if there's no history
    if (!gameState.betHistory || gameState.betHistory.length === 0) {
        const emptyMessage = document.createElement('div');
        emptyMessage.textContent = 'No bets placed yet.';
        emptyMessage.style.textAlign = 'center';
        emptyMessage.style.color = '#666';
        emptyMessage.style.padding = '10px';
        betHistoryDiv.appendChild(emptyMessage);
        return;
    }
    
    // Add each bet history item
    gameState.betHistory.forEach((bet, index) => {
        const historyItem = document.createElement('div');
        historyItem.className = `bet-history-item ${bet.player.toLowerCase()}`;
        
        // Format the action text
        let actionText = bet.action;
        if (bet.action === 'raise' || bet.action === 'call') {
            actionText += ` $${bet.amount}`;
        }
        
        // Create player section
        const playerSection = document.createElement('div');
        playerSection.innerHTML = `<strong>${bet.player}</strong>`;
        
        // Create action section
        const actionSection = document.createElement('div');
        actionSection.className = 'action';
        actionSection.textContent = actionText;
        
        // Create stage section 
        const stageSection = document.createElement('div');
        stageSection.className = 'stage';
        stageSection.textContent = formatGameStage(bet.gameStage);
        
        // Add sections to item
        historyItem.appendChild(playerSection);
        historyItem.appendChild(actionSection);
        historyItem.appendChild(stageSection);
        
        // Add animation delay based on index
        historyItem.style.animationDelay = `${index * 0.05}s`;
        
        betHistoryDiv.appendChild(historyItem);
    });
    
    // Scroll to bottom of history
    betHistoryDiv.scrollTop = betHistoryDiv.scrollHeight;
}

// Format game stage name for display
function formatGameStage(gameStage) {
    const stageNames = {
        "pre_flop": "Pre-Flop",
        "flop": "Flop",
        "turn": "Turn",
        "river": "River",
        "showdown": "Showdown"
    };
    return stageNames[gameStage] || gameStage;
}

// Set up event listeners
function setupEventListeners() {
    // Button event listeners
    newGameBtn.addEventListener('click', startNewGame);
    changeAiBtn.addEventListener('click', changeAiMode);
    backToMenuBtn.addEventListener('click', () => {
        window.location.href = '/';
    });
    
    // Action buttons
    foldBtn.addEventListener('click', () => handlePlayerAction('fold'));
    checkBtn.addEventListener('click', () => handlePlayerAction('check'));
    callBtn.addEventListener('click', () => handlePlayerAction('call'));
    raiseBtn.addEventListener('click', () => {
        betSliderContainer.style.display = 'flex';
    });
    
    // Bet slider and confirmation
    betSlider.addEventListener('input', () => {
        const value = betSlider.value;
        betValueText.textContent = value;
        gameState.betAmount = parseInt(value);
    });
    confirmBetBtn.addEventListener('click', () => {
        betSliderContainer.style.display = 'none';
        handlePlayerAction('raise', gameState.betAmount);
    });
    
    // Winner overlay buttons
    playAgainBtn.addEventListener('click', () => {
        winnerOverlay.classList.remove('active');
        startNewGame();
    });
    returnToMenuBtn.addEventListener('click', () => {
        window.location.href = '/';
    });
}

// Initialize when the DOM content is loaded
document.addEventListener('DOMContentLoaded', initGame);
