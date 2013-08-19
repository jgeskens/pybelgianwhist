import Tkinter as Tk
from collections import defaultdict
import time
from PIL import ImageTk, Image

from whist import Game, Player, AI, Human, Card


class UIHuman(Human):
    def play(self, player, game):
        game.ui.clicked_card = None

        def get_clicked_card():
            if game.ui.clicked_card is None:
                return None
            player_id, card_id = game.ui.clicked_card
            return game.players[player_id].hand[card_id]

        game.ui.redraw()

        while game.ui.clicked_card is None or not get_clicked_card() in player.valid_cards(game):
            game.ui.parent.update()
            time.sleep(0.03)

        return player.hand.pop(player.hand.index(get_clicked_card()))


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
        self.card_imgs = dict((c, ImageTk.PhotoImage(Image.open('cards/%s.gif' % (c[1]+c[0]).lower())))
            for c in cards)
        self.blank_img = ImageTk.PhotoImage(Image.open('cards/b1fv.gif'))

        self.card_size = (self.card_imgs['2H'].width(), self.card_imgs['2H'].height())
        self.middle = ((self.size[0] - (self.card_offset[0] * 12 + self.card_size[0])) / 2,
                       (self.size[1] - (self.card_offset[1] * 12 + self.card_size[1])) / 2)

        # Widgets
        self.canvas = Tk.Canvas(self, width=self.size[0], height=self.size[1], bg='darkgreen', highlightthickness=0)
        self.canvas.pack(fill=Tk.BOTH, expand=1)
        self.canvas.bg_tiles = {}

        self.draw_background()

        # Players

        self.canvas.players = [[None] * 13 for p in xrange(4)]
        self.tag_to_card = {}

        for c in xrange(13):
            self.canvas.players[3][c] = self.canvas.create_image((self.middle[0] + c * self.card_offset[0],
                                                                  16),
                                                                 image=None, anchor='nw')
            self.tag_to_card[self.canvas.players[3][c]] = (3, c)

        for c in xrange(13):
            self.canvas.players[2][c] = self.canvas.create_image((self.size[0] - 16 - self.card_size[0],
                                                                  self.middle[1] + c * self.card_offset[1]),
                                                                 image=None, anchor='nw')
            self.tag_to_card[self.canvas.players[2][c]] = (2, c)

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

        for t in self.tag_to_card.keys():
            self.canvas.tag_bind(t, '<ButtonRelease-1>', self.handle_card_click_factory(t))

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


        self.pack(fill=Tk.BOTH, expand=1)


    def draw_background(self):
        for x in range(self.size[0] / self.bg_img.width() + 1):
            for y in range(self.size[1] / self.bg_img.height() + 1):
                if not (x, y) in self.canvas.bg_tiles:
                    i = self.canvas.create_image((x * self.bg_img.width(),
                                                  y * self.bg_img.height()),
                                                 image=self.bg_img, anchor='nw')
                    self.canvas.bg_tiles[(x, y)] = i

    def draw_players(self):
        for p in xrange(4):
            for c in xrange(13):
                if c >= len(self.game.players[p].hand):
                    img = ''
                elif isinstance(self.game.players[p].ai, AI):
                    img = self.blank_img
                else:
                    img = self.card_imgs[str(self.game.players[p].hand[c])]

                self.canvas.itemconfigure(self.canvas.players[p][c],
                                          image=img)

    def draw_trick(self):
        if self.game.trick:
            for i, c in enumerate(self.canvas.trick):
                img = ''
                if i < len(self.game.trick.played_cards):
                    img = self.card_imgs[str(self.game.trick.played_cards[i][0])]

                self.canvas.itemconfigure(c, image=img)
        else:
            for c in self.canvas.trick:
                self.canvas.itemconfigure(c, image='')

    def handle_card_click_factory(self, tag):
        def handle_card_click(event):
            self.clicked_card = self.tag_to_card[tag]
        return handle_card_click

    def redraw(self):
        self.draw_players()
        self.draw_trick()

    def play_game(self):
        self.game.start()
        self.redraw()
        while True:
            self.game.round()
            self.redraw()



if __name__ == '__main__':
    g = Game([Player('Jef', UIHuman()),
              Player('Ingo', AI()),
              Player('Koen', AI()),
              Player('Olivier', AI())])


    root = Tk.Tk()
    root.title("Belgian Whist")

    app = WhistApp(root, g)

    root.lift()
    root.call('wm', 'attributes', '.', '-topmost', True)
    root.after_idle(root.call, 'wm', 'attributes', '.', '-topmost', False)

    root.mainloop()
