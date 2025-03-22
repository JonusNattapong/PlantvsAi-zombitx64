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
    betAmount: 10
};

// DOM elements
const pokerTable = document.querySelector('.poker-table');
const communityCardsDiv = document.getElementById('community-cards');
const playerHandDiv = document.getElementById('player-hand');
const aiHandDiv = document.getElementById('ai-hand');
const potText = document.getElementById('pot');
const gameStageText = document.getElementById('game-stage');
const playerInfoText = document.getElementById('player-info');
const aiInfoText = document.getElementById('ai-info');

// Control elements
const aiModeSelect = document.getElementById('ai-mode');
const newGameBtn = document.getElementById('new-game-btn');
const changeAiBtn = document.getElementById('change-ai-btn');
const backToMenuBtn = document.getElementById('back-to-menu-btn');

// Action buttons
const foldBtn = document.getElementById('fold-btn');
const checkBtn = document.getElementById('check-btn');
const callBtn = document.getElementById('call-btn');
const raiseBtn = document.getElementById('raise-btn');
const betSliderContainer = document.getElementById('bet-slider-container');
const betSlider = document.getElementById('bet-slider');
const betValueText = document.getElementById('bet-value');
const confirmBetBtn = document.getElementById('confirm-bet-btn');

// Winner overlay
const winnerOverlay = document.getElementById('winner-overlay');
const winnerText = document.getElementById('winner-text');
const handDescription = document.getElementById('hand-description');
const playAgainBtn = document.getElementById('play-again-btn');
const returnToMenuBtn = document.getElementById('return-to-menu-btn');

// Statistics elements
const totalGamesElement = document.getElementById('total-games');
const playerWinsElement = document.getElementById('player-wins');
const aiWinsElement = document.getElementById('ai-wins');
const winRateElement = document.getElementById('win-rate');
const biggestPotElement = document.getElementById('biggest-pot');

// Card suits symbols
const SUIT_SYMBOLS = {
    'hearts': '♥',
    'diamonds': '♦',
    'clubs': '♣',
    'spades': '♠'
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
}

// Generate a random session ID
function generateSessionId() {
    return Math.floor(Math.random() * 100000).toString();
}

// Start a new poker game
function startNewGame() {
    // Clear the UI
    communityCardsDiv.innerHTML = '';
    playerHandDiv.innerHTML = '';
    aiHandDiv.innerHTML = '';
    
    // Reset the bet slider container
    betSliderContainer.style.display = 'none';
    
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
    })
    .catch(error => {
        console.error('Error starting new game:', error);
    });
}

// Update the game state from server response
function updateGameState(data) {
    gameState = {
        ...gameState,
        pot: data.pot,
        currentBet: data.current_bet,
        gameStage: data.game_stage,
        communityCards: data.community_cards,
        players: data.players,
        currentPlayer: data.current_player,
        winner: data.winner
    };
    
    // Update the UI
    updateUI();
    
    // If the game is in showdown or has a winner, show the result
    if (gameState.gameStage === 'showdown' || gameState.winner) {
        showGameResult();
    }
    // If it's AI's turn, let the AI make a move
    else if (gameState.currentPlayer === 'AI') {
        setTimeout(aiMove, 1000);
    }
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
}

// Update community cards display
function updateCommunityCards() {
    communityCardsDiv.innerHTML = '';
    
    // Add each community card
    gameState.communityCards.forEach(card => {
        const cardElement = createCardElement(card);
        communityCardsDiv.appendChild(cardElement);
    });
}

// Update player hand display
function updatePlayerHand() {
    playerHandDiv.innerHTML = '';
    
    const player = gameState.players.find(p => p.name === 'Player');
    if (player && player.hand && player.hand.length > 0) {
        player.hand.forEach(card => {
            const cardElement = createCardElement(card);
            playerHandDiv.appendChild(cardElement);
        });
    }
}

// Update AI hand display
function updateAIHand() {
    aiHandDiv.innerHTML = '';
    
    const ai = gameState.players.find(p => p.name === 'AI');
    if (ai) {
        if (gameState.gameStage === 'showdown' && ai.hand && ai.hand.length > 0) {
            // Show AI cards in showdown
            ai.hand.forEach(card => {
                const cardElement = createCardElement(card);
                aiHandDiv.appendChild(cardElement);
            });
        } else {
            // Show face-down cards
            for (let i = 0; i < 2; i++) {
                const cardElement = document.createElement('div');
                cardElement.className = 'card back';
                aiHandDiv.appendChild(cardElement);
            }
        }
    }
}

// Create a card element from card data
function createCardElement(card) {
    const cardElement = document.createElement('div');
    cardElement.className = `card ${card.suit}`;
    
    // Add rank and suit to the card
    const rankSpan = document.createElement('span');
    rankSpan.className = 'rank';
    rankSpan.textContent = card.rank;
    cardElement.appendChild(rankSpan);
    
    const suitSpan = document.createElement('span');
    suitSpan.className = 'suit';
    suitSpan.textContent = SUIT_SYMBOLS[card.suit];
    cardElement.appendChild(suitSpan);
    
    // If we have SVG cards, use them instead
    const cardImg = document.createElement('img');
    cardImg.src = `/static/svg_cards/${card.rank}_of_${card.suit}.svg`;
    cardImg.alt = `${card.rank} of ${card.suit}`;
    cardImg.onerror = () => {
        // If SVG loading fails, use the text fallback (already created)
        cardImg.style.display = 'none';
    };
    cardImg.style.width = '100%';
    cardImg.style.height = '100%';
    cardImg.style.position = 'absolute';
    cardImg.style.top = '0';
    cardImg.style.left = '0';
    
    cardElement.appendChild(cardImg);
    
    return cardElement;
}

