

from protorpc import messages


# - - - - ProtoRPC message class definitions for TicTicToe API. - - - -


# Game Forms
class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField  (1, required=True)
    board = messages.StringField        (2, required=True)
    boardSize = messages.IntegerField   (3, required=True)
    player_x = messages.StringField     (4, required=True)
    player_o = messages.StringField     (5, required=True)
    nextMove = messages.StringField     (6, required=True)
    game_over = messages.BooleanField   (7, required=True)
    winner = messages.StringField       (8)
    draw = messages.StringField         (9)


class GameForms(messages.Message):
    """GameForms -- multiple games outbound form message"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    player_x = messages.StringField     (1, required=True)
    player_o = messages.StringField     (2, required=True)
    boardSize = messages.IntegerField   (3)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user_name = messages.StringField    (1, required=True)
    move = messages.IntegerField        (2, required=True)

# Score Forms
class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    date = messages.StringField         (1, required=True)
    player_x = messages.StringField     (2, required=True)
    player_o = messages.StringField     (3, required=True)
    result = messages.StringField       (4)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField       (1, required=True)


# User Forms
class UserForm(messages.Message):
    """User Form for outbound player information"""
    name = messages.StringField                     (1, required=True)
    email = messages.StringField                    (2)
    wins = messages.IntegerField                    (3, required=True)
    draws = messages.IntegerField                   (4, required=True)
    totalGamePlayed = messages.IntegerField         (5, required=True)
    cal_win_draw_percentage = messages.FloatField   (6, required=True)
    points = messages.IntegerField                  (7)


class UserForms(messages.Message):
    """UserForms -- multiple users outbound form message"""
    items = messages.MessageField(UserForm, 1, repeated=True)