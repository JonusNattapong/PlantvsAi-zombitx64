// JavaScript สำหรับเกม Tic Tac Toe

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
const statusText = document.querySelector('.status');
const aiAlgorithms = document.querySelectorAll('.ai-algorithm');
const newGameBtn = document.getElementById('new-game-btn');
const changeAiBtn = document.getElementById('change-ai-btn');
const backToMenuBtn = document.getElementById('back-to-menu-btn');
const playAgainBtn = document.getElementById('play-again-btn');
const returnToMenuBtn = document.getElementById('return-to-menu-btn');
const winnerOverlay = document.getElementById('winner-overlay');
const winnerText = document.getElementById('winner-text');

// Statistics elements
const totalGamesElement = document.getElementById('total-games');
const playerWinsElement = document.getElementById('player-wins');
const aiWinsElement = document.getElementById('ai-wins');
const drawsElement = document.getElementById('draws');
const winRateElement = document.getElementById('win-rate');

// เริ่มเกม
function initGame() {
    // สร้าง sessionId
    gameState.sessionId = generateSessionId();
    
    // ตั้งค่าโหมด AI จาก URL parameters (ถ้ามี)
    const urlParams = new URLSearchParams(window.location.search);
    const aiParam = urlParams.get('ai');
    if (aiParam !== null) {
        gameState.aiMode = parseInt(aiParam);
        // ไฮไลต์ algorithm ที่เลือก
        aiAlgorithms.forEach(algo => {
            algo.classList.remove('selected');
            if (algo.dataset.algorithm === aiParam) {
                algo.classList.add('selected');
            }
        });
    }
    
    // เริ่มเกมใหม่
    startNewGame();
    
    // โหลดสถิติ
    loadGameStats();
    
    // สร้างกระดาน
    createBoard();
    
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

// ตั้งค่า event listeners
function setupEventListeners() {
    // เปลี่ยน AI algorithm เมื่อคลิก
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
}

// เริ่มต้นเกมเมื่อโหลดหน้าเสร็จ
document.addEventListener('DOMContentLoaded', initGame);
