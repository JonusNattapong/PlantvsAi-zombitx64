class GameSettings:
    """
    คลาสสำหรับการจัดการการตั้งค่าเกมทั้งหมด
    """
    def __init__(self):
        self.difficulty_levels = {
            'easy': {
                'search_depth': 2,
                'pattern_weight': 0.5,
                'randomness': 0.3,
                'base_time_limit': 2.0,
                'time_per_move': 0.5,
                'time_per_complexity': 0.1,
                'hint_enabled': True,
                'undo_moves': True,
                'ai_delay': 1.0,
                'poker': {
                    'search_depth': 3,
                    'randomness': 0.2,
                    'ai_delay': 0.8
                }
            },
            'medium': {
                'search_depth': 4,
                'pattern_weight': 0.7,
                'randomness': 0.2,
                'base_time_limit': 1.0,
                'time_per_move': 0.3,
                'time_per_complexity': 0.2,
                'hint_enabled': True,
                'undo_moves': True,
                'ai_delay': 0.5,
                'poker': {
                    'search_depth': 5,
                    'randomness': 0.15,
                    'ai_delay': 0.5
                }
            },
            'hard': {
                'search_depth': 6,
                'pattern_weight': 0.9,
                'randomness': 0.1,
                'base_time_limit': 0.5,
                'time_per_move': 0.2,
                'time_per_complexity': 0.3,
                'hint_enabled': False,
                'undo_moves': False,
                'ai_delay': 0.2,
                'poker': {
                    'search_depth': 7,
                    'randomness': 0.1,
                    'ai_delay': 0.3
                }
            }
        }
        
        self.current_difficulty = 'medium'
        self.settings = self.difficulty_levels[self.current_difficulty]
        
    def set_difficulty(self, difficulty):
        """ตั้งค่าระดับความยาก"""
        if difficulty in self.difficulty_levels:
            self.current_difficulty = difficulty
            self.settings = self.difficulty_levels[difficulty]
            return True
        return False
    
    def get_settings(self):
        """รับการตั้งค่าปัจจุบัน"""
        return self.settings
    
    def get_difficulty_levels(self):
        """รับรายการระดับความยากทั้งหมด"""
        return list(self.difficulty_levels.keys())
    
    def get_current_difficulty(self):
        """รับระดับความยากปัจจุบัน"""
        return self.current_difficulty
    
    def get_poker_settings(self):
        """Get poker-specific settings"""
        return self.settings.get('poker', {})
    
    def calculate_thinking_time(self, game_type, move_count, complexity):
        """
        คำนวณเวลาคิดของ AI ตามระดับความยาก, จำนวนการเคลื่อนที่ และความซับซ้อน
        """
        base_settings = self.settings
        poker_settings = self.get_poker_settings()

        # ปรับพื้นฐานตามประเภทเกม
        if game_type == 'poker':
            base_time = poker_settings.get('ai_delay', base_settings['base_time_limit'])
            time_per_move = base_settings['time_per_move'] * 0.8
            time_per_complexity = base_settings['time_per_complexity'] * 1.2
        elif game_type == 'chess':
            base_time = base_settings['base_time_limit'] * 2
            time_per_move = base_settings['time_per_move'] * 1.5
            time_per_complexity = base_settings['time_per_complexity'] * 2
        elif game_type == 'tictactoe':
            base_time = base_settings['base_time_limit'] / 2
            time_per_move = base_settings['time_per_move'] * 0.5
            time_per_complexity = base_settings['time_per_complexity'] * 0.5
        elif game_type == 'checkers':
            base_time = base_settings['base_time_limit'] * 1.5
            time_per_move = base_settings['time_per_move'] * 1.2
            time_per_complexity = base_settings['time_per_complexity'] * 1.5
        elif game_type == 'connect_four':
            base_time = base_settings['base_time_limit'] * 1.2
            time_per_move = base_settings['time_per_move'] * 1.3
            time_per_complexity = base_settings['time_per_complexity'] * 1.2
        else:
            base_time = base_settings['base_time_limit']
            time_per_move = base_settings['time_per_move']
            time_per_complexity = base_settings['time_per_complexity']
        
        # คำนวณเวลาตามจำนวนการเคลื่อนที่
        move_time = move_count * time_per_move
        
        # คำนวณเวลาตามความซับซ้อน
        complexity_time = complexity * time_per_complexity
        
        # รวมเวลาทั้งหมด
        total_time = base_time + move_time + complexity_time
        
        # ตรวจสอบไม่เกินค่าสูงสุดตามระดับความยาก
        if self.current_difficulty == 'easy':
            max_time = 5.0
        elif self.current_difficulty == 'medium':
            max_time = 3.0
        else:  # hard
            max_time = 2.0
        
        return max(0.2, min(total_time, max_time))
    
    def adjust_settings(self, game_type):
        """
        ปรับการตั้งค่าตามประเภทเกม
        """
        base_settings = self.settings
        
        if game_type == 'chess':
            return {
                'search_depth': base_settings['search_depth'] * 2,
                'pattern_weight': base_settings['pattern_weight'],
                'randomness': base_settings['randomness'] / 2,
                'time_limit': base_settings['base_time_limit'] * 2,
                'opening_book': True,
                'hint_enabled': base_settings['hint_enabled'],
                'undo_moves': base_settings['undo_moves'],
                'ai_delay': base_settings['ai_delay']
            }
        elif game_type == 'tictactoe':
            return {
                'search_depth': min(base_settings['search_depth'], 5),
                'pattern_weight': base_settings['pattern_weight'] * 1.5,
                'randomness': base_settings['randomness'] * 1.5,
                'time_limit': base_settings['base_time_limit'] / 2,
                'hint_enabled': base_settings['hint_enabled'],
                'undo_moves': base_settings['undo_moves'],
                'ai_delay': base_settings['ai_delay']
            }
        elif game_type == 'checkers':
            return {
                'search_depth': base_settings['search_depth'] * 1.5,
                'pattern_weight': base_settings['pattern_weight'] * 1.2,
                'randomness': base_settings['randomness'] * 0.8,
                'time_limit': base_settings['base_time_limit'] * 1.5,
                'king_capture_bonus': 1.5,
                'hint_enabled': base_settings['hint_enabled'],
                'undo_moves': base_settings['undo_moves'],
                'ai_delay': base_settings['ai_delay']
            }
        elif game_type == 'connect_four':
            return {
                'search_depth': base_settings['search_depth'] * 1.2,
                'pattern_weight': base_settings['pattern_weight'] * 1.3,
                'randomness': base_settings['randomness'] * 0.9,
                'time_limit': base_settings['base_time_limit'] * 1.2,
                'connect_bonus': 1.5,
                'hint_enabled': base_settings['hint_enabled'],
                'undo_moves': base_settings['undo_moves'],
                'ai_delay': base_settings['ai_delay']
            }
        elif game_type == 'poker':
            return {
                'search_depth': base_settings['poker']['search_depth'],
                'pattern_weight': base_settings['pattern_weight'],
                'randomness': base_settings['poker']['randomness'],
                'time_limit': base_settings['poker']['ai_delay'],
                'hint_enabled': base_settings['hint_enabled'],
                'undo_moves': base_settings['undo_moves'],
                'ai_delay': base_settings['poker']['ai_delay']
            }
        else:
            return base_settings
