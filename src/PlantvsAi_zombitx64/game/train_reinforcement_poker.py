from PlantvsAi_zombitx64.game.reinforcement_poker_model import ReinforcementPokerModel, AdvancedSelfLearningModel
from PlantvsAi_zombitx64.game.poker_model import PokerModel
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='ฝึกฝนโมเดลโป๊กเกอร์ด้วย Reinforcement Learning')
    parser.add_argument('--model', type=str, choices=['reinforcement', 'advanced'], 
                      default='reinforcement', help='เลือกโมเดลที่จะฝึกฝน')
    parser.add_argument('--games', type=int, default=5000, 
                      help='จำนวนเกมที่ใช้ในการฝึกฝน')
    parser.add_argument('--self-play', action='store_true', 
                      help='ฝึกฝนด้วยการเล่นกับตัวเองหรือไม่')
    parser.add_argument('--load', action='store_true', 
                      help='โหลดโมเดลที่มีอยู่หรือไม่')
    
    args = parser.parse_args()
    
    # สร้างโฟลเดอร์สำหรับเก็บข้อมูล
    os.makedirs('DatasetPokerzombitx64', exist_ok=True)
    
    # สร้างโมเดลตามที่เลือก
    if args.model == 'reinforcement':
        model = ReinforcementPokerModel()
        model_filename = 'reinforcement_poker_model.safetensors'
        print("===== เทรนโมเดลโป๊กเกอร์แบบ Reinforcement Learning =====")
    else:
        model = AdvancedSelfLearningModel()
        model_filename = 'advanced_poker_model.safetensors'
        print("===== เทรนโมเดลโป๊กเกอร์แบบ Advanced Self-Learning =====")
    
    # โหลดโมเดลหากต้องการ
    if args.load:
        success = model.load_model(model_filename)
        if success:
            print(f"โหลดโมเดลจาก {model_filename} สำเร็จ")
        else:
            print(f"ไม่สามารถโหลดโมเดลได้ จะสร้างโมเดลใหม่แทน")
            model.build_model()
    else:
        print("สร้างโมเดลใหม่")
        model.build_model()
    
    # เลือกวิธีการฝึกฝน
    if args.self_play:
        print(f"เริ่มการฝึกฝนด้วยการเล่นกับตัวเอง จำนวน {args.games} เกม")
        model.train_self_play(num_games=args.games)
    else:
        # ฝึกฝนกับโมเดลอื่น
        print(f"เริ่มการฝึกฝนกับโมเดลพื้นฐาน จำนวน {args.games} เกม")
        
        # สร้างโมเดลคู่ต่อสู้
        opponent = PokerModel()
        opponent_path = os.path.join('DatasetPokerzombitx64', 'poker_model.safetensors')
        
        if os.path.exists(opponent_path):
            print("โหลดโมเดลคู่ต่อสู้จากไฟล์ที่มีอยู่")
            opponent.load_model('poker_model.safetensors')
        else:
            print("สร้างโมเดลคู่ต่อสู้ใหม่")
            opponent.build_model()
        
        # เริ่มการฝึกฝน
        if isinstance(model, AdvancedSelfLearningModel):
            model.train_with_opponent(opponent, num_games=args.games)
        else:
            # สำหรับโมเดลพื้นฐานที่ไม่มีเมธอด train_with_opponent
            model.train_self_play(num_games=args.games)
    
    print(f"การฝึกฝนเสร็จสิ้น โมเดลถูกบันทึกไว้ที่ DatasetPokerzombitx64/{model_filename}")

if __name__ == "__main__":
    main()
