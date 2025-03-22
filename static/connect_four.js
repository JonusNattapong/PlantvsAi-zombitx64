// JavaScript สำหรับเกม Connect Four

// สถานะเกม
let gameState = {
    board: null,
    sessionId: null,
    gameOver: false,
    winner: null,
    playerTurn: true,
    aiMode: 0
};

// DOM elements
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
const totalGamesElement = document.getElementById('total-games');
const playerWinsElement = document.getElementById('player-wins');
const aiWinsElement = document.getElementById('ai-wins');
const drawsElement = document.getElementById('draws');
const winRateElement = document.getElementById('win-rate');

// Game configuration
const ROWS = 6;
const COLS = 7;
const CELL_SIZE = 60;
const HOVER_SIZE = 20;

// เริ่มเกม
function initGame() {
    // สร้าง sessionId
    gameState.sessionId = generateSessionId();
    
    // ตั้งค่าโหมด AI จาก URL parameters (ถ้ามี)
    const urlParams = new URLSearchParams(window.location.search);
    const aiParam = urlParams.get('ai');
    if (aiParam !== null) {
        gameState.aiMode = parseInt(aiParam);
        aiModeSelect.value = aiParam;
    }
    
    // เริ่มเกมใหม่
    startNewGame();
    
    // สร้างกระดานและ hover indicators
    createBoard();
    createColumnHovers();
    
    // โหลดสถิติ
    loadGameStats();
    
    // ตั้งค่า event listeners
    setupEventListeners();
}

// สร้าง sessionId แบบสุ่ม
function generateSessionId() {
    return Math.floor(Math.random() * 100000).toString();
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
        totalGamesElement.textContent = data.total_games;
        playerWinsElement.textContent = data.player_wins;
        aiWinsElement.textContent = data.ai_wins;
        drawsElement.textContent = data.draws;
        winRateElement.textContent = data.win_rate + '%';
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
}

// เริ่มต้นเกมเมื่อโหลดหน้าเสร็จ
document.addEventListener('DOMContentLoaded', initGame);
