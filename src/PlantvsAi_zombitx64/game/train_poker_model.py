from PlantvsAi_zombitx64.game.poker_data_generator import PokerDataGenerator
from PlantvsAi_zombitx64.game.poker_model import PokerModel
import os

def main():
    # Create data generator
    generator = PokerDataGenerator(num_samples=10000)
    
    # Generate dataset if not exists
    if not os.path.exists('DatasetPokerzombitx64/poker_dataset.json'):
        print("Generating dataset...")
        generator.generate_dataset()
        generator.save_dataset()
        print("Dataset generated")
    else:
        print("Loading existing dataset...")
        generator.load_dataset()
    
    # Get training data
    X, y = generator.get_training_data()
    
    # Create and train model
    model = PokerModel()
    model.build_model()
    print("\nTraining model...")
    model.train(X, y, epochs=50, batch_size=32, validation_split=0.2)
    
    # Save model
    model.save_model()
    print("\nModel training completed and saved")

if __name__ == "__main__":
    main()
