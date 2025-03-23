import json
import os
import random
import numpy as np
from collections import Counter

class Card:
    """
    คลาสสำหรับเก็บข้อมูลของไพ่แต่ละใบ
    """
    SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
    
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __repr__(self):
        rank_map = {
            '2': '2', '3': '3', '4': '4', '5': '5', '6': '6',
            '7': '7', '8': '8', '9': '9', '10': '10',
            'jack': 'J', 'queen': 'Q', 'king': 'K', 'ace': 'A'
        }
        suit_map = {
            'hearts': 'Hearts', 'diamonds': 'Diamonds',
            'clubs': 'Clubs', 'spades': 'Spades'
        }
        return f"{rank_map[self.rank]} of {suit_map[self.suit]}"
    
    def to_dict(self):
        return {
            'suit': self.suit,
            'rank': self.rank
        }
    
    @staticmethod
    def from_dict(card_dict):
        return Card(card_dict['suit'], card_dict['rank'])
    
    def get_rank_value(self):
        """แปลงค่าของไพ่เป็นตัวเลข"""
        return Card.RANKS.index(self.rank)


class Deck:
    """
    คลาสสำหรับสำรับไพ่
    """
    def __init__(self):
        self.cards = []
        self.build()
    
    def build(self):
        """สร้างสำรับไพ่ใหม่ 52 ใบ"""
        self.cards = [Card(suit, rank) for suit in Card.SUITS for rank in Card.RANKS]
    
    def shuffle(self):
        """สับไพ่"""
        random.shuffle(self.cards)
    
    def deal(self):
        """แจกไพ่ 1 ใบ"""
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            return None


class PokerHand:
    """
    คลาสสำหรับมือของผู้เล่น
    """
    HAND_RANKS = {
        'High Card': 0,
        'One Pair': 1,
        'Two Pair': 2,
        'Three of a Kind': 3,
        'Straight': 4,
        'Flush': 5,
        'Full House': 6,
        'Four of a Kind': 7,
        'Straight Flush': 8,
        'Royal Flush': 9
    }
    
    def __init__(self, cards=None):
        self.cards = cards or []
    
    def add_card(self, card):
        """เพิ่มไพ่ในมือ"""
        self.cards.append(card)
    
    def to_dict(self):
        return [card.to_dict() for card in self.cards]
    
    @staticmethod
    def from_dict(cards_dict):
        hand = PokerHand()
        hand.cards = [Card.from_dict(card) for card in cards_dict]
        return hand
    
    def get_hand_rank(self, community_cards):
        """ตรวจสอบอันดับของมือ (5 ใบที่ดีที่สุด)"""
        all_cards = self.cards + community_cards
        
        # ดึงข้อมูล suit และ rank
        ranks = [card.rank for card in all_cards]
        suits = [card.suit for card in all_cards]
        
        # Convert ranks to numbers
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
                      '8': 8, '9': 9, '10': 10, 'jack': 11, 'queen': 12, 'king': 13, 'ace': 14}
        numeric_ranks = [rank_values[rank] for rank in ranks]
        
        # Check for flush
        flush = any(suits.count(suit) >= 5 for suit in Card.SUITS)
        
        # Check for straight
        sorted_ranks = sorted(numeric_ranks)
        is_straight = any(sorted_ranks[i] == sorted_ranks[i+1] - 1 
                         for i in range(len(sorted_ranks)-4))
        
        # Count rank frequencies
        rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
        
        # Determine hand type
        if flush and is_straight:
            if set(ranks) == {'10', 'jack', 'queen', 'king', 'ace'}:
                return 'Royal Flush', 10
            return 'Straight Flush', 9
        elif 4 in rank_counts.values():
            return 'Four of a Kind', 8
        elif 3 in rank_counts.values() and 2 in rank_counts.values():
            return 'Full House', 7
        elif flush:
            return 'Flush', 6
        elif is_straight:
            return 'Straight', 5
        elif 3 in rank_counts.values():
            return 'Three of a Kind', 4
        elif list(rank_counts.values()).count(2) == 2:
            return 'Two Pair', 3
        elif 2 in rank_counts.values():
            return 'One Pair', 2
        return 'High Card', 1

    def evaluate(self):
        """Evaluate the hand and return detailed features"""
        # Get hand type and value
        hand_type, value = self.get_hand_rank([])
        
        # Get ranks and suits
        ranks = [card.rank for card in self.cards]
        suits = [card.suit for card in self.cards]
        
        # Convert ranks to numbers
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
                      '8': 8, '9': 9, '10': 10, 'jack': 11, 'queen': 12, 'king': 13, 'ace': 14}
        numeric_ranks = [rank_values[rank] for rank in ranks]
        
        # Get rank and suit frequencies
        rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
        suit_counts = {suit: suits.count(suit) for suit in set(suits)}
        
        # Calculate features
        highest_rank = max(numeric_ranks)
        lowest_rank = min(numeric_ranks)
        rank_diff = highest_rank - lowest_rank
        max_rank_count = max(rank_counts.values()) if rank_counts else 0
        max_suit_count = max(suit_counts.values()) if suit_counts else 0
        is_suited = len(set(suits)) == 1
        
        return {
            'hand_type': hand_type,
            'value': value,
            'highest_rank': highest_rank,
            'lowest_rank': lowest_rank,
            'rank_diff': rank_diff,
            'max_rank_count': max_rank_count,
            'max_suit_count': max_suit_count,
            'is_suited': is_suited
        }
    
    def compare_with(self, other_hand, community_cards):
        """เปรียบเทียบมือของตัวเองกับมืออื่น"""
        my_rank, my_value = self.get_hand_rank(community_cards)
        other_rank, other_value = other_hand.get_hand_rank(community_cards)
        
        my_rank_value = PokerHand.HAND_RANKS[my_rank]
        other_rank_value = PokerHand.HAND_RANKS[other_rank]
        
        # ถ้าอันดับต่างกัน
        if my_rank_value > other_rank_value:
            return 1  # มือเราชนะ
        elif my_rank_value < other_rank_value:
            return -1  # มือเราแพ้
        
        # ถ้าอันดับเท่ากัน ต้องเปรียบเทียบค่าในอันดับนั้นๆ
        if isinstance(my_value, tuple) and isinstance(other_value, tuple):
            # เปรียบเทียบทีละค่า
            for my_val, other_val in zip(my_value, other_value):
                if my_val > other_val:
                    return 1
                elif my_val < other_val:
                    return -1
        elif isinstance(my_value, list) and isinstance(other_value, list):
            # สำหรับไพ่ flush เปรียบเทียบทีละค่า
            for my_val, other_val in zip(my_value, other_value):
                if my_val > other_val:
                    return 1
                elif my_val < other_val:
                    return -1
        else:
            # เปรียบเทียบค่าปกติ
            if my_value > other_value:
                return 1
            elif my_value < other_value:
                return -1
        
        # เสมอกัน
        return 0


