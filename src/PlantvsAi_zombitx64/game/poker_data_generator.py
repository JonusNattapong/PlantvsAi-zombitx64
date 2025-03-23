import numpy as np
from poker import Card, PokerHand
import json
import os

class PokerDataGenerator:
    def __init__(self, num_samples=100000):  
        self.num_samples = num_samples
        self.data = []
        
    def generate_hand(self):
        """Generate a random poker hand with more features"""
        deck = [Card(suit, rank) for suit in Card.SUITS for rank in Card.RANKS]
        np.random.shuffle(deck)
        
        # Deal cards
        player_hand = PokerHand(deck[:2])
        ai_hand = PokerHand(deck[2:4])
        community_cards = deck[4:9]
        
        return player_hand, ai_hand, community_cards
    
    def evaluate_hand(self, hand, community_cards):
        """Evaluate the strength of a poker hand with more detailed features"""
        # Get hand type and value
        hand_type, value = hand.get_hand_rank(community_cards)
        
        # Get ranks and suits
        ranks = [card.rank for card in hand.cards]
        suits = [card.suit for card in hand.cards]
        
        # Convert ranks to numbers
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
                      '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        numeric_ranks = [rank_values[rank] for rank in ranks]
        
        # Get rank and suit frequencies
        rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
        suit_counts = {suit: suits.count(suit) for suit in set(suits)}
        
        # Get highest and lowest ranks
        highest_rank = max(numeric_ranks)
        lowest_rank = min(numeric_ranks)
        rank_diff = highest_rank - lowest_rank
        
        return {
            'hand_type': PokerHand.HAND_RANKS[hand_type],
            'value': value,
            'highest_rank': highest_rank,
            'lowest_rank': lowest_rank,
            'rank_diff': rank_diff,
            'max_rank_count': max(rank_counts.values()) if rank_counts else 0,
            'max_suit_count': max(suit_counts.values()) if suit_counts else 0,
            'is_suited': len(set(suits)) == 1,
            'pair_rank': next((r for r, c in rank_counts.items() if c == 2), None)
        }
    
    def generate_dataset(self):
        """Generate poker dataset with more features"""
        for _ in range(self.num_samples):
            player_hand, ai_hand, community_cards = self.generate_hand()
            
            # Evaluate both hands
            player_features = self.evaluate_hand(player_hand, community_cards)
            ai_features = self.evaluate_hand(ai_hand, community_cards)
            
            # Determine winner
            if player_features['hand_type'] > ai_features['hand_type']:
                winner = 'player'
            elif player_features['hand_type'] < ai_features['hand_type']:
                winner = 'ai'
            else:
                # Compare values if ranks are equal
                if player_features['value'] > ai_features['value']:
                    winner = 'player'
                elif player_features['value'] < ai_features['value']:
                    winner = 'ai'
                else:
                    winner = 'draw'
            
            # Create feature vector with more features
            features = {
                'player_cards': [card.to_dict() for card in player_hand.cards],
                'ai_cards': [card.to_dict() for card in ai_hand.cards],
                'community_cards': [card.to_dict() for card in community_cards],
                'player_hand_type': player_features['hand_type'],
                'ai_hand_type': ai_features['hand_type'],
                'player_highest_rank': player_features['highest_rank'],
                'ai_highest_rank': ai_features['highest_rank'],
                'player_lowest_rank': player_features['lowest_rank'],
                'ai_lowest_rank': ai_features['lowest_rank'],
                'player_rank_diff': player_features['rank_diff'],
                'ai_rank_diff': ai_features['rank_diff'],
                'player_max_rank_count': player_features['max_rank_count'],
                'ai_max_rank_count': ai_features['max_rank_count'],
                'player_max_suit_count': player_features['max_suit_count'],
                'ai_max_suit_count': ai_features['max_suit_count'],
                'player_is_suited': int(player_features['is_suited']),
                'ai_is_suited': int(ai_features['is_suited']),
                'winner': winner
            }
            
            self.data.append(features)
        
        print(f"Generated {len(self.data)} poker games dataset")
    
    def get_training_data(self):
        """Convert dataset to numpy arrays for training"""
        X = []
        y = []
        
        for game in self.data:
            # Create feature vector with more features
            features = [
                game['player_hand_type'],
                game['ai_hand_type'],
                game['player_highest_rank'],
                game['ai_highest_rank'],
                game['player_lowest_rank'],
                game['ai_lowest_rank'],
                game['player_rank_diff'],
                game['ai_rank_diff'],
                game['player_max_rank_count'],
                game['ai_max_rank_count'],
                game['player_max_suit_count'],
                game['ai_max_suit_count'],
                game['player_is_suited'],
                game['ai_is_suited']
            ]
            
            # Convert winner to numeric label
            if game['winner'] == 'player':
                label = 1.0
            elif game['winner'] == 'ai':
                label = 0.0
            else:
                label = 0.5
            
            X.append(features)
            y.append(label)
        
        return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)
    
    def save_dataset(self, filename='poker_dataset.json'):
        """Save dataset to file"""
        os.makedirs('DatasetPokerzombitx64', exist_ok=True)
        with open(os.path.join('DatasetPokerzombitx64', filename), 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def load_dataset(self, filename='poker_dataset.json'):
        """Load dataset from file"""
        with open(os.path.join('DatasetPokerzombitx64', filename), 'r') as f:
            self.data = json.load(f)

if __name__ == "__main__":
    generator = PokerDataGenerator(num_samples=100000)  
    generator.generate_dataset()
    generator.save_dataset()
    print("Dataset generation completed")
