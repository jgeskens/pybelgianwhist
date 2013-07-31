import random
import sys

RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace')
SUITS = ('spades', 'clubs', 'diamonds', 'hearts')

class Card(object):
    """
    Represents a playing card
    """
    
    def __init__(self, rank, suit):
        self.name = '%s of %s' % (RANKS[rank], SUITS[suit])
        self.rank = rank
        self.suit = suit
        
    def __repr__(self):
        return '<Card: %s>' % self.name
    
    def __str__(self):
        return self.name


def find_card_from_string(s, cards):
    rank_str, suit_str = s.split(' of ')
    rank = RANKS.index(rank_str)
    suit = SUITS.index(suit_str)
    found = [i for i, c in enumerate(cards) if c.rank == rank and c.suit == suit]
    return found[0] if found else None


class Deck(object):
    def __init__(self):
        self.deck = [Card(i % 13, i / 13) for i in xrange(52)]
    
    def shuffle(self):
        random.shuffle(self.deck)
    
    def hef_af(self, height=-1):
        height = height >= 0 and height or random.randrange(52)
        self.deck = self.deck[height:] + self.deck[:height]
    
    def pop(self, count):
        popped = self.deck[:count]
        self.deck = self.deck[count:]
        return popped


class Game(object):
    def __init__(self, players):
        self.deck = Deck()
        self.players = players
        self.dealer = 0
        self.trump = None
        self.playing = 1
    
    def deal(self):
        p = (self.dealer + 1) % 4
        
        for i in xrange(4):
            self.players[p].hand += self.deck.pop(4)
            p = (p + 1) % 4
        
        for i in xrange(4):
            self.players[p].hand += self.deck.pop(4)
            p = (p + 1) % 4
        
        for i in xrange(4):
            self.players[p].hand += self.deck.pop(5)
            if i == 3:
                self.trump = self.players[p].hand[-1]
            self.players[p].sort()
            p = (p + 1) % 4
    
    def bidding(self):
        pass

class Player(object):
    def __init__(self, name, ai):
        self.hand = []
        self.name = name
        self.ai = ai
    
    def sort(self):
        self.hand = sum((self.sorted_suit(i) for i in (0, 2, 1, 3)), [])
    
    def sorted_suit(self, suit):
        return sorted((c for c in self.hand if c.suit == suit), key=lambda card: card.rank)
    
    def highest(self, suit):
        return self.sorted_suit(suit)[-1]
    
    def lowest(self, suit):
        return self.sorted_suit(suit)[0]
    
    def play(self, game):
        card = self.ai.play(self, game)
        print('%s plays %s.' % (self.name, card))
    
    def __repr__(self):
        return '<Player: %s (%s)>' % (self.name, ', '.join(map(str, self.hand)))
    

class AI(object):
    def play(self, player, game):
        return player.hand.pop()

class Human(object):
    def play(self, player, game):
        print(player)
        print('%s, which card? ' % player.name)
        
        sys.stdout.flush()
        card_index = find_card_from_string(raw_input(), player.hand)
        
        return player.hand.pop(card_index)

if __name__ == '__main__':
    random.seed()
    
    print('Welcome to Belgian Whist!')
    g = Game((Player('Jef', AI()), Player('Koen', Human()), Player('Ingo', AI()), Player('Olivier', AI())))
    g.deck.shuffle()
    g.deck.hef_af()
    g.deal()
    print('Trump card is %s.' % g.trump)
    
    player = g.players[g.playing]
    while len(player.hand) > 0:
        player.play(g)
        
        g.playing = (g.playing + 1) % 4
        player = g.players[g.playing]
    
    