class PokerPlayer:
    """
    คลาสสำหรับผู้เล่น
    """
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.hand = PokerHand()
        self.is_folded = False
        self.is_all_in = False
        self.current_bet = 0
    
    def reset_for_new_hand(self):
        """รีเซ็ตสถานะสำหรับมือใหม่"""
        self.hand = PokerHand()
        self.is_folded = False
        self.is_all_in = False
        self.current_bet = 0
    
    def bet(self, amount):
        """วางเดิมพัน"""
        amount = min(amount, self.chips)
        self.chips -= amount
        self.current_bet += amount
        
        if self.chips == 0:
            self.is_all_in = True
            
        return amount
    
    def fold(self):
        """พับ"""
        self.is_folded = True
    
    def to_dict(self):
        return {
            'name': self.name,
            'chips': self.chips,
            'hand': self.hand.to_dict(),
            'is_folded': self.is_folded,
            'is_all_in': self.is_all_in,
            'current_bet': self.current_bet
        }
    
    @staticmethod
    def from_dict(player_dict):
        player = PokerPlayer(player_dict['name'], player_dict['chips'])
        player.hand = PokerHand.from_dict(player_dict['hand'])
        player.is_folded = player_dict['is_folded']
        player.is_all_in = player_dict['is_all_in']
        player.current_bet = player_dict['current_bet']
        return player


