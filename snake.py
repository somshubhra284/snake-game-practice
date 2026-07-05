import pygame, random, sys, math

WIDTH, HEIGHT, CELL = 600, 600, 20
BASE_FPS, FPS_STEP, MAX_FPS = 6, 2, 20  # level-up every 5 apples
COLS, ROWS = WIDTH // CELL, HEIGHT // CELL

RENDER_FPS = 60  # decouple render rate from logic tick rate

TONGUE_CYCLE        = 2.0   # seconds per full flick cycle
TONGUE_OUT_DURATION = 0.20  # seconds tongue stays extended each cycle

PARTICLE_LIFETIME    = 0.35
SCORE_POP_LIFETIME   = 0.55
SCORE_POP_SPEED      = 60    # px/s upward
DEATH_FLASH_DURATION = 0.35
DEATH_SHAKE_FRAMES   = 12

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
RED    = (220,  50,  50)
GRAY   = (40,  40,  40)

GRASS_DARK  = (40,  90,  20)
GRASS_LIGHT = (55, 115,  25)

SNAKE_HEAD_COL = (80, 230,  60)
SNAKE_TAIL_COL = (80, 140,  20)
SNAKE_OUTLINE  = (20,  80,  10)

PARTICLE_COLORS = [(220, 50, 50), (255, 100, 30), (255, 200, 50)]

UP, DOWN, LEFT, RIGHT = (0,-1), (0,1), (-1,0), (1,0)


