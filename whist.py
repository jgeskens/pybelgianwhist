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


class Trick(object):
    def __init__(self):
        self.played_cards = []

    def play(self, card, player):
        self.played_cards.append((card, player))

    def sort(self, suit, trump=-1):
        suit_rank = dict((s, (2 if s == trump else \
                             (1 if s == suit else \
                              0))) for s in xrange(4))
        return sorted(self.played_cards,
                      key=lambda p: suit_rank[p[0].suit] * 13 + p[0].rank)

    def winning(self, suit, trump=-1):
        return self.sort(suit, trump)[-1]


class Game(object):
    def __init__(self, players):
        self.deck = Deck()
        self.players = players
        self.dealer = 0
        self.trump = None
        self.playing = 1
        self.tricks = []
        self.trick = None

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

    def round(self):
        print('---')
        self.trick = Trick()
        suit = -1
        for i in xrange(4):
            player = self.players[self.playing]
            played_card = player.play(self)
            if i == 0:
                suit = played_card.suit
            self.trick.play(played_card, player)
            self.playing = (self.playing + 1) % 4

        winning_card, winning_player = self.trick.winning(suit, self.trump.suit)
        print('%s gets the trick' % winning_player)
        self.tricks.append(self.trick)
        winning_player.tricks.append(self.trick)
        self.trick = None
        self.playing = self.players.index(winning_player)

    def valid_cards(self, hand):
        if len(self.trick.played_cards) == 0:
            return hand
        suit = self.trick.played_cards[0][0].suit
        hand_in_suit = [c for c in hand if c.suit == suit]
        if hand_in_suit:
            return hand_in_suit
        return hand

    def bidding(self):
        pass

class Player(object):
    def __init__(self, name, ai):
        self.hand = []
        self.name = name
        self.ai = ai
        self.tricks = []

    def sort(self):
        self.hand = sum((self.sorted_suit(i) for i in (0, 2, 1, 3)), [])

    def sorted_suit(self, suit, hand=None):
        hand = hand or self.hand
        return sorted((c for c in hand if c.suit == suit), key=lambda card: card.rank)

    def highest(self, suit):
        return self.sorted_suit(suit)[-1]

    def lowest(self, suit):
        return self.sorted_suit(suit)[0]

    def play(self, game):
        card = self.ai.play(self, game)
        print('%s plays %s.' % (self.name, card))
        return card

    def valid_cards(self, game):
        return game.valid_cards(self.hand)

    def __repr__(self):
        return '<Player: %s (%s)>' % (self.name, ', '.join(map(str, self.hand)))

    def __str__(self):
        return self.name


class AI(object):
    def play(self, player, game):
        if len(game.trick.played_cards) > 0:
            in_suits = player.sorted_suit(game.trick.played_cards[0][0].suit)
            if in_suits:
                return player.hand.pop(player.hand.index(in_suits[-1]))
            trumps = player.sorted_suit(game.trump.suit)
            if trumps:
                return player.hand.pop(player.hand.index(trumps[-1]))
            lowest = sorted(player.hand, key=lambda c: c.rank)[0]
            return player.hand.pop(player.hand.index(lowest))
        else:
            trumps = player.sorted_suit(game.trump.suit)
            if trumps:
                return player.hand.pop(player.hand.index(trumps[-1]))
            highest = sorted(player.hand, key=lambda c: c.rank)[-1]
            return player.hand.pop(player.hand.index(highest))


class Human(object):
    def play(self, player, game):
        print(repr(player))
        print('%s, which card? ' % player.name)

        sys.stdout.flush()
        card_index = find_card_from_string(raw_input(), player.hand)

        return player.hand.pop(card_index)


if __name__ == '__main__':
    random.seed()

    print('Welcome to Belgian Whist!')
    g = Game((Player('Jef', AI()), Player('Koen', AI()), Player('Ingo', AI()), Player('Olivier', AI())))
    g.deck.shuffle()
    g.deck.hef_af()
    g.deal()
    print('Trump card is %s.' % g.trump)

    for i in xrange(4):
        g.players[i].original = repr(g.players[i])

    player = g.players[g.playing]
    while len(player.hand) > 0:
        g.round()

        player = g.players[g.playing]

    print('---')
    print('Ranking:')

    for i in xrange(4):
        print(g.players[i].original)
        for t in g.players[i].tricks:
            print '*',
        print('')