class PokerGame:
    """
    คลาสหลักสำหรับเกม Poker
    """
    def __init__(self):
        """Initialize Poker game"""
        self.deck = Deck()
        self.community_cards = []
        self.players = []  # [0] is player, [1] is AI
        self.pot = 0
        self.current_player_idx = 0
        self.small_blind = 5
        self.big_blind = 10
        self.current_bet = 0
        self.game_stage = "pre_flop"  # pre_flop, flop, turn, river, showdown
        self.winner = None
        self.stats = self.load_stats()
        self.bet_history = []
        self.action_log = []
        self.game_settings = GameSettings()
        self.poker_settings = self.game_settings.get_poker_settings()
        
        # Initialize poker models
        try:
            from poker_model import PokerModel
            self.poker_model = PokerModel()
            self.poker_model.load_model()
            
            # ใช้โมเดลแบบ Reinforcement Learning ถ้ามีไฟล์โมเดลอยู่
            try:
                from PlantvsAi_zombitx64.game.reinforcement_poker_model import ReinforcementPokerModel, AdvancedSelfLearningModel
                
                # ลองโหลดโมเดล reinforcement learning
                self.reinforcement_model = ReinforcementPokerModel()
                if os.path.exists(os.path.join('DatasetPokerzombitx64', 'reinforcement_poker_model.safetensors')):
                    self.reinforcement_model.load_model()
                    self.has_reinforcement_model = True
                else:
                    self.has_reinforcement_model = False
                
                # ลองโหลดโมเดลขั้นสูง
                self.advanced_model = AdvancedSelfLearningModel()
                if os.path.exists(os.path.join('DatasetPokerzombitx64', 'advanced_poker_model.safetensors')):
                    self.advanced_model.load_model()
                    self.has_advanced_model = True
                else:
                    self.has_advanced_model = False
            except Exception as e:
                print(f"ไม่สามารถโหลดโมเดล Reinforcement Learning ได้: {e}")
                self.has_reinforcement_model = False
                self.has_advanced_model = False
        except Exception as e:
            print(f"ไม่สามารถโหลดโมเดลโป๊กเกอร์ได้: {e}")
            self.poker_model = None
    
    def load_stats(self):
        """Load game statistics from file"""
        stats_file = 'poker_stats.json'
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading Poker stats: {e}")
        
        # Default stats
        return {
            "total_games": 0,
            "player_wins": 0,
            "ai_wins": 0,
            "draws": 0,
            "win_rate": 0,
            "ai_mode_stats": {},
            "biggest_pot": 0,
            "best_hand": ""
        }
    
    def save_stats(self):
        """Save game statistics to file"""
        stats_file = 'poker_stats.json'
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving Poker stats: {e}")
    
    def update_stats(self, ai_mode_name, winner, pot_size, best_hand_name=None):
        """Update game statistics after a game ends"""
        self.stats["total_games"] += 1
        
        # Initialize AI mode stats if not exists
        if ai_mode_name not in self.stats["ai_mode_stats"]:
            self.stats["ai_mode_stats"][ai_mode_name] = {"wins": 0, "losses": 0, "draws": 0}
        
        # Update based on winner
        if winner == "ai":
            self.stats["ai_wins"] += 1
            self.stats["ai_mode_stats"][ai_mode_name]["wins"] += 1
        elif winner == "player":
            self.stats["player_wins"] += 1
            self.stats["ai_mode_stats"][ai_mode_name]["losses"] += 1
        else:  # Draw
            self.stats["draws"] += 1
            self.stats["ai_mode_stats"][ai_mode_name]["draws"] += 1
        
        # Update win rate
        total_games = self.stats["total_games"]
        if total_games > 0:
            self.stats["win_rate"] = round((self.stats["player_wins"] / total_games) * 100)
        
        # Update biggest pot
        if pot_size > self.stats["biggest_pot"]:
            self.stats["biggest_pot"] = pot_size
        
        # Update best hand
        if best_hand_name and (not self.stats["best_hand"] or 
                              PokerHand.HAND_RANKS.get(best_hand_name, -1) > 
                              PokerHand.HAND_RANKS.get(self.stats["best_hand"], -1)):
            self.stats["best_hand"] = best_hand_name
        
        # Save updated stats
        self.save_stats()
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = []
        
        # Reset players' hands
        for player in self.players:
            player.reset_for_new_hand()
        
        self.pot = 0
        self.current_player_idx = 0
        self.current_bet = 0
        self.game_stage = "pre_flop"
        self.winner = None
        self.bet_history = []
        self.action_log = []
    
    def setup_new_game(self, player_chips=1000, ai_chips=1000):
        """Set up a new game with players"""
        self.players = [
            PokerPlayer("Player", player_chips),
            PokerPlayer("AI", ai_chips)
        ]
        self.reset_game()
        
        # Deal two cards to each player
        for _ in range(2):
            for player in self.players:
                player.hand.add_card(self.deck.deal())
        
        # Post blinds
        self.players[0].bet(self.small_blind)  # Player posts small blind
        self.players[1].bet(self.big_blind)    # AI posts big blind
        self.current_bet = self.big_blind
        self.pot = self.small_blind + self.big_blind
        
        # บันทึกการเดิมพัน blinds
        self.bet_history.append({
            'player': "Player",
            'action': "small blind",
            'amount': self.small_blind,
            'stage': "pre_flop"
        })
        self.bet_history.append({
            'player': "AI",
            'action': "big blind",
            'amount': self.big_blind,
            'stage': "pre_flop"
        })
        
        # บันทึกการกระทำ
        self.action_log.append(f"Player posts small blind: {self.small_blind}")
        self.action_log.append(f"AI posts big blind: {self.big_blind}")
        
        # Player acts first pre-flop
        self.current_player_idx = 0
    
    def get_game_state(self, show_ai_cards=False):
        """Get the current game state"""
        state = {
            'pot': self.pot,
            'current_bet': self.current_bet,
            'game_stage': self.game_stage,
            'community_cards': [card.to_dict() for card in self.community_cards],
            'players': [
                {
                    'name': player.name,
                    'chips': player.chips,
                    'current_bet': player.current_bet,
                    'is_folded': player.is_folded,
                    'is_all_in': player.is_all_in,
                    'hand': player.hand.to_dict() if player.name == "Player" or show_ai_cards else [],
                    'hand_name': getattr(player, 'hand_name', None) if player.name == "Player" or show_ai_cards or self.game_stage == "showdown" else None
                }
                for player in self.players
            ],
            'current_player': self.players[self.current_player_idx].name,
            'winner': self.winner,
            'hand_descriptions': {
                'High Card': 'High Card',
                'One Pair': 'One Pair',
                'Two Pair': 'Two Pair',
                'Three of a Kind': 'Three of a Kind',
                'Straight': 'Straight',
                'Flush': 'Flush',
                'Full House': 'Full House',
                'Four of a Kind': 'Four of a Kind',
                'Straight Flush': 'Straight Flush',
                'Royal Flush': 'Royal Flush'
            },
            'bet_history': self.bet_history,
            'action_log': self.action_log
        }
        return state
    
    def next_stage(self):
        """Move to the next stage of the game"""
        stage_names = {
            "pre_flop": "Flop",
            "flop": "Turn",
            "turn": "River",
            "river": "Showdown"
        }
        
        if self.game_stage == "pre_flop":
            self.game_stage = "flop"
            # Deal flop (3 cards)
            flop_cards = []
            for _ in range(3):
                card = self.deck.deal()
                flop_cards.append(card)
                self.community_cards.append(card)
            
            # บันทึกการแจกไพ่ flop
            self.action_log.append(f"Dealing Flop: {', '.join(str(card) for card in flop_cards)}")
        
        elif self.game_stage == "flop":
            self.game_stage = "turn"
            # Deal turn (1 card)
            turn_card = self.deck.deal()
            self.community_cards.append(turn_card)
            
            # บันทึกการแจกไพ่ turn
            self.action_log.append(f"Dealing Turn: {turn_card}")
        
        elif self.game_stage == "turn":
            self.game_stage = "river"
            # Deal river (1 card)
            river_card = self.deck.deal()
            self.community_cards.append(river_card)
            
            # บันทึกการแจกไพ่ river
            self.action_log.append(f"Dealing River: {river_card}")
        
        elif self.game_stage == "river":
            self.game_stage = "showdown"
            self.action_log.append("Showdown")
            self.determine_winner()
        
        # Reset betting round
        self.current_player_idx = 0
        self.current_bet = 0
        for player in self.players:
            if not player.is_folded and not player.is_all_in:
                player.current_bet = 0
        
        # บันทึกการเปลี่ยน stage
        if self.game_stage != "showdown":
            self.action_log.append(f"Starting {stage_names.get(self.game_stage, self.game_stage)} betting round")
    
    def determine_winner(self):
        """Determine the winner at showdown"""
        active_players = [player for player in self.players if not player.is_folded]
        
        if len(active_players) == 1:
            # Only one player left (others folded)
            self.winner = active_players[0].name.lower()
            active_players[0].chips += self.pot
            
            # Save best hand
            hand_name, _ = active_players[0].hand.get_hand_rank(self.community_cards)
            active_players[0].hand_name = hand_name  # Store the hand name
            
            # บันทึกผลลัพธ์
            self.action_log.append(f"{active_players[0].name} wins {self.pot} chips with {hand_name}")
            self.update_stats("default", self.winner, self.pot, hand_name)
            
            return
        
        # Compare hands
        best_player = None
        best_hand_name = None
        
        for player in active_players:
            hand_name, _ = player.hand.get_hand_rank(self.community_cards)
            player.hand_name = hand_name  # Store the hand name for each player
            
            # บันทึกมือของผู้เล่น
            self.action_log.append(f"{player.name} shows {player.hand.cards[0]} and {player.hand.cards[1]} - {hand_name}")
            
            if best_player is None:
                best_player = player
                best_hand_name = hand_name
                continue
            
            # Compare hands
            result = player.hand.compare_with(best_player.hand, self.community_cards)
            if result > 0:
                best_player = player
                best_hand_name = hand_name
        
        if best_player:
            self.winner = best_player.name.lower()
            best_player.chips += self.pot
            
            # บันทึกผู้ชนะ
            self.action_log.append(f"{best_player.name} wins {self.pot} chips with {best_hand_name}")
        else:
            # No winner (shouldn't happen)
            self.winner = "draw"
            self.action_log.append(f"Game ended in a draw!")
        
        # Update stats
        self.update_stats("default", self.winner, self.pot, best_hand_name)
    
    def player_action(self, action, bet_amount=0):
        """Process player action (call, raise, fold)"""
        if self.game_stage == "showdown" or self.winner:
            return False
        
        current_player = self.players[self.current_player_idx]
        player_name = current_player.name
        
        # สร้างข้อมูลสำหรับบันทึกประวัติการเดิมพัน
        action_record = {
            'player': player_name,
            'action': action,
            'amount': 0,
            'stage': self.game_stage
        }
        
        if action == "fold":
            current_player.fold()
            self.action_log.append(f"{player_name} folds")
            
            # Check if only one player left
            active_players = [p for p in self.players if not p.is_folded]
            if len(active_players) == 1:
                self.winner = active_players[0].name.lower()
                active_players[0].chips += self.pot
                self.action_log.append(f"{active_players[0].name} wins {self.pot} chips (opponent folded)")
                self.update_stats("default", self.winner, self.pot)
                return True
        
        elif action == "call":
            amount_to_call = self.current_bet - current_player.current_bet
            amount_called = current_player.bet(amount_to_call)
            self.pot += amount_called
            
            # อัปเดตข้อมูลการเดิมพัน
            action_record['amount'] = amount_called
            self.action_log.append(f"{player_name} calls {amount_called}")
        
        elif action == "raise" or action == "bet":
            # Minimum raise is double the current bet
            min_raise = max(self.current_bet * 2, self.big_blind)
            bet_amount = max(min_raise, bet_amount)
            
            amount_to_raise = bet_amount - current_player.current_bet
            amount_raised = current_player.bet(amount_to_raise)
            self.pot += amount_raised
            self.current_bet = current_player.current_bet
            
            # อัปเดตข้อมูลการเดิมพัน
            action_record['amount'] = amount_raised
            action_name = "raises" if self.current_bet > 0 else "bets"
            self.action_log.append(f"{player_name} {action_name} {amount_raised}")
        
        elif action == "check":
            # Check is only valid if no bet has been made
            if current_player.current_bet < self.current_bet:
                return False
            # No action needed for check
            self.action_log.append(f"{player_name} checks")
        
        # เพิ่มข้อมูลการเดิมพันเข้าไปในประวัติ
        if action != "check":  # ไม่บันทึกการ check เนื่องจากไม่มีการเดิมพัน
            self.bet_history.append(action_record)
        
        # Switch to next player
        self.next_player()
        
        # Check if round is over
        self.check_round_complete()
        
        return True
    
    def next_player(self):
        """Switch to next player"""
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        
        # Skip folded or all-in players
        while (self.players[self.current_player_idx].is_folded or 
               self.players[self.current_player_idx].is_all_in):
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            
            # If we've gone through all players, break
            if self.current_player_idx == 0:
                break
    
    def check_round_complete(self):
        """Check if the current betting round is complete"""
        # If only one player is active (not folded), round is complete
        active_players = [p for p in self.players if not p.is_folded]
        if len(active_players) == 1:
            self.next_stage()
            return True
        
        # Check if all active players have bet the same amount or are all-in
        active_bets = set()
        for player in active_players:
            if player.is_all_in:
                continue
            active_bets.add(player.current_bet)
        
        # If all active players have the same bet, or all but one are all-in
        if len(active_bets) <= 1:
            # Check if we've gone through all players
            if self.current_player_idx == 0:
                self.next_stage()
                return True
        
        return False
    
    def get_valid_actions(self):
        """Get valid actions for current player"""
        if self.game_stage == "showdown" or self.winner:
            return []
        
        current_player = self.players[self.current_player_idx]
        
        if current_player.is_folded or current_player.is_all_in:
            return []
        
        actions = ["fold"]
        
        # If no bet or player has already matched current bet
        if current_player.current_bet >= self.current_bet:
            actions.append("check")
        else:
            actions.append("call")
        
        # Can raise if player has enough chips
        if current_player.chips > self.current_bet - current_player.current_bet:
            actions.append("raise")
        
        return actions
    
    def ai_move(self, ai_mode=0):
        """Handle AI's move based on selected mode"""
        valid_actions = self.get_valid_actions()
        
        # Load poker settings
        self.poker_settings = self.game_settings.get_poker_settings()
        search_depth = self.poker_settings.get('search_depth', 5)
        
        # Calculate game complexity for dynamic thinking time
        complexity = self.calculate_game_complexity()
        move_count = len(self.action_log)
        thinking_time = self.game_settings.calculate_thinking_time('poker', move_count, complexity)
        
        # Log AI thinking
        self.action_log.append(f"AI is thinking... (complexity: {complexity:.2f})")
        
        # Simulate AI thinking time
        import time
        time.sleep(thinking_time)
        
        # แบ่งประเภทของ AI ตามโมเดลที่มี
        if ai_mode == 0:
            # โหมดง่าย - ใช้กลยุทธ์ AI แบบง่าย
            return self.ai_move_simple(valid_actions)
        elif ai_mode == 1:
            # โหมดปานกลาง - ใช้การคำนวณความน่าจะเป็น
            return self.ai_move_probability(valid_actions, search_depth)
        elif ai_mode == 2:
            # โหมดยาก - ใช้ ML model พื้นฐาน
            return self.ai_move_advanced(valid_actions, search_depth)
        elif ai_mode == 3 and hasattr(self, 'has_reinforcement_model') and self.has_reinforcement_model:
            # โหมด Reinforcement Learning
            return self.ai_move_reinforcement(valid_actions)
        elif ai_mode == 4 and hasattr(self, 'has_advanced_model') and self.has_advanced_model:
            # โหมด Advanced Self-Learning
            return self.ai_move_advanced_learning(valid_actions)
        else:
            # ถ้าเลือกโหมดที่ไม่มี ให้ใช้โหมดยากแทน
            return self.ai_move_advanced(valid_actions, search_depth)
    
    # เพิ่มฟังก์ชั่นใหม่สำหรับ AI โหมด Reinforcement Learning
    def ai_move_reinforcement(self, valid_actions):
        """AI strategy using Reinforcement Learning model"""
        try:
            # สร้างสถานะปัจจุบันของเกม
            state = self._create_state_for_reinforcement()
            
            # ใช้โมเดล RL ทำนายการกระทำที่ดีที่สุด
            q_values = self.reinforcement_model.model.predict(np.array([state]))[0]
            action_idx = np.argmax(q_values)  # 0: call, 1: raise, 2: fold
            
            # แปลงดัชนีเป็นการกระทำที่ใช้ได้จริง
            if action_idx == 0 and 'call' in valid_actions:
                # Call
                self.action_log.append(f"AI decides to call {self.current_bet}")
                return self.player_action('call')
            elif action_idx == 1 and 'raise' in valid_actions:
                # Raise
                ai_player = self.players[1]
                # คำนวณจำนวนเงินที่จะเรียก
                min_raise = self.current_bet + self.big_blind
                max_raise = ai_player.chips
                
                if min_raise >= max_raise:
                    # All-in
                    raise_amount = max_raise
                else:
                    # เลือกจำนวนเงินที่จะเรียกเพิ่ม
                    raise_amount = min(max_raise, max(min_raise, int(min_raise * (1 + np.random.random()))))
                
                self.action_log.append(f"AI decides to raise to {raise_amount}")
                return self.player_action('raise', raise_amount)
            else:
                # Fold หรือกรณีที่ทำการกระทำที่เลือกไม่ได้
                if 'fold' in valid_actions:
                    self.action_log.append("AI decides to fold")
                    return self.player_action('fold')
                elif 'check' in valid_actions:
                    self.action_log.append("AI decides to check")
                    return self.player_action('call')  # check = call with 0 bet
                else:
                    # ตัวเลือกสุดท้าย คือ call
                    self.action_log.append(f"AI decides to call {self.current_bet}")
                    return self.player_action('call')
                    
        except Exception as e:
            print(f"Error in reinforcement AI: {e}")
            # ใช้ AI แบบง่ายเป็น fallback
            return self.ai_move_simple(valid_actions)
    
    def ai_move_advanced_learning(self, valid_actions):
        """AI strategy using Advanced Self-Learning model with Monte Carlo Tree Search"""
        try:
            # สร้างสถานะปัจจุบันของเกม
            state = self._create_state_for_reinforcement()
            
            # ใช้โมเดลขั้นสูงทำนายการกระทำที่ดีที่สุด
            q_values = self.advanced_model.model.predict(np.array([state]))[0]
            
            # เพิ่มความหลากหลายในการเล่น (exploration)
            if random.random() < 0.1:  # 10% โอกาสที่จะบลัฟ
                # สลับการให้ความสำคัญกับการกระทำเพื่อสร้างความไม่แน่นอน
                action_priorities = list(range(3))
                random.shuffle(action_priorities)
                action_idx = action_priorities[0]
            else:
                action_idx = np.argmax(q_values)
            
            # แปลงดัชนีเป็นการกระทำ
            if action_idx == 0 and 'call' in valid_actions:
                self.action_log.append(f"AI decides to call {self.current_bet}")
                return self.player_action('call')
            elif action_idx == 1 and 'raise' in valid_actions:
                ai_player = self.players[1]
                min_raise = self.current_bet + self.big_blind
                max_raise = ai_player.chips
                
                # คำนวณเงินเดิมพันตามความมั่นใจของโมเดล
                confidence = q_values[action_idx] / sum(q_values) if sum(q_values) > 0 else 0.33
                raise_amount = min(max_raise, max(min_raise, int(ai_player.chips * confidence)))
                
                self.action_log.append(f"AI decides to raise to {raise_amount} (confidence: {confidence:.2f})")
                return self.player_action('raise', raise_amount)
            else:
                if 'fold' in valid_actions:
                    self.action_log.append("AI decides to fold")
                    return self.player_action('fold')
                elif 'check' in valid_actions:
                    self.action_log.append("AI decides to check")
                    return self.player_action('call')
                else:
                    self.action_log.append(f"AI decides to call {self.current_bet}")
                    return self.player_action('call')
                    
        except Exception as e:
            print(f"Error in advanced learning AI: {e}")
            # ใช้ AI ที่เป็น Reinforcement แบบปกติเป็น fallback
            return self.ai_move_reinforcement(valid_actions)
    
    def _create_state_for_reinforcement(self):
        """สร้างสถานะของเกมในรูปแบบที่ใช้กับโมเดล Reinforcement Learning"""
        player = self.players[0]
        ai = self.players[1]
        
        # แปลงไพ่ให้อยู่ในรูปแบบที่ใช้กับโมเดล
        player_cards = [card.to_dict() for card in player.hand.cards]
        ai_cards = [card.to_dict() for card in ai.hand.cards]
        community_cards = [card.to_dict() for card in self.community_cards]
        
        # ใช้ฟังก์ชั่นประเมินมือจากโมเดล
        try:
            if hasattr(self, 'reinforcement_model') and self.reinforcement_model:
                win_prob = self.reinforcement_model.evaluate_hands(player_cards, ai_cards, community_cards)
                
                # สร้างเวกเตอร์สถานะ
                rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
                              '8': 8, '9': 9, '10': 10, 'jack': 11, 'queen': 12, 'king': 13, 'ace': 14}
                
                # สร้าง features จากข้อมูลเกม
                player_hand = PokerHand(player.hand.cards)
                ai_hand = PokerHand(ai.hand.cards)
                player_features = player_hand.evaluate()
                ai_features = ai_hand.evaluate()
                
                # สร้างเวกเตอร์สถานะที่ใช้กับ reinforcement model
                state = [
                    player_features.get('value', 0),
                    ai_features.get('value', 0),
                    player_features.get('highest_rank', 0),
                    ai_features.get('highest_rank', 0),
                    player_features.get('lowest_rank', 0),
                    ai_features.get('lowest_rank', 0),
                    player_features.get('rank_diff', 0),
                    ai_features.get('rank_diff', 0),
                    player_features.get('max_rank_count', 0),
                    ai_features.get('max_rank_count', 0),
                    player_features.get('max_suit_count', 0),
                    ai_features.get('max_suit_count', 0),
                    int(player_features.get('is_suited', False)),
                    int(ai_features.get('is_suited', False))
                ]
                
                return state
            else:
                # สร้างสถานะพื้นฐานถ้าไม่มีโมเดล
                return [0] * 14
        except Exception as e:
            print(f"Error creating state for reinforcement model: {e}")
            return [0] * 14
    
    # Calculate probability of winning with current hand
    def calculate_win_probability(self, hand):
        """Calculate probability of winning with current hand using Monte Carlo simulation"""
        # ใช้ Monte Carlo simulation เพื่อประเมินโอกาสชนะ
        if not self.community_cards:
            # ถ้ายังไม่มีไพ่กลาง ใช้การประเมินไพ่มือ
            return self.evaluate_hole_cards(hand)
        
        num_simulations = 1000
        wins = 0
        
        # สร้างสำรับไพ่ที่เหลือ
        remaining_deck = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                # ตรวจสอบว่าไพ่ไม่ได้อยู่ในมือหรือไพ่กลางแล้ว
                card_in_use = False
                for card in hand.cards + self.community_cards:
                    if card.suit == suit and card.rank == rank:
                        card_in_use = True
                        break
                
                if not card_in_use:
                    remaining_deck.append(Card(suit, rank))
        
        # สร้างโคลนของมือผู้เล่น
        opponent_hand = PokerHand()
        for player in self.players:
            if player.hand != hand:
                opponent_hand = player.hand
                break
        
        # ถ้าไม่รู้ไพ่ของคู่ต่อสู้ (แบบซิมมูเลชัน)
        if not opponent_hand.cards:
            # สุ่มไพ่ให้คู่ต่อสู้ 2 ใบ
            for _ in range(2):
                if remaining_deck:
                    card_idx = random.randint(0, len(remaining_deck) - 1)
                    opponent_hand.add_card(remaining_deck.pop(card_idx))
        
        # ทำซิมมูเลชัน
        for _ in range(num_simulations):
            # สร้างชุดไพ่กลางจากไพ่กลางปัจจุบัน
            community = self.community_cards.copy()
            
            # สร้างสำรับไพ่ที่เหลือสำหรับซิมมูเลชันนี้
            sim_deck = remaining_deck.copy()
            random.shuffle(sim_deck)
            
            # เพิ่มไพ่กลางให้ครบ 5 ใบ
            while len(community) < 5 and sim_deck:
                community.append(sim_deck.pop())
            
            # เปรียบเทียบมือและนับผลลัพธ์
            result = hand.compare_with(opponent_hand, community)
            if result > 0:
                wins += 1
            elif result == 0:
                wins += 0.5  # เสมอนับเป็นครึ่งชัยชนะ
        
        return wins / num_simulations
    
    # Evaluate the strength of a hand (0-1 scale)
    def evaluate_hand_strength(self, hand):
        """Evaluate the strength of a hand on a scale of 0-1"""
        if not self.community_cards:
            return self.evaluate_hole_cards(hand)
        
        # ประเมินโดยตรงจากอันดับของมือ
        hand_name, val = hand.get_hand_rank(self.community_cards)
        hand_value = PokerHand.HAND_RANKS[hand_name] / 9.0  # Normalize to 0-1
        
        # ปรับค่าตามจำนวนไพ่กลาง
        # ถ้ามีไพ่กลางน้อย ความแน่นอนก็น้อย
        confidence = min(1.0, len(self.community_cards) / 3.0)
        
        # ผสมค่าความน่าจะเป็นเริ่มต้นกับค่าที่ประเมินได้
        initial_prob = self.evaluate_hole_cards(hand)
        adjusted_prob = initial_prob * (1 - confidence) + hand_value * confidence
        
        return adjusted_prob
    
    # Evaluate pre-flop hand strength
    def evaluate_hole_cards(self, hand):
        """Evaluate pre-flop hand strength based on starting hand rankings"""
        if len(hand.cards) != 2:
            return 0.5  # Default probability for incomplete hands
        
        # แปลงค่า rank เป็นตัวเลข
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
                      '8': 8, '9': 9, '10': 10, 'jack': 11, 'queen': 12, 'king': 13, 'ace': 14}
        
        rank1 = rank_values[hand.cards[0].rank]
        rank2 = rank_values[hand.cards[1].rank]
        
        # ตรวจสอบว่าไพ่เป็นดอกเดียวกันหรือไม่
        suited = hand.cards[0].suit == hand.cards[1].suit
        
        # ประเมินตามเกณฑ์พื้นฐาน
        
        # Pair
        if rank1 == rank2:
            # High pairs (AA, KK, QQ, JJ, TT)
            if rank1 >= 10:
                return 0.8 + (rank1 - 10) * 0.04  # 0.8 - 0.96
            # Medium pairs (99, 88, 77)
            elif rank1 >= 7:
                return 0.65 + (rank1 - 7) * 0.05  # 0.65 - 0.75
            # Low pairs
            else:
                return 0.5 + (rank1 - 2) * 0.03  # 0.5 - 0.65
        
        # ไพ่ไม่เป็นคู่
        high_card = max(rank1, rank2)
        low_card = min(rank1, rank2)
        gap = high_card - low_card - 1  # ช่องว่างระหว่างไพ่ (0 = ติดกัน)
        
        # Premium hands (AK, AQ, AJ, KQ)
        if high_card >= 11 and low_card >= 10:
            base = 0.65
            if suited:
                base += 0.1
            return base
        
        # Aces with kicker
        if high_card == 14:  # Ace
            base = 0.6 - gap * 0.03
            if suited:
                base += 0.05
            return max(0.3, base)
        
        # Face cards
        if high_card >= 11:  # K, Q, J
            base = 0.5 - gap * 0.03
            if suited:
                base += 0.05
            return max(0.25, base)
        
        # Connected cards (potential straights)
        if gap == 0:
            base = 0.4 + (high_card - 7) * 0.02
            if suited:
                base += 0.1
            return max(0.2, min(0.6, base))
        
        # ไพ่ดอกเดียวกัน (potential flush)
        if suited:
            base = 0.35 + (high_card - 7) * 0.01 - gap * 0.02
            return max(0.2, min(0.5, base))
        
        # ไพ่ทั่วไป
        base = 0.2 + (high_card - 7) * 0.01 - gap * 0.02
        return max(0.1, min(0.4, base))


