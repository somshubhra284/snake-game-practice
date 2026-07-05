import pygame, random, sys

WIDTH, HEIGHT, CELL = 600, 600, 20
BASE_FPS, FPS_STEP, MAX_FPS = 6, 2, 20  # level-up every 5 apples
COLS, ROWS = WIDTH // CELL, HEIGHT // CELL
BLACK, WHITE, GREEN, RED, GRAY = (0,0,0), (255,255,255), (50,200,50), (220,50,50), (40,40,40)
DARK_GREEN = (30, 140, 30)
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

    def draw(self, surface, eating=False):
        for i, (c, r) in enumerate(self.body):
            cx, cy = c * CELL + CELL // 2, r * CELL + CELL // 2
            rad = CELL // 2 - 1
            pygame.draw.circle(surface, DARK_GREEN, (cx, cy), rad + 2)
            pygame.draw.circle(surface, GREEN, (cx, cy), rad)

        # head details
        hc, hr = self.body[0]
        cx, cy = hc * CELL + CELL // 2, hr * CELL + CELL // 2
        dx, dy = self.direction

        # eyes (offset perpendicular to direction)
        perp = (-dy, dx)
        for side in (1, -1):
            ex = cx + dx * 3 + perp[0] * 4 * side
            ey = cy + dy * 3 + perp[1] * 4 * side
            pygame.draw.circle(surface, WHITE, (int(ex), int(ey)), 3)
            pygame.draw.circle(surface, BLACK, (int(ex + dx), int(ey + dy)), 1)

        # tongue (flicks when eating)
        if eating:
            tx, ty = cx + dx * (rad + 2), cy + dy * (rad + 2)
            tip1 = (tx + dx * 5 - dy * 3, ty + dy * 5 + dx * 3)
            tip2 = (tx + dx * 5 + dy * 3, ty + dy * 5 - dx * 3)
            pygame.draw.line(surface, RED, (cx + dx * rad, cy + dy * rad), (int(tx), int(ty)), 2)
            pygame.draw.line(surface, RED, (int(tx), int(ty)), (int(tip1[0]), int(tip1[1])), 2)
            pygame.draw.line(surface, RED, (int(tx), int(ty)), (int(tip2[0]), int(tip2[1])), 2)


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
        cx, cy = c * CELL + CELL // 2, r * CELL + CELL // 2
        rad = CELL // 2 - 2
        pygame.draw.circle(surface, (180, 0, 0), (cx, cy), rad + 1)
        pygame.draw.circle(surface, RED, (cx, cy), rad)
        pygame.draw.circle(surface, (255, 120, 120), (cx - rad//3, cy - rad//3), rad//3)  # shine
        # stem
        pygame.draw.line(surface, (101, 67, 33), (cx, cy - rad), (cx + 2, cy - rad - 4), 2)
        # leaf
        pygame.draw.line(surface, (0, 180, 0), (cx + 2, cy - rad - 2), (cx + 6, cy - rad - 5), 2)


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
        self.eating = False

    @property
    def level(self):
        return self.score // 5 + 1

    @property
    def fps(self):
        return min(BASE_FPS + (self.level - 1) * FPS_STEP, MAX_FPS)

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
            self.eating = True
        else:
            self.snake.move()
            self.eating = False

    def draw(self):
        self.screen.fill(BLACK)
        for c in range(COLS):
            for r in range(ROWS):
                pygame.draw.rect(self.screen, GRAY, (c*CELL, r*CELL, CELL, CELL), 1)
        self.apple.draw(self.screen)
        self.snake.draw(self.screen, eating=self.eating)
        self.screen.blit(self.font.render(f"Score: {self.score}  Level: {self.level}", True, WHITE), (8, 8))
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
            self.clock.tick(self.fps)


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