class Snake:
    def __init__(self, body, direction):
        self.body      = body
        self.direction = direction
        self.prev_body    = list(body)
        self.tongue_timer = 0.0
        self.tongue_out   = False

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

    def update_tongue(self, dt):
        self.tongue_timer = (self.tongue_timer + dt) % TONGUE_CYCLE
        self.tongue_out = self.tongue_timer < TONGUE_OUT_DURATION

    def draw(self, surface, progress=1.0, growing=False):
        n = len(self.body)

        # Build interpolated pixel positions
        positions = []
        for i in range(n):
            c_curr, r_curr = self.body[i]
            if i < len(self.prev_body):
                c_prev, r_prev = self.prev_body[i]
            else:
                c_prev, r_prev = c_curr, r_curr  # new grow segment: stays in place
            px = (c_prev + (c_curr - c_prev) * progress) * CELL + CELL // 2
            py = (r_prev + (r_curr - r_prev) * progress) * CELL + CELL // 2
            positions.append((px, py))

        def seg_color(i):
            t = i / max(n - 1, 1)
            r = int(SNAKE_HEAD_COL[0] + (SNAKE_TAIL_COL[0] - SNAKE_HEAD_COL[0]) * t)
            g = int(SNAKE_HEAD_COL[1] + (SNAKE_TAIL_COL[1] - SNAKE_HEAD_COL[1]) * t)
            b = int(SNAKE_HEAD_COL[2] + (SNAKE_TAIL_COL[2] - SNAKE_HEAD_COL[2]) * t)
            return (r, g, b)

        # Pass 1: dark outline (tail → head so head is on top)
        for i in range(n - 1, -1, -1):
            pos = (int(positions[i][0]), int(positions[i][1]))
            if i > 0:
                prev_pos = (int(positions[i - 1][0]), int(positions[i - 1][1]))
                pygame.draw.line(surface, SNAKE_OUTLINE, pos, prev_pos, CELL)
            pygame.draw.circle(surface, SNAKE_OUTLINE, pos, CELL // 2)

        # Pass 2: colored fill
        fill_r = CELL // 2 - 1
        for i in range(n - 1, -1, -1):
            pos = (int(positions[i][0]), int(positions[i][1]))
            color = seg_color(i)
            r = fill_r
            if growing and i == n - 1:
                r = max(1, int(fill_r * progress))  # tail grows out from radius 0 → full
            if i > 0:
                prev_pos = (int(positions[i - 1][0]), int(positions[i - 1][1]))
                pygame.draw.line(surface, color, pos, prev_pos, CELL - 2)
            pygame.draw.circle(surface, color, pos, r)

        # Pass 3: head overlay (brighter, slightly larger)
        hx, hy = int(positions[0][0]), int(positions[0][1])
        pygame.draw.circle(surface, SNAKE_OUTLINE, (hx, hy), CELL // 2 + 1)
        pygame.draw.circle(surface, SNAKE_HEAD_COL, (hx, hy), CELL // 2)

        # Pass 4: eyes
        dx, dy = self.direction
        perp = (-dy, dx)
        for side in (1, -1):
            ex = hx + dx * 3 + perp[0] * 4 * side
            ey = hy + dy * 3 + perp[1] * 4 * side
            pygame.draw.circle(surface, WHITE, (int(ex), int(ey)), 3)
            pygame.draw.circle(surface, BLACK, (int(ex + dx), int(ey + dy)), 1)

        # Pass 5: tongue (periodic flick; also resets to 0 on eat for immediate flick)
        if self.tongue_out:
            rad = CELL // 2
            tx = hx + dx * (rad + 2)
            ty = hy + dy * (rad + 2)
            tip1 = (tx + dx * 5 - dy * 3, ty + dy * 5 + dx * 3)
            tip2 = (tx + dx * 5 + dy * 3, ty + dy * 5 - dx * 3)
            pygame.draw.line(surface, RED, (hx + dx * rad, hy + dy * rad), (int(tx), int(ty)), 2)
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
        pygame.draw.line(surface, (101, 67, 33), (cx, cy - rad), (cx + 2, cy - rad - 4), 2)
        pygame.draw.line(surface, (0, 180, 0), (cx + 2, cy - rad - 2), (cx + 6, cy - rad - 5), 2)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock   = pygame.time.Clock()
        self.font     = pygame.font.SysFont("monospace", 24)
        self.font_big = pygame.font.SysFont("monospace", 48, bold=True)
        self.reset()

        # Pre-render static checkerboard background (done once)
        self._bg = pygame.Surface((WIDTH, HEIGHT))
        self._bg.fill(GRASS_DARK)
        for c in range(COLS):
            for r in range(ROWS):
                if (c + r) % 2 == 0:
                    pygame.draw.rect(self._bg, GRASS_LIGHT, (c * CELL, r * CELL, CELL, CELL))

    def reset(self):
        self.snake = Snake([(COLS//2, ROWS//2)], RIGHT)
        self.apple = Apple(self.snake.body)
        self.score = 0
        self.over  = False
        # Smooth movement state
        self.move_timer        = 0.0
        self.progress          = 0.0
        self.growing           = False
        self.pending_direction = None
        # Visual effects
        self.particles    = []
        self.score_pops   = []
        self.death_flash  = 0.0
        self.shake_frames = 0
        self.shake_offset = (0, 0)

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
                    # Buffer direction between logic ticks; use pending if already queued
                    effective = self.pending_direction if self.pending_direction is not None else self.snake.direction
                    if e.key == pygame.K_UP    and effective != DOWN:  self.pending_direction = UP
                    if e.key == pygame.K_DOWN  and effective != UP:    self.pending_direction = DOWN
                    if e.key == pygame.K_LEFT  and effective != RIGHT: self.pending_direction = LEFT
                    if e.key == pygame.K_RIGHT and effective != LEFT:  self.pending_direction = RIGHT

    def _do_move_tick(self):
        # Apply buffered direction change
        if self.pending_direction is not None:
            self.snake.direction = self.pending_direction
            self.pending_direction = None

        # Snapshot body before moving (used by draw() for interpolation)
        self.snake.prev_body = list(self.snake.body)

        if self.snake.wall_hit() or self.snake.self_hit():
            self.over = True
            self.death_flash  = 1.0
            self.shake_frames = DEATH_SHAKE_FRAMES
            return

        if self.snake.next_head() == self.apple.position:
            self.snake.grow()
            self.score  += 1
            self.growing = True
            self.snake.tongue_timer = 0.0  # force immediate flick on eat
            self._spawn_particles(self.apple.position)
            self._spawn_score_pop(self.apple.position)
            self.apple.respawn(self.snake.body)
        else:
            self.snake.move()
            self.growing = False

    def update(self, dt):
        if self.over:
            self._update_effects(dt)
            return
        self.snake.update_tongue(dt)
        self._update_particles(dt)
        self._update_score_pops(dt)
        move_interval = 1.0 / self.fps
        self.move_timer += dt
        if self.move_timer >= move_interval:
            self.move_timer -= move_interval
            self.move_timer = min(self.move_timer, move_interval)  # safety clamp
            self._do_move_tick()
        self.progress = min(self.move_timer / move_interval, 1.0)

    # ── Particle system ──────────────────────────────────────────────────────

    def _spawn_particles(self, apple_pos):
        cx = apple_pos[0] * CELL + CELL // 2
        cy = apple_pos[1] * CELL + CELL // 2
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 110)
            self.particles.append({
                'x': float(cx), 'y': float(cy),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': PARTICLE_LIFETIME,
                'max_life': PARTICLE_LIFETIME,
                'color': random.choice(PARTICLE_COLORS),
                'radius': random.uniform(2.0, 4.0),
            })

    def _update_particles(self, dt):
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
        self.particles = [p for p in self.particles if p['life'] > 0]

    def _draw_particles(self, surface):
        for p in self.particles:
            t = p['life'] / p['max_life']
            color = (int(p['color'][0] * t), int(p['color'][1] * t), int(p['color'][2] * t))
            rad = max(1, int(p['radius'] * t))
            pygame.draw.circle(surface, color, (int(p['x']), int(p['y'])), rad)

    # ── Score pop ────────────────────────────────────────────────────────────

    def _spawn_score_pop(self, apple_pos):
        self.score_pops.append({
            'x': float(apple_pos[0] * CELL + CELL // 2),
            'y': float(apple_pos[1] * CELL),
            'life': SCORE_POP_LIFETIME,
            'max_life': SCORE_POP_LIFETIME,
        })

    def _update_score_pops(self, dt):
        for p in self.score_pops:
            p['y'] -= SCORE_POP_SPEED * dt
            p['life'] -= dt
        self.score_pops = [p for p in self.score_pops if p['life'] > 0]

    def _draw_score_pops(self, surface):
        for p in self.score_pops:
            alpha = int(255 * p['life'] / p['max_life'])
            surf = self.font.render("+1", True, (255, 255, 100))
            surf.set_alpha(alpha)
            surface.blit(surf, (int(p['x']) - surf.get_width() // 2, int(p['y'])))

    # ── Death effects ────────────────────────────────────────────────────────

    def _update_effects(self, dt):
        if self.death_flash > 0:
            self.death_flash = max(0.0, self.death_flash - dt / DEATH_FLASH_DURATION)
        if self.shake_frames > 0:
            amp = int(5 * self.shake_frames / DEATH_SHAKE_FRAMES)
            self.shake_offset = (random.randint(-amp, amp), random.randint(-amp, amp))
            self.shake_frames -= 1
        else:
            self.shake_offset = (0, 0)
        self._update_particles(dt)
        self._update_score_pops(dt)

    # ── Drawing ──────────────────────────────────────────────────────────────

    def draw(self):
        # Render game world to intermediate surface so shake_offset works cleanly
        game_surf = pygame.Surface((WIDTH, HEIGHT))
        game_surf.blit(self._bg, (0, 0))
        self.apple.draw(game_surf)
        self._draw_particles(game_surf)
        self.snake.draw(game_surf, progress=self.progress, growing=self.growing)
        self._draw_score_pops(game_surf)

        self.screen.fill(BLACK)  # black border shows during shake
        self.screen.blit(game_surf, self.shake_offset)

        # HUD drawn directly to screen (no shake)
        self.screen.blit(
            self.font.render(f"Score: {self.score}  Level: {self.level}", True, WHITE), (8, 8))

        if self.death_flash > 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 30, 30, int(self.death_flash * 180)))
            self.screen.blit(flash, (0, 0))

        if self.over:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            self.screen.blit(ov, (0, 0))
            label = self.font_big.render("GAME OVER", True, RED)
            self.screen.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
            sc = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(sc, sc.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
            hint = self.font.render("R = Restart  Q = Quit", True, GRAY)
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 55)))

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(RENDER_FPS) / 1000.0
            dt = min(dt, 0.05)  # clamp: skip physics if frame took >50ms
            self.handle_input()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
