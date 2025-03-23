// JavaScript สำหรับเกม Connect Four

// สถานะเกม
let gameState = {
    board: null,
    sessionId: null,
    gameOver: false,
    winner: null,
    playerTurn: true,
    aiMode: 0,
    isLoading: false,
    errorMessage: null,
    lastAction: null,
    animationsEnabled: true,
    soundEnabled: true
};

// DOM elements - แคชไว้เพื่อเพิ่มประสิทธิภาพ
const gameBoard = document.getElementById('game-board');
const columnHovers = document.getElementById('column-hovers');
const statusText = document.querySelector('.status');
const aiModeSelect = document.getElementById('ai-mode');
const newGameBtn = document.getElementById('new-game');
const changeAiBtn = document.getElementById('change-ai');
const backToMenuBtn = document.getElementById('back-to-menu');
const playAgainBtn = document.getElementById('play-again');
const returnToMenuBtn = document.getElementById('return-to-menu');
const winnerOverlay = document.getElementById('winner-overlay');
const winnerText = document.getElementById('winner-text');

// Statistics elements
const statsElements = {
    totalGames: document.getElementById('total-games'),
    playerWins: document.getElementById('player-wins'),
    aiWins: document.getElementById('ai-wins'),
    draws: document.getElementById('draws'),
    winRate: document.getElementById('win-rate')
};

// Game configuration
const ROWS = 6;
const COLS = 7;
const CELL_SIZE = 60;
const HOVER_SIZE = 20;

// เริ่มเกม
function initGame() {
    try {
        console.log('Initializing Connect Four game...');
        
        // สร้าง sessionId
        gameState.sessionId = generateSessionId();
        
        // ตั้งค่าโหมด AI จาก URL parameters (ถ้ามี)
        const urlParams = new URLSearchParams(window.location.search);
        const aiParam = urlParams.get('ai');
        if (aiParam !== null) {
            gameState.aiMode = parseInt(aiParam);
            if (aiModeSelect) aiModeSelect.value = aiParam;
        }
        
        // โหลดค่าพรีเฟอเรนซ์จาก localStorage
        loadPreferences();
        
        // เริ่มเกมใหม่
        startNewGame();
        
        // สร้างกระดานและ hover indicators
        createBoard();
        createColumnHovers();
        
        // โหลดสถิติ
        loadGameStats();
        
        // ตั้งค่า event listeners
        setupEventListeners();
        
        console.log('Connect Four game initialized successfully');
    } catch (error) {
        console.error('Error initializing Connect Four game:', error);
        showErrorMessage('เกิดข้อผิดพลาดในการโหลดเกม โปรดรีเฟรชหน้า');
    }
}

// โหลดค่าพรีเฟอเรนซ์จาก localStorage
function loadPreferences() {
    // โหลดการตั้งค่าแอนิเมชัน
    if (localStorage.getItem('connectFourAnimationsEnabled') !== null) {
        gameState.animationsEnabled = localStorage.getItem('connectFourAnimationsEnabled') === 'true';
        updateAnimationToggle();
    }
    
    // โหลดการตั้งค่าเสียง
    if (localStorage.getItem('connectFourSoundEnabled') !== null) {
        gameState.soundEnabled = localStorage.getItem('connectFourSoundEnabled') === 'true';
        updateSoundToggle();
    }
}

// อัปเดตปุ่มเปิด/ปิดแอนิเมชัน
function updateAnimationToggle() {
    const animationToggle = document.getElementById('animation-toggle');
    if (animationToggle) {
        animationToggle.textContent = gameState.animationsEnabled ? 
            '✨ เอฟเฟกต์: เปิด' : '✨ เอฟเฟกต์: ปิด';
    }
    
    // เพิ่มหรือลบคลาสสำหรับแอนิเมชัน
    document.body.classList.toggle('animations-disabled', !gameState.animationsEnabled);
}

// อัปเดตปุ่มเปิด/ปิดเสียง
function updateSoundToggle() {
    const soundToggle = document.getElementById('sound-toggle');
    if (soundToggle) {
        soundToggle.textContent = gameState.soundEnabled ? '🔊' : '🔇';
    }
}

// เปิด/ปิดแอนิเมชัน
function toggleAnimations() {
    gameState.animationsEnabled = !gameState.animationsEnabled;
    updateAnimationToggle();
    
    // บันทึกค่าพรีเฟอเรนซ์
    localStorage.setItem('connectFourAnimationsEnabled', gameState.animationsEnabled.toString());
}

// เปิด/ปิดเสียง
function toggleSound() {
    gameState.soundEnabled = !gameState.soundEnabled;
    updateSoundToggle();
    
    // บันทึกค่าพรีเฟอเรนซ์
    localStorage.setItem('connectFourSoundEnabled', gameState.soundEnabled.toString());
}

// สร้าง sessionId แบบสุ่มที่มีความปลอดภัยมากขึ้น
function generateSessionId() {
    const timestamp = new Date().getTime().toString(36);
    const randomPart = Math.random().toString(36).substring(2, 10);
    return `${timestamp}-${randomPart}`;
}

