import random
import sys


RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king',
         'ace')
SUITS = ('spades', 'clubs', 'diamonds', 'hearts')
BIDS = ('ask', 'join', 'pass')


class Card(object):
    """
    Represents a playing card
    """

    def __init__(self, rank, suit):
        #self.name = '%s of %s' % (RANKS[rank], SUITS[suit])
        self.name = '%s%s' % (RANKS[rank][0] if rank != 8 else 't',
                              SUITS[suit][0].upper())
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return '<Card: %s>' % self.name

    def __str__(self):
        return self.name


def find_card_from_string(s, cards):
    if ' of ' in s:
        rank_str, suit_str = s.split(' of ')
        rank = RANKS.index(rank_str)
        suit = SUITS.index(suit_str)
        found = [i for i, c in enumerate(cards)
                 if c.rank == rank and c.suit == suit]
    else:
        found = [i for i, c in enumerate(cards) if RANKS[c.rank][0] == s[0]
                 or (c.rank == 8 and s[0] == 't')
                 and SUITS[c.suit][0] == s[1].lower()]
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

    def suit(self):
        if len(self.played_cards) > 0:
            return self.played_cards[0][0].suit
        return -1

    def play(self, card, player):
        self.played_cards.append((card, player))

    def sort(self, trump=-1):
        return sorted(self.played_cards,
                      key=lambda p: self.sort_key(p[0], trump))

    def winning(self, trump=-1):
        return self.sort(trump)[-1]

    def sort_key(self, card, trump=-1):
        suit_rank = 0
        suit = self.suit()
        if card.suit == trump:
            suit_rank = 2
        elif suit == -1 or suit == card.suit:
            suit_rank = 1
        return suit_rank * 13 + card.rank

    def winning_cards(self, cards, trump):
        if len(self.played_cards) == 0:
            return []
        winning = self.sort_key(self.winning(trump)[0], trump)
        return [card for card in cards if self.sort_key(card, trump) > winning]


class GameMode(object):
    NORMAL = 'normal'
    offensive = []        # Player(s) on the offensive side
    defensive = []        # Players on the defensive side

    def __init__(self, players, proposals):
        for i, proposal in enumerate(proposals):
            if proposal == 'ask' or proposal == 'join':
                self.offensive.append(players[i])
            else:
                self.defensive.append(players[i])
        self.mode = self.NORMAL
        self.offensive_names = [player.name for player in self.offensive]
        self.defensive_names = [player.name for player in self.defensive]

    def post_game(self):
        """
        Decide who won
        """
        if self.mode == self.NORMAL:
            count = 0
            for player in self.offensive:
                count += player.trick_count()
            if count > 7:
                winners = self.offensive_names
                winning_count = count
            else:
                winners = self.defensive_names
                winning_count = 13 - count
        print('Har har hooray, %s won with %d tricks.' %
              (' and '.join(winners), winning_count))

    def __repr__(self):
        return '<GameMode: %s | %s vs. %s>' % (self.mode,
                                               ', '.join(self.offensive_names),
                                               ', '.join(self.defensive_names))


