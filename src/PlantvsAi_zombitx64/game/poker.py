class Card:
    SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        
    def to_dict(self):
        return {'suit': self.suit, 'rank': self.rank}

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def __repr__(self):
        return str(self)


class PokerHand:
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

    def __init__(self, cards):
        self.cards = cards
        
    def get_hand_rank(self, community_cards):
        all_cards = self.cards + community_cards
        ranks = [card.rank for card in all_cards]
        suits = [card.suit for card in all_cards]
        
        # Check for flush
        flush = any(suits.count(suit) >= 5 for suit in Card.SUITS)
        
        # Convert ranks to numbers
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
                      '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        numeric_ranks = [rank_values[rank] for rank in ranks]
        
        # Check for straight
        sorted_ranks = sorted(numeric_ranks)
        is_straight = any(sorted_ranks[i] == sorted_ranks[i+1] - 1 
                         for i in range(len(sorted_ranks)-4))
        
        # Count rank frequencies
        rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
        
        # Determine hand type
        if flush and is_straight:
            if set(ranks) == {'10', 'J', 'Q', 'K', 'A'}:
                return 'Royal Flush', max(numeric_ranks)
            return 'Straight Flush', max(numeric_ranks)
        elif 4 in rank_counts.values():
            return 'Four of a Kind', max(numeric_ranks)
        elif 3 in rank_counts.values() and 2 in rank_counts.values():
            return 'Full House', max(numeric_ranks)
        elif flush:
            return 'Flush', max(numeric_ranks)
        elif is_straight:
            return 'Straight', max(numeric_ranks)
        elif 3 in rank_counts.values():
            return 'Three of a Kind', max(numeric_ranks)
        elif list(rank_counts.values()).count(2) == 2:
            return 'Two Pair', max(numeric_ranks)
        elif 2 in rank_counts.values():
            return 'One Pair', max(numeric_ranks)
        return 'High Card', max(numeric_ranks)
