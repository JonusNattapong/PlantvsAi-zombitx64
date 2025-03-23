// JavaScript สำหรับเกม Tic Tac Toe (XO)

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
const statusText = document.getElementById('status');
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
const BOARD_SIZE = 3;
const CELL_SIZE = 100;

// เริ่มเกม
function initGame() {
    try {
        console.log('Initializing Tic Tac Toe game...');
        
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
        
        // สร้างกระดาน
        createBoard();
        
        // โหลดสถิติ
        loadGameStats();
        
        // ตั้งค่า event listeners
        setupEventListeners();
        
        console.log('Tic Tac Toe game initialized successfully');
    } catch (error) {
        console.error('Error initializing Tic Tac Toe game:', error);
        showErrorMessage('เกิดข้อผิดพลาดในการโหลดเกม โปรดรีเฟรชหน้า');
    }
}

// โหลดค่าพรีเฟอเรนซ์จาก localStorage
function loadPreferences() {
    // โหลดการตั้งค่าแอนิเมชัน
    if (localStorage.getItem('tictactoeAnimationsEnabled') !== null) {
        gameState.animationsEnabled = localStorage.getItem('tictactoeAnimationsEnabled') === 'true';
        updateAnimationToggle();
    }
    
    // โหลดการตั้งค่าเสียง
    if (localStorage.getItem('tictactoeSoundEnabled') !== null) {
        gameState.soundEnabled = localStorage.getItem('tictactoeSoundEnabled') === 'true';
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
    localStorage.setItem('tictactoeAnimationsEnabled', gameState.animationsEnabled.toString());
}

// เปิด/ปิดเสียง
function toggleSound() {
    gameState.soundEnabled = !gameState.soundEnabled;
    updateSoundToggle();
    
    // บันทึกค่าพรีเฟอเรนซ์
    localStorage.setItem('tictactoeSoundEnabled', gameState.soundEnabled.toString());
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
            place: '/static/sounds/Audio/place.mp3',
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
    
    for (let row = 0; row < 3; row++) {
        for (let col = 0; col < 3; col++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = row;
            cell.dataset.col = col;
            cell.addEventListener('click', handleCellClick);
            
            // ตั้งค่าเนื้อหาของเซลล์ตามสถานะกระดาน
            if (gameState.board && gameState.board[row][col]) {
                cell.textContent = gameState.board[row][col];
                cell.classList.add(gameState.board[row][col] === 'O' ? 'player' : 'ai');
            }
            
            gameBoard.appendChild(cell);
        }
    }
}

// อัปเดตกระดานจากสถานะเกม
function updateBoard() {
    const cells = document.querySelectorAll('.cell');
    
    cells.forEach(cell => {
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        
        cell.textContent = gameState.board[row][col] || '';
        cell.classList.remove('player', 'ai');
        
        if (gameState.board[row][col] === 'O') {
            cell.classList.add('player');
        } else if (gameState.board[row][col] === 'X') {
            cell.classList.add('ai');
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
            statusText.textContent = 'ตาของคุณ! เลือกตำแหน่งที่ต้องการวาง O';
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
            game_type: 'TicTacToe'
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

// จัดการคลิกที่เซลล์
function handleCellClick(event) {
    // ไม่ทำอะไรถ้าไม่ใช่ตาของผู้เล่นหรือเกมจบแล้ว
    if (!gameState.playerTurn || gameState.gameOver) {
        return;
    }
    
    const cell = event.target;
    const row = parseInt(cell.dataset.row);
    const col = parseInt(cell.dataset.col);
    
    // เช็คว่าเซลล์ว่างอยู่หรือไม่
    if (gameState.board[row][col]) {
        return;
    }
    
    // ส่งการเคลื่อนที่ไปยัง API
    makeMove(row, col);
}

// ทำการเคลื่อนที่
function makeMove(row, col) {
    fetch('/api/make_move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: gameState.sessionId,
            row: row,
            col: col
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error making move:', data.error);
            return;
        }
        
        // อัปเดตสถานะเกมจาก API
        gameState.board = data.board;
        gameState.playerTurn = data.player_turn;
        gameState.gameOver = data.game_over;
        gameState.winner = data.winner;
        
        // อัปเดต UI
        updateBoard();
        updateGameStatus();
        
        // ถ้าไม่ใช่ตาของผู้เล่นและเกมยังไม่จบ ให้ AI เคลื่อนที่
        if (!gameState.playerTurn && !gameState.gameOver) {
            // เพิ่มการหน่วงเล็กน้อยเพื่อให้รู้สึกเหมือนการคิด
            setTimeout(() => {
                requestAiMove();
            }, 500);
        }
    })
    .catch(error => {
        console.error('Error making move:', error);
    });
}

// ขอให้ AI เคลื่อนที่
function requestAiMove() {
    fetch('/api/ai_move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: gameState.sessionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error requesting AI move:', data.error);
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
    })
    .catch(error => {
        console.error('Error requesting AI move:', error);
    });
}

// เปลี่ยนโหมด AI
function changeAiMode() {
    const selectedAlgorithm = document.querySelector('.ai-algorithm.selected');
    const newMode = parseInt(selectedAlgorithm.dataset.algorithm);
    
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

// โหลดสถิติเกม
function loadGameStats() {
    fetch('/api/get_stats?game_type=TicTacToe')
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

// ตั้งค่า event listeners
function setupEventListeners() {
    // เปลี่ยน AI algorithm เมื่อคลิก
    const aiAlgorithms = document.querySelectorAll('.ai-algorithm');
    aiAlgorithms.forEach(algorithm => {
        algorithm.addEventListener('click', () => {
            // ยกเลิกการเลือกทั้งหมด
            aiAlgorithms.forEach(a => a.classList.remove('selected'));
            // เลือกอันที่คลิก
            algorithm.classList.add('selected');
        });
    });
    
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
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (event) => {
        // 'R' กดเพื่อเริ่มเกมใหม่
        if (event.key === 'r' || event.key === 'R') {
            startNewGame();
        }
        // 'ESC' กดเพื่อกลับไปยังเมนูหลัก
        else if (event.key === 'Escape') {
            window.location.href = '/';
        }
    });
    
    // Toggle animation
    const animationToggle = document.getElementById('animation-toggle');
    if (animationToggle) {
        animationToggle.addEventListener('click', toggleAnimations);
    }
    
    // Toggle sound
    const soundToggle = document.getElementById('sound-toggle');
    if (soundToggle) {
        soundToggle.addEventListener('click', toggleSound);
    }
}

// เริ่มต้นเกมเมื่อโหลดหน้าเสร็จ
document.addEventListener('DOMContentLoaded', initGame);
