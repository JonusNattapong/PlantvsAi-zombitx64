// JavaScript สำหรับเกม Checkers (หมากฮอต)

// สถานะเกม
let gameState = {
    board: null,
    sessionId: null,
    gameOver: false,
    winner: null,
    playerTurn: true,
    aiMode: 0,
    selectedPiece: null,
    validMoves: {}
};

// DOM elements
const gameBoard = document.getElementById('checkers-board');
const gameStatus = document.getElementById('game-status');
const aiModeSelect = document.getElementById('ai-mode');
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

// Game configuration
const BOARD_SIZE = 8;
const SQUARE_SIZE = 60; // ขนาดของช่องบนกระดาน

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
    
    // สร้างตาราง 8x8
    for (let row = 0; row < BOARD_SIZE; row++) {
        for (let col = 0; col < BOARD_SIZE; col++) {
            const square = document.createElement('div');
            square.className = 'square';
            square.dataset.row = row;
            square.dataset.col = col;
            
            // กำหนด class light หรือ dark ตามตำแหน่ง
            const isLight = (row + col) % 2 === 0;
            square.classList.add(isLight ? 'light' : 'dark');
            
            // เพิ่ม event listener สำหรับช่องสีเข้มเท่านั้น (ที่หมากเดินได้)
            if (!isLight) {
                square.addEventListener('click', handleSquareClick);
            }
            
            // ถ้ามีข้อมูลกระดาน ให้แสดงหมาก
            if (gameState.board && gameState.board[row][col]) {
                const piece = document.createElement('div');
                piece.className = 'piece';
                
                // กำหนดสีและสถานะ king
                const pieceData = gameState.board[row][col];
                piece.classList.add(pieceData.piece === 'O' ? 'player' : 'ai');
                
                if (pieceData.king) {
                    piece.classList.add('king');
                }
                
                square.appendChild(piece);
            }
            
            gameBoard.appendChild(square);
        }
    }
}

// อัปเดตกระดานจากสถานะเกม
function updateBoard() {
    // ล้างการเลือกทั้งหมด
    clearSelection();
    
    // อัปเดตตำแหน่งหมากทั้งหมด
    for (let row = 0; row < BOARD_SIZE; row++) {
        for (let col = 0; col < BOARD_SIZE; col++) {
            const square = getSquare(row, col);
            
            // ลบหมากเก่าออก
            while (square.firstChild) {
                square.removeChild(square.firstChild);
            }
            
            // ถ้ามีหมากในตำแหน่งนี้ ให้สร้างใหม่
            if (gameState.board[row][col]) {
                const piece = document.createElement('div');
                piece.className = 'piece';
                
                const pieceData = gameState.board[row][col];
                piece.classList.add(pieceData.piece === 'O' ? 'player' : 'ai');
                
                if (pieceData.king) {
                    piece.classList.add('king');
                }
                
                square.appendChild(piece);
            }
        }
    }
}

// อัปเดตข้อความสถานะเกม
function updateGameStatus() {
    if (gameState.gameOver) {
        if (gameState.winner === 'O') {
            gameStatus.textContent = 'คุณชนะ!';
            showWinnerOverlay('คุณชนะ! ยินดีด้วย!');
        } else if (gameState.winner === 'X') {
            gameStatus.textContent = 'AI ชนะ!';
            showWinnerOverlay('AI ชนะ! ลองอีกครั้ง!');
        } else {
            gameStatus.textContent = 'เกมเสมอ!';
            showWinnerOverlay('เกมจบลงด้วยการเสมอ!');
        }
    } else {
        if (gameState.playerTurn) {
            if (gameState.selectedPiece) {
                gameStatus.textContent = 'เลือกตำแหน่งที่ต้องการเดิน';
            } else {
                gameStatus.textContent = 'ตาของคุณ! เลือกหมากที่ต้องการเคลื่อนย้าย';
            }
        } else {
            gameStatus.textContent = 'AI กำลังคิด...';
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
            game_type: 'Checkers'
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
        gameState.selectedPiece = null;
        gameState.validMoves = {};
        
        // อัปเดต UI
        createBoard();
        updateGameStatus();
    })
    .catch(error => {
        console.error('Error starting new game:', error);
    });
}

