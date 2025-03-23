import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, clone_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import os
import random
from collections import deque
import safetensors.numpy
from PlantvsAi_zombitx64.game.poker_model import PokerModel, Card, PokerHand

class ReinforcementPokerModel(PokerModel):
    """
    เป็นโมเดลที่ใช้ Reinforcement Learning กับเกมโป๊กเกอร์
    สามารถเรียนรู้จากการเล่นจริงได้ด้วยตัวเอง (Self-Learning)
    """
    def __init__(self, lr=0.001, gamma=0.95, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        super().__init__()
        self.lr = lr                  # อัตราการเรียนรู้
        self.gamma = gamma            # ค่าส่วนลดของรางวัลในอนาคต
        self.epsilon = epsilon        # โอกาสในการสุ่มแอคชั่น (สำรวจ)
        self.epsilon_decay = epsilon_decay  # อัตราการลดลงของ epsilon
        self.epsilon_min = epsilon_min      # ค่าต่ำสุดของ epsilon
        self.memory = deque(maxlen=10000)   # หน่วยความจำเก็บประสบการณ์
        self.target_model = None            # โมเดลเป้าหมาย
        
    def build_model(self):
        """สร้างโมเดล Q-Network"""
        # สร้างโมเดลหลัก
        self.model = Sequential([
            Dense(256, activation='relu', input_shape=(14,)),
            Dropout(0.3),
            Dense(128, activation='relu'),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dense(3, activation='linear')  # 3 แอคชั่น: check/call, raise, fold
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=self.lr),
            loss='mse'
        )
        
        # สร้างโมเดลเป้าหมาย (Target Network)
        self.target_model = clone_model(self.model)
        self.target_model.set_weights(self.model.get_weights())
    
    def remember(self, state, action, reward, next_state, done):
        """บันทึกประสบการณ์ลงในหน่วยความจำ"""
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state):
        """เลือกการกระทำโดยใช้นโยบาย epsilon-greedy"""
        if np.random.rand() <= self.epsilon:
            return random.randrange(3)  # สุ่มแอคชั่น (สำรวจ)
        
        q_values = self.model.predict(np.array([state]))[0]
        return np.argmax(q_values)  # เลือกแอคชั่นที่ให้ค่า Q สูงสุด
    
    def replay(self, batch_size=32):
        """เรียนรู้จากประสบการณ์ที่เก็บไว้"""
        if len(self.memory) < batch_size:
            return
        
        # สุ่มตัวอย่างจากหน่วยความจำ
        minibatch = random.sample(self.memory, batch_size)
        
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                # ใช้ Target Network เพื่อลดการสั่นของค่า Q
                target = reward + self.gamma * np.amax(self.target_model.predict(np.array([next_state]))[0])
            
            target_f = self.model.predict(np.array([state]))[0]
            target_f[action] = target
            
            # อัพเดทโมเดล
            self.model.fit(np.array([state]), np.array([target_f]), epochs=1, verbose=0)
        
        # ลดค่า epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def update_target_model(self):
        """อัพเดทโมเดลเป้าหมายให้เหมือนกับโมเดลหลัก"""
        self.target_model.set_weights(self.model.get_weights())
    
    def save_model(self, filename='reinforcement_poker_model.safetensors'):
        """บันทึกโมเดลลงไฟล์"""
        os.makedirs('DatasetPokerzombitx64', exist_ok=True)
        
        # บันทึกค่าพารามิเตอร์
        params = {
            'epsilon': self.epsilon,
            'lr': self.lr,
            'gamma': self.gamma
        }
        
        # บันทึกน้ำหนักโมเดล
        weights = self.model.get_weights()
        weights_dict = {f'layer_{i}': w for i, w in enumerate(weights)}
        
        # รวมข้อมูลทั้งหมด
        save_dict = {**weights_dict, **{f'param_{k}': np.array([v]) for k, v in params.items()}}
        
        # บันทึกในรูปแบบ safetensors
        safetensors.numpy.save_file(save_dict, os.path.join('DatasetPokerzombitx64', filename))
    
    def load_model(self, filename='reinforcement_poker_model.safetensors'):
        """โหลดโมเดลจากไฟล์"""
        path = os.path.join('DatasetPokerzombitx64', filename)
        if not os.path.exists(path):
            print(f"ไม่พบไฟล์โมเดล: {path}")
            return False
            
        # โหลดข้อมูลจาก safetensors
        loaded_dict = safetensors.numpy.load_file(path)
        
        # แยกพารามิเตอร์และน้ำหนัก
        param_keys = [k for k in loaded_dict.keys() if k.startswith('param_')]
        weight_keys = [k for k in loaded_dict.keys() if k.startswith('layer_')]
        
        # อัพเดทพารามิเตอร์
        for key in param_keys:
            param_name = key.replace('param_', '')
            if hasattr(self, param_name):
                setattr(self, param_name, loaded_dict[key][0])
        
        # สร้างโมเดล
        self.build_model()
        
        # อัพเดทน้ำหนัก
        weights = [loaded_dict[f'layer_{i}'] for i in range(len(weight_keys))]
        self.model.set_weights(weights)
        self.target_model.set_weights(weights)
        
        return True

    def train_self_play(self, num_games=1000, update_target_every=100, save_every=500):
        """เทรนโมเดลโดยการเล่นกับตัวเอง (Self-Play)"""
        from PlantvsAi_zombitx64.game.poker import PokerGame
        
        print(f"เริ่มการเรียนรู้ด้วยตัวเองผ่านการเล่น {num_games} เกม...")
        
        for game_num in range(num_games):
            # สร้างเกมใหม่
            game = PokerGame()
            game.start_new_game()
            
            done = False
            total_reward = 0
            
            # เล่นจนจบเกม
            while not done:
                # สถานะปัจจุบัน
                current_state = self._get_state_from_game(game)
                
                # เลือกแอคชั่น
                action_idx = self.act(current_state)
                action = self._idx_to_action(action_idx, game)
                
                # ดำเนินการตามแอคชั่น
                reward, done = self._perform_action(game, action)
                total_reward += reward
                
                # สถานะใหม่
                next_state = self._get_state_from_game(game)
                
                # บันทึกประสบการณ์
                self.remember(current_state, action_idx, reward, next_state, done)
                
                # เรียนรู้จากประสบการณ์
                self.replay()
            
            # อัพเดทโมเดลเป้าหมายทุกๆ n เกม
            if game_num % update_target_every == 0:
                self.update_target_model()
            
            # บันทึกโมเดลทุกๆ n เกม
            if game_num % save_every == 0:
                self.save_model()
            
            # แสดงผลความก้าวหน้า
            if game_num % 100 == 0:
                print(f"เกมที่ {game_num}/{num_games} - รางวัลรวม: {total_reward} - Epsilon: {self.epsilon:.4f}")
        
        # บันทึกโมเดลสุดท้าย
        self.save_model()
        print("การเรียนรู้ด้วยตัวเองเสร็จสิ้น")
    
    def _get_state_from_game(self, game):
        """แปลงสถานะของเกมให้เป็นข้อมูลสำหรับโมเดล"""
        # ตัวอย่าง: สร้างข้อมูลสถานะจากเกม
        # ต้องปรับให้เข้ากับโครงสร้างของเกมจริง
        player_cards = game.player_hand if hasattr(game, 'player_hand') else []
        ai_cards = game.ai_hand if hasattr(game, 'ai_hand') else []
        community = game.community if hasattr(game, 'community') else []
        
        # สร้าง PokerHand
        player_hand = PokerHand([Card(card.suit, card.rank) for card in player_cards])
        ai_hand = PokerHand([Card(card.suit, card.rank) for card in ai_cards])
        community_cards = [Card(card.suit, card.rank) for card in community]
        
        # ประเมินไพ่
        player_features = self.evaluate_hand(player_hand, community_cards)
        ai_features = self.evaluate_hand(ai_hand, community_cards)
        
        # สร้างเวกเตอร์สถานะ
        state = [
            player_features['hand_type'],
            ai_features['hand_type'],
            player_features['highest_rank'],
            ai_features['highest_rank'],
            player_features['lowest_rank'],
            ai_features['lowest_rank'],
            player_features['rank_diff'],
            ai_features['rank_diff'],
            player_features['max_rank_count'],
            ai_features['max_rank_count'],
            player_features['max_suit_count'],
            ai_features['max_suit_count'],
            int(player_features['is_suited']),
            int(ai_features['is_suited'])
        ]
        
        return state
    
    def _idx_to_action(self, action_idx, game):
        """แปลงดัชนีแอคชั่นเป็นการกระทำในเกม"""
        # แปลง index 0, 1, 2 เป็นการกระทำ check/call, raise, fold
        actions = ['call', 'raise', 'fold']
        return actions[action_idx]
    
    def _perform_action(self, game, action):
        """ดำเนินการตามแอคชั่นในเกมและรับรางวัล"""
        # ต้องปรับให้เข้ากับโครงสร้างของเกมจริง
        
        # ดำเนินการตามแอคชั่น
        if action == 'call':
            result = game.check_or_call()
        elif action == 'raise':
            result = game.raise_bet(game.min_raise)
        elif action == 'fold':
            result = game.fold()
        else:
            result = False
        
        # ตรวจสอบว่าเกมจบหรือยัง
        done = game.is_game_over() if hasattr(game, 'is_game_over') else False
        
        # คำนวณรางวัล
        reward = 0
        if done:
            # ถ้าชนะได้รางวัลบวก ถ้าแพ้ได้รางวัลลบ
            if hasattr(game, 'winner') and game.winner == 'player':
                reward = game.pot_size  # รางวัลเท่ากับขนาดของหม้อ
            else:
                reward = -game.pot_size
        else:
            # รางวัลเล็กน้อยสำหรับการอยู่ในเกม
            reward = 0.1
        
        return reward, done

