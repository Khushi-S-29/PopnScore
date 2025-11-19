import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcade shooting game")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
BLUE = (50, 50, 255)

score = 0
missed = 0
max_missed = 15
level = 1
target_width = WIDTH // 8
target_height = 80
target_speed = 1.0
spawn_timer = 0
spawn_delay = 100

targets = []
particles = []

font = pygame.font.SysFont(None, 36)
game_over_font = pygame.font.SysFont(None, 80)

hit_sound = pygame.mixer.Sound("hit.mp3")

class Target:
    def __init__(self):
        self.x = random.randint(0, 7) * target_width
        self.y = -target_height
        self.width = target_width
        self.height = target_height
        self.color = random.choice([RED, GREEN, BLUE, YELLOW])
        self.speed = target_speed + random.uniform(-0.2, 0.2)
        self.points = 100
        self.oscillation = random.uniform(0, 2*math.pi)
        self.osc_speed = random.uniform(0.008, 0.02)
        self.osc_amp = random.uniform(3, 8)
        
    def update(self):
        self.y += self.speed
        self.x += self.osc_amp * math.sin(self.oscillation) * 0.5
        self.oscillation += self.osc_speed
        return self.y > HEIGHT
        
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        inner_color = tuple(min(c+40, 255) for c in self.color)
        pygame.draw.rect(screen, inner_color, (self.x+5, self.y+5, self.width-10, self.height-10))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)
        
    def check_hit(self, pos):
        x, y = pos
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.life = random.randint(12, 20)
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-1.5, 1.5)
        self.size = random.randint(3, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        return self.life <= 0
    
    def draw(self):
        if self.size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

def draw_divisions():
    for i in range(1, 8):
        x = i * target_width
        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT), 2)

def draw_ui():
    ui_text = font.render(f"Score: {score}   Missed: {missed}/{max_missed}   Level: {level}", True, WHITE)
    screen.blit(ui_text, (10, 10))

def show_game_over():
    text = game_over_font.render("GAME OVER", True, RED)
    score_text = game_over_font.render(f"Score: {score}", True, WHITE)
    screen.fill(BLACK)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 100))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    pygame.time.delay(4000)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for target in targets[:]:
                if target.check_hit(event.pos):
                    score += target.points
                    for _ in range(10):
                        particles.append(Particle(target.x + target.width/2, target.y + target.height/2, target.color))
                    targets.remove(target)
                    hit_sound.play()
                    break
    
    spawn_timer += 1
    if spawn_timer >= spawn_delay:
        num_targets = min(1 + level//2, 3)
        for _ in range(num_targets):
            targets.append(Target())
        spawn_timer = 0
        
    for target in targets[:]:
        if target.update():
            targets.remove(target)
            missed += 1
            if missed >= max_missed:
                running = False
    
    for particle in particles[:]:
        if particle.update():
            particles.remove(particle)
    
    if score >= level * 500:
        level += 1
        target_speed += 0.1
        spawn_delay = max(50, spawn_delay - 5)
    
    screen.fill(BLACK)
    draw_divisions()
    for target in targets:
        target.draw()
    for particle in particles:
        particle.draw()
    draw_ui()
    
    pygame.display.flip()
    clock.tick(60)

show_game_over()
pygame.quit()
sys.exit()