class GameSettings:
    def __init__(self):
        self.settings = {
            'poker': {
                'search_depth': 5,
                'randomness': 0.1,
                'ai_delay': 0.5,
                'ai_modes': [
                    "Easy - Simple Strategy",
                    "Medium - Probability Based",
                    "Hard - ML Model",
                    "Expert - Reinforcement Learning", 
                    "Master - Advanced Self-Learning"
                ]
            }
        }
    
    def adjust_settings(self, game_type):
        return self.settings.get(game_type, {})
    
    def get_poker_settings(self):
        return self.settings.get('poker', {})
    
    def calculate_thinking_time(self, game_type, move_count, complexity):
        # คำนวณเวลาคิดตามจำนวนการเคลื่อนไหวและความซับซ้อนของเกม
        thinking_time = 0.5 + (move_count * 0.1) + (complexity * 0.2)
        return thinking_time

# สร้างฟังก์ชันเพื่อแสดงเกมในรูปแบบกราฟิก
def display_game(game_state):
    """แสดงเกมในรูปแบบที่เข้าใจง่ายขึ้น"""
    # สีพื้นฐานสำหรับข้อความ
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    
    # สัญลักษณ์ไพ่
    suit_symbols = {
        'hearts': '♥',
        'diamonds': '♦',
        'clubs': '♣',
        'spades': '♠'
    }
    
    suit_colors = {
        'hearts': RED,
        'diamonds': RED,
        'clubs': BLUE,
        'spades': BLUE
    }
    
    # แสดงข้อมูลเกม
    print("\n" + "="*60)
    print(f"{CYAN}♠ ♥ TEXAS HOLD'EM POKER ♦ ♣{RESET}")
    print("="*60)
    
    # แสดงข้อมูลผู้เล่น
    player = game_state['players'][0]
    ai = game_state['players'][1]
    
    # แสดงข้อมูล AI
    print(f"\n{MAGENTA}AI (Difficulty: {game_state.get('ai_level', 'Medium')}){RESET}")
    print(f"Chips: {ai['chips']} | Current Bet: {ai['current_bet']}")
    
    if ai['is_folded']:
        print(f"{RED}[FOLDED]{RESET}")
    elif ai['is_all_in']:
        print(f"{YELLOW}[ALL IN]{RESET}")
    
    # แสดงไพ่ของ AI ถ้าอยู่ในโหมดแสดงไพ่
    ai_cards = []
    if game_state.get('show_ai_cards', False):
        for card in ai['hand']:
            suit_color = suit_colors[card['suit']]
            ai_cards.append(f"{suit_color}{card['rank']}{suit_symbols[card['suit']]}{RESET}")
        print(f"Cards: {' '.join(ai_cards)}")
    else:
        print(f"Cards: {BLUE}[?] [?]{RESET}")
    
    # แสดงข้อมูลกองกลาง
    print("\n" + "-"*60)
    print(f"{GREEN}POT: {game_state['pot']} chips | STAGE: {game_state['stage'].upper()}{RESET}")
    print("-"*60)
    
    # แสดงไพ่กลาง
    if game_state['community_cards']:
        community = []
        for card in game_state['community_cards']:
            suit_color = suit_colors[card['suit']]
            community.append(f"{suit_color}{card['rank']}{suit_symbols[card['suit']]}{RESET}")
        print(f"\nCommunity Cards: {' '.join(community)}")
    else:
        print("\nCommunity Cards: None")
    
    # แสดงข้อมูลผู้เล่น
    print("\n" + "-"*60)
    print(f"{CYAN}YOUR TURN{RESET}" if game_state['current_player_idx'] == 0 else "")
    print(f"{YELLOW}YOU (Player){RESET}")
    print(f"Chips: {player['chips']} | Current Bet: {player['current_bet']}")
    
    if player['is_folded']:
        print(f"{RED}[FOLDED]{RESET}")
    elif player['is_all_in']:
        print(f"{YELLOW}[ALL IN]{RESET}")
    
    # แสดงไพ่ของผู้เล่น
    player_cards = []
    for card in player['hand']:
        suit_color = suit_colors[card['suit']]
        player_cards.append(f"{suit_color}{card['rank']}{suit_symbols[card['suit']]}{RESET}")
    
    print(f"Your Cards: {' '.join(player_cards)}")
    
    # แสดงผู้ชนะถ้ามี
    if game_state.get('winner'):
        print("\n" + "="*60)
        if game_state['winner'] == 'player':
            print(f"\n{GREEN}🏆 YOU WIN! 🏆{RESET}")
        elif game_state['winner'] == 'ai':
            print(f"\n{RED}👑 AI WINS 👑{RESET}")
        else:
            print(f"\n{YELLOW}🤝 DRAW 🤝{RESET}")
        
        # แสดงไพ่ดีที่สุด
        if game_state.get('best_hands'):
            print(f"\nYour best hand: {game_state['best_hands'].get('player', 'None')}")
            print(f"AI's best hand: {game_state['best_hands'].get('ai', 'None')}")
    
    # แสดงการกระทำล่าสุด
    if game_state.get('action_log') and len(game_state['action_log']) > 0:
        print("\nRecent actions:")
        for i, action in enumerate(game_state['action_log'][-3:]):
            print(f"  {action}")
    
    print("\n" + "="*60)


