import Tkinter as Tk
import os
import time
from PIL import ImageTk, Image

from whist import Game, Player, AI, Human, Card, Trick


class UIHuman(Human):
    def play(self, player, game):
        game.ui.clicked_card = None

        def get_clicked_card():
            if game.ui.clicked_card is None:
                return None
            player_id, card_id = game.ui.clicked_card
            return game.players[player_id].hand[card_id]

        game.ui.redraw()

        while game.ui.clicked_card is None\
                or not get_clicked_card() in player.valid_cards(game):
            game.ui.parent.update()
            time.sleep(0.03)

        return player.hand.pop(player.hand.index(get_clicked_card()))

    def bid(self, player, game):
        self.proposition = None
        possible_bids = game.get_possible_bids()
        dialog = Tk.Toplevel(game.ui.parent)
        dialog.title('Bid')
        dialog.lift()

        Tk.Label(dialog, text="Possible bids: " + ', '.join(possible_bids)).pack()
        e = Tk.Entry(dialog)
        e.pack()

        def callback():
            self.proposition = e.get()
            if self.proposition in possible_bids:
                dialog.destroy()
            else:
                print("Please enter a valid bid.")
        b = Tk.Button(dialog, text="Bid!", command=callback)
        b.pack()

        dialog.wait_window()

        return self.proposition


def test_handler_factory(root):
    def test_handler(event):
        print repr(event.__dict__)
    return test_handler


