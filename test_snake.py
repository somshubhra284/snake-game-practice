import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from snake import Snake, Apple, COLS, ROWS, RIGHT, LEFT, UP, DOWN


def test_snake_moves_correctly():
    snake = Snake([(2, 2), (2, 1)], RIGHT)
    snake.move()
    assert snake.body[0] == (3, 2)
    assert len(snake.body) == 2  # tail removed


def test_snake_grows_when_eating():
    snake = Snake([(1, 1), (0, 1)], RIGHT)
    snake.grow()
    assert snake.body[0] == (2, 1)
    assert len(snake.body) == 3  # tail kept


def test_wall_hit():
    snake = Snake([(0, 0)], LEFT)   # heading out of left wall
    assert snake.wall_hit() is True


def test_no_wall_hit():
    snake = Snake([(5, 5)], RIGHT)
    assert snake.wall_hit() is False


def test_self_hit():
    # head will move into second segment
    snake = Snake([(1, 0), (0, 0)], LEFT)
    assert snake.self_hit() is True


def test_apple_not_on_snake():
    snake = Snake([(c, r) for c in range(COLS) for r in range(ROWS - 1)], RIGHT)
    apple = Apple(snake.body)
    assert apple.position not in snake.body


def test_apple_respawn():
    snake = Snake([(5, 5)], RIGHT)
    apple = Apple(snake.body)
    first = apple.position
    # force respawn several times; position should always be off the snake
    for _ in range(10):
        apple.respawn(snake.body)
        assert apple.position not in snake.body
