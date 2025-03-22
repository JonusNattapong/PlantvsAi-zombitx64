import sys
sys.path.append('src/PlantvsAi_zombitx64/game')

from poker_model import PokerModel
from poker import Card, PokerHand
import numpy as np

def test_poker():
    # Create a model instance
    model = PokerModel()
    model.load_model()
    
    # Example cards
    player_cards = [Card('Hearts', 'A'), Card('Diamonds', 'K')]
    ai_cards = [Card('Clubs', 'Q'), Card('Spades', 'J')]
    community_cards = [
        Card('Hearts', '10'),
        Card('Diamonds', '9'),
        Card('Clubs', '8'),
        Card('Spades', '7'),
        Card('Hearts', '6')
    ]
    
    # Get win probability
    win_prob = model.evaluate_hand(
        player_cards=[card.to_dict() for card in player_cards],
        ai_cards=[card.to_dict() for card in ai_cards],
        community_cards=[card.to_dict() for card in community_cards]
    )
    
    print(f"Player cards: {[str(card) for card in player_cards]}")
    print(f"AI cards: {[str(card) for card in ai_cards]}")
    print(f"Community cards: {[str(card) for card in community_cards]}")
    print(f"Player win probability: {win_prob:.2%}")

if __name__ == "__main__":
    test_poker()