// จัดการคลิกที่ช่องบนกระดาน
function handleSquareClick(event) {
    // ไม่ทำอะไรถ้าไม่ใช่ตาของผู้เล่นหรือเกมจบแล้ว
    if (!gameState.playerTurn || gameState.gameOver) {
        return;
    }
    
    const square = event.currentTarget;
    const row = parseInt(square.dataset.row);
    const col = parseInt(square.dataset.col);
    
    // กรณีที่ยังไม่ได้เลือกหมาก
    if (!gameState.selectedPiece) {
        // เช็คว่ามีหมากของผู้เล่นในช่องนี้หรือไม่
        if (gameState.board[row][col] && gameState.board[row][col].piece === 'O') {
            // เลือกหมาก
            selectPiece(row, col);
        }
    } 
    // กรณีที่เลือกหมากไว้แล้ว
    else {
        // เช็คว่าช่องที่คลิกเป็นการเคลื่อนที่ที่ถูกต้องหรือไม่
        const moveKey = `${row},${col}`;
        if (moveKey in gameState.validMoves) {
            // ทำการเคลื่อนที่
            makeMove(gameState.selectedPiece.row, gameState.selectedPiece.col, row, col);
        } 
        // ถ้าคลิกที่หมากของตัวเองอันอื่น
        else if (gameState.board[row][col] && gameState.board[row][col].piece === 'O') {
            // เลือกหมากใหม่
            selectPiece(row, col);
        } 
        // ถ้าคลิกที่อื่น
        else {
            // ยกเลิกการเลือก
            clearSelection();
        }
    }
}

// เลือกหมาก
function selectPiece(row, col) {
    // ล้างการเลือกเก่า
    clearSelection();
    
    // เลือกหมากใหม่
    gameState.selectedPiece = { row, col };
    
    // ไฮไลต์ช่องที่เลือก
    const square = getSquare(row, col);
    square.classList.add('selected');
    
    // ขอการเคลื่อนที่ที่ถูกต้องจาก API
    getValidMoves(row, col);
}

// ล้างการเลือก
function clearSelection() {
    // ล้างไฮไลต์ช่องที่เลือก
    const squares = document.querySelectorAll('.square');
    squares.forEach(square => {
        square.classList.remove('selected', 'valid-move');
    });
    
    gameState.selectedPiece = null;
    gameState.validMoves = {};
    
    updateGameStatus();
}

// รับช่องจากตำแหน่ง
function getSquare(row, col) {
    return document.querySelector(`.square[data-row="${row}"][data-col="${col}"]`);
}

// ขอการเคลื่อนที่ที่ถูกต้องจาก API
function getValidMoves(row, col) {
    fetch('/api/get_valid_moves', {
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
            console.error('Error getting valid moves:', data.error);
            return;
        }
        
        // บันทึกการเคลื่อนที่ที่ถูกต้อง
        gameState.validMoves = data.valid_moves || {};
        
        // ไฮไลต์การเคลื่อนที่ที่ถูกต้อง
        for (const moveKey in gameState.validMoves) {
            const [moveRow, moveCol] = moveKey.split(',').map(Number);
            const square = getSquare(moveRow, moveCol);
            square.classList.add('valid-move');
        }
        
        updateGameStatus();
    })
    .catch(error => {
        console.error('Error getting valid moves:', error);
    });
}

// ทำการเคลื่อนที่
function makeMove(fromRow, fromCol, toRow, toCol) {
    fetch('/api/make_move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: gameState.sessionId,
            from_row: fromRow,
            from_col: fromCol,
            to_row: toRow,
            to_col: toCol,
            game_type: 'Checkers'
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
        gameState.selectedPiece = null;
        gameState.validMoves = {};
        
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
    fetch('/api/get_stats?game_type=Checkers')
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
