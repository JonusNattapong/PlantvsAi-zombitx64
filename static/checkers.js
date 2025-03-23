// JavaScript สำหรับเกม Checkers (หมากฮอต)

// สถานะเกม
let gameState = {
    board: null,
    sessionId: null,
    gameOver: false,
    winner: null,
    playerTurn: true,
    aiMode: 1, // เริ่มต้นที่ระดับปานกลาง
    selectedPiece: null,
    validMoves: {},
    isLoading: false,
    errorMessage: null,
    animationsEnabled: true,
    soundEnabled: true,
    lastAction: null,
    playerColor: 'white'  // เริ่มต้นผู้เล่นเป็นฝั่งขาว
};

// Sound effects
const SOUNDS = {
    move: '/static/sounds/move.mp3',
    capture: '/static/sounds/capture.mp3',
    win: '/static/sounds/win.mp3',
    lose: '/static/sounds/lose.mp3',
    error: '/static/sounds/error.mp3',
    select: '/static/sounds/select.mp3'
};

// DOM elements - แคชไว้เพื่อเพิ่มประสิทธิภาพ
const gameBoard = document.getElementById('game-board');
const gameStatus = document.getElementById('status');
const newGameBtn = document.getElementById('new-game');
const changeAiBtn = document.getElementById('change-ai');
const backToMenuBtn = document.getElementById('back-to-menu');
const playAgainBtn = document.getElementById('play-again');
const returnToMenuBtn = document.getElementById('return-to-menu');
const winnerOverlay = document.getElementById('winner-overlay');
const winnerText = document.getElementById('winner-text');
const moveHistory = document.getElementById('move-history');
const animationToggle = document.getElementById('animation-toggle');
const soundToggle = document.getElementById('sound-toggle');
const playerWhiteBtn = document.getElementById('btn-player-white');
const playerBlackBtn = document.getElementById('btn-player-black');

// Statistics elements
const statsElements = {
    totalGames: document.getElementById('total-games'),
    playerWins: document.getElementById('player-wins'),
    aiWins: document.getElementById('ai-wins'),
    draws: document.getElementById('draws'),
    winRate: document.getElementById('win-rate')
};

// Game configuration
const BOARD_SIZE = 8;
const SQUARE_SIZE = 60; // ขนาดของช่องบนกระดาน

// เริ่มเกม
function initGame() {
    try {
        console.log('Initializing Checkers game...');
        
        // สร้าง sessionId
        gameState.sessionId = generateSessionId();
        
        // ตั้งค่าโหมด AI จาก URL parameters (ถ้ามี)
        const urlParams = new URLSearchParams(window.location.search);
        const aiParam = urlParams.get('ai');
        if (aiParam !== null) {
            gameState.aiMode = parseInt(aiParam);
        }
        
        // โหลดค่าพรีเฟอเรนซ์จาก localStorage
        loadPreferences();
        
        // เริ่มเกมใหม่
        startNewGame();
        
        // โหลดสถิติ
        loadGameStats();
        
        // ตั้งค่า event listeners
        setupEventListeners();
        
        console.log('Checkers game initialized successfully');
    } catch (error) {
        console.error('Error initializing Checkers game:', error);
        showErrorMessage('เกิดข้อผิดพลาดในการโหลดเกม โปรดรีเฟรชหน้า');
    }
}

// โหลดค่าพรีเฟอเรนซ์จาก localStorage
function loadPreferences() {
    // โหลดการตั้งค่าแอนิเมชัน
    if (localStorage.getItem('checkersAnimationsEnabled') !== null) {
        gameState.animationsEnabled = localStorage.getItem('checkersAnimationsEnabled') === 'true';
        updateAnimationToggle();
    }
    
    // โหลดการตั้งค่าเสียง
    if (localStorage.getItem('checkersSoundEnabled') !== null) {
        gameState.soundEnabled = localStorage.getItem('checkersSoundEnabled') === 'true';
        updateSoundToggle();
    }
}

// อัปเดตปุ่มเปิด/ปิดแอนิเมชัน
function updateAnimationToggle() {
    if (animationToggle) {
        animationToggle.textContent = gameState.animationsEnabled ? 
            '✨ เอฟเฟกต์: เปิด' : '✨ เอฟเฟกต์: ปิด';
    }
    
    // เพิ่มหรือลบคลาสสำหรับแอนิเมชัน
    document.body.classList.toggle('animations-disabled', !gameState.animationsEnabled);
}

// อัปเดตปุ่มเปิด/ปิดเสียง
function updateSoundToggle() {
    if (soundToggle) {
        soundToggle.textContent = gameState.soundEnabled ? '🔊' : '🔇';
    }
}

