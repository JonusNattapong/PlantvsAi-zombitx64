# Tictactoe-zombitx64

เกมกระดานที่มี AI หลายรูปแบบให้เล่นต่อสู้ด้วย

## เกมที่มีให้เล่น

1. **Tic Tac Toe** - เกม XO แบบคลาสสิก
2. **Connect Four** - เกมต่อเรียง 4
3. **Checkers** - เกมหมากฮอส
4. **Chess** - เกมหมากรุกสากล
5. **Poker** - เกมไพ่โป๊กเกอร์

## อัลกอริทึม AI ที่ใช้

1. **Minimax with Alpha-Beta Pruning** - อัลกอริทึมการค้นหาแบบรอบด้านที่มีการตัดแขนงที่ไม่จำเป็น
2. **Pattern Recognition** - การจดจำรูปแบบการเล่นและตอบโต้ตามรูปแบบที่เคยพบ
3. **Q-Learning** - อัลกอริทึมการเรียนรู้แบบเสริมกำลัง (Reinforcement Learning)
4. **Neural Network** - การใช้เครือข่ายประสาทเทียมในการประเมินสถานการณ์
5. **MCTS (Monte Carlo Tree Search)** - การสุ่มจำลองเกมจำนวนมากเพื่อหาทางเล่นที่ดีที่สุด
6. **Genetic Algorithm** - อัลกอริทึมเชิงวิวัฒนาการที่ปรับปรุงกลยุทธ์ด้วยการสุ่มกลายพันธุ์และการคัดเลือก

## การติดตั้ง

```bash
# Clone repository
git clone https://github.com/yourusername/tictactoe-zombitx64.git
cd tictactoe-zombitx64

# สร้างสภาพแวดล้อมเสมือน
python -m venv venv
source venv/bin/activate  # สำหรับ Unix/MacOS
venv\Scripts\activate  # สำหรับ Windows

# ติดตั้ง dependencies
pip install -r requirements.txt

# รันแอปพลิเคชัน
python app.py
```

จากนั้นเข้าไปที่ http://localhost:5000 ในเว็บเบราว์เซอร์เพื่อเริ่มเล่นเกม

## การใช้งาน

1. เลือกเกมที่ต้องการเล่นจากหน้าหลัก
2. เลือกอัลกอริทึม AI ที่ต้องการเล่นด้วย
3. เล่นเกมตามกติกาของแต่ละเกม
4. สถิติการเล่นจะถูกบันทึกไว้และแสดงผลในหน้าเกม

## License

MIT