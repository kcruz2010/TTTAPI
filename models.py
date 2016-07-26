"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

from datetime import date
from forms import GameForm, ScoreForm, UserForm
from google.appengine.ext import ndb


# - - - - NDB model definitions for TicTicToe API. - - - -

# :::::: USER NDB MODEL :::::::::::
class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required = True)
    email = ndb.StringProperty(required = True)
    wins = ndb.IntegerProperty(default = 0)
    draws = ndb.IntegerProperty(default = 0)
    totalGamePlayed = ndb.IntegerProperty(default = 0)

# User Class Methods
    @classmethod
    def get_current_user(cls, username):
        """Returns a current user. Returns none if no user is found"""
        return User.query(User.name == username).get()

    def update_user_stats(self):
        """Adds Game played to the user, and update user status each time a new game starts"""
        self.totalGamePlayed +=1
        self.put()

    def user_win(self):
        """Adds a win to user stats each time user wins a game"""
        self.wins +=1
        self.update_user_stats()

    def user_draw(self):
        """Adds a draw to user stats each time user ties a game"""
        self.draws +=1
        self.update_user_stats()

    def user_loss(self):
        """Adds a loss when user loses a game"""
        self.update_user_stats()

# User Class Property
    @property
    def points(self):
        """returns the User win and draw points"""
        return self.wins*3+self.draws

    @property
    def cal_win_percentage(self):
        """Returns claculation of user wins for the amount of game played"""
        if self.totalGamePlayed > 0:
            return float(self.wins) / float(self.totalGamePlayed)
        else:
            return 0
    @property
    def cal_win_draw_percentage(self):
        """Returns calculation User wins plus draws for the amount of game played"""
        if self.totalGamePlayed > 0:
            return (float(self.wins) + float(self.draws)) / float(self.totalGamePlayed)

    def to_form(self):
        return UserForm(name = self.name,
                        email = self.email,
                        wins = self.wins,
                        draws = self.draws,
                        totalGamePlayed = self.totalGamePlayed,
                        cal_win_draw_percentage = self.cal_win_draw_percentage,
                        points = self.points)


#::::::: GAME NDB MODEL :::::::
class Game(ndb.Model):
    """Game object"""
    board = ndb.PickleProperty          (required=True)
    boardSize = ndb.IntegerProperty     (required=True, default=3)
    player_x = ndb.KeyProperty          (required=True, kind='User')
    player_o = ndb.KeyProperty          (required=True, kind='User')
    nextMove = ndb.KeyProperty          (required=True)
    winner = ndb.KeyProperty()
    draw = ndb.BooleanProperty          (default=False)
    game_over = ndb.BooleanProperty     (required=True, default=False)
    game_history = ndb.PickleProperty   (required=True)

# Game Class Methods
    @classmethod
    def new_game(cls, player_x, player_o, boardSize=3):
        """Creates and returns a new game"""
        game = Game(player_x=player_x,
                    player_o=player_o,
                    nextMove=player_x)
        game.board = ['' for _ in range(boardSize*boardSize)]
        game.game_history = []
        game.boardSize = boardSize
        game.put()
        return game

    def to_form(self):
        """Returns a GameForm representation of the Game"""
        form = GameForm(urlsafe_key = self.key.urlsafe(),
                        board = str(self.board),
                        boardSize = self.boardSize,
                        player_x = self.player_x.get().name,
                        player_o = self.player_o.get().name,
                        nextMove = self.nextMove.get().name,
                        game_over = self.game_over
                        )
        if self.winner:
            # send winner to Game form and get winner's name
            form.winner = self.winner.get().name
        if self.draw:
            form.draw = self.draw
        return form

    def end_game( self, winner=False):
        """Ends the game - if winner is True, the player won. - if winner is False,
        the player match is draw, or player lost."""
        self.game_over = True
        if winner:
            self.winner = winner
        else:
            self.draw = True
        self.put()
        if winner:
            result = 'player_x' if winner == self.player_x else 'player_o'
        else:
            result = 'draw'

        # Add the game to the score 'board'
        score = Score(player_x = self.player_x,
                      player_o = self.player_o,
                      date=date.today(),
                      result = result
                      )
        score.put()

        # Update the User's stats model
        if winner:
            winner.get().user_win()
            loser = self.player_x if winner == self.player_o else self.player_o
            loser.get().user_loss()
        else:
            self.player_x.get().user_draw()
            self.player_o.get().user_draw()



class Score(ndb.Model):
    """Score object"""
    date = ndb.DateProperty(required=True)
    player_x = ndb.KeyProperty(required=True, kind = 'User')
    player_o = ndb.KeyProperty(required=True, kind = 'User')
    result = ndb.StringProperty(required=True)

    def to_form(self):
        return ScoreForm(date=str(self.date),
                         player_x=self.player_x.get().name,
                         player_o=self.player_o.get().name,
                         result=self.result)