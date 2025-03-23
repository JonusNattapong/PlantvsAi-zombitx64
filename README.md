# PlantvsAi เกมกระดานที่มี AI หลายรูปแบบให้เล่นต่อสู้ด้วย

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-orange)](https://flask.palletsprojects.com/)

## เกมที่มีให้เล่น

1. **Tic Tac Toe** - เกม XO แบบคลาสสิก
2. **Connect Four** - เกมต่อเรียง 4
3. **Checkers** - เกมหมากฮอส
4. **Chess** - เกมหมากรุกสากล
5. **Poker** - เกมไพ่โป๊กเกอร์ (Texas Hold'em)

## อัลกอริทึม AI ที่ใช้

1. **Minimax with Alpha-Beta Pruning** - อัลกอริทึมการค้นหาแบบรอบด้านที่มีการตัดแขนงที่ไม่จำเป็น
2. **Pattern Recognition** - การจดจำรูปแบบการเล่นและตอบโต้ตามรูปแบบที่เคยพบ
3. **Q-Learning** - อัลกอริทึมการเรียนรู้แบบเสริมกำลัง (Reinforcement Learning)
4. **Neural Network** - การใช้เครือข่ายประสาทเทียมในการประเมินสถานการณ์
5. **MCTS (Monte Carlo Tree Search)** - การสุ่มจำลองเกมจำนวนมากเพื่อหาทางเล่นที่ดีที่สุด
6. **Genetic Algorithm** - อัลกอริทึมเชิงวิวัฒนาการที่ปรับปรุงกลยุทธ์ด้วยการสุ่มกลายพันธุ์และการคัดเลือก
7. **ZomPokerX64** - โมเดล AI ขั้นสูงสำหรับเกมโป๊กเกอร์ที่ใช้ Machine Learning และ Neural Networks

## คุณสมบัติเกม Poker (Texas Hold'em)

1. **ระบบ AI ขั้นสูง**:
   - 5 ระดับความยากของ AI
   - การเรียนรู้แบบเสริมกำลัง (Reinforcement Learning)
   - การวิเคราะห์รูปแบบการเล่นของผู้เล่น
   - การประเมินความแข็งแกร่งของมือไพ่

2. **อินเทอร์เฟซที่ทันสมัย**:
   - ดีไซน์ทันสมัยด้วย Tailwind CSS
   - การแสดงผลไพ่แบบ 3D
   - ระบบเสียงเอฟเฟกต์
   - สถิติเกมแบบเรียลไทม์

3. **ฟีเจอร์เกม**:
   - การเดิมพันแบบหลายระดับ
   - การแสดงผลมือไพ่ที่ดีที่สุด
   - ประวัติการเดิมพัน
   - บันทึกเกมแบบเรียลไทม์
   - สถิติการเล่น

4. **ระบบเสียง**:
   - เสียงเอฟเฟกต์เมื่อมีการกระทำ
   - เสียงไพ่เมื่อแจกไพ่
   - เสียงชิปเมื่อวางเดิมพัน
   - เสียงชัยชนะ/แพ้

## โครงสร้างโปรเจค

```
PlantvsAi-zombitx64/
├── src/                    # โค้ดหลักของโปรเจค
├── tests/                  # การทดสอบ
├── docs/                   # เอกสารประกอบ
│   ├── api/                # เอกสาร API
│   ├── architecture/       # เอกสารสถาปัตยกรรม
│   └── user-guide/         # คู่มือการใช้งาน
├── static/                 # ไฟล์สถิต (CSS, JS, Images)
│   ├── css/                # ไฟล์ CSS
│   ├── js/                 # ไฟล์ JavaScript
│   ├── sounds/             # เสียงเอฟเฟกต์
│   └── svg_cards/          # ไฟล์ภาพ SVG ของไพ่
├── templates/              # เทมเพลต HTML
├── app.py                  # แอปพลิเคชัน Flask หลัก
├── .env.example            # ตัวอย่างไฟล์ environment variables
├── .gitignore              # ไฟล์ที่ git ควรเพิกเฉย
├── .editorconfig           # การกำหนดค่าสำหรับเครื่องมือแก้ไข
├── .pre-commit-config.yaml # การกำหนดค่า pre-commit hooks
├── CHANGELOG.md            # ประวัติการเปลี่ยนแปลง
├── CODE_OF_CONDUCT.md      # จรรยาบรรณของผู้มีส่วนร่วม
├── CONTRIBUTING.md         # คู่มือการมีส่วนร่วม
├── LICENSE                 # ข้อตกลงใบอนุญาต
├── Makefile                # คำสั่งทั่วไปสำหรับโปรเจค
├── pyproject.toml          # การกำหนดค่าโปรเจค Python
├── pytest.ini              # การกำหนดค่า pytest
├── README.md               # ไฟล์ README นี้
├── requirements.txt        # dependencies หลัก
├── requirements-dev.txt    # dependencies สำหรับการพัฒนา
└── setup.py                # สคริปต์การติดตั้ง
```

## การติดตั้ง

สามารถใช้ได้สองวิธี:

### วิธีที่ 1: ใช้ Makefile (แนะนำ)

```bash
# Clone repository
git clone https://github.com/JonusNattapong/PlantvsAi-zombitx64.git
cd PlantvsAi-zombitx64

# ติดตั้งและตั้งค่าสภาพแวดล้อม
make setup

# เปิดใช้งานสภาพแวดล้อมเสมือน
# สำหรับ Unix/MacOS:
source venv/bin/activate
# สำหรับ Windows:
venv\Scripts\activate

# รันเซิร์ฟเวอร์
make server
```

### วิธีที่ 2: ใช้คำสั่งทั่วไป

```bash
# Clone repository
git clone https://github.com/JonusNattapong/PlantvsAi-zombitx64.git
cd PlantvsAi-zombitx64

# ติดตั้ง dependencies
pip install -r requirements.txt

# รันเซิร์ฟเวอร์
python app.py
```

## วิธีการเล่น Poker

1. เลือกระดับความยากของ AI (0-4)
2. เริ่มเกมใหม่
3. ระบบจะแจกไพ่ให้ผู้เล่นและ AI
4. ผู้เล่นสามารถ:
   - ตรวจสอบ (Check) - ถ้าไม่มีการเดิมพันก่อนหน้านี้
   - เรียก (Call) - ตามการเดิมพันที่มีอยู่
   - เพิ่ม (Raise) - เพิ่มการเดิมพัน
   - พับ (Fold) - ออกจากเกมรอบนี้
5. ระบบจะแสดงผลมือไพ่ที่ดีที่สุดของผู้เล่นและ AI
6. ผู้เล่นที่มีมือไพ่ดีกว่าจะชนะและได้รับชิป

## รายละเอียดการตั้งค่า AI

- **ระดับ 0 (ง่าย)**: ใช้ยุทธศาสตร์ง่ายๆ ในการตัดสินใจ
- **ระดับ 1 (ปานกลาง)**: ใช้ความน่าจะเป็นในการตัดสินใจ
- **ระดับ 2 (ยาก)**: ใช้โมเดล Machine Learning
- **ระดับ 3 (ผู้เชี่ยวชาญ)**: ใช้ Reinforcement Learning
- **ระดับ 4 (ผู้เชี่ยวชาญขั้นสูง)**: ใช้ Advanced Self-Learning

## การมีส่วนร่วมในโปรเจค

เรายินดีต้อนรับการมีส่วนร่วมจากทุกคน! โปรดดูที่ [CONTRIBUTING.md](CONTRIBUTING.md) สำหรับรายละเอียดเกี่ยวกับวิธีการมีส่วนร่วม

## จรรยาบรรณ

โปรดอ่านและปฏิบัติตาม [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## ใบอนุญาต

โปรเจคนี้ใช้ใบอนุญาต MIT License - ดูที่ [LICENSE](LICENSE) สำหรับรายละเอียดเพิ่มเติม

## ผู้พัฒนา

- **Jonus Nattapong** - ผู้สร้างและผู้รับผิดชอบหลัก
- **ผู้มีส่วนร่วม** - ดูที่ [CONTRIBUTORS.md](CONTRIBUTORS.md)

## รับการอัพเดท

ติดตามการพัฒนาและอัพเดทล่าสุดได้ที่:
- [GitHub Repository](https://github.com/JonusNattapong/PlantvsAi-zombitx64)
- [Twitter](https://twitter.com/jonusnattapong)
- [Discord](https://discord.gg/your-invite)

## การสนับสนุน

หากคุณพบปัญหาหรือต้องการความช่วยเหลือ โปรด:
1. เปิด Issue ใน GitHub
2. ติดต่อผ่าน Discord
3. อีเมล: jonus.nattapong@example.com

## ข้อตกลงการใช้งาน

การใช้งานโปรเจคนี้ถือว่าคุณยอมรับ:
- ข้อตกลงใบอนุญาต MIT
- จรรยาบรรณของผู้มีส่วนร่วม
- นโยบายความเป็นส่วนตัว

## ข้อมูลเพิ่มเติม

- [เอกสาร API](docs/api/)
- [คู่มือการใช้งาน](docs/user-guide/)
- [เอกสารสถาปัตยกรรม](docs/architecture/)

## รุ่นปัจจุบัน

- **เวอร์ชัน**: 1.0.0
- **วันที่**: 2025-03-23
- **การเปลี่ยนแปลงหลัก**:
  - เพิ่มเกม Poker (Texas Hold'em)
  - ปรับปรุงอินเทอร์เฟซทั้งหมดให้ทันสมัยด้วย Tailwind CSS
  - เพิ่มระบบ AI ขั้นสูงสำหรับเกม Poker
  - ปรับปรุงระบบเสียงเอฟเฟกต์
  - เพิ่มสถิติเกมแบบเรียลไทม์