// เปิด/ปิดแอนิเมชัน
function toggleAnimations() {
    gameState.animationsEnabled = !gameState.animationsEnabled;
    updateAnimationToggle();
    
    // บันทึกค่าพรีเฟอเรนซ์
    localStorage.setItem('checkersAnimationsEnabled', gameState.animationsEnabled.toString());
}

// เปิด/ปิดเสียง
function toggleSound() {
    gameState.soundEnabled = !gameState.soundEnabled;
    updateSoundToggle();
    
    // บันทึกค่าพรีเฟอเรนซ์
    localStorage.setItem('checkersSoundEnabled', gameState.soundEnabled.toString());
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
        const audio = new Audio(SOUNDS[soundName]);
        audio.play().catch(err => console.warn('Sound play error:', err));
    } catch (error) {
        console.warn(`Error playing sound ${soundName}:`, error);
    }
}

// สร้างกระดานเกม
function createBoard() {
    if (!gameBoard) return;
    
    // ล้างกระดานเดิม
    gameBoard.innerHTML = '';
    
    // สร้างกระดานใหม่
    for (let row = 0; row < BOARD_SIZE; row++) {
        for (let col = 0; col < BOARD_SIZE; col++) {
            const square = document.createElement('div');
            const isLight = (row + col) % 2 === 0;
            
            // กำหนด class ตามสีของช่อง (สลับสีขาว-ดำ)
            square.className = `aspect-square relative ${isLight ? 'bg-board-light' : 'bg-board-dark'}`;
            square.dataset.row = row;
            square.dataset.col = col;
            
            // เพิ่มไปที่กระดาน
            gameBoard.appendChild(square);
        }
    }
    
    // สร้างหมากบนกระดาน
    if (gameState.board) {
        updateBoard();
    }
}

// อัปเดตกระดานจากสถานะเกม
function updateBoard() {
    if (!gameBoard || !gameState.board) return;
    
    // Reset all squares
    const squares = gameBoard.querySelectorAll('div');
    squares.forEach(square => {
        // เก็บ class สีของช่องไว้
        const isLight = square.classList.contains('bg-board-light');
        square.className = `aspect-square relative ${isLight ? 'bg-board-light' : 'bg-board-dark'}`;
        
        // ล้างหมาก
        const piece = square.querySelector('.piece');
        if (piece) {
            square.removeChild(piece);
        }
    });
    
    // ใส่หมากตามสถานะเกม
    for (let row = 0; row < BOARD_SIZE; row++) {
        for (let col = 0; col < BOARD_SIZE; col++) {
            const pieceType = gameState.board[row][col];
            if (pieceType !== 0) {
                const square = getSquare(row, col);
                
                if (square) {
                    // สร้างหมาก
                    const piece = document.createElement('div');
                    
                    // กำหนดประเภทของหมาก
                    const isWhite = pieceType === 1 || pieceType === 3;
                    const isKing = pieceType === 3 || pieceType === 4;
                    
                    piece.className = `piece ${isWhite ? 'piece-white' : 'piece-black'} ${isKing ? 'king' : ''}`;
                    
                    // เพิ่มหมากลงในช่อง
                    square.appendChild(piece);
                    
                    // เพิ่ม class ถ้าเป็นหมากที่ถูกเลือก
                    if (gameState.selectedPiece && 
                        gameState.selectedPiece.row === row && 
                        gameState.selectedPiece.col === col) {
                        square.classList.add('piece-selected');
                    }
                }
            }
        }
    }
    
    // แสดงช่องที่สามารถเดินได้
    if (gameState.selectedPiece && gameState.validMoves) {
        Object.entries(gameState.validMoves).forEach(([key, moveInfo]) => {
            const [toRow, toCol] = key.split(',').map(Number);
            const square = getSquare(toRow, toCol);
            if (square) {
                square.classList.add('valid-move');
            }
        });
    }
    
    // ถ้าแอนิเมชันถูกปิด ให้เพิ่ม class ให้กับ body
    document.body.classList.toggle('animations-disabled', !gameState.animationsEnabled);
}

// อัปเดตข้อความสถานะเกม
function updateGameStatus() {
    if (!gameStatus) return;
    
    let statusText = '';
    
    if (gameState.gameOver) {
        if (gameState.winner === 'player') {
            statusText = '<span class="text-green-500">คุณชนะ!</span> ';
        } else if (gameState.winner === 'ai') {
            statusText = '<span class="text-red-500">AI ชนะ!</span> ';
        } else {
            statusText = '<span class="text-yellow-500">เสมอ!</span> ';
        }
    } else {
        if (gameState.playerTurn) {
            statusText = 'ตาของคุณ';
        } else {
            statusText = 'AI กำลังคิด...';
        }
    }
    
    gameStatus.innerHTML = statusText;
}

// แสดง overlay ผู้ชนะ
function showWinnerOverlay(message) {
    if (winnerText && winnerOverlay) {
        winnerText.innerHTML = message;
        winnerOverlay.classList.remove('hidden');
    }
}

