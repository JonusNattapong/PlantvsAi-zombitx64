// JavaScript สำหรับเกมหมากรุก (Chess)

// สถานะเกม
let gameState = {
    board: null,
    sessionId: null,
    gameOver: false,
    winner: null,
    playerTurn: true,
    aiMode: 0,
    selectedPiece: null,
    validMoves: {},
    promotionMove: null
};

// DOM elements
const gameBoard = document.getElementById('chess-board');
const gameStatus = document.getElementById('game-status');
const aiModeSelect = document.getElementById('ai-mode');
const newGameBtn = document.getElementById('new-game-btn');
const changeAiBtn = document.getElementById('change-ai-btn');
const backToMenuBtn = document.getElementById('back-to-menu-btn');
const playAgainBtn = document.getElementById('play-again-btn');
const returnToMenuBtn = document.getElementById('return-to-menu-btn');
const winnerOverlay = document.getElementById('winner-overlay');
const winnerText = document.getElementById('winner-text');
const promotionOverlay = document.getElementById('promotion-overlay');
const promotionOptions = document.getElementById('promotion-options');

// Statistics elements
const totalGamesElement = document.getElementById('total-games');
const playerWinsElement = document.getElementById('player-wins');
const aiWinsElement = document.getElementById('ai-wins');
const drawsElement = document.getElementById('draws');
const winRateElement = document.getElementById('win-rate');

// Game configuration
const BOARD_SIZE = 8;
const SQUARE_SIZE = 60; // ขนาดของช่องบนกระดาน

// Piece unicode symbols
const PIECES = {
    'white': {
        'P': '♙',
        'R': '♖',
        'N': '♘',
        'B': '♗',
        'Q': '♕',
        'K': '♔'
    },
    'black': {
        'P': '♟',
        'R': '♜',
        'N': '♞',
        'B': '♝',
        'Q': '♛',
        'K': '♚'
    }
};

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
            
            // เพิ่ม event listener
            square.addEventListener('click', handleSquareClick);
            
            // ถ้ามีข้อมูลกระดาน ให้แสดงหมาก
            if (gameState.board && gameState.board[row][col]) {
                const pieceElement = createPieceElement(gameState.board[row][col]);
                square.appendChild(pieceElement);
            }
            
            gameBoard.appendChild(square);
        }
    }
}

// Create a piece element from piece data
function createPieceElement(pieceData) {
    const pieceElement = document.createElement('div');
    pieceElement.className = `piece ${pieceData.color}`;
    
    // Add piece symbol
    pieceElement.textContent = PIECES[pieceData.color][pieceData.piece];
    
    // If we have SVG pieces, use them instead
    const pieceImg = document.createElement('img');
    pieceImg.src = `/static/svg_cards/${pieceData.piece}_${pieceData.color}.svg`;
    pieceImg.alt = `${pieceData.piece} of ${pieceData.color}`;
    pieceImg.onerror = () => {
        // If SVG loading fails, use the text fallback (already created)
        pieceImg.style.display = 'none';
    };
    pieceImg.style.width = '100%';
    pieceImg.style.height = '100%';
    pieceImg.style.position = 'absolute';
    pieceImg.style.top = '0';
    pieceImg.style.left = '0';
    
    pieceElement.appendChild(pieceImg);
    
    return pieceElement;
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
                const pieceElement = createPieceElement(gameState.board[row][col]);
                square.appendChild(pieceElement);
            }
        }
    }
}