// แสดงข้อความผิดพลาด
function showErrorMessage(message) {
    gameState.errorMessage = message;
    
    // ตรวจสอบว่ามี element แสดงข้อผิดพลาดหรือไม่ ถ้าไม่มีให้สร้างใหม่
    let errorElement = document.getElementById('game-error-message');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.id = 'game-error-message';
        errorElement.className = 'bg-red-500 text-white p-3 rounded-lg fixed top-4 right-4 z-50 shadow-lg';
        document.body.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    
    // ซ่อนอัตโนมัติหลังจาก 5 วินาที
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 5000);
}

// แสดง/ซ่อนสถานะการโหลด
function updateLoadingState(isLoading) {
    gameState.isLoading = isLoading;
    
    // สร้างหรือปรับปรุงตัวแสดงสถานะการโหลด
    let loaderElement = document.getElementById('game-loader');
    
    if (isLoading) {
        if (!loaderElement) {
            loaderElement = document.createElement('div');
            loaderElement.id = 'game-loader';
            loaderElement.className = 'fixed top-0 left-0 right-0 bottom-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
            loaderElement.innerHTML = `
                <div class="bg-dark-secondary p-4 rounded-lg shadow-lg flex flex-col items-center">
                    <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
                    <p class="mt-2 text-white">กำลังโหลด...</p>
                </div>
            `;
            document.body.appendChild(loaderElement);
        } else {
            loaderElement.style.display = 'flex';
        }
    } else if (loaderElement) {
        loaderElement.style.display = 'none';
    }
}

// เล่นเสียงเอฟเฟกต์
function playSound(soundName) {
    if (!gameState.soundEnabled) return;
    
    try {
        const sounds = {
            drop: '/static/sounds/Audio/drop.mp3',
            win: '/static/sounds/Audio/win.mp3',
            lose: '/static/sounds/Audio/lose.mp3',
            draw: '/static/sounds/Audio/draw.mp3'
        };
        
        if (sounds[soundName]) {
            const audio = new Audio(sounds[soundName]);
            audio.play().catch(err => console.warn('Sound play error:', err));
        }
    } catch (error) {
        console.warn(`Error playing sound ${soundName}:`, error);
    }
}

// สร้างกระดานเกม
function createBoard() {
    gameBoard.innerHTML = '';
    gameBoard.style.gridTemplateColumns = `repeat(${COLS}, ${CELL_SIZE}px)`;
    
    // สร้างคอลัมน์
    for (let col = 0; col < COLS; col++) {
        const column = document.createElement('div');
        column.className = 'column';
        
        // สร้างเซลล์ในแต่ละคอลัมน์ (จากบนลงล่าง)
        for (let row = 0; row < ROWS; row++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = row;
            cell.dataset.col = col;
            
            // ตั้งค่าเนื้อหาของเซลล์ตามสถานะกระดาน
            if (gameState.board && gameState.board[row][col]) {
                cell.classList.add(gameState.board[row][col] === 'O' ? 'yellow' : 'red');
            }
            
            column.appendChild(cell);
        }
        
        gameBoard.appendChild(column);
    }
}

// สร้าง hover indicators
function createColumnHovers() {
    columnHovers.innerHTML = '';
    
    // สร้าง hover indicator สำหรับแต่ละคอลัมน์
    for (let col = 0; col < COLS; col++) {
        const hover = document.createElement('div');
        hover.className = 'column-hover';
        hover.dataset.col = col;
        hover.style.width = `${CELL_SIZE}px`;
        
        hover.addEventListener('mouseenter', () => {
            if (gameState.playerTurn && !gameState.gameOver) {
                hover.classList.add('highlight');
            }
        });
        
        hover.addEventListener('mouseleave', () => {
            hover.classList.remove('highlight');
        });
        
        hover.addEventListener('click', handleColumnClick);
        
        columnHovers.appendChild(hover);
    }
}

// อัปเดตกระดานจากสถานะเกม
function updateBoard() {
    const cells = document.querySelectorAll('.cell');
    
    cells.forEach(cell => {
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        
        cell.classList.remove('yellow', 'red');
        
        if (gameState.board[row][col] === 'O') {
            cell.classList.add('yellow');
        } else if (gameState.board[row][col] === 'X') {
            cell.classList.add('red');
        }
    });
}

// อัปเดตข้อความสถานะเกม
function updateGameStatus() {
    if (gameState.gameOver) {
        if (gameState.winner === 'O') {
            statusText.textContent = 'คุณชนะ!';
            showWinnerOverlay('คุณชนะ! ยินดีด้วย!');
        } else if (gameState.winner === 'X') {
            statusText.textContent = 'AI ชนะ!';
            showWinnerOverlay('AI ชนะ! ลองอีกครั้ง!');
        } else {
            statusText.textContent = 'เกมเสมอ!';
            showWinnerOverlay('เกมจบลงด้วยการเสมอ!');
        }
    } else {
        if (gameState.playerTurn) {
            statusText.textContent = 'ตาของคุณ! เลือกคอลัมน์ที่ต้องการวางหมาก';
        } else {
            statusText.textContent = 'AI กำลังคิด...';
        }
    }
}