// ซ่อน overlay ผู้ชนะ
function hideWinnerOverlay() {
    if (winnerOverlay) {
        winnerOverlay.classList.add('hidden');
    }
}

// เริ่มเกมใหม่
function startNewGame() {
    try {
        // ดำเนินการด้วยค่า AI mode ปัจจุบัน
        const data = {
            ai_mode: gameState.aiMode,
            session_id: gameState.sessionId,
            player_color: gameState.playerColor
        };
        
        // แสดงสถานะการโหลด
        updateLoadingState(true);
        
        // ส่งคำขอไปยัง API
        fetch('/api/checkers/new_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            // ตั้งค่าสถานะเกมใหม่
            gameState.board = data.board;
            gameState.playerTurn = data.player_turn;
            gameState.gameOver = false;
            gameState.winner = null;
            gameState.selectedPiece = null;
            gameState.validMoves = {};
            
            // อัปเดตกระดานและสถานะ
            createBoard();
            updateGameStatus();
            updateBoard();
            
            // ล้างประวัติการเคลื่อนที่หากมี
            if (moveHistory) {
                moveHistory.innerHTML = '<div class="text-center p-2 text-gray-400">ยังไม่มีการเคลื่อนที่</div>';
            }
            
            // ซ่อน overlay
            hideWinnerOverlay();
            
            // เพิ่มข้อมูลใน log
            console.log('เริ่มเกมใหม่:', data);
        })
        .catch(error => {
            console.error('Error starting new game:', error);
            showErrorMessage('เกิดข้อผิดพลาดในการเริ่มเกมใหม่');
        })
        .finally(() => {
            updateLoadingState(false);
        });
    } catch (error) {
        console.error('Error in startNewGame:', error);
        showErrorMessage('เกิดข้อผิดพลาดในการเริ่มเกมใหม่');
        updateLoadingState(false);
    }
}

// จัดการคลิกที่ช่องบนกระดาน
function handleSquareClick(event) {
    // ตรวจสอบว่ากำลังโหลดอยู่หรือไม่
    if (gameState.isLoading || gameState.gameOver || !gameState.playerTurn) {
        return;
    }
    
    const square = event.target.closest('[data-row]');
    if (!square) return;
    
    const row = parseInt(square.dataset.row);
    const col = parseInt(square.dataset.col);
    
    // ตรวจสอบว่าเป็นช่องที่มีหมากที่เลือกได้หรือไม่
    if (gameState.selectedPiece) {
        // ถ้ามีหมากที่เลือกอยู่แล้ว ให้ตรวจสอบว่าคลิกที่ช่องที่เดินได้หรือไม่
        const key = `${row},${col}`;
        
        if (gameState.validMoves && gameState.validMoves[key]) {
            // ทำการเคลื่อนที่
            makeMove(
                gameState.selectedPiece.row,
                gameState.selectedPiece.col,
                row,
                col
            );
        } else if (gameState.board[row][col] !== 0) {
            // ถ้าคลิกที่หมากตัวอื่น ให้เปลี่ยนการเลือก (ถ้าเป็นหมากของผู้เล่น)
            const pieceType = gameState.board[row][col];
            const isPlayerPiece = (gameState.playerColor === 'white' && (pieceType === 1 || pieceType === 3)) ||
                              (gameState.playerColor === 'black' && (pieceType === 2 || pieceType === 4));
            
            if (isPlayerPiece) {
                selectPiece(row, col);
            }
        } else {
            // คลิกที่ช่องว่างที่เดินไม่ได้ ให้ยกเลิกการเลือก
            clearSelection();
        }
    } else {
        // ถ้ายังไม่มีหมากที่เลือก ให้เลือกหมากถ้าคลิกที่หมากของผู้เล่น
        const pieceType = gameState.board[row][col];
        if (pieceType === 0) return; // ไม่มีหมาก
        
        const isPlayerPiece = (gameState.playerColor === 'white' && (pieceType === 1 || pieceType === 3)) ||
                          (gameState.playerColor === 'black' && (pieceType === 2 || pieceType === 4));
        
        if (isPlayerPiece) {
            selectPiece(row, col);
        }
    }
}

// เลือกหมาก
function selectPiece(row, col) {
    // ตรวจสอบว่ากำลังโหลดอยู่หรือไม่
    if (gameState.isLoading) return;
    
    // เล่นเสียงเลือก
    playSound('select');
    
    // ล้างการเลือกเดิม
    clearSelection();
    
    // บันทึกหมากที่เลือก
    gameState.selectedPiece = { row, col };
    
    // ขอการเคลื่อนที่ที่ถูกต้อง
    getValidMoves(row, col);
    
    // อัปเดตสถานะบนกระดาน
    updateBoard();
}

