import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import json
import os
import safetensors.numpy
import tensorflow as tf
from poker_data_generator import PokerDataGenerator

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

class PokerHand:
    def __init__(self, cards):
        self.cards = cards

    def evaluate(self):
        # This method should evaluate the hand and return features
        # For simplicity, let's assume we have the following features
        hand_type = 0  # 0: High card, 1: Pair, 2: Two pairs, 3: Three of a kind, 4: Straight, 5: Flush, 6: Full house, 7: Four of a kind, 8: Straight flush, 9: Royal flush
        highest_rank = 0
        lowest_rank = 0
        rank_diff = 0
        max_rank_count = 0
        max_suit_count = 0
        is_suited = 0

        # Implement the logic to calculate these features
        # For now, let's just assign some dummy values
        hand_type = 1
        highest_rank = 10
        lowest_rank = 5
        rank_diff = 5
        max_rank_count = 2
        max_suit_count = 3
        is_suited = 1

        return {
            'hand_type': hand_type,
            'highest_rank': highest_rank,
            'lowest_rank': lowest_rank,
            'rank_diff': rank_diff,
            'max_rank_count': max_rank_count,
            'max_suit_count': max_suit_count,
            'is_suited': is_suited
        }

class PokerModel:
    def __init__(self):
        self.model = None
        self.history = None
        
    def build_model(self):
        """Build the neural network model with more layers for better performance"""
        self.model = Sequential([
            Dense(256, activation='relu', input_shape=(14,)),  # More input features
            Dropout(0.3),
            Dense(128, activation='relu'),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
    
    def train(self, X, y, epochs=100, batch_size=64, validation_split=0.2):
        """Train the model with more epochs and larger batch size"""
        self.history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )
    
    def predict(self, X):
        """Make predictions"""
        return self.model.predict(X)
    
    def save_model(self, filename='poker_model.safetensors'):
        """Save the model to file in safetensors format"""
        os.makedirs('DatasetPokerzombitx64', exist_ok=True)
        
        # Get model weights
        weights = self.model.get_weights()
        
        # Convert weights to numpy arrays
        weights_dict = {f'layer_{i}': w for i, w in enumerate(weights)}
        
        # Save in safetensors format
        safetensors.numpy.save_file(weights_dict, os.path.join('DatasetPokerzombitx64', filename))
    
    def load_model(self, filename='poker_model.safetensors'):
        """Load the model from file"""
        # Load weights from safetensors
        weights_dict = safetensors.numpy.load_file(os.path.join('DatasetPokerzombitx64', filename))
        
        # Build the model architecture
        self.build_model()
        
        # Set weights
        self.model.set_weights([weights_dict[f'layer_{i}'] for i in range(len(weights_dict))])
    
    def evaluate_hand(self, hand, community):
        """Evaluate a poker hand using the model"""
        return hand.evaluate()

    def evaluate_hands(self, player_cards, ai_cards, community_cards):
        """Evaluate a poker hand using the model"""
        # Create feature vector with more features
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
                      '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        # Create PokerHand objects
        player_hand = PokerHand([Card(card['suit'], card['rank']) for card in player_cards])
        ai_hand = PokerHand([Card(card['suit'], card['rank']) for card in ai_cards])
        community = PokerHand([Card(card['suit'], card['rank']) for card in community_cards])
        
        # Get hand features
        player_features = self.evaluate_hand(player_hand, community.cards)
        ai_features = self.evaluate_hand(ai_hand, community.cards)
        
        features = [
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
        
        # Make prediction
        prediction = self.predict(np.array([features]))[0][0]
        
        # Convert prediction to win probability
        win_prob = max(0, min(1, prediction))
        
        return win_prob

if __name__ == "__main__":
    # Generate dataset if not exists
    if not os.path.exists('DatasetPokerzombitx64/poker_dataset.json'):
        generator = PokerDataGenerator(num_samples=100000)
        generator.generate_dataset()
        generator.save_dataset()
    
    # Load dataset
    generator = PokerDataGenerator()
    generator.load_dataset()
    X, y = generator.get_training_data()
    
    # Train model
    model = PokerModel()
    model.build_model()
    model.train(X, y)
    model.save_model()
    
    print("Model training completed and saved")
