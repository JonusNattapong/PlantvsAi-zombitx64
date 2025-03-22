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
};  handDescriptions: {
        'high_card': 'High Card',
// DOM elements 'Pair',
const pokerTable = document.querySelector('.poker-table');
const communityCardsDiv = document.getElementById('community-cards');
const playerHandDiv = document.getElementById('player-hand');
const aiHandDiv = document.getElementById('ai-hand');
const potText = document.getElementById('pot');
const gameStageText = document.getElementById('game-stage');
const playerInfoText = document.getElementById('player-info');
const aiInfoText = document.getElementById('ai-info');
    },
// Control elements
const aiModeSelect = document.getElementById('ai-mode');
const newGameBtn = document.getElementById('new-game-btn');
const changeAiBtn = document.getElementById('change-ai-btn');
const backToMenuBtn = document.getElementById('back-to-menu-btn');
        check: null,
// Action buttonsl
const foldBtn = document.getElementById('fold-btn');
const checkBtn = document.getElementById('check-btn');
const callBtn = document.getElementById('call-btn');
const raiseBtn = document.getElementById('raise-btn');
const betSliderContainer = document.getElementById('bet-slider-container');
const betSlider = document.getElementById('bet-slider');nity-cards');
const betValueText = document.getElementById('bet-value');');
const confirmBetBtn = document.getElementById('confirm-bet-btn');
const potText = document.getElementById('pot');
// Winner overlayxt = document.getElementById('game-stage');
const winnerOverlay = document.getElementById('winner-overlay');
const winnerText = document.getElementById('winner-text');
const handDescription = document.getElementById('hand-description');
const playAgainBtn = document.getElementById('play-again-btn');
const returnToMenuBtn = document.getElementById('return-to-menu-btn');
const newGameBtn = document.getElementById('new-game-btn');
// Statistics elementscument.getElementById('change-ai-btn');
const totalGamesElement = document.getElementById('total-games');;
const playerWinsElement = document.getElementById('player-wins');
const aiWinsElement = document.getElementById('ai-wins');
const winRateElement = document.getElementById('win-rate');
const biggestPotElement = document.getElementById('biggest-pot');
const callBtn = document.getElementById('call-btn');
// Card suits symbolsment.getElementById('raise-btn');
const SUIT_SYMBOLS = {er = document.getElementById('bet-slider-container');
    'hearts': '♥',document.getElementById('bet-slider');
    'diamonds': '♦', document.getElementById('bet-value');
    'clubs': '♣',tn = document.getElementById('confirm-bet-btn');
    'spades': '♠'
}; Winner overlay
const winnerOverlay = document.getElementById('winner-overlay');
// Initialize the gameument.getElementById('winner-text');
function initGame() { = document.getElementById('hand-description');
    // Generate session IDent.getElementById('play-again-btn');
    gameState.sessionId = generateSessionId();d('return-to-menu-btn');
    
    // Set AI mode from URL parameters if provided
    const urlParams = new URLSearchParams(window.location.search);
    const aiParam = urlParams.get('ai');ementById('player-wins');
    if (aiParam !== null) {ent.getElementById('ai-wins');
        gameState.aiMode = parseInt(aiParam);d('win-rate');
        aiModeSelect.value = aiParam;tElementById('biggest-pot');
    }
    ard suits symbols
    // Start a new game
    startNewGame();
    'diamonds': '♦',
    // Load game statistics
    loadGameStats();
    
    // Set up event listeners
    setupEventListeners();
}unction initGame() {
    // Generate session ID
// Generate a random session IDateSessionId();
function generateSessionId() {
    return Math.floor(Math.random() * 100000).toString();
}   const urlParams = new URLSearchParams(window.location.search);
    const aiParam = urlParams.get('ai');
// Start a new poker game {
function startNewGame() {= parseInt(aiParam);
    // Clear the UIt.value = aiParam;
    communityCardsDiv.innerHTML = '';
    playerHandDiv.innerHTML = '';
    aiHandDiv.innerHTML = '';
    startNewGame();
    // Reset the bet slider container
    betSliderContainer.style.display = 'none';
    loadGameStats();
    // Send request to start a new game
    fetch('/api/new_game', {s
        method: 'POST',();
        headers: {
            'Content-Type': 'application/json',
        },unds();
        body: JSON.stringify({
            session_id: gameState.sessionId,
            ai_mode: gameState.aiMode,
            game_type: 'Poker'
        }) Math.floor(Math.random() * 100000).toString();
    })
    .then(response => response.json())
    .then(data => {r game
        if (data.error) {
            console.error('Error starting new game:', data.error);
            return;iv.innerHTML = '';
        }rHandDiv.innerHTML = '';
        ndDiv.innerHTML = '';
        // Update game state
        updateGameState(data);ntainer
        liderContainer.style.display = 'none';
        // Reset winner overlay
        winnerOverlay.classList.remove('active');
    })tch('/api/new_game', {
    .catch(error => {',
        console.error('Error starting new game:', error);
    });     'Content-Type': 'application/json',
}       },
        body: JSON.stringify({
// Update the game state from server response
function updateGameState(data) {iMode,
    gameState = {type: 'Poker'
        ...gameState,
        pot: data.pot,
        currentBet: data.current_bet,)
        gameStage: data.game_stage,
        communityCards: data.community_cards,
        players: data.players,or starting new game:', data.error);
        currentPlayer: data.current_player,
        winner: data.winner
    };  
        // Update game state
    // Update the UIate(data);
    updateUI();
        // Reset winner overlay
    // If the game is in showdown or has a winner, show the result
    if (gameState.gameStage === 'showdown' || gameState.winner) {
        showGameResult();
    }   console.error('Error starting new game:', error);
    // If it's AI's turn, let the AI make a move
    else if (gameState.currentPlayer === 'AI') {
        setTimeout(aiMove, 1000);
    }etTimeout(() => {
}       if (gameState.sounds.deal) gameState.sounds.deal.play();
    }, 500);
// Update the UI based on current game state
function updateUI() {
    // Update pote state from server response
    potText.textContent = `Pot: $${gameState.pot}`;
    gameState = {
    // Update game stage
    const stageNames = {
        "pre_flop": "Pre-Flop",t_bet,
        "flop": "Flop",.game_stage,
        "turn": "Turn", data.community_cards,
        "river": "River",yers,
        "showdown": "Showdown"rrent_player,
    };  winner: data.winner
    gameStageText.textContent = stageNames[gameState.gameStage] || gameState.gameStage;
    
    // Update player informationf available
    const player = gameState.players.find(p => p.name === 'Player');
    const ai = gameState.players.find(p => p.name === 'AI');
            ...gameState.handDescriptions,
    if (player) {ta.hand_descriptions
        playerInfoText.textContent = `Player: $${player.chips} ${player.current_bet > 0 ? `(Bet: $${player.current_bet})` : ''}`;
    }
    
    if (ai) { the UI
        aiInfoText.textContent = `AI: $${ai.chips} ${ai.current_bet > 0 ? `(Bet: $${ai.current_bet})` : ''}`;
    }
    // If the game is in showdown or has a winner, show the result
    // Update community cards== 'showdown' || gameState.winner) {
    updateCommunityCards();
    }
    // Update player hand let the AI make a move
    updatePlayerHand();currentPlayer === 'AI') {
        setTimeout(aiMove, 1000);
    // Update AI hand (face down unless showdown)
    updateAIHand();
    
    // Update action buttonsrrent game state
    updateActionButtons();
    // Update pot
    // Update bet slider= `Pot: $${gameState.pot}`;
    updateBetSlider(player ? player.chips : 0);
}   // Update game stage
    const stageNames = {
// Update community cards display
function updateCommunityCards() {
    communityCardsDiv.innerHTML = '';
        "river": "River",
    // Add each community card
    gameState.communityCards.forEach(card => {
        const cardElement = createCardElement(card);.gameStage] || gameState.gameStage;
        communityCardsDiv.appendChild(cardElement);
    });Update player information
}   const player = gameState.players.find(p => p.name === 'Player');
    const ai = gameState.players.find(p => p.name === 'AI');
// Update player hand display
function updatePlayerHand() {
    playerHandDiv.innerHTML = '';t = `Player: $${player.chips} ${player.current_bet > 0 ? `(Bet: $${player.current_bet})` : ''}`;
    }
    const player = gameState.players.find(p => p.name === 'Player');
    if (player && player.hand && player.hand.length > 0) {
        player.hand.forEach(card => { $${ai.chips} ${ai.current_bet > 0 ? `(Bet: $${ai.current_bet})` : ''}`;
            const cardElement = createCardElement(card);
            playerHandDiv.appendChild(cardElement);
        });te community cards
    }pdateCommunityCards();
}   
    // Update player hand
// Update AI hand display
function updateAIHand() {
    aiHandDiv.innerHTML = '';own unless showdown)
    updateAIHand();
    const ai = gameState.players.find(p => p.name === 'AI');
    if (ai) { action buttons
        if (gameState.gameStage === 'showdown' && ai.hand && ai.hand.length > 0) {
            // Show AI cards in showdown
            ai.hand.forEach(card => {
                const cardElement = createCardElement(card);
                aiHandDiv.appendChild(cardElement);
            });
        } else {ity cards display
            // Show face-down cards
            for (let i = 0; i < 2; i++) {
                const cardElement = document.createElement('div');
                cardElement.className = 'card back';
                aiHandDiv.appendChild(cardElement);
            } cardElement = createCardElement(card);
        }ommunityCardsDiv.appendChild(cardElement);
    });
}

// Create a card element from card data
function createCardElement(card) {
    const cardElement = document.createElement('div');
    cardElement.className = `card ${card.suit}`;
    const player = gameState.players.find(p => p.name === 'Player');
    // Add rank and suit to the cardyer.hand.length > 0) {
    const rankSpan = document.createElement('span');
    rankSpan.className = 'rank';createCardElement(card);
    rankSpan.textContent = card.rank;(cardElement);
    cardElement.appendChild(rankSpan);
    }
    const suitSpan = document.createElement('span');
    suitSpan.className = 'suit';
    suitSpan.textContent = SUIT_SYMBOLS[card.suit];
    cardElement.appendChild(suitSpan);
    aiHandDiv.innerHTML = '';
    // If we have SVG cards, use them instead
    const cardImg = document.createElement('img');=== 'AI');
    cardImg.src = `/static/svg_cards/${card.rank}_of_${card.suit}.svg`;
    cardImg.alt = `${card.rank} of ${card.suit}`; ai.hand && ai.hand.length > 0) {
    cardImg.onerror = () => {in showdown
        // If SVG loading fails, use the text fallback (already created)
        cardImg.style.display = 'none';ateCardElement(card);
    };          aiHandDiv.appendChild(cardElement);
    cardImg.style.width = '100%';
    cardImg.style.height = '100%';
    cardImg.style.position = 'absolute';
    cardImg.style.top = '0';i < 2; i++) {
    cardImg.style.left = '0';ment = document.createElement('div');
                cardElement.className = 'card back';
    cardElement.appendChild(cardImg);(cardElement);
            }
    return cardElement;
}   }
}
// Update action buttons based on valid actions
function updateActionButtons() {rd data
    // Hide all buttons by default
    foldBtn.style.display = 'none';eateElement('div');
    checkBtn.style.display = 'none';card.suit}`;
    callBtn.style.display = 'none';
    raiseBtn.style.display = 'none';
    const cardSvgUrl = `/static/svg_cards/${card.rank.toLowerCase()}_of_${card.suit}.svg`;
    // If game is over or it's not player's turn, hide all buttons
    if (gameState.gameStage === 'showdown' || gameState.winner || gameState.currentPlayer !== 'Player') {
        return;ntainer = document.createElement('div');
    }vgContainer.className = 'svg-card-container';
    svgContainer.style.width = '100%';
    // Find current playerght = '100%';
    const player = gameState.players.find(p => p.name === 'Player');
    if (!player || player.is_folded || player.is_all_in) {
        return;r.style.left = '0';
    }
    // Add the SVG image
    // Determine valid actions based on game state
    const validActions = getValidActions();
    cardImg.alt = `${card.rank} of ${card.suit}`;
    // Show appropriate buttons';
    validActions.forEach(action => {
        switch(action) {
            case 'fold':he SVG fails to load
                foldBtn.style.display = 'block';
                break;display = 'none';
            case 'check':
                checkBtn.style.display = 'block';
                break; = document.createElement('span');
            case 'call':me = 'rank';
                callBtn.style.display = 'block';
                // Show call amountkSpan);
                const callAmount = gameState.currentBet - player.current_bet;
                callBtn.textContent = `Call $${callAmount}`;
                break;Name = 'suit';
            case 'raise':ent = SUIT_SYMBOLS[card.suit];
                raiseBtn.style.display = 'block';
                break;
        }
    });Container.appendChild(cardImg);
}   cardElement.appendChild(svgContainer);
    
// Get valid actions based on current game state
function getValidActions() {d('deal-animation');
    // Simple implementation - you might want to get this from the server instead
    const player = gameState.players.find(p => p.name === 'Player');
    if (!player) return [];
    
    const actions = ['fold'];
    
    // If no bet or player has already matched current bet
    if (player.current_bet >= gameState.currentBet) {
        actions.push('check'); {
    } else {all buttons by default
        actions.push('call');none';
    }heckBtn.style.display = 'none';
    callBtn.style.display = 'none';
    // Can raise if player has enough chips
    if (player.chips > gameState.currentBet - player.current_bet) {
        actions.push('raise'); not player's turn, hide all buttons
    }f (gameState.gameStage === 'showdown' || gameState.winner || gameState.currentPlayer !== 'Player') {
        return;
    return actions;
}   
    // Find current player
// Update bet slider based on player's chips=> p.name === 'Player');
function updateBetSlider(playerChips) {player.is_all_in) {
    // Set min bet to current bet or minimum raise
    const minBet = Math.max(gameState.currentBet * 2, 10);
    
    // Set max bet to player's chips on game state
    const maxBet = playerChips;idActions();
    
    // Update slider attributes
    betSlider.min = minBet;tion => {
    betSlider.max = maxBet;
    betSlider.value = minBet;
                foldBtn.style.display = 'block';
    // Update displayed bet value
    betValueText.textContent = minBet;
    gameState.betAmount = minBet;splay = 'block';
}               break;
            case 'call':
// Handle player action (fold, check, call, raise)
function handlePlayerAction(action) {
    if (action === 'raise') {unt = gameState.currentBet - player.current_bet;
        // Show bet slider for raise= `Call $${callAmount}`;
        betSliderContainer.style.display = 'flex';
        return;e 'raise':
    }           raiseBtn.style.display = 'block';
                break;
    // Send action to server
    fetch('/api/poker_action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',e
        },etValidActions() {
        body: JSON.stringify({ you might want to get this from the server instead
            session_id: gameState.sessionId,=> p.name === 'Player');
            action: action,
            bet_amount: action === 'raise' ? gameState.betAmount : 0
        })actions = ['fold'];
    })
    .then(response => response.json()) matched current bet
    .then(data => {ent_bet >= gameState.currentBet) {
        if (data.error) {ck');
            console.error('Error making move:', data.error);
            return;h('call');
        }
        
        // Update game stateas enough chips
        updateGameState(data);te.currentBet - player.current_bet) {
    })  actions.push('raise');
    .catch(error => {
        console.error('Error making move:', error);
    });urn actions;
}

// Handle confirming a raise betayer's chips
function confirmBet() {r(playerChips) {
    // Hide bet slidercurrent bet or minimum raise
    betSliderContainer.style.display = 'none';et * 2, 10);
    
    // Send raise action with bet amount
    handlePlayerAction('raise');
}   
    // Update slider attributes
// Handle AI move = minBet;
function aiMove() { maxBet;
    fetch('/api/ai_move', {t;
        method: 'POST',
        headers: {layed bet value
            'Content-Type': 'application/json',
        },ate.betAmount = minBet;
        body: JSON.stringify({
            session_id: gameState.sessionId,
            game_type: 'Poker',check, call, raise)
            ai_mode: gameState.aiMode
        })tion === 'raise') {
    })  // Show bet slider for raise
    .then(response => response.json())ay = 'flex';
    .then(data => {
        if (data.error) {
            console.error('Error making AI move:', data.error);
            return;ffect based on action
        }ction === 'fold' && gameState.sounds.fold) {
        gameState.sounds.fold.play();
        // Update game stateheck' && gameState.sounds.check) {
        updateGameState(data);.play();
    })else if ((action === 'call' || action === 'raise') && gameState.sounds.chip) {
    .catch(error => {nds.chip.play();
        console.error('Error making AI move:', error);
    });
}   // Send action to server
    fetch('/api/poker_action', {
// Show game resultST',
function showGameResult() {
    // Update UI to show final statetion/json',
    updateUI();
        body: JSON.stringify({
    // Determine winner messagete.sessionId,
    let resultMessage = '';
    let handName = '';: action === 'raise' ? gameState.betAmount : 0
        })
    if (gameState.winner === 'player') {
        resultMessage = 'You Win! 🎉';
    } else if (gameState.winner === 'ai') {
        resultMessage = 'AI Wins! 😎';
    } else {console.error('Error making move:', data.error);
        resultMessage = 'It\'s a Draw!';
    }   }
        
    // Get hand descriptions if available
    if (gameState.handDescription) {
        handName = gameState.handDescription;
    }catch(error => {
        console.error('Error making move:', error);
    // Update overlay content
    winnerText.textContent = resultMessage;
    handDescription.textContent = handName;
    andle confirming a raise bet
    // Show overlay() {
    winnerOverlay.classList.add('active');
    betSliderContainer.style.display = 'none';
    // Update statistics
    loadGameStats();tion with bet amount
}   handlePlayerAction('raise');
}
// Load game statistics
function loadGameStats() {
    fetch('/api/get_stats?game_type=Poker')
    .then(response => response.json())
    .then(data => {ST',
        // Update stats display
        totalGamesElement.textContent = data.total_games;
        playerWinsElement.textContent = data.player_wins;
        aiWinsElement.textContent = data.ai_wins;
        winRateElement.textContent = data.win_rate + '%';
            game_type: 'Poker',
        // Update poker-specific stats
        if (data.biggest_pot) {
            biggestPotElement.textContent = '$' + data.biggest_pot;
        }(response => response.json())
    })hen(data => {
    .catch(error => {r) {
        console.error('Error loading game stats:', error);ror);
    });     return;
}       }
        
// Change AI mode game state
function changeAiMode() {ata);
    const newMode = parseInt(aiModeSelect.value);
    .catch(error => {
    fetch('/api/change_ai_mode', {g AI move:', error);
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },me result
        body: JSON.stringify({
            session_id: gameState.sessionId,
            ai_mode: newMode
        })
    }) Get player and AI hands
    .then(response => response.json())ind(p => p.name === 'Player');
    .then(data => {State.players.find(p => p.name === 'AI');
        if (data.error) {
            console.error('Error changing AI mode:', data.error);
            return;ge = '';
        }andName = '';
        
        gameState.aiMode = data.ai_mode;
        alert(`Changed AI level to ${getAiModeName(gameState.aiMode)}`);
    })  if (gameState.sounds.win) gameState.sounds.win.play();
    .catch(error => {
        console.error('Error changing AI mode:', error);se
    }); if (player && player.hand_name) {
}           handName = gameState.handDescriptions[player.hand_name] || player.hand_name;
        }
// Get AI mode name from mode number'ai') {
function getAiModeName(mode) {ns! 😎';
    const modes = [te.sounds.lose) gameState.sounds.lose.play();
        "Simple AI",
        "Probability AI",description from API response
        "Advanced AI"hand_name) {
    ];      handName = gameState.handDescriptions[ai.hand_name] || ai.hand_name;
    return modes[mode] || "Unknown";
}   } else {
        resultMessage = 'It\'s a Draw!';
// Set up event listeners
function setupEventListeners() {
    // Button event listeners
    newGameBtn.addEventListener('click', startNewGame);
    changeAiBtn.addEventListener('click', changeAiMode);
    backToMenuBtn.addEventListener('click', () => {
        window.location.href = '/'; = `Winning hand: ${handName}`;
    }); handDescription.style.display = 'block';
    } else {
    // Action buttonson.style.display = 'none';
    foldBtn.addEventListener('click', () => handlePlayerAction('fold'));
    checkBtn.addEventListener('click', () => handlePlayerAction('check'));
    callBtn.addEventListener('click', () => handlePlayerAction('call'));
    raiseBtn.addEventListener('click', () => {
        betSliderContainer.style.display = 'flex';
    });Update statistics
    loadGameStats();
    // Bet slider and confirmation
    betSlider.addEventListener('input', () => {
        const value = betSlider.value;
        betValueText.textContent = value;
        gameState.betAmount = parseInt(value);
    });en(response => response.json())
    confirmBetBtn.addEventListener('click', confirmBet);
        // Update stats display
    // Winner overlay buttonstContent = data.total_games;
    playAgainBtn.addEventListener('click', () => {r_wins;
        winnerOverlay.classList.remove('active');
        startNewGame();textContent = data.win_rate + '%';
    }); 
    returnToMenuBtn.addEventListener('click', () => {
        window.location.href = '/';
    });     biggestPotElement.textContent = '$' + data.biggest_pot;
           }
    // Sound toggle    })
    const soundToggle = document.getElementById('sound-toggle');
    soundToggle.addEventListener('click', toggleSound););
}    });

// Load game sounds
function loadSounds() {
    gameState.sounds.deal = new Audio('/static/sounds/Audio/deal.ogg');
    gameState.sounds.chip = new Audio('/static/sounds/Audio/bet.ogg');
    gameState.sounds.win = new Audio('/static/sounds/Audio/win.ogg');
    gameState.sounds.lose = new Audio('/static/sounds/Audio/lose.ogg');
    gameState.sounds.check = new Audio('/static/sounds/Audio/check.ogg');
    gameState.sounds.fold = new Audio('/static/sounds/Audio/fold.ogg');
    
    // Set volume
    Object.values(gameState.sounds).forEach(sound => {
        if (sound) sound.volume = 0.5;
    });
}

// Initialize when the DOM content is loaded
document.addEventListener('DOMContentLoaded', initGame);