// ล้างการเลือก
function clearSelection() {
    gameState.selectedPiece = null;
    gameState.validMoves = {};
    
    // ล้าง class piece-selected ออกจากทุกช่อง
    const squares = gameBoard.querySelectorAll('.piece-selected, .valid-move');
    squares.forEach(square => {
        square.classList.remove('piece-selected');
        square.classList.remove('valid-move');
    });
}

// รับช่องจากตำแหน่ง
function getSquare(row, col) {
    return gameBoard.querySelector(`[data-row="${row}"][data-col="${col}"]`);
}

// ขอการเคลื่อนที่ที่ถูกต้องจาก API
function getValidMoves(row, col) {
    // ตรวจสอบว่ากำลังโหลดอยู่หรือไม่
    if (gameState.isLoading) return;
    
    updateLoadingState(true);
    
    fetch('/api/checkers/valid_moves', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
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
            throw new Error(data.error);
        }
        
        gameState.validMoves = data.valid_moves;
        updateBoard();
    })
    .catch(error => {
        console.error('Error getting valid moves:', error);
        showErrorMessage('ไม่สามารถดึงข้อมูลการเคลื่อนที่ที่ถูกต้องได้');
        clearSelection();
    })
    .finally(() => {
        updateLoadingState(false);
    });
}

// ทำการเคลื่อนที่
function makeMove(fromRow, fromCol, toRow, toCol) {
    // ตรวจสอบว่ากำลังโหลดอยู่หรือไม่
    if (gameState.isLoading) return;
    
    updateLoadingState(true);
    
    fetch('/api/checkers/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: gameState.sessionId,
            from_row: fromRow,
            from_col: fromCol,
            to_row: toRow,
            to_col: toCol
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        
        // เล่นเสียงตามการเคลื่อนที่
        if (data.captured) {
            playSound('capture');
        } else {
            playSound('move');
        }
        
        // อัปเดตสถานะเกม
        gameState.board = data.board;
        gameState.playerTurn = data.player_turn;
        gameState.gameOver = data.game_over;
        gameState.winner = data.winner;
        
        // อัปเดตประวัติการเคลื่อนที่
        if (moveHistory && data.last_move) {
            // ลบข้อความ "ยังไม่มีการเคลื่อนที่" ถ้ามี
            if (moveHistory.querySelector('.text-gray-400')) {
                moveHistory.innerHTML = '';
            }
            
            const moveEntry = document.createElement('div');
            moveEntry.className = 'p-1 border-b border-gray-700';
            
            // แปลง row, col เป็นตำแหน่งแบบหมากฮอต (เช่น A1, B2)
            const cols = 'ABCDEFGH';
            const fromPosition = `${cols[fromCol]}${8-fromRow}`;
            const toPosition = `${cols[toCol]}${8-toRow}`;
            
            const playerName = data.last_move.player === 'player' ? 'คุณ' : 'AI';
            const captureText = data.captured ? ' กิน! ' : '';
            
            moveEntry.innerHTML = `<span class="${data.last_move.player === 'player' ? 'text-blue-400' : 'text-red-400'}">${playerName}</span>: ${fromPosition} → ${toPosition}${captureText}`;
            
            moveHistory.insertBefore(moveEntry, moveHistory.firstChild);
        }
        
        // ล้างการเลือก
        clearSelection();
        
        // อัปเดตกระดานและสถานะ
        updateBoard();
        updateGameStatus();
        
        // ถ้าเกมจบแล้ว ให้แสดง overlay
        if (data.game_over) {
            let winMessage = '';
            if (data.winner === 'player') {
                winMessage = '<span class="text-green-500 text-2xl">คุณชนะ! </span><br>ยินดีด้วย!';
                playSound('win');
            } else if (data.winner === 'ai') {
                winMessage = '<span class="text-red-500 text-2xl">AI ชนะ! </span><br>ลองอีกครั้ง!';
                playSound('lose');
            } else {
                winMessage = '<span class="text-yellow-500 text-2xl">เสมอ! </span><br>เกมที่สูสี!';
            }
            
            // อัปเดตสถิติการเล่น
            loadGameStats();
            
            // แสดง overlay ผู้ชนะ
            setTimeout(() => {
                showWinnerOverlay(winMessage);
            }, 500);
        }
    })
    .catch(error => {
        console.error('Error making move:', error);
        showErrorMessage('ไม่สามารถทำการเคลื่อนที่ได้');
        clearSelection();
    })
    .finally(() => {
        updateLoadingState(false);
    });
}

// โหลดสถิติเกม
function loadGameStats() {
    fetch('/api/get_stats?game_type=Checkers')
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
}

// เริ่มต้นเกมเมื่อโหลดหน้าเสร็จ
document.addEventListener('DOMContentLoaded', initGame);
