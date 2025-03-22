import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import json
import os

class PokerModel:
    def __init__(self):
        self.model = None
        self.history = None
        
    def build_model(self):
        """Build the neural network model"""
        self.model = Sequential([
            Dense(128, activation='relu', input_shape=(6,)),
            Dropout(0.2),
            Dense(64, activation='relu'),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
    
    def train(self, X, y, epochs=50, batch_size=32, validation_split=0.2):
        """Train the model"""
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
    
    def save_model(self, filename='poker_model.h5'):
        """Save the model to file"""
        os.makedirs('DatasetPokerzombitx64', exist_ok=True)
        self.model.save(os.path.join('DatasetPokerzombitx64', filename))
    
    def load_model(self, filename='poker_model.h5'):
        """Load the model from file"""
        from tensorflow.keras.models import load_model
        self.model = load_model(os.path.join('DatasetPokerzombitx64', filename))
    
    def evaluate_hand(self, player_cards, ai_cards, community_cards):
        """Evaluate a poker hand using the model"""
        # Create feature vector
        features = [
            player_cards[0]['rank'],
            player_cards[1]['rank'],
            ai_cards[0]['rank'],
            ai_cards[1]['rank'],
            community_cards[0]['rank'],
            community_cards[1]['rank']
        ]
        
        # Make prediction
        prediction = self.predict(np.array([features]))[0][0]
        
        # Convert prediction to win probability
        win_prob = max(0, min(1, prediction))
        
        return win_prob

if __name__ == "__main__":
    # Generate dataset if not exists
    if not os.path.exists('DatasetPokerzombitx64/poker_dataset.json'):
        from poker_data_generator import PokerDataGenerator
        generator = PokerDataGenerator()
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
