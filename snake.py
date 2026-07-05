import pygame
import random
import sys

# Constants
WIDTH, HEIGHT = 600, 600
CELL = 20
COLS = WIDTH // CELL
ROWS = HEIGHT // CELL
FPS = 10

BLACK  = (0,   0,   0)
GREEN  = (50, 200,  50)
DGREEN = (30, 150,  30)
RED    = (220,  50,  50)
WHITE  = (255, 255, 255)
GRAY   = (40,  40,  40)

UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

def random_food(snake):
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in snake:
            return pos

def draw_cell(surface, col, row, color, inner_color=None):
    rect = pygame.Rect(col * CELL, row * CELL, CELL, CELL)
    pygame.draw.rect(surface, color, rect)
    if inner_color:
        inner = rect.inflate(-4, -4)
        pygame.draw.rect(surface, inner_color, inner, border_radius=3)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    font_big   = pygame.font.SysFont("monospace", 48, bold=True)
    font_small = pygame.font.SysFont("monospace", 24)

    def new_game():
        snake = [(COLS // 2, ROWS // 2)]
        direction = RIGHT
        food = random_food(snake)
        score = 0
        return snake, direction, food, score

    snake, direction, food, score = new_game()
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        snake, direction, food, score = new_game()
                        game_over = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                else:
                    if event.key == pygame.K_UP    and direction != DOWN:  direction = UP
                    elif event.key == pygame.K_DOWN  and direction != UP:   direction = DOWN
                    elif event.key == pygame.K_LEFT  and direction != RIGHT: direction = LEFT
                    elif event.key == pygame.K_RIGHT and direction != LEFT:  direction = RIGHT

        if not game_over:
            head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            if head[0] < 0 or head[0] >= COLS or head[1] < 0 or head[1] >= ROWS or head in snake:
                game_over = True
            else:
                snake.insert(0, head)
                if head == food:
                    score += 1
                    food = random_food(snake)
                else:
                    snake.pop()

        # Draw
        screen.fill(BLACK)

        # Grid
        for c in range(COLS):
            for r in range(ROWS):
                pygame.draw.rect(screen, GRAY, (c * CELL, r * CELL, CELL, CELL), 1)

        # Food
        draw_cell(screen, food[0], food[1], RED)

        # Snake
        for i, (c, r) in enumerate(snake):
            color = GREEN if i == 0 else DGREEN
            draw_cell(screen, c, r, color, (0, 100, 0) if i == 0 else None)

        # Score
        score_surf = font_small.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surf, (8, 8))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            go_surf = font_big.render("GAME OVER", True, RED)
            screen.blit(go_surf, go_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))

            sc_surf = font_small.render(f"Score: {score}", True, WHITE)
            screen.blit(sc_surf, sc_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

            hint = font_small.render("R = Restart   Q = Quit", True, GRAY)
            screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
