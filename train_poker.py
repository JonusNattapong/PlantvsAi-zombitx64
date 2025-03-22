import sys
sys.path.append('src/PlantvsAi_zombitx64/game')

from poker_model import PokerModel
from poker_data_generator import PokerDataGenerator
import os

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
