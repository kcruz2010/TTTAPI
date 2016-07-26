"""utils.py - File for collecting general utility functions."""

from google.appengine.ext import ndb
import endpoints

def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity

def check_winner(board, size=3):
    """Check the board. If there is a winner, return the symbol of the winner"""
    # Check rows
    for i in range(size):
        if board[size * i]:
            if all_same(board[size * i:size * i + size]):
                return board[size * i]
    # Check columns
    for i in range(size):
        if board[i]:
            if all_same(board[i:size * size:size]):
                return board[i]
    # Check diagonals
    if board[0]:
        if all_same(board[0:size * size:size + 1]):
            return board[0]
    if board[size - 1]:
        if all_same(board[size - 1:size * (size - 1) + 1:size - 1]):
            return board[size - 1]


def check_full(board):
    """Return true if the board is full"""
    for cell in board:
        if not cell:
            return False
    return True


def all_same(items):
    """Check if all items in list have the same value."""
    return all(x == items[0] for x in items)