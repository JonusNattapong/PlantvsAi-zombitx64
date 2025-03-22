import numpy as np
from PlantvsAi_zombitx64.game.poker import Card, PokerHand
import json
import os

class PokerDataGenerator:
    def __init__(self, num_samples=10000):
        self.num_samples = num_samples
        self.data = []
        
    def generate_hand(self):
        """Generate a random poker hand"""
        deck = [Card(suit, rank) for suit in Card.SUITS for rank in Card.RANKS]
        np.random.shuffle(deck)
        
        # Deal 2 cards to player and AI
        player_hand = PokerHand(deck[:2])
        ai_hand = PokerHand(deck[2:4])
        
        # Deal community cards
        community_cards = deck[4:9]
        
        return player_hand, ai_hand, community_cards
    
    def evaluate_hand(self, hand, community_cards):
        """Evaluate the strength of a poker hand"""
        hand_type, value = hand.get_hand_rank(community_cards)
        return PokerHand.HAND_RANKS[hand_type], value
    
    def generate_dataset(self):
        """Generate poker dataset"""
        for _ in range(self.num_samples):
            player_hand, ai_hand, community_cards = self.generate_hand()
            
            # Evaluate both hands
            player_rank, player_value = self.evaluate_hand(player_hand, community_cards)
            ai_rank, ai_value = self.evaluate_hand(ai_hand, community_cards)
            
            # Determine winner
            if player_rank > ai_rank:
                winner = 'player'
            elif player_rank < ai_rank:
                winner = 'ai'
            else:
                # Compare values if ranks are equal
                if player_value > ai_value:
                    winner = 'player'
                elif player_value < ai_value:
                    winner = 'ai'
                else:
                    winner = 'draw'
            
            # Create feature vector
            features = {
                'player_cards': [card.to_dict() for card in player_hand.cards],
                'ai_cards': [card.to_dict() for card in ai_hand.cards],
                'community_cards': [card.to_dict() for card in community_cards],
                'player_rank': player_rank,
                'ai_rank': ai_rank,
                'winner': winner
            }
            
            self.data.append(features)
        
    def save_dataset(self, filename='poker_dataset.json'):
        """Save dataset to file"""
        os.makedirs('DatasetPokerzombitx64', exist_ok=True)
        with open(os.path.join('DatasetPokerzombitx64', filename), 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def load_dataset(self, filename='poker_dataset.json'):
        """Load dataset from file"""
        with open(os.path.join('DatasetPokerzombitx64', filename), 'r') as f:
            self.data = json.load(f)
    
    def get_training_data(self):
        """Convert dataset to numpy arrays for training"""
        X = []
        y = []
        
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
                      '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        for game in self.data:
            # Create feature vector with numeric values
            features = [
                rank_values[game['player_cards'][0]['rank']],
                rank_values[game['player_cards'][1]['rank']],
                rank_values[game['ai_cards'][0]['rank']],
                rank_values[game['ai_cards'][1]['rank']],
                game['player_rank'],
                game['ai_rank']
            ]
            
            # Convert winner to numeric label
            if game['winner'] == 'player':
                label = 1
            elif game['winner'] == 'ai':
                label = 0
            else:
                label = 0.5
            
            X.append(features)
            y.append(label)
        
        return np.array(X), np.array(y)

if __name__ == "__main__":
    generator = PokerDataGenerator(num_samples=10000)
    generator.generate_dataset()
    generator.save_dataset()
    print(f"Generated {len(generator.data)} poker games dataset")