class WhistApp(Tk.Frame):
    clicked_card = None
    parent = None
    game = None
    size = (800, 600)
    card_offset = (32, 32)
    card_size = (0, 0)
    middle = (0, 0)

    def __init__(self, parent, game):
        Tk.Frame.__init__(self, parent)

        self.parent = parent
        self.game = game
        self.game.ui = self

        self.setup_ui()
        self.redraw()
        self.parent.after(0, self.play_game)

    def setup_ui(self):
        # Images
        self.bg_img = ImageTk.PhotoImage(Image.open('cards/green020.png'))
        cards = (str(Card(i % 13, i / 13)) for i in xrange(52))
        self.card_imgs = dict((c, ImageTk.PhotoImage(
            Image.open('cards/%s.gif' % (c[1]+c[0]).lower()))) for c in cards)
        self.blank_img = ImageTk.PhotoImage(Image.open('cards/b1fv.gif'))

        self.card_size = (self.card_imgs['2H'].width(),
                          self.card_imgs['2H'].height())
        self.middle = ((self.size[0] - (self.card_offset[0] * 12 +
                                        self.card_size[0])) / 2,
                       (self.size[1] - (self.card_offset[1] * 12 +
                                        self.card_size[1])) / 2)

        # Widgets
        self.canvas = Tk.Canvas(self, width=self.size[0], height=self.size[1],
                                bg='darkgreen', highlightthickness=0)
        self.canvas.pack(fill=Tk.BOTH, expand=1)
        self.canvas.bg_tiles = {}

        self.draw_background()

        # Players

        self.canvas.players = [[None] * 13 for p in xrange(4)]
        self.tag_to_card = {}

        for c in xrange(13):
            self.canvas.players[0][c] = self.canvas.create_image((self.middle[0] + c * self.card_offset[0],
                                                                  self.size[1] - 16 - self.card_size[1]),
                                                                 image=None, anchor='nw')
            self.tag_to_card[self.canvas.players[0][c]] = (0, c)

        for c in xrange(13):
            self.canvas.players[1][c] = self.canvas.create_image((16,
                                                                  self.middle[1] + c * self.card_offset[1]),
                                                                 image=None, anchor='nw')
            self.tag_to_card[self.canvas.players[1][c]] = (1, c)

        for c in xrange(13):
            self.canvas.players[2][c] = self.canvas.create_image((self.middle[0] + c * self.card_offset[0],
                                                                  16),
                                                                 image=None, anchor='nw')
            self.tag_to_card[self.canvas.players[2][c]] = (2, c)

        for c in xrange(13):
            self.canvas.players[3][c] = self.canvas.create_image((self.size[0] - 16 - self.card_size[0],
                                                                  self.middle[1] + c * self.card_offset[1]),
                                                                 image=None, anchor='nw')
            self.tag_to_card[self.canvas.players[3][c]] = (3, c)


        for t in self.tag_to_card.keys():
            self.canvas.tag_bind(t, '<ButtonRelease-1>', self.handle_card_click_factory(t))

        # Player labels

        self.canvas.player_labels = [None] * 4
        self.canvas.player_labels[0] = self.canvas.create_text((self.middle[0],
                                                                self.size[1] - self.card_size[1] - 16),
                                                               text='Player 1', anchor='sw')
        self.canvas.player_labels[1] = self.canvas.create_text((16,
                                                                self.middle[1]),
                                                               text='Player 2', anchor='sw')
        self.canvas.player_labels[2] = self.canvas.create_text((self.middle[0],
                                                                self.card_size[1] + 32),
                                                               text='Player 3', anchor='sw')
        self.canvas.player_labels[3] = self.canvas.create_text((self.size[0] - self.card_size[0] - 16,
                                                                self.middle[1]),
                                                               text='Player 4', anchor='sw')

        # Tricks

        self.canvas.tricks = [[None] * 13 for p in xrange(4)]

        for c in xrange(13):
            self.canvas.tricks[0][c] = self.canvas.create_image((self.middle[0] + c * 4,
                                                                 self.size[1] - self.card_size[1] - 32),
                                                                image='', anchor='sw')

        for c in xrange(13):
            self.canvas.tricks[1][c] = self.canvas.create_image((self.card_size[0] + 32 + c * 4,
                                                                 self.size[1] / 2),
                                                                image='', anchor='w')

        for c in xrange(13):
            self.canvas.tricks[2][c] = self.canvas.create_image((self.middle[0] + c * 4,
                                                                 self.card_size[1] + 32),
                                                                image='', anchor='nw')

        for c in xrange(13):
            self.canvas.tricks[3][c] = self.canvas.create_image((self.size[0] - self.card_size[0] - 32 + (c - 12) * 4,
                                                                 self.size[1] / 2),
                                                                image='', anchor='e')

        # Trick

        self.canvas.trick = [None] * 4
        self.canvas.trick[0] = self.canvas.create_image((self.size[0] / 2 - self.card_offset[0],
                                                         self.size[1] / 2 + 0 * self.card_offset[1]), image=None)
        self.canvas.trick[1] = self.canvas.create_image((self.size[0] / 2 + 0 * self.card_offset[0],
                                                         self.size[1] / 2 - self.card_offset[1]), image=None)
        self.canvas.trick[2] = self.canvas.create_image((self.size[0] / 2 + self.card_offset[0],
                                                         self.size[1] / 2 + 0 * self.card_offset[1]), image=None)
        self.canvas.trick[3] = self.canvas.create_image((self.size[0] / 2 + 0 * self.card_offset[0],
                                                         self.size[1] / 2 + self.card_offset[1]), image=None)


        # Trump
        self.canvas.trump = self.canvas.create_image((192 + self.card_size[0],
                                                      self.size[1] / 2), image=self.blank_img)

        self.pack(fill=Tk.BOTH, expand=1)


    def draw_background(self):
        for x in range(self.size[0] / self.bg_img.width() + 1):
            for y in range(self.size[1] / self.bg_img.height() + 1):
                if not (x, y) in self.canvas.bg_tiles:
                    i = self.canvas.create_image((x * self.bg_img.width(),
                                                  y * self.bg_img.height()),
                                                 image=self.bg_img, anchor='nw')
                    self.canvas.bg_tiles[(x, y)] = i

    def draw_trump(self):
        img = self.card_imgs[str(self.game.trump)] if self.game.trump and not self.game.tricks else ''
        self.canvas.itemconfigure(self.canvas.trump, image=img)

    def draw_players(self):
        for p in xrange(4):
            self.canvas.itemconfigure(self.canvas.player_labels[p],
                                      text = self.game.players[p].name)

            for c in xrange(13):
                if c >= len(self.game.players[p].hand):
                    img = ''
                elif isinstance(self.game.players[p].ai, AI):
                    img = self.blank_img
                else:
                    img = self.card_imgs[str(self.game.players[p].hand[c])]

                self.canvas.itemconfigure(self.canvas.players[p][c],
                                          image=img)

    def draw_tricks(self):
        for p in xrange(4):
            for c in xrange(13):
                img = self.blank_img if c < len(self.game.players[p].tricks) else ''
                self.canvas.itemconfigure(self.canvas.tricks[p][c], image=img)

    def draw_trick(self):
        if self.game.trick:
            for i in xrange(4):
                img = ''
                if i < len(self.game.trick.played_cards):
                    img = self.card_imgs[str(self.game.trick.played_cards[i][0])]
                self.canvas.itemconfigure(self.canvas.trick[(i + self.game.playing - 1) % 4], image=img)
        else:
            for c in self.canvas.trick:
                self.canvas.itemconfigure(c, image='')

    def handle_card_click_factory(self, tag):
        def handle_card_click(event):
            self.clicked_card = self.tag_to_card[tag]
        return handle_card_click

    def redraw(self):
        self.draw_trump()
        self.draw_players()
        self.draw_trick()
        self.draw_tricks()

    def play_game(self):
        while True:
            self.game.deck.shuffle()
            self.game.deck.hef_af()
            self.game.deal()
            self.redraw()
            self.game.bidding()
            while len(self.game.players[self.game.playing].hand) > 0:
                print('---')
                self.game.trick = Trick()

                currently_playing = self.game.playing
                for i in xrange(4):
                    player = self.game.players[currently_playing]
                    played_card = player.play(self.game)
                    self.game.trick.play(played_card, player)
                    currently_playing = (currently_playing + 1) % 4
                    self.redraw()
                    self.parent.update()
                    time.sleep(1)

                winning_card, winning_player = self.game.trick.winning(self.game.trump.suit)
                print('%s gets the trick' % winning_player)
                self.game.tricks.append(self.game.trick)
                winning_player.tricks.append(self.game.trick)
                self.game.trick = None
                self.game.playing = self.game.players.index(winning_player)
                self.redraw()
                self.parent.update()
            print('---')
            print('Ranking:')

            for i in xrange(4):
                print(self.game.players[i].name)
                for t in self.game.players[i].tricks:
                    print '*',
                print('')
            self.game.mode.post_game()
            self.game.collect()


if __name__ == '__main__':
    g = Game([Player('Jef', UIHuman()),
              Player('Ingo', AI()),
              Player('Koen', AI()),
              Player('Olivier', AI())])


    root = Tk.Tk()
    root.title("Belgian Whist")

    app = WhistApp(root, g)

    root.lift()
    # root.call('wm', 'attributes', '.', '-topmost', True)
    # root.after_idle(root.call, 'wm', 'attributes', '.', '-topmost', False)

    root.mainloop()
