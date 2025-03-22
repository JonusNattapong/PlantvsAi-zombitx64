# API ของเกมโป๊กเกอร์

เอกสารนี้อธิบาย API สำหรับเกมโป๊กเกอร์ใน Tictactoe-zombitx64

## RESTful API Endpoints

เกมโป๊กเกอร์ใช้ RESTful API ในการสื่อสารระหว่าง frontend และ backend โดยมี endpoints ดังนี้

### 1. เริ่มเกมใหม่

```
POST /api/poker/new_game
```

เริ่มเกมโป๊กเกอร์ใหม่และสร้าง session ID

**Request Body**: ไม่มี

**Response**:

```json
{
  "session_id": "unique-session-id",
  "status": "success",
  "message": "New game started",
  "game_state": {
    // ข้อมูลสถานะเกม
  }
}
```

### 2. ดึงสถานะเกม

```
GET /api/poker/game_state
```

ดึงสถานะปัจจุบันของเกม

**Request Parameters**:
- `session_id`: ID ของเซสชันเกม

**Response**:

```json
{
  "status": "success",
  "game_state": {
    "pot": 150,
    "current_bet": 50,
    "community_cards": ["2H", "KC", "AD", "9S", "QH"],
    "player": {
      "hand": ["AS", "KH"],
      "chips": 950,
      "bet": 50,
      "is_current_player": true
    },
    "ai_player": {
      "hand": [],  // ไม่เปิดเผยไพ่ของ AI
      "chips": 850,
      "bet": 100
    },
    "current_player": "player",
    "stage": "river",
    "actions": ["check", "bet", "fold"],
    "logs": [
      "Player raises to 50",
      "AI calls 50"
    ]
  }
}
```

### 3. ดำเนินการของผู้เล่น

```
POST /api/poker/action
```

ส่งการกระทำของผู้เล่นไปยังเซิร์ฟเวอร์

**Request Body**:

```json
{
  "session_id": "unique-session-id",
  "action": "raise",
  "amount": 100  // เฉพาะกรณี raise
}
```

**Response**:

```json
{
  "status": "success",
  "message": "Action processed",
  "game_state": {
    // ข้อมูลสถานะเกมที่อัปเดตแล้ว
  },
  "ai_action": {
    "action": "call",
    "amount": 100
  }
}
```

### 4. เริ่มมือใหม่

```
POST /api/poker/new_hand
```

เริ่มมือใหม่หลังจากจบมือปัจจุบัน

**Request Body**:

```json
{
  "session_id": "unique-session-id"
}
```

**Response**:

```json
{
  "status": "success",
  "message": "New hand started",
  "game_state": {
    // ข้อมูลสถานะเกมที่อัปเดตแล้ว
  }
}
```

### 5. ดึงสถิติ

```
GET /api/poker/stats
```

ดึงสถิติการเล่นเกม

**Request Parameters**:
- `session_id`: ID ของเซสชันเกม

**Response**:

```json
{
  "status": "success",
  "stats": {
    "hands_played": 10,
    "hands_won": 6,
    "hands_lost": 4,
    "biggest_pot": 500,
    "biggest_win": 300,
    "biggest_hand": "Flush",
    "chips_history": [1000, 1100, 950, 1200, 800, 1300]
  }
}
```

## โครงสร้างข้อมูล

### Game State Object

Game State object ประกอบด้วยข้อมูลต่อไปนี้:

- `pot`: จำนวนชิปทั้งหมดในหม้อ
- `current_bet`: การเดิมพันปัจจุบันบนโต๊ะ
- `community_cards`: ไพ่กลางที่เปิด (อาเรย์ของรหัสไพ่)
- `player`: ข้อมูลของผู้เล่น
  - `hand`: ไพ่ในมือของผู้เล่น
  - `chips`: จำนวนชิปที่เหลือ
  - `bet`: จำนวนชิปที่ผู้เล่นเดิมพันในรอบนี้
  - `is_current_player`: เป็น true ถ้าเป็นตาของผู้เล่น
- `ai_player`: ข้อมูลของผู้เล่น AI
  - `hand`: ไพ่ในมือของ AI (จะว่างเปล่าจนกว่าจะถึงรอบ showdown)
  - `chips`: จำนวนชิปที่เหลือ
  - `bet`: จำนวนชิปที่ AI เดิมพันในรอบนี้
- `current_player`: ผู้เล่นปัจจุบัน ("player" หรือ "ai")
- `stage`: สถานะของเกม ("preflop", "flop", "turn", "river", "showdown")
- `actions`: การกระทำที่เป็นไปได้สำหรับผู้เล่นปัจจุบัน
- `logs`: บันทึกการกระทำที่เกิดขึ้นในเกม

### Card Format

รหัสไพ่ประกอบด้วยอักขระสองตัว:
- อักขระแรกแทนค่าของไพ่: 2-9, T (10), J (Jack), Q (Queen), K (King), A (Ace)
- อักขระที่สองแทนดอกของไพ่: H (Heart), C (Club), D (Diamond), S (Spade)

ตัวอย่างเช่น:
- "AH" = Ace of Hearts
- "2C" = 2 of Clubs
- "KD" = King of Diamonds
- "9S" = 9 of Spades

## รหัสสถานะและข้อผิดพลาด

API ใช้รหัสสถานะ HTTP มาตรฐานร่วมกับข้อความข้อผิดพลาดในรูปแบบ JSON:

- `200 OK`: คำขอสำเร็จ
- `400 Bad Request`: คำขอไม่ถูกต้อง (เช่น ส่งพารามิเตอร์ที่จำเป็นไม่ครบ)
- `404 Not Found`: ไม่พบทรัพยากรที่ร้องขอ (เช่น session_id ไม่ถูกต้อง)
- `500 Internal Server Error`: เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์

ตัวอย่างการตอบกลับข้อผิดพลาด:

```json
{
  "status": "error",
  "message": "Invalid session ID",
  "error_code": "SESSION_NOT_FOUND"
}
```

## ตัวอย่างการใช้งาน

ตัวอย่างการใช้ API ด้วย JavaScript Fetch API:

```javascript
// เริ่มเกมใหม่
async function startNewGame() {
  const response = await fetch('/api/poker/new_game', {
    method: 'POST',
  });
  const data = await response.json();
  localStorage.setItem('session_id', data.session_id);
  updateGameUI(data.game_state);
}

// ส่งการกระทำของผู้เล่น
async function sendPlayerAction(action, amount = null) {
  const session_id = localStorage.getItem('session_id');
  const requestBody = {
    session_id: session_id,
    action: action
  };
  
  if (amount !== null) {
    requestBody.amount = amount;
  }
  
  const response = await fetch('/api/poker/action', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestBody)
  });
  
  const data = await response.json();
  updateGameUI(data.game_state);
  
  // แสดงการกระทำของ AI
  if (data.ai_action) {
    displayAIAction(data.ai_action);
  }
} 