// อัปเดตข้อความสถานะเกม
function updateGameStatus() {
    if (gameState.gameOver) {
        if (gameState.winner === 'white') {
            gameStatus.textContent = 'คุณชนะ!';
            showWinnerOverlay('คุณชนะ! ยินดีด้วย!');
        } else if (gameState.winner === 'black') {
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

// แสดง overlay สำหรับเลือกการเลื่อนขั้นของเบี้ย
function showPromotionOverlay(from_row, from_col, to_row, to_col) {
    // บันทึกข้อมูลการเคลื่อนที่
    gameState.promotionMove = {
        from_row: from_row,
        from_col: from_col,
        to_row: to_row,
        to_col: to_col
    };
    
    // แสดงตัวเลือก
    promotionOverlay.classList.add('active');
    
    // สร้างตัวเลือก
    promotionOptions.innerHTML = '';
    const options = ['Q', 'R', 'N', 'B'];
    
    options.forEach(piece => {
        const option = document.createElement('div');
        option.className = 'promotion-option';
        option.textContent = PIECES['white'][piece];
        option.dataset.piece = piece;
        option.addEventListener('click', () => {
            handlePromotion(piece);
        });
        promotionOptions.appendChild(option);
    });
}

// ซ่อน overlay เลือกการเลื่อนขั้น
function hidePromotionOverlay() {
    promotionOverlay.classList.remove('active');
    gameState.promotionMove = null;
}

// จัดการการเลื่อนขั้นของเบี้ย
function handlePromotion(piece) {
    if (!gameState.promotionMove) {
        return;
    }
    
    const { from_row, from_col, to_row, to_col } = gameState.promotionMove;
    
    // ทำการเคลื่อนที่พร้อมเลื่อนขั้น
    makeMove(from_row, from_col, to_row, to_col, piece);
    
    // ซ่อน overlay
    hidePromotionOverlay();
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
            game_type: 'Chess'
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
        gameState.promotionMove = null;
        
        // อัปเดต UI
        createBoard();
        updateGameStatus();
        hidePromotionOverlay();
    })
    .catch(error => {
        console.error('Error starting new game:', error);
    });
}

// จัดการคลิกที่ช่องบนกระดาน
function handleSquareClick(event) {
    // ไม่ทำอะไรถ้าเกมจบแล้ว หรือไม่ใช่ตาของผู้เล่น
    if (gameState.gameOver || !gameState.playerTurn) {
        return;
    }
    
    const square = event.currentTarget;
    const row = parseInt(square.dataset.row);
    const col = parseInt(square.dataset.col);
    
    // กรณีที่ยังไม่ได้เลือกหมาก
    if (!gameState.selectedPiece) {
        // เช็คว่ามีหมากของผู้เล่นในช่องนี้หรือไม่
        if (gameState.board[row][col] && gameState.board[row][col].color === 'white') {
            // เลือกหมาก
            selectPiece(row, col);
        }
    } 
    // กรณีที่เลือกหมากไว้แล้ว
    else {
        const fromRow = gameState.selectedPiece.row;
        const fromCol = gameState.selectedPiece.col;
        
        // ถ้าคลิกที่ตำแหน่งเดิม = ยกเลิกการเลือก
        if (row === fromRow && col === fromCol) {
            clearSelection();
            return;
        }
        
        // เช็คว่าช่องที่คลิกเป็นการเคลื่อนที่ที่ถูกต้องหรือไม่
        const moveKey = `${row},${col}`;
        if (moveKey in gameState.validMoves) {
            const moveInfo = gameState.validMoves[moveKey];
            
            // ตรวจสอบการเลื่อนขั้นของเบี้ย
            if (moveInfo.promotion) {
                showPromotionOverlay(fromRow, fromCol, row, col);
                return;
            }
            
            // ทำการเคลื่อนที่
            makeMove(fromRow, fromCol, row, col);
        } 
        // ถ้าคลิกที่หมากของตัวเองอันอื่น
        else if (gameState.board[row][col] && gameState.board[row][col].color === 'white') {
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
            col: col,
            game_type: 'Chess'
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
function makeMove(fromRow, fromCol, toRow, toCol, promotionPiece = null) {
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
            promotion_piece: promotionPiece,
            game_type: 'Chess'
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
        
        // ถ้าเป็นตาของ AI และเกมยังไม่จบ
        if (!gameState.playerTurn && !gameState.gameOver) {
            // แสดงข้อความ AI กำลังคิด
            gameStatus.textContent = 'AI กำลังคิด...';
            
            // ให้ AI คิดสักพักก่อนเดิน
            setTimeout(() => {
                aiMove();
            }, 500);
        }
    })
    .catch(error => {
        console.error('Error making move:', error);
    });
}

// AI เดินหมาก
function aiMove() {
    fetch('/api/ai_move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: gameState.sessionId,
            game_type: 'Chess',
            ai_mode: gameState.aiMode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error making AI move:', data.error);
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
        console.error('Error making AI move:', error);
    });
}

// โหลดสถิติเกม
function loadGameStats() {
    fetch('/api/get_stats?game_type=Chess')
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

// ตัวอย่างการเพิ่มเสียงในอนาคต (ถ้าต้องการ)
function loadChessSounds() {
    const sounds = {
        move: new Audio('/static/sounds/Audio/move.ogg'),
        capture: new Audio('/static/sounds/Audio/capture.ogg'),
        check: new Audio('/static/sounds/Audio/check.ogg'),
        castle: new Audio('/static/sounds/Audio/castle.ogg'),
        win: new Audio('/static/sounds/Audio/win.ogg'),
        lose: new Audio('/static/sounds/Audio/lose.ogg')
    };
    
    return sounds;
}