// Update action buttons based on valid actions
function updateActionButtons() {
    // Hide all buttons by default
    foldBtn.style.display = 'none';
    checkBtn.style.display = 'none';
    callBtn.style.display = 'none';
    raiseBtn.style.display = 'none';
    
    // If game is over or it's not player's turn, hide all buttons
    if (gameState.gameStage === 'showdown' || gameState.winner || gameState.currentPlayer !== 'Player') {
        return;
    }
    
    // Find current player
    const player = gameState.players.find(p => p.name === 'Player');
    if (!player || player.is_folded || player.is_all_in) {
        return;
    }
    
    // Determine valid actions based on game state
    const validActions = getValidActions();
    
    // Show appropriate buttons
    validActions.forEach(action => {
        switch(action) {
            case 'fold':
                foldBtn.style.display = 'block';
                break;
            case 'check':
                checkBtn.style.display = 'block';
                break;
            case 'call':
                callBtn.style.display = 'block';
                // Show call amount
                const callAmount = gameState.currentBet - player.current_bet;
                callBtn.textContent = `Call $${callAmount}`;
                break;
            case 'raise':
                raiseBtn.style.display = 'block';
                break;
        }
    });
}

// Get valid actions based on current game state
function getValidActions() {
    // Simple implementation - you might want to get this from the server instead
    const player = gameState.players.find(p => p.name === 'Player');
    if (!player) return [];
    
    const actions = ['fold'];
    
    // If no bet or player has already matched current bet
    if (player.current_bet >= gameState.currentBet) {
        actions.push('check');
    } else {
        actions.push('call');
    }
    
    // Can raise if player has enough chips
    if (player.chips > gameState.currentBet - player.current_bet) {
        actions.push('raise');
    }
    
    return actions;
}

// Update bet slider based on player's chips
function updateBetSlider(playerChips) {
    // Set min bet to current bet or minimum raise
    const minBet = Math.max(gameState.currentBet * 2, 10);
    
    // Set max bet to player's chips
    const maxBet = playerChips;
    
    // Update slider attributes
    betSlider.min = minBet;
    betSlider.max = maxBet;
    betSlider.value = minBet;
    
    // Update displayed bet value
    betValueText.textContent = minBet;
    gameState.betAmount = minBet;
}

// Handle player action (fold, check, call, raise)
function handlePlayerAction(action) {
    if (action === 'raise') {
        // Show bet slider for raise
        betSliderContainer.style.display = 'flex';
        return;
    }
    
    // Send action to server
    fetch('/api/poker_action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: gameState.sessionId,
            action: action,
            bet_amount: action === 'raise' ? gameState.betAmount : 0
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error making move:', data.error);
            return;
        }
        
        // Update game state
        updateGameState(data);
    })
    .catch(error => {
        console.error('Error making move:', error);
    });
}

// Handle confirming a raise bet
function confirmBet() {
    // Hide bet slider
    betSliderContainer.style.display = 'none';
    
    // Send raise action with bet amount
    handlePlayerAction('raise');
}

// Handle AI move
function aiMove() {
    fetch('/api/ai_move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: gameState.sessionId,
            game_type: 'Poker',
            ai_mode: gameState.aiMode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error making AI move:', data.error);
            return;
        }
        
        // Update game state
        updateGameState(data);
    })
    .catch(error => {
        console.error('Error making AI move:', error);
    });
}

// Show game result
function showGameResult() {
    // Update UI to show final state
    updateUI();
    
    // Determine winner message
    let resultMessage = '';
    let handName = '';
    
    if (gameState.winner === 'player') {
        resultMessage = 'You Win! 🎉';
    } else if (gameState.winner === 'ai') {
        resultMessage = 'AI Wins! 😎';
    } else {
        resultMessage = 'It\'s a Draw!';
    }
    
    // Get hand descriptions if available
    if (gameState.handDescription) {
        handName = gameState.handDescription;
    }
    
    // Update overlay content
    winnerText.textContent = resultMessage;
    handDescription.textContent = handName;
    
    // Show overlay
    winnerOverlay.classList.add('active');
    
    // Update statistics
    loadGameStats();
}

// Load game statistics
function loadGameStats() {
    fetch('/api/get_stats?game_type=Poker')
    .then(response => response.json())
    .then(data => {
        // Update stats display
        totalGamesElement.textContent = data.total_games;
        playerWinsElement.textContent = data.player_wins;
        aiWinsElement.textContent = data.ai_wins;
        winRateElement.textContent = data.win_rate + '%';
        
        // Update poker-specific stats
        if (data.biggest_pot) {
            biggestPotElement.textContent = '$' + data.biggest_pot;
        }
    })
    .catch(error => {
        console.error('Error loading game stats:', error);
    });
}

// Change AI mode
function changeAiMode() {
    const newMode = parseInt(aiModeSelect.value);
    
    fetch('/api/change_ai_mode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: gameState.sessionId,
            ai_mode: newMode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error changing AI mode:', data.error);
            return;
        }
        
        gameState.aiMode = data.ai_mode;
        alert(`Changed AI level to ${getAiModeName(gameState.aiMode)}`);
    })
    .catch(error => {
        console.error('Error changing AI mode:', error);
    });
}

// Get AI mode name from mode number
function getAiModeName(mode) {
    const modes = [
        "Simple AI",
        "Probability AI",
        "Advanced AI"
    ];
    return modes[mode] || "Unknown";
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
    confirmBetBtn.addEventListener('click', confirmBet);
    
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
