import pygame, random, sys

WIDTH, HEIGHT, CELL, FPS = 600, 600, 20, 10
COLS, ROWS = WIDTH // CELL, HEIGHT // CELL
BLACK, WHITE, GREEN, RED, GRAY = (0,0,0), (255,255,255), (50,200,50), (220,50,50), (40,40,40)
UP, DOWN, LEFT, RIGHT = (0,-1), (0,1), (-1,0), (1,0)


class Snake:
    def __init__(self, body, direction):
        self.body = body
        self.direction = direction

    def move(self):
        new_head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
        self.body.insert(0, new_head)
        self.body.pop()

    def grow(self):
        new_head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
        self.body.insert(0, new_head)

    def next_head(self):
        return (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])

    def wall_hit(self):
        h = self.next_head()
        return h[0] < 0 or h[0] >= COLS or h[1] < 0 or h[1] >= ROWS

    def self_hit(self):
        return self.next_head() in self.body

    def draw(self, surface):
        for i, (c, r) in enumerate(self.body):
            pygame.draw.rect(surface, GREEN, (c*CELL, r*CELL, CELL, CELL))
            if i == 0:
                inner = pygame.Rect(c*CELL+3, r*CELL+3, CELL-6, CELL-6)
                pygame.draw.rect(surface, (0,120,0), inner, border_radius=3)


class Apple:
    def __init__(self, snake_body):
        self.position = None
        self.respawn(snake_body)

    def respawn(self, snake_body):
        while True:
            pos = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
            if pos not in snake_body:
                self.position = pos
                return

    def draw(self, surface):
        c, r = self.position
        pygame.draw.rect(surface, RED, (c*CELL, r*CELL, CELL, CELL))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 24)
        self.font_big = pygame.font.SysFont("monospace", 48, bold=True)
        self.reset()

    def reset(self):
        self.snake = Snake([(COLS//2, ROWS//2)], RIGHT)
        self.apple = Apple(self.snake.body)
        self.score = 0
        self.over = False

    def handle_input(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if self.over:
                    if e.key == pygame.K_r: self.reset()
                    if e.key == pygame.K_q: pygame.quit(); sys.exit()
                else:
                    s = self.snake
                    if e.key == pygame.K_UP    and s.direction != DOWN:  s.direction = UP
                    if e.key == pygame.K_DOWN   and s.direction != UP:   s.direction = DOWN
                    if e.key == pygame.K_LEFT   and s.direction != RIGHT: s.direction = LEFT
                    if e.key == pygame.K_RIGHT  and s.direction != LEFT:  s.direction = RIGHT

    def update(self):
        if self.over: return
        if self.snake.wall_hit() or self.snake.self_hit():
            self.over = True; return
        if self.snake.next_head() == self.apple.position:
            self.snake.grow()
            self.score += 1
            self.apple.respawn(self.snake.body)
        else:
            self.snake.move()

    def draw(self):
        self.screen.fill(BLACK)
        for c in range(COLS):
            for r in range(ROWS):
                pygame.draw.rect(self.screen, GRAY, (c*CELL, r*CELL, CELL, CELL), 1)
        self.apple.draw(self.screen)
        self.snake.draw(self.screen)
        self.screen.blit(self.font.render(f"Score: {self.score}", True, WHITE), (8, 8))
        if self.over:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0,0,0,160)); self.screen.blit(ov, (0,0))
            self.screen.blit(self.font_big.render("GAME OVER", True, RED),
                             self.font_big.render("GAME OVER", True, RED).get_rect(center=(WIDTH//2, HEIGHT//2-30)))
            self.screen.blit(self.font.render(f"Score: {self.score}", True, WHITE),
                             self.font.render(f"Score: {self.score}", True, WHITE).get_rect(center=(WIDTH//2, HEIGHT//2+20)))
            self.screen.blit(self.font.render("R = Restart  Q = Quit", True, GRAY),
                             self.font.render("R = Restart  Q = Quit", True, GRAY).get_rect(center=(WIDTH//2, HEIGHT//2+55)))
        pygame.display.flip()

    def render(self):
        grid = [['O'] * COLS for _ in range(ROWS)]
        grid[self.apple.position[1]][self.apple.position[0]] = '*'
        for c, r in self.snake.body:
            grid[r][c] = '#'
        border = '+' + '-' * COLS + '+'
        rows = '\n'.join('|' + ''.join(row) + '|' for row in grid)
        print(f"{border}\n{rows}\n{border}\nScore: {self.score}")

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)


def verify():
    """Step 3: print initial board state without launching pygame."""
    import os; os.environ["SDL_VIDEODRIVER"] = "dummy"; os.environ["SDL_AUDIODRIVER"] = "dummy"
    snake = Snake([(COLS//2, ROWS//2)], RIGHT)
    apple = Apple(snake.body)
    print(f"Board: {COLS}w x {ROWS}h  |  Snake head: {snake.body[0]}  |  Direction: {snake.direction}")
    grid = [['O'] * COLS for _ in range(ROWS)]
    grid[apple.position[1]][apple.position[0]] = '*'
    grid[snake.body[0][1]][snake.body[0][0]] = '#'
    border = '+' + '-' * COLS + '+'
    print(border)
    for row in grid: print('|' + ''.join(row) + '|')
    print(border)

if __name__ == "__main__":
    import sys
    if "--verify" in sys.argv:
        verify()
    else:
        Game().run()