# ปรับปรุงส่วนทดสอบเกม
if __name__ == "__main__":
    # ตรวจสอบว่าระบบรองรับการแสดงผลสีหรือไม่
    try:
        import colorama
        colorama.init()
        has_color = True
    except ImportError:
        has_color = False
        print("Note: Install 'colorama' for colored display (pip install colorama)")
    
    game = PokerGame()
    game.setup_new_game()
    
    # ทดสอบการเล่นเกม
    playing = True
    ai_mode = 1  # เริ่มต้นด้วย AI ระดับกลาง
    
    print("\n" + "="*60)
    print("🃏 Welcome to Texas Hold'em Poker! 🃏")
    print("="*60)
    print("\nSelect AI difficulty level:")
    print("0: Easy (Simple AI)")
    print("1: Medium (Probability-based AI)")
    print("2: Hard (ML Model)")
    print("3: Expert (Reinforcement Learning)")
    print("4: Master (Advanced Self-Learning)")
    
    ai_choice = input("Enter AI level (0-4, default 1): ")
    if ai_choice in ["0", "1", "2", "3", "4"]:
        ai_mode = int(ai_choice)
    
    print(f"\nPlaying against AI level {ai_mode}")
    print("Starting game...\n")
    
    # กำหนดตัวแปรเพื่อเก็บประวัติเกม
    game_history = []
    current_game_record = {}
    
    try:
        while playing:
            # แสดงสถานะเกม
            state = game.get_game_state(show_ai_cards=False)
            state['ai_level'] = ["Easy", "Medium", "Hard", "Expert", "Master"][ai_mode]
            display_game(state)
            
            # ถ้ามีผู้ชนะแล้ว ให้เริ่มเกมใหม่หรือจบเกม
            if game.winner:
                # บันทึกผลลัพธ์ของเกม
                current_game_record = {
                    'winner': game.winner,
                    'pot': game.pot,
                    'community_cards': [card.to_dict() for card in game.community_cards],
                    'player_hand': game.players[0].hand.to_dict(),
                    'ai_hand': game.players[1].hand.to_dict(),
                    'ai_mode': ai_mode
                }
                game_history.append(current_game_record)
                
                # แสดงไพ่ของ AI ตอนจบเกม
                if not game.players[1].is_folded:
                    print("\nAI's cards:")
                    for card in game.players[1].hand.cards:
                        print(f"  {card}")
                
                choice = input("\nPlay again? (y/n): ")
                if choice.lower() != 'y':
                    playing = False
                    print("Thanks for playing!")
                    break
                
                # เริ่มเกมใหม่โดยเก็บชิปต่อ
                player_chips = game.players[0].chips
                ai_chips = game.players[1].chips
                game.setup_new_game(player_chips, ai_chips)
                continue
            
            # ถ้าถึงตาผู้เล่น
            if game.current_player_idx == 0:
                valid_actions = game.get_valid_actions()
                
                # แสดงตัวเลือกการเล่น
                options = []
                for action in valid_actions:
                    if action == "fold":
                        options.append("(f)old")
                    elif action == "check":
                        options.append("(c)heck")
                    elif action == "call":
                        call_amount = game.current_bet - game.players[0].current_bet
                        options.append(f"(c)all ({call_amount} chips)")
                    elif action == "raise":
                        min_raise = max(game.current_bet * 2, game.big_blind)
                        options.append(f"(r)aise (min {min_raise} chips)")
                    elif action == "all-in":
                        options.append("all-(i)n")
                
                action_prompt = f"\nYour turn. Choose action ({', '.join(options)}): "
                user_input = input(action_prompt).lower()
                
                # แปลงคำสั่งย่อเป็นคำสั่งเต็ม
                action = None
                if user_input in ['f', 'fold']:
                    action = "fold"
                elif user_input in ['c', 'check', 'call']:
                    if "check" in valid_actions:
                        action = "check"
                    elif "call" in valid_actions:
                        action = "call"
                elif user_input in ['r', 'raise']:
                    action = "raise"
                elif user_input in ['i', 'all-in']:
                    action = "all-in"
                
                # ตรวจสอบว่าการกระทำถูกต้อง
                if action not in valid_actions:
                    print(f"Invalid action. Please choose from: {', '.join(valid_actions)}")
                    continue
                
                # รับจำนวนเงินเดิมพันถ้าเลือก raise
                bet_amount = 0
                if action == "raise":
                    min_bet = max(game.current_bet * 2, game.big_blind)
                    max_bet = game.players[0].chips + game.players[0].current_bet
                    bet_prompt = f"Enter bet amount ({min_bet}-{max_bet}): "
                    
                    try:
                        bet_amount = int(input(bet_prompt))
                        if bet_amount < min_bet or bet_amount > max_bet:
                            print(f"Invalid bet amount. Must be between {min_bet} and {max_bet}")
                            continue
                    except ValueError:
                        print("Please enter a valid number")
                        continue
                
                # ดำเนินการตามที่ผู้เล่นเลือก
                game.player_action(action, bet_amount)
                
                # บันทึกประวัติการเล่น
                if 'actions' not in current_game_record:
                    current_game_record['actions'] = []
                
                current_game_record['actions'].append({
                    'player': 'player',
                    'action': action,
                    'amount': bet_amount if action == 'raise' else 0,
                    'stage': game.game_stage
                })
            
            # ถ้าถึงตา AI
            else:
                print("\nAI is thinking...")
                import time
                
                # คำนวณเวลาคิดตามความซับซ้อนของเกม
                complexity = game.calculate_game_complexity()
                thinking_time = game.game_settings.calculate_thinking_time(
                    'poker', 
                    len(game_state.get('action_log', [])), 
                    complexity
                )
                
                # ใช้ advanced AI ถ้าเลือกระดับยาก
                if ai_mode == 2:
                    try:
                        # ลองเรียกใช้ huggingface model
                        from huggingface_poker import load_model, predict
                        
                        # แสดงว่ากำลังใช้ advanced AI
                        print("Using advanced AI...")
                        
                        # ข้อมูลไพ่
                        player_cards = [card.to_dict() for card in game.players[0].hand.cards]
                        ai_cards = [card.to_dict() for card in game.players[1].hand.cards]
                        community_cards = [card.to_dict() for card in game.community_cards]
                        
                        # ถ้าไพ่กลางยังไม่ครบ ใช้การคาดเดา
                        while len(community_cards) < 2:
                            # สร้างไพ่สมมติ
                            dummy_card = {"rank": "2", "suit": "Clubs"}
                            community_cards.append(dummy_card)
                        
                        # โหลดโมเดลเพื่อทำนาย
                        try:
                            tokenizer, model = load_model()
                            prediction = predict(tokenizer, model, player_cards, ai_cards, community_cards[:2])
                            print(f"AI prediction: {prediction}")
                            # AI จะปรับกลยุทธ์ตามผลการทำนาย
                        except Exception as e:
                            print(f"Advanced AI error: {e}")
                            # ถ้าเกิดข้อผิดพลาด ใช้ AI แบบธรรมดา
                            ai_mode = 1
                    except ImportError:
                        print("Advanced AI model not available, using standard AI")
                        ai_mode = 1
                
                # แสดงเวลาที่ AI ใช้คิด
                time.sleep(thinking_time)
                
                # AI ตัดสินใจ
                game.ai_move(ai_mode)
                
                # บันทึกประวัติการเล่น
                if 'actions' not in current_game_record:
                    current_game_record['actions'] = []
                
                current_game_record['actions'].append({
                    'player': 'ai',
                    'action': game.action_log[-1] if game.action_log else 'unknown',
                    'stage': game.game_stage
                })
                
        # บันทึกประวัติการเล่นลงไฟล์
        if game_history:
            try:
                history_path = os.path.join('DatasetPokerzombitx64', 'game_history.json')
                os.makedirs(os.path.dirname(history_path), exist_ok=True)
                
                existing_history = []
                if os.path.exists(history_path):
                    with open(history_path, 'r') as f:
                        existing_history = json.load(f)
                
                combined_history = existing_history + game_history
                
                with open(history_path, 'w') as f:
                    json.dump(combined_history, f, indent=2)
                print(f"\nGame history saved to {history_path}")
            except Exception as e:
                print(f"Error saving game history: {e}")
    
    except KeyboardInterrupt:
        print("\nGame interrupted. Exiting...")
    except Exception as e:
        import traceback
        print(f"\nError occurred: {e}")
        traceback.print_exc()
    finally:
        # แสดงผลสถิติสุดท้าย
        print("\nFinal Statistics:")
        print(f"Games played: {game.stats['total_games']}")
        print(f"Player wins: {game.stats['player_wins']}")
        print(f"AI wins: {game.stats['ai_wins']}")
        print(f"Player win rate: {(game.stats['player_wins'] / max(1, game.stats['total_games'])) * 100:.1f}%")
        print(f"Biggest pot: {game.stats['biggest_pot']} chips")
        if game.stats.get('best_hand'):
            print(f"Best hand achieved: {game.stats['best_hand']}")
        
        if colorama and has_color:
            colorama.deinit()