class Game(object):
    def __init__(self, players):
        self.deck = Deck()
        self.players = players
        self.dealer = 0
        self.trump = None
        self.playing = 1
        self.tricks = []
        self.trick = None
        self.mode = None
        self.bids = []

    def start(self):
        self.deck.shuffle()
        self.deck.hef_af()
        self.deal()
        self.bidding()

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

    def collect(self):
        for trick in self.tricks:
            for played_card in trick.played_cards:
                self.deck.deck.append(played_card[0])
        for player in self.players:
            player.tricks = []
        self.tricks = []
        self.dealer = (self.dealer + 1) % 4
        self.playing = (self.dealer + 1) % 4

    def round(self):
        print('---')
        self.trick = Trick()

        for i in xrange(4):
            player = self.players[self.playing]
            played_card = player.play(self)
            self.trick.play(played_card, player)
            self.playing = (self.playing + 1) % 4

        winning_card, winning_player = self.trick.winning(self.trump.suit)
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
        self.bids = []
        players = []
        bidding_player = (self.dealer + 1) % 4
        for i in xrange(4):
            bid = self.players[bidding_player].bid(self)
            players.append(self.players[bidding_player])
            self.bids.append(bid)
            bidding_player = (bidding_player + 1) % 4
        self.mode = GameMode(players, self.bids)

    def get_possible_bids(self):
        """
        Return the remaining possible bids
        """
        possible_bids = []
        if not 'ask' in self.bids:
            possible_bids.append('ask')
        else:
            if not 'join' in self.bids:
                possible_bids.append('join')
        possible_bids.append('pass')
        return possible_bids


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
        return sorted((c for c in hand if c.suit == suit),
                      key=lambda card: card.rank)

    def highest(self, suit):
        return self.sorted_suit(suit)[-1]

    def lowest(self, suit):
        return self.sorted_suit(suit)[0]

    def play(self, game):
        card = self.ai.play(self, game)
        print('%s plays %s.' % (self.name, card))
        return card

    def bid(self, game):
        bid = self.ai.bid(self, game)
        print('%s proposes %s.' % (self.name, bid))
        return bid

    def valid_cards(self, game):
        return game.valid_cards(self.hand)

    def trick_count(self):
        return len(self.tricks)

    def __repr__(self):
        return '<Player: %s (%s)>' % (self.name,
                                      ', '.join(map(str, self.hand)))

    def __str__(self):
        return self.name


class AI(object):
    def play(self, player, game):
        if len(game.trick.played_cards) > 0:
            in_suits = player.sorted_suit(game.trick.played_cards[0][0].suit)
            if in_suits:
                winning_cards = game.trick.winning_cards(in_suits,
                                                         game.trump.suit)
                if winning_cards:
                    return player.hand.pop(
                        player.hand.index(winning_cards[-1]))
                else:
                    return player.hand.pop(player.hand.index(in_suits[0]))
            trumps = player.sorted_suit(game.trump.suit)
            if trumps:
                winning_cards =\
                    game.trick.winning_cards(trumps, game.trump.suit)
                if winning_cards:
                    return player.hand.pop(
                        player.hand.index(winning_cards[-1]))
                else:
                    lowest_non_trump = sorted(
                        player.hand,
                        key=lambda c: c.rank * (2 if c.suit == game.trump.suit
                                                else 1))[0]
                    return player.hand.pop(player.hand.index(lowest_non_trump))
            lowest = sorted(player.hand, key=lambda c: c.rank)[0]
            return player.hand.pop(player.hand.index(lowest))
        else:
            trumps = player.sorted_suit(game.trump.suit)
            if trumps and trumps[-1].rank > 8:
                return player.hand.pop(player.hand.index(trumps[-1]))
            highest = sorted(player.hand, key=lambda c: c.rank)[-1]
            return player.hand.pop(player.hand.index(highest))

    def bid(self, player, game):
        possible_bids = game.get_possible_bids()
        return possible_bids[0]


class Human(object):
    def play(self, player, game):
        print(repr(player))
        print(repr(game.trick.winning_cards(player.valid_cards(game),
                                            game.trump)))
        print('%s, which card? ' % player.name)

        sys.stdout.flush()
        card_index = find_card_from_string(raw_input(), player.hand)

        return player.hand.pop(card_index)

    def bid(self, player, game):
        print(repr(player))
        possible_bids = game.get_possible_bids()
        print(possible_bids)
        print('%s, please make a bid' % player.name)

        sys.stdout.flush()
        proposition = raw_input()
        while not proposition in possible_bids:
            print('Please choose from', possible_bids)
            proposition = raw_input()

        return proposition


if __name__ == '__main__':
    random.seed()

    print('Welcome to Belgian Whist!')
    g = Game((
        Player('Jef', Human()),
        Player('Koen', AI()),
        Player('Ingo', AI()),
        Player('Olivier', AI())
    ))
    g.start()
    print('Trump card is %s.' % g.trump)

    for i in xrange(4):
        g.players[i].original = repr(g.players[i])

    player = g.players[g.playing]
    while len(player.hand) > 0:
        g.round()

        player = g.players[g.playing]

    g.mode.post_game()
    g.collect()
    print('---')
    print('Ranking:')

    for i in xrange(4):
        print(g.players[i].original)
        for t in g.players[i].tricks:
            print '*',
        print('')
