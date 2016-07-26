
#  Tic Tac Toe game design 
- This application implements a simple Tic tac toe game using Google Cloud Endpoints, App Engine with Python 2.7
# Game Description 
- a game in which two players seek in alternate turns to complete a row, a column, or a diagonal with either three O's or three X's drawn in the spaces of a grid of nine squares.
# Game Play
 - Create `user_name` by providing an email  which it will be used for future emails
 - Each game uses a board size typically a `3x3` including `Player_X` and `Player_O`
 - Urlsafer_key is created with a new game in order to retrieve data
 - The user that initiate the game is able to cancel the game 
 - If the game is in current use, using the "current game state" game key will demostrate whose turn is it and what moves the player has made
 - Once the game finishes in a win, lose, or draw using the game key one can retrieve  user scores , user games, game history, number of finishes
 # Files
- `TTTapi.py` : Endpoint and tic tac toe logic design
- `app.yaml` : App configuration
- `cron.yaml` : CronJob configuration
- `form.py` : Message definitions
- `main.py` : Handler for taskqueue
- `utils.py` : Helper function for retrieving ndb. Models by urlsafe Key string
# Endpoints: 
- **cancel_game**

  * Path: 'game/{urlsafe_game_key}'
  * Method: DELETE
  * Parameters: urlsafe_game_key
  * Returns: StringMessage
  * Description: Deletes game provided with key. Game must not have finished yet.
- **create_user**

  * Path: 'user'
  * Method: POST
  * Parameters: user_name
  * Returns: Message confirming creation of the User.
  * Description: Creates a new User. user_name provided must be unique. Will raise a ConflictException if a User with that user_name already exists.
  
- **new_game**

 * Path: 'game'
 * Method: POST
 * Parameters: user_x, user_y, board_size
 * Returns: GameForm with initial game state.
 * Description: Creates a new Game. user_x and user_o are the names of the 'X' and 'O' player respectively. Board size represents board as board_size x board_size.
- **get_game**

 * Path: 'game/{urlsafe_game_key}'
 * Method: GET
 * Parameters: urlsafe_game_key
 * Returns: GameForm with current game state.
 * Description: Returns the current state of a game.
- **make_move**

 * Path: 'game/{urlsafe_game_key}'
 * Method: PUT
 * Parameters: urlsafe_game_key, user_name, move
 * Returns: GameForm with new game state.
 * Description: Accepts a move and returns the updated state of the game. A move is a number from 0 - max index on board depending od board size, corresponding to one of the possible positions on the board. If this causes a game to end, a corresponding Score entity will be created.
- **get_scores**

  * Path: 'scores'
  * Method: GET
  * Parameters: None
  * Returns: ScoreForms.
  * Description: Returns all Scores in the database (unordered).
- **get_user_scores**

  * Path: 'scores/user/{user_name}'
  * Method: GET
  * Parameters: user_name
  * Returns: ScoreForms.
  * Description: Returns all Scores recorded by the provided player (unordered). Will raise a NotFoundException if the User does not exist.
- **get_finished_games**

  * Path: 'games/finished_games'
  * Method: GET
  * Parameters: None
  * Returns: StringMessage
  * Description: Gets the number of games played from a previously cached memcache key.
- **get_game_history**

  * Path: 'game/{urlsafe_game_key}/history'
  * Method: GET
  * Parameters: urlsafe_game_key
  * Returns: StringMessage
  * Description: Return a Game's move history.
- **get_user_games**

  * Path: 'user/games'
  * Method: GET
  * Parameters: user_name, email
  * Returns: GameForms
  * Description: Return all User's active games.
- **get_user_rankings**

  * Path: 'user/ranking'
  * Method: GET
  * Parameters: None
  * Returns: UserForms sorted by user points.
  * Description: Return all Users ranked by their points.

 # Models Included:

- **User**

  * Stores unique user_name and (optional) email address.
  * Also keeps track of wins, ties and total_played.
- **Game**

  * Stores unique game states. Associated with User models via KeyProperties user_x and user_o.
- **Score**

    * Records completed games. Associated with Users model via KeyProperty as well.

# Forms Included:

- **GameForm**
    * Representation of a Game's state (urlsafe_key, board, user_x, user_o, game_over, winner).
- **GameForms**
    * Multiple GameForm container.
- **NewGameForm**
    * Used to create a new game (user_x, user_o)
- **MakeMoveForm**
    * Inbound make move form (user_name, move).
- **ScoreForm**
    * Representation of a completed game's Score (date, winner, loser).
- **ScoreForms**
    * Multiple ScoreForm container.
- **UserForm**
    * Representation of User. Includes winning percentage
- **UserForms**
    * Container for one or more UserForm.
- **StringMessage**
    * General purpose String container.
# TTTAPI

Third party resources:
[Google API doc](https://cloud.google.com/appengine/docs/python/refdocs/)
[Skeleton Game](https://github.com/udacity/FSND-P4-Design-A-Game/blob/master/Skeleton%20Project%20Guess-a-Number/api.py)