// แสดง overlay ผู้ชนะ
function showWinnerOverlay(message) {
    winnerText.textContent = message;
    winnerOverlay.classList.add('active');
}

// ซ่อน overlay ผู้ชนะ
function hideWinnerOverlay() {
    winnerOverlay.classList.remove('active');
}

// เริ่มเกมใหม่
function startNewGame() {
    // ส่งคำขอ API เพื่อเริ่มเกมใหม่
    fetch('/api/new_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: gameState.sessionId,
            ai_mode: gameState.aiMode,
            game_type: 'ConnectFour'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error starting new game:', data.error);
            return;
        }
        
        // อัปเดตสถานะเกม
        gameState.board = data.board;
        gameState.playerTurn = data.player_turn;
        gameState.gameOver = data.game_over;
        gameState.winner = data.winner;
        
        // อัปเดต UI
        createBoard();
        updateGameStatus();
    })
    .catch(error => {
        console.error('Error starting new game:', error);
    });
}

// จัดการคลิกที่คอลัมน์
function handleColumnClick(event) {
    // ไม่ทำอะไรถ้าไม่ใช่ตาของผู้เล่นหรือเกมจบแล้ว
    if (!gameState.playerTurn || gameState.gameOver) {
        return;
    }
    
    const col = parseInt(event.target.dataset.col);
    
    // ส่งการเคลื่อนที่ไปยัง API
    makeMove(col);
}

// ทำการเคลื่อนที่
function makeMove(col) {
    fetch('/api/make_move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: gameState.sessionId,
            col: col,
            game_type: 'ConnectFour'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error making move:', data.error);
            return;
        }
        
        // อัปเดตสถานะเกม
        gameState.board = data.board;
        gameState.playerTurn = data.player_turn;
        gameState.gameOver = data.game_over;
        gameState.winner = data.winner;
        
        // อัปเดต UI
        updateBoard();
        updateGameStatus();
        
        // อัปเดตสถิติถ้าเกมจบแล้ว
        if (gameState.gameOver) {
            loadGameStats();
        }
    })
    .catch(error => {
        console.error('Error making move:', error);
    });
}

// โหลดสถิติเกม
function loadGameStats() {
    fetch('/api/get_stats?game_type=ConnectFour')
    .then(response => response.json())
    .then(data => {
        // อัปเดตแสดงสถิติ
        statsElements.totalGames.textContent = data.total_games;
        statsElements.playerWins.textContent = data.player_wins;
        statsElements.aiWins.textContent = data.ai_wins;
        statsElements.draws.textContent = data.draws;
        statsElements.winRate.textContent = data.win_rate + '%';
    })
    .catch(error => {
        console.error('Error loading game stats:', error);
    });
}

// เปลี่ยนโหมด AI
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
        alert(`เปลี่ยนอัลกอริทึม AI เป็น ${getAiModeName(gameState.aiMode)}`);
    })
    .catch(error => {
        console.error('Error changing AI mode:', error);
    });
}

// ดึงชื่อโหมด AI
function getAiModeName(mode) {
    const modes = [
        "Minimax",
        "Pattern Recognition",
        "Q-Learning",
        "Neural Network",
        "MCTS",
        "Genetic Algorithm"
    ];
    return modes[mode] || "Unknown";
}

// ตั้งค่า event listeners
function setupEventListeners() {
    // ปุ่มเริ่มเกมใหม่
    newGameBtn.addEventListener('click', startNewGame);
    
    // ปุ่มเปลี่ยน AI
    changeAiBtn.addEventListener('click', changeAiMode);
    
    // ปุ่มกลับไปเมนู
    backToMenuBtn.addEventListener('click', () => {
        window.location.href = '/';
    });
    
    // ปุ่มเล่นอีกครั้งใน overlay
    playAgainBtn.addEventListener('click', () => {
        hideWinnerOverlay();
        startNewGame();
    });
    
    // ปุ่มกลับเมนูใน overlay
    returnToMenuBtn.addEventListener('click', () => {
        window.location.href = '/';
    });
    
    // ปุ่มเลือกโหมด AI
    aiModeSelect.addEventListener('change', () => {
        gameState.aiMode = parseInt(aiModeSelect.value);
    });
    
    // ปุ่มเปิด/ปิดแอนิเมชัน
    document.getElementById('animation-toggle').addEventListener('click', toggleAnimations);
    
    // ปุ่มเปิด/ปิดเสียง
    document.getElementById('sound-toggle').addEventListener('click', toggleSound);
}

// เริ่มต้นเกมเมื่อโหลดหน้าเสร็จ
document.addEventListener('DOMContentLoaded', initGame);
