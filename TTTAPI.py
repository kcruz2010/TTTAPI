# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache, mail
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import (
    User, 
    Game, 
    Score,
)
from forms import (
    StringMessage, 
    NewGameForm, 
    GameForm, 
    GameForms, 
    MakeMoveForm,
    ScoreForms, 
    UserForms
)
from utils import (
    get_by_urlsafe,
    check_winner, 
    check_full
)

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

MEMCACHE_GAMES_PLAYED = 'GAMES_PLAYED'


@endpoints.api(name='tictactoe', version='v1')
class TicTacToeApi(remote.Service):
    """Tic Tac Toe API"""

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.get_current_user(request.user_name):
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        if not mail.is_email_valid(request.user_name):
            raise endpoints.ConflictException(
                    'Not a good email address')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        player_x = User.get_current_user(request.player_x)
        player_o = User.get_current_user(request.player_o)
        if not (player_x and player_o):
            wrong_user = player_x if not player_x else player_o
            raise endpoints.NotFoundException(
              'User % does not exists!' % wrong_user.name)
# Board size
        boardSize = 3
        if not boardSize: 
            raise endpoints.BadRequestException('Board Size not valid')
  
        game = Game.new_game(player_x.key, player_o.key, boardSize)

        return game.to_form()

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Cancel a game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and not game.game_over:
            game.key.delete()
            return StringMessage(message='Game with key: {} deleted'.format(request.urlsafe_game_key))
        elif game.game_over:
            raise endpoints.BadRequestException('Game over!')
        else:
            raise endpoints.NotFoundException('Game is not found!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return to current game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form()
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        if game.game_over:
            raise endpoints.NotFoundException('Game already over!')

# Prevent a user from playing twice back to back
        user = User.get_current_user(request.user_name)
        if user.key != game.nextMove:
            raise endpoints.BadRequestException('It\'s not your turn!')
        x = True if user.key == game.player_x else False

# Make a move
        move = request.move
        size = game.boardSize * game.boardSize - 1
        if move < 0 or move > size:
            raise endpoints.BadRequestException('Bad Move!')
        if game.board[move] != '':
            raise endpoints.BadRequestException('Invalid Move')

# Make a move, and send the move to game history
        game.board[move] = 'X' if x else 'O'
        game.game_history.append(('X' if x else 'O', move))
        game.nextMove = game.player_o if x else game.player_x

# Check if there is a winner in the game and end the game
        winner = check_winner(game.board, game.boardSize)
        if winner:
            game.end_game(user.key)
        else:
            # game ends in a draw
            if check_full(game.board):
                game.end_game()
            else:
                # Send email reminder to player if game still in progress
                taskqueue.add(url='/tasks/send_move_email',
                              params={'user_key': game.nextMove.urlsafe(),
                                      'game_key': game.key.urlsafe()})

        game.put()

# Update the Memcache if the game is over
        if game.game_over:
            taskqueue.add(url='/task/cache_games_finished')
        return game.to_form()

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(ndb.OR(Score.player_x == user.key,
                                    Score.player_o == user.key))
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='usergames',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return active games for Users"""
        user = User.get_current_user(request.user_name)
        if not user:
            raise endpoints.BadRequestException('User not found!')
        games = Game.query(ndb.OR(Game.player_x == user.key,
                                  Game.player_o == user.key)).filter(Game.game_over == False)
        return GameForms(items=[game.to_form() for game in games])

    @endpoints.method(response_message=StringMessage,
                      path='games/finished_games',
                      name='get_finished_games',
                      http_method='GET')
    def get_finished_games(self, request):
        """Get the cached number of games finished"""
        return StringMessage(message=memcache.get(MEMCACHE_GAMES_PLAYED) or '')

    @staticmethod
    def _update_finished_games():
        """Populates memcache with the number of games finished"""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            cont = len(games)
            memcache.set(MEMCACHE_GAMES_PLAYED, 'The games finished number is %s' % cont),

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return history of User's play"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return StringMessage(message=str(game.game_history))

    @endpoints.method(response_message=UserForms,
                      path='user/ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Ranking base on win/draw percentage"""
        users = User.query(User.totalGamePlayed > 0).fetch()
        users = sorted(users, key=lambda x: x.points, reverse=True)
        return UserForms(items=[user.to_form()for user in users])


api = endpoints.api_server([TicTacToeApi])
