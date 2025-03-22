import json
import os
import random
import numpy np
from collections import Counter

class Card:
    """
    คลาสสำหรับเก็บข้อมูลของไพ่แต่ละใบ
    """
    SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __repr__(self):
        return f"{self.rank} of {self.suit}"
    
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
        'high_card': 0,
        'pair': 1,
        'two_pair': 2,
        'three_of_a_kind': 3,
        'straight': 4,
        'flush': 5,
        'full_house': 6,
        'four_of_a_kind': 7,
        'straight_flush': 8,
        'royal_flush': 9
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
        suits = [card.suit for card in all_cards]
        ranks = [card.get_rank_value() for card in all_cards]
        
        # ตรวจสอบ flush
        is_flush = any(suits.count(suit) >= 5 for suit in Card.SUITS)
        
        # ตรวจสอบ straight
        sorted_ranks = sorted(set(ranks))
        straight_count = 1
        is_straight = False
        
        for i in range(1, len(sorted_ranks)):
            if sorted_ranks[i] == sorted_ranks[i-1] + 1:
                straight_count += 1
                if straight_count >= 5:
                    is_straight = True
            else:
                straight_count = 1
        
        # ตรวจสอบ A-5 straight (special case ที่ A มีค่าเป็น 1)
        if 12 in ranks and all(i in ranks for i in range(4)):
            is_straight = True
        
        # นับจำนวนไพ่แต่ละอัน
        rank_counts = Counter(ranks)
        
        # ตรวจสอบ combos
        has_four = 4 in rank_counts.values()
        has_three = 3 in rank_counts.values()
        pairs = sum(1 for count in rank_counts.values() if count == 2)
        
        # Royal flush
        if is_flush and is_straight and 12 in ranks and 11 in ranks and 10 in ranks and 9 in ranks and 8 in ranks:
            return ('royal_flush', None)
        
        # Straight flush
        if is_flush and is_straight:
            return ('straight_flush', max(sorted_ranks))
        
        # Four of a kind
        if has_four:
            four_rank = next(rank for rank, count in rank_counts.items() if count == 4)
            return ('four_of_a_kind', four_rank)
        
        # Full house
        if has_three and pairs > 0:
            three_rank = next(rank for rank, count in rank_counts.items() if count == 3)
            pair_rank = next(rank for rank, count in rank_counts.items() if count == 2)
            return ('full_house', (three_rank, pair_rank))
        
        # Flush
        if is_flush:
            flush_suit = next(suit for suit in Card.SUITS if suits.count(suit) >= 5)
            flush_cards = [card for card in all_cards if card.suit == flush_suit]
            ranks = sorted([card.get_rank_value() for card in flush_cards], reverse=True)
            return ('flush', ranks[:5])
        
        # Straight
        if is_straight:
            # Handle A-5 straight
            if 12 in ranks and all(i in ranks for i in range(4)):
                return ('straight', 3)  # 5-high straight
            return ('straight', max(sorted_ranks))
        
        # Three of a kind
        if has_three:
            three_rank = next(rank for rank, count in rank_counts.items() if count == 3)
            return ('three_of_a_kind', three_rank)
        
        # Two pair
        if pairs >= 2:
            pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
            pair_ranks.sort(reverse=True)
            return ('two_pair', (pair_ranks[0], pair_ranks[1]))
        
        # Pair
        if pairs == 1:
            pair_rank = next(rank for rank, count in rank_counts.items() if count == 2)
            return ('pair', pair_rank)
        
        # High card
        high_card = max(ranks)
        return ('high_card', high_card)
    
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
            # Add hand descriptions
            'hand_descriptions': {
                'high_card': 'High Card',
                'pair': 'Pair',
                'two_pair': 'Two Pair',
                'three_of_a_kind': 'Three of a Kind',
                'straight': 'Straight',
                'flush': 'Flush',
                'full_house': 'Full House',
                'four_of_a_kind': 'Four of a Kind',
                'straight_flush': 'Straight Flush',
                'royal_flush': 'Royal Flush'
            }
        }
        return state
    
    def next_stage(self):
        """Move to the next stage of the game"""
        if self.game_stage == "pre_flop":
            self.game_stage = "flop"
            # Deal flop (3 cards)
            for _ in range(3):
                self.community_cards.append(self.deck.deal())
        
        elif self.game_stage == "flop":
            self.game_stage = "turn"
            # Deal turn (1 card)
            self.community_cards.append(self.deck.deal())
        
        elif self.game_stage == "turn":
            self.game_stage = "river"
            # Deal river (1 card)
            self.community_cards.append(self.deck.deal())
        
        elif self.game_stage == "river":
            self.game_stage = "showdown"
            self.determine_winner()
        
        # Reset betting round
        self.current_player_idx = 0
        self.current_bet = 0
        for player in self.players:
            if not player.is_folded and not player.is_all_in:
                player.current_bet = 0
    
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
            self.update_stats("default", self.winner, self.pot, hand_name)
            
            return
        
        # Compare hands
        best_player = None
        best_hand_name = None
        
        for player in active_players:
            hand_name, _ = player.hand.get_hand_rank(self.community_cards)
            player.hand_name = hand_name  # Store the hand name for each player
            
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
        else:
            # No winner (shouldn't happen)
            self.winner = "draw"
        
        # Update stats
        self.update_stats("default", self.winner, self.pot, best_hand_name)
    
    def player_action(self, action, bet_amount=0):
        """Process player action (call, raise, fold)"""
        if self.game_stage == "showdown" or self.winner:
            return False
        
        current_player = self.players[self.current_player_idx]
        
        if action == "fold":
            current_player.fold()
            # Check if only one player left
            active_players = [p for p in self.players if not p.is_folded]
            if len(active_players) == 1:
                self.winner = active_players[0].name.lower()
                active_players[0].chips += self.pot
                self.update_stats("default", self.winner, self.pot)
                return True
        
        elif action == "call":
            amount_to_call = self.current_bet - current_player.current_bet
            amount_called = current_player.bet(amount_to_call)
            self.pot += amount_called
        
        elif action == "raise" or action == "bet":
            # Minimum raise is double the current bet
            min_raise = self.current_bet * 2
            bet_amount = max(min_raise, bet_amount)
            
            amount_to_raise = bet_amount - current_player.current_bet
            amount_raised = current_player.bet(amount_to_raise)
            self.pot += amount_raised
            self.current_bet = current_player.current_bet
        
        elif action == "check":
            # Check is only valid if no bet has been made
            if current_player.current_bet < self.current_bet:
                return False
            # No action needed for check
        
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
        """Handle AI's move"""
        if self.game_stage == "showdown" or self.winner:
            return False
        
        if self.current_player_idx != 1:  # AI is player 1
            return False
        
        ai_player = self.players[1]
        
        if ai_player.is_folded or ai_player.is_all_in:
            return False
        
        # Get valid actions
        valid_actions = self.get_valid_actions()
        
        # Use different AI strategies based on mode
        if ai_mode == 0:  # Simple AI
            return self.ai_move_simple(valid_actions)
        elif ai_mode == 1:  # Probability-based AI
            return self.ai_move_probability(valid_actions)
        elif ai_mode == 2:  # Advanced AI with bluffing
            return self.ai_move_advanced(valid_actions)
        else:
            return self.ai_move_simple(valid_actions)
    
    def ai_move_simple(self, valid_actions):
        """Simple AI strategy"""
        ai_player = self.players[1]
        hand_strength = self.evaluate_hand_strength(ai_player.hand)
        
        # Simple thresholds for decisions
        if hand_strength > 0.7:
            # Strong hand
            if "raise" in valid_actions:
                bet_amount = min(self.current_bet * 2, ai_player.chips)
                return self.player_action("raise", bet_amount)
            elif "call" in valid_actions:
                return self.player_action("call")
            else:
                return self.player_action("check")
        elif hand_strength > 0.4:
            # Medium hand
            if "call" in valid_actions and self.current_bet <= ai_player.chips // 5:
                return self.player_action("call")
            elif "check" in valid_actions:
                return self.player_action("check")
            else:
                return self.player_action("fold")
        else:
            # Weak hand
            if "check" in valid_actions:
                return self.player_action("check")
            else:
                return self.player_action("fold")
    
    def ai_move_probability(self, valid_actions):
        """Probability-based AI strategy"""
        ai_player = self.players[1]
        hand_strength = self.evaluate_hand_strength(ai_player.hand)
        
        # Calculate pot odds
        pot_odds = (self.current_bet - ai_player.current_bet) / (self.pot + (self.current_bet - ai_player.current_bet))
        
        # Decision making based on pot odds and hand strength
        if hand_strength > pot_odds * 1.5:
            # Positive expected value - raise or call
            if "raise" in valid_actions and hand_strength > 0.6:
                bet_amount = min(self.current_bet * 2, ai_player.chips)
                if random.random() < hand_strength:
                    # Sometimes raise more with stronger hands
                    bet_amount = min(self.current_bet * 3, ai_player.chips)
                return self.player_action("raise", bet_amount)
            elif "call" in valid_actions:
                return self.player_action("call")
            else:
                return self.player_action("check")
        elif hand_strength > pot_odds:
            # Borderline call
            if "call" in valid_actions:
                return self.player_action("call")
            else:
                return self.player_action("check")
        else:
            # Negative expected value - check or fold
            if "check" in valid_actions:
                return self.player_action("check")
            else:
                # Occasionally call anyway (semi-bluff)
                if random.random() < 0.2 and "call" in valid_actions:
                    return self.player_action("call")
                else:
                    return self.player_action("fold")
    
    def ai_move_advanced(self, valid_actions):
        """Advanced AI strategy with bluffing"""
        ai_player = self.players[1]
        hand_strength = self.evaluate_hand_strength(ai_player.hand)
        
        # Calculate pot odds
        pot_odds = (self.current_bet - ai_player.current_bet) / (self.pot + (self.current_bet - ai_player.current_bet)) if self.current_bet > ai_player.current_bet else 0
        
        # Track opponent's behavior
        opponent_aggression = 0.5  # Default: medium aggression
        
        # Adjust for game stage
        stage_multiplier = {
            "pre_flop": 0.8,
            "flop": 1.0,
            "turn": 1.2,
            "river": 1.5
        }
        adjusted_strength = hand_strength * stage_multiplier.get(self.game_stage, 1.0)
        
        # Bluffing probability based on position and opponent
        bluff_probability = 0.1
        if self.game_stage in ["turn", "river"]:
            bluff_probability = 0.25
        
        # Decision making
        if adjusted_strength > 0.8:
            # Very strong hand - maximize value
            if "raise" in valid_actions:
                # Size bet based on pot and stage
                if self.game_stage in ["turn", "river"]:
                    bet_amount = min(self.pot, ai_player.chips)
                else:
                    bet_amount = min(self.current_bet * 2.5, ai_player.chips)
                return self.player_action("raise", bet_amount)
            else:
                return self.player_action("call" if "call" in valid_actions else "check")
        
        elif adjusted_strength > 0.6:
            # Strong hand
            if "raise" in valid_actions and random.random() < 0.7:
                bet_amount = min(self.current_bet * 2, ai_player.chips)
                return self.player_action("raise", bet_amount)
            else:
                return self.player_action("call" if "call" in valid_actions else "check")
        
        elif adjusted_strength > pot_odds * 1.2:
            # Decent hand with positive expected value
            if "call" in valid_actions:
                return self.player_action("call")
            else:
                return self.player_action("check")
        
        else:
            # Weak hand - check, fold, or bluff
            if "check" in valid_actions:
                return self.player_action("check")
            
            # Consider bluffing
            elif random.random() < bluff_probability:
                if "raise" in valid_actions:
                    bet_amount = min(self.current_bet * 2, ai_player.chips)
                    return self.player_action("raise", bet_amount)
                else:
                    return self.player_action("call")
            else:
                return self.player_action("fold")
    
    def evaluate_hand_strength(self, hand):
        """Evaluate the strength of a hand (0-1 scale)"""
        if not self.community_cards:
            # Pre-flop - evaluate based on hole cards only
            return self.evaluate_hole_cards(hand)
        
        # Post-flop - evaluate based on best 5-card hand
        hand_rank, _ = hand.get_hand_rank(self.community_cards)
        rank_value = PokerHand.HAND_RANKS[hand_rank]
        
        # Base strength on hand rank (0-9)
        base_strength = rank_value / 9.0
        
        # Adjust based on game stage
        if self.game_stage == "flop":
            # On the flop, discount strength since more cards coming
            return base_strength * 0.8
        elif self.game_stage == "turn":
            # On the turn, slightly discount strength
            return base_strength * 0.9
        else:
            # On the river, full strength
            return base_strength
    
    def evaluate_hole_cards(self, hand):
        """Evaluate pre-flop hand strength"""
        if len(hand.cards) != 2:
            return 0
        
        # Convert cards to ranks and suits
        ranks = [card.get_rank_value() for card in hand.cards]
        suits = [card.suit for card in hand.cards]
        
        # Check for pair
        if ranks[0] == ranks[1]:
            # Scale based on rank (higher pairs are stronger)
            pair_value = (ranks[0] / 12.0) * 0.8 + 0.2
            return pair_value
        
        # Check for suited cards
        suited = suits[0] == suits[1]
        
        # High card value
        high_card = max(ranks)
        low_card = min(ranks)
        
        # Connected cards (straight potential)
        connected = abs(ranks[0] - ranks[1]) <= 3
        
        # Base strength calculation
        strength = (high_card / 12.0) * 0.4  # High card contributes 40%
        
        if suited:
            strength += 0.1  # Suited bonus
        
        if connected:
            strength += 0.1  # Connected bonus
            # Closer cards get more bonus
            strength += 0.05 * (3 - abs(ranks[0] - ranks[1]))
        
        # Adjust for specific hand types
        if high_card >= 10 and low_card >= 10:
            strength += 0.15  # Both high cards
        
        # Cap strength
        return min(max(strength, 0), 1)

# Test the Poker game
if __name__ == "__main__":
    game = PokerGame()
    game.setup_new_game()
    
    # Display initial state
    print("Initial game state:")
    print(f"Pot: {game.pot}")
    print(f"Player hand: {game.players[0].hand.cards}")
    print(f"AI hand: {game.players[1].hand.cards}")
    
    # Simulate player calling
    print("\nPlayer calls...")
    game.player_action("call")
    
    # Simulate AI checking
    print("AI checks...")
    game.ai_move_simple(game.get_valid_actions())
    
    # Deal flop
    print("\nDealing flop...")
    game.next_stage()
    print(f"Community cards: {game.community_cards}")
    
    # Evaluate hands
    print("\nHand evaluations:")
    player_rank = game.players[0].hand.get_hand_rank(game.community_cards)
    ai_rank = game.players[1].hand.get_hand_rank(game.community_cards)
    print(f"Player hand: {player_rank[0]}")
    print(f"AI hand: {ai_rank[0]}")