class AdvancedSelfLearningModel(ReinforcementPokerModel):
    """
    โมเดลที่มีการเรียนรู้ขั้นสูงที่ใช้เทคนิค Monte Carlo Tree Search 
    ร่วมกับ Deep Reinforcement Learning เพื่อเพิ่มประสิทธิภาพ
    """
    def __init__(self, lr=0.0005, gamma=0.99, epsilon=1.0, epsilon_decay=0.997, epsilon_min=0.01):
        super().__init__(lr, gamma, epsilon, epsilon_decay, epsilon_min)
        self.prev_states = []  # เก็บประวัติสถานะเพื่อใช้ในการเรียนรู้แบบ Monte Carlo
        
    def build_model(self):
        """สร้างโมเดลที่ซับซ้อนมากขึ้น"""
        self.model = Sequential([
            Dense(512, activation='relu', input_shape=(14,)),
            Dropout(0.2),
            Dense(256, activation='relu'),
            Dropout(0.2),
            Dense(128, activation='relu'),
            Dropout(0.2),
            Dense(64, activation='relu'),
            Dense(3, activation='linear')  # 3 แอคชั่น: check/call, raise, fold
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=self.lr),
            loss='huber_loss'  # ใช้ Huber Loss เพื่อให้ทนทานต่อ outliers
        )
        
        # โมเดลเป้าหมาย
        self.target_model = clone_model(self.model)
        self.target_model.set_weights(self.model.get_weights())
    
    def monte_carlo_update(self, states, actions, final_reward):
        """เรียนรู้แบบ Monte Carlo จากผลลัพธ์สุดท้ายของเกม"""
        for i, (state, action) in enumerate(zip(states, actions)):
            # คำนวณรางวัลที่ลดลงตามเวลา
            discounted_reward = final_reward * (self.gamma ** (len(states) - i - 1))
            
            # อัพเดทค่า Q
            q_values = self.model.predict(np.array([state]))[0]
            q_values[action] = discounted_reward
            
            # เทรนโมเดล
            self.model.fit(np.array([state]), np.array([q_values]), epochs=1, verbose=0)
    
    def train_with_opponent(self, opponent_model, num_games=1000, update_target_every=50, save_every=200):
        """เรียนรู้โดยการเล่นกับคู่ต่อสู้ที่เป็นโมเดลอื่น"""
        from PlantvsAi_zombitx64.game.poker import PokerGame
        
        print(f"เริ่มการเรียนรู้โดยเล่นกับคู่ต่อสู้ {num_games} เกม...")
        
        win_count = 0
        
        for game_num in range(num_games):
            # สร้างเกมใหม่
            game = PokerGame()
            game.start_new_game()
            
            states = []
            actions = []
            
            done = False
            player_turn = True  # สลับเล่นระหว่างโมเดลของเรากับคู่ต่อสู้
            
            # เล่นจนจบเกม
            while not done:
                # สถานะปัจจุบัน
                current_state = self._get_state_from_game(game)
                
                # เลือกแอคชั่น
                if player_turn:
                    action_idx = self.act(current_state)
                    states.append(current_state)
                    actions.append(action_idx)
                else:
                    # ให้คู่ต่อสู้เลือกแอคชั่น
                    action_idx = opponent_model.act(current_state)
                
                action = self._idx_to_action(action_idx, game)
                
                # ดำเนินการตามแอคชั่น
                _, done = self._perform_action(game, action)
                
                # สลับตาเล่น
                player_turn = not player_turn
            
            # คำนวณรางวัลสุดท้าย
            final_reward = 1.0 if game.winner == 'player' else -1.0
            
            # อัพเดทโมเดลด้วย Monte Carlo
            self.monte_carlo_update(states, actions, final_reward)
            
            # นับจำนวนชนะ
            if game.winner == 'player':
                win_count += 1
            
            # อัพเดทโมเดลเป้าหมาย
            if game_num % update_target_every == 0:
                self.update_target_model()
            
            # บันทึกโมเดล
            if game_num % save_every == 0:
                self.save_model(filename='advanced_poker_model.safetensors')
                win_rate = win_count / (game_num + 1)
                print(f"เกมที่ {game_num}/{num_games} - Win Rate: {win_rate:.4f} - Epsilon: {self.epsilon:.4f}")
        
        self.save_model(filename='advanced_poker_model.safetensors')
        win_rate = win_count / num_games
        print(f"การเรียนรู้เสร็จสิ้น - Win Rate สุดท้าย: {win_rate:.4f}")
