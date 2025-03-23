import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import numpy as np

# เพิ่มไดเร็กทอรีหลักเข้าไปใน path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PlantvsAi_zombitx64.game.reinforcement_poker_model import ReinforcementPokerModel, AdvancedSelfLearningModel
from PlantvsAi_zombitx64.game.poker_model import PokerModel

class TrainingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Poker Training - ZombitX64")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        self.model_type = tk.StringVar(value="reinforcement")
        self.num_games = tk.StringVar(value="1000")
        self.learning_mode = tk.StringVar(value="self")
        self.load_existing = tk.BooleanVar(value=False)
        
        self.training_active = False
        self.training_thread = None
        self.training_data = {
            'games': [],
            'rewards': [],
            'win_rates': [],
            'epsilons': []
        }
        
        self.create_widgets()
        
    def create_widgets(self):
        # สร้างเฟรมหลัก
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ส่วนด้านซ้าย (การตั้งค่า)
        left_frame = ttk.LabelFrame(main_frame, text="การตั้งค่าการเทรน", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # เลือกประเภทโมเดล
        ttk.Label(left_frame, text="ประเภทโมเดล:").grid(row=0, column=0, sticky=tk.W, pady=5)
        model_combo = ttk.Combobox(left_frame, textvariable=self.model_type, 
                                  values=["reinforcement", "advanced"], 
                                  state="readonly", width=20)
        model_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Label(left_frame, text="reinforcement = RL พื้นฐาน\nadvanced = RL ขั้นสูง").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # จำนวนเกม
        ttk.Label(left_frame, text="จำนวนเกม:").grid(row=2, column=0, sticky=tk.W, pady=5)
        games_entry = ttk.Entry(left_frame, textvariable=self.num_games, width=10)
        games_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # โหมดการเรียนรู้
        ttk.Label(left_frame, text="โหมดการเรียนรู้:").grid(row=3, column=0, sticky=tk.W, pady=5)
        mode_combo = ttk.Combobox(left_frame, textvariable=self.learning_mode, 
                                 values=["self", "opponent"], 
                                 state="readonly", width=20)
        mode_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Label(left_frame, text="self = เล่นกับตัวเอง\nopponent = เล่นกับโมเดลคู่แข่ง").grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # โหลดโมเดลที่มีอยู่
        load_check = ttk.Checkbutton(left_frame, text="โหลดโมเดลที่มีอยู่", variable=self.load_existing)
        load_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # ปุ่มเริ่มการเทรน
        style = ttk.Style()
        style.configure('Green.TButton', foreground='black', background='green')
        
        start_button = ttk.Button(left_frame, text="เริ่มการเทรน", 
                                 command=self.start_training, style='Green.TButton')
        start_button.grid(row=6, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        # ปุ่มหยุดการเทรน
        stop_button = ttk.Button(left_frame, text="หยุดการเทรน", 
                               command=self.stop_training, style='TButton')
        stop_button.grid(row=7, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        # ข้อมูลโมเดล
        model_info_frame = ttk.LabelFrame(left_frame, text="ข้อมูลโมเดล", padding=5)
        model_info_frame.grid(row=8, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        self.model_info_text = tk.Text(model_info_frame, height=8, width=25, wrap=tk.WORD)
        self.model_info_text.pack(fill=tk.BOTH, expand=True)
        self.update_model_info()
        
        # ส่วนด้านขวา (แสดงผล)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # แท็บสำหรับแสดงผลต่างๆ
        tab_control = ttk.Notebook(right_frame)
        
        # แท็บกราฟ
        graph_tab = ttk.Frame(tab_control)
        tab_control.add(graph_tab, text="กราฟการเรียนรู้")
        
        # สร้างกราฟ
        self.fig, self.ax = plt.subplots(2, 1, figsize=(8, 6), dpi=80)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_tab)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # แท็บล็อก
        log_tab = ttk.Frame(tab_control)
        tab_control.add(log_tab, text="ล็อกการเทรน")
        
        self.log_text = scrolledtext.ScrolledText(log_tab, height=25, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        tab_control.pack(fill=tk.BOTH, expand=True)
        
    def update_model_info(self):
        self.model_info_text.delete(1.0, tk.END)
        
        # ตรวจสอบโมเดลที่มีอยู่
        reinforcement_exists = os.path.exists(os.path.join('DatasetPokerzombitx64', 'reinforcement_poker_model.safetensors'))
        advanced_exists = os.path.exists(os.path.join('DatasetPokerzombitx64', 'advanced_poker_model.safetensors'))
        
        info_text = "สถานะโมเดล:\n\n"
        
        if reinforcement_exists:
            info_text += "✓ มีโมเดล Reinforcement\n"
        else:
            info_text += "✗ ไม่มีโมเดล Reinforcement\n"
            
        if advanced_exists:
            info_text += "✓ มีโมเดล Advanced\n"
        else:
            info_text += "✗ ไม่มีโมเดล Advanced\n"
            
        # แสดงข้อมูลเพิ่มเติม
        info_text += "\nการปรับปรุงโมเดลล่าสุด:\n"
        if reinforcement_exists:
            try:
                mtime = os.path.getmtime(os.path.join('DatasetPokerzombitx64', 'reinforcement_poker_model.safetensors'))
                info_text += f"Reinforcement: {time.ctime(mtime)}\n"
            except:
                info_text += "Reinforcement: ไม่สามารถอ่านได้\n"
        
        if advanced_exists:
            try:
                mtime = os.path.getmtime(os.path.join('DatasetPokerzombitx64', 'advanced_poker_model.safetensors'))
                info_text += f"Advanced: {time.ctime(mtime)}\n"
            except:
                info_text += "Advanced: ไม่สามารถอ่านได้\n"
        
        self.model_info_text.insert(tk.END, info_text)
        
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        
    def update_graphs(self):
        # อัปเดตกราฟ
        self.ax[0].clear()
        self.ax[1].clear()
        
        games = self.training_data['games']
        
        if len(games) > 0:
            # กราฟบน: รางวัลและอัตราชนะ
            self.ax[0].plot(games, self.training_data['rewards'], 'r-', label='รางวัลเฉลี่ย')
            self.ax[0].plot(games, self.training_data['win_rates'], 'g-', label='อัตราชนะ')
            self.ax[0].set_title('ประสิทธิภาพการเรียนรู้')
            self.ax[0].set_xlabel('จำนวนเกม')
            self.ax[0].set_ylabel('คะแนน')
            self.ax[0].legend()
            self.ax[0].grid(True)
            
            # กราฟล่าง: ค่า epsilon (การสำรวจ)
            self.ax[1].plot(games, self.training_data['epsilons'], 'b-', label='Epsilon')
            self.ax[1].set_title('อัตราการสำรวจ (Epsilon)')
            self.ax[1].set_xlabel('จำนวนเกม')
            self.ax[1].set_ylabel('Epsilon')
            self.ax[1].grid(True)
            
        self.canvas.draw()
        
    def start_training(self):
        if self.training_active:
            messagebox.showwarning("กำลังเทรน", "การเทรนกำลังดำเนินการอยู่")
            return
        
        try:
            num_games = int(self.num_games.get())
            if num_games <= 0:
                messagebox.showerror("ข้อผิดพลาด", "จำนวนเกมต้องมากกว่า 0")
                return
        except ValueError:
            messagebox.showerror("ข้อผิดพลาด", "จำนวนเกมต้องเป็นตัวเลข")
            return
        
        # สร้างโฟลเดอร์สำหรับเก็บข้อมูล
        os.makedirs('DatasetPokerzombitx64', exist_ok=True)
        
        self.training_active = True
        self.training_data = {'games': [], 'rewards': [], 'win_rates': [], 'epsilons': []}
        
        # เริ่ม thread การเทรน
        self.training_thread = threading.Thread(target=self.training_process)
        self.training_thread.daemon = True
        self.training_thread.start()
        
        self.log(f"เริ่มการเทรนโมเดล {self.model_type.get()} ด้วยโหมด {self.learning_mode.get()}")
        self.log(f"จำนวนเกมที่จะเทรน: {num_games}")
        
    def stop_training(self):
        if not self.training_active:
            messagebox.showinfo("ไม่มีการเทรน", "ไม่มีการเทรนที่กำลังดำเนินการอยู่")
            return
            
        self.training_active = False
        self.log("กำลังหยุดการเทรน...")
        
    def training_process(self):
        try:
            # สร้างหรือโหลดโมเดล
            if self.model_type.get() == "reinforcement":
                model = ReinforcementPokerModel()
                model_filename = 'reinforcement_poker_model.safetensors'
            else:
                model = AdvancedSelfLearningModel()
                model_filename = 'advanced_poker_model.safetensors'
            
            # โหลดโมเดลที่มีอยู่หรือสร้างใหม่
            if self.load_existing.get():
                success = model.load_model(model_filename)
                if success:
                    self.log(f"โหลดโมเดลจาก {model_filename} สำเร็จ")
                else:
                    self.log(f"ไม่พบโมเดล จะสร้างโมเดลใหม่")
                    model.build_model()
            else:
                self.log("สร้างโมเดลใหม่")
                model.build_model()
            
            # เตรียมโมเดลคู่แข่ง (ถ้าใช้โหมด opponent)
            opponent = None
            if self.learning_mode.get() == "opponent":
                opponent = PokerModel()
                opponent_path = os.path.join('DatasetPokerzombitx64', 'poker_model.safetensors')
                
                if os.path.exists(opponent_path):
                    self.log("โหลดโมเดลคู่แข่งจากไฟล์ที่มีอยู่")
                    opponent.load_model('poker_model.safetensors')
                else:
                    self.log("สร้างโมเดลคู่แข่งใหม่")
                    opponent.build_model()
            
            # ข้อมูลการเทรน
            num_games = int(self.num_games.get())
            batch_size = 32
            win_count = 0
            total_rewards = 0
            update_interval = max(1, num_games // 100)  # อัปเดตทุก 1% ของการเทรน
            
            # เริ่มการเทรน
            for game_num in range(num_games):
                if not self.training_active:
                    self.log("หยุดการเทรนตามคำขอของผู้ใช้")
                    break
                
                # เทรนแบบต่างๆ ตามโหมดที่เลือก
                if self.learning_mode.get() == "opponent" and isinstance(model, AdvancedSelfLearningModel) and opponent:
                    # เทรนกับคู่แข่ง (สำหรับโมเดลขั้นสูงเท่านั้น)
                    game_result = self._train_with_opponent(model, opponent)
                else:
                    # เทรนด้วยการเล่นกับตัวเอง (ใช้ได้กับทุกโมเดล)
                    game_result = self._train_self_play(model)
                
                # อัปเดตสถิติ
                win_count += 1 if game_result['win'] else 0
                total_rewards += game_result['reward']
                win_rate = win_count / (game_num + 1)
                avg_reward = total_rewards / (game_num + 1)
                
                # อัปเดตกราฟและแสดงความก้าวหน้า
                if game_num % update_interval == 0 or game_num == num_games - 1:
                    self.training_data['games'].append(game_num + 1)
                    self.training_data['rewards'].append(avg_reward)
                    self.training_data['win_rates'].append(win_rate)
                    self.training_data['epsilons'].append(model.epsilon)
                    
                    # อัปเดต UI
                    self.root.after(0, self.update_graphs)
                    self.root.after(0, self.log, 
                                   f"เกม {game_num+1}/{num_games} - " +
                                   f"Win Rate: {win_rate:.4f} - " +
                                   f"Reward: {game_result['reward']:.2f} - " +
                                   f"Epsilon: {model.epsilon:.4f}")
                
                # อัปเดตโมเดลเป้าหมายและบันทึกโมเดลเป็นระยะ
                if game_num % 100 == 0 and game_num > 0:
                    model.update_target_model()
                    
                if game_num % 500 == 0 and game_num > 0:
                    model.save_model(model_filename)
                    self.root.after(0, self.log, f"บันทึกโมเดลที่เกม {game_num}")
                    self.root.after(0, self.update_model_info)
            
            # บันทึกโมเดลเมื่อเทรนเสร็จ
            model.save_model(model_filename)
            
            # อัปเดต UI เมื่อเสร็จสิ้น
            self.root.after(0, self.log, "การเทรนเสร็จสิ้น")
            self.root.after(0, self.update_model_info)
            self.root.after(0, messagebox.showinfo, "เสร็จสิ้น", 
                          f"การเทรนเสร็จสิ้น\nWin Rate: {win_rate:.4f}\nEpsilon สุดท้าย: {model.epsilon:.4f}")
            
        except Exception as e:
            self.root.after(0, self.log, f"เกิดข้อผิดพลาด: {str(e)}")
            self.root.after(0, messagebox.showerror, "ข้อผิดพลาด", str(e))
            
        finally:
            self.training_active = False
    
    def _train_self_play(self, model):
        """เทรนโดยการเล่นกับตัวเอง"""
        from PlantvsAi_zombitx64.game.poker import PokerGame
        
        # สร้างเกมใหม่
        game = PokerGame()
        game.setup_new_game()
        
        done = False
        total_reward = 0
        actions_taken = []
        states = []
        
        # เล่นจนจบเกม
        while not done:
            # ตรวจสอบว่าเกมจบหรือไม่
            if game.winner is not None:
                done = True
                continue
                
            # ดำเนินการเล่น
            current_state = self._get_state_from_game(game)
            states.append(current_state)
            
            # เลือกแอคชั่น
            action_idx = model.act(current_state)
            actions_taken.append(action_idx)
            
            # แปลงเป็นแอคชั่นในเกม
            action = self._idx_to_action(action_idx)
            
            # ดำเนินการตามแอคชั่น
            if action == "call":
                game.player_action("call")
            elif action == "raise":
                min_raise = game.big_blind
                bet_amount = min_raise * 2
                game.player_action("raise", bet_amount)
            elif action == "fold":
                game.player_action("fold")
            
            # ให้ AI เล่น
            if not done and game.winner is None:
                game.ai_move(0)  # ใช้ AI ระดับง่าย
            
            # ตรวจสอบว่าเกมจบหรือไม่
            if game.winner is not None:
                done = True
        
        # คำนวณรางวัล
        reward = 1.0 if game.winner == "player" else -1.0
        total_reward = reward
        
        # อัปเดตแบบ Monte Carlo
        for i, (state, action) in enumerate(zip(states, actions_taken)):
            # คำนวณรางวัลที่ลดลงตามเวลา
            discounted_reward = reward * (model.gamma ** (len(states) - i - 1))
            
            # อัปเดตโมเดล
            target = model.model.predict(np.array([state]))[0]
            target[action] = discounted_reward
            model.model.fit(np.array([state]), np.array([target]), epochs=1, verbose=0)
        
        # ลดค่า epsilon
        if model.epsilon > model.epsilon_min:
            model.epsilon *= model.epsilon_decay
        
        return {
            'win': game.winner == "player",
            'reward': total_reward
        }
    
    def _train_with_opponent(self, model, opponent):
        """เทรนโดยการเล่นกับคู่แข่ง"""
        from PlantvsAi_zombitx64.game.poker import PokerGame
        
        # สร้างเกมใหม่
        game = PokerGame()
        game.setup_new_game()
        
        done = False
        total_reward = 0
        states = []
        actions = []
        
        # เล่นจนจบเกม
        while not done:
            # ตรวจสอบว่าเกมจบหรือไม่
            if game.winner is not None:
                done = True
                continue
            
            # ดำเนินการเล่น
            current_state = self._get_state_from_game(game)
            
            # ให้โมเดลเราเล่น
            action_idx = model.act(current_state)
            states.append(current_state)
            actions.append(action_idx)
            
            # แปลงเป็นแอคชั่นในเกม
            action = self._idx_to_action(action_idx)
            
            # ดำเนินการตามแอคชั่น
            if action == "call":
                game.player_action("call")
            elif action == "raise":
                min_raise = game.big_blind
                bet_amount = min_raise * 2
                game.player_action("raise", bet_amount)
            elif action == "fold":
                game.player_action("fold")
            
            # ให้ AI คู่แข่งเล่น
            if not done and game.winner is None:
                game.ai_move(1)  # ใช้ AI ระดับปานกลาง
            
            # ตรวจสอบว่าเกมจบหรือไม่
            if game.winner is not None:
                done = True
        
        # คำนวณรางวัล
        reward = 1.0 if game.winner == "player" else -1.0
        total_reward = reward
        
        # ใช้ Monte Carlo Tree Search สำหรับโมเดลขั้นสูง
        if isinstance(model, AdvancedSelfLearningModel):
            model.monte_carlo_update(states, actions, reward)
        else:
            # อัปเดตแบบปกติสำหรับโมเดลพื้นฐาน
            for i, (state, action) in enumerate(zip(states, actions)):
                # คำนวณรางวัลที่ลดลงตามเวลา
                discounted_reward = reward * (model.gamma ** (len(states) - i - 1))
                
                # อัปเดตโมเดล
                target = model.model.predict(np.array([state]))[0]
                target[action] = discounted_reward
                model.model.fit(np.array([state]), np.array([target]), epochs=1, verbose=0)
        
        # ลดค่า epsilon
        if model.epsilon > model.epsilon_min:
            model.epsilon *= model.epsilon_decay
        
        return {
            'win': game.winner == "player",
            'reward': total_reward
        }
    
    def _get_state_from_game(self, game):
        """แปลงสถานะของเกมให้เป็นข้อมูลสำหรับโมเดล"""
        player = game.players[0]
        ai = game.players[1]
        
        # ข้อมูลพื้นฐาน
        # ใช้ข้อมูลที่ง่ายกว่าในการเทรน
        pot_ratio = min(1.0, game.pot / 1000)
        player_chips_ratio = min(1.0, player.chips / 1000)
        ai_chips_ratio = min(1.0, ai.chips / 1000)
        
        # สร้างเวกเตอร์สถานะ
        state = [0] * 14  # ใช้ขนาดเดียวกับที่ใช้ในโมเดล
        
        # ใส่ข้อมูลพื้นฐานเข้าไป
        state[0] = pot_ratio
        state[1] = player_chips_ratio
        state[2] = ai_chips_ratio
        
        # ข้อมูลอื่นๆ ให้เป็น 0 ไปก่อน (ในการเทรนจริงต้องใส่ข้อมูลที่ถูกต้อง)
        
        return state
    
    def _idx_to_action(self, action_idx):
        """แปลงดัชนีแอคชั่นเป็นการกระทำในเกม"""
        actions = ['call', 'raise', 'fold']
        return actions[action_idx]

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingGUI(root)
    root.mainloop()
