import pygame
import random
from pygame.math import Vector2

# Variáveis de configuração
WIDTH = 800
HEIGHT = 600
BG_COLOR = (255, 255, 255)
PEDESTRIAN_COLOR = (0, 0, 0)
LANE_COLOR = (200, 200, 200)
NUM_PEDESTRIANS = 30
MAX_SPEED = 2
RADIUS = 10

# Classe Pedestrian
class Pedestrian(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((RADIUS * 2, RADIUS * 2))
        self.image.fill(PEDESTRIAN_COLOR)
        self.rect = self.image.get_rect(center=position)
        self.position = Vector2(position)
        self.velocity = Vector2(0, random.uniform(-MAX_SPEED, MAX_SPEED))

    def update(self, pedestrians):
        avoidance_radius = 50
        alignment_radius = 100
        cohesion_radius = 500

        separation = Vector2(0, 0)
        alignment = Vector2(0, 0)
        cohesion = Vector2(0, 0)

        for other in pedestrians:
            if other != self:
                distance = self.position.distance_to(other.position)

                if distance < avoidance_radius:
                    diff = self.position - other.position
                    diff.scale_to_length(avoidance_radius / distance)
                    separation += diff

                if distance < alignment_radius:
                    alignment += other.velocity

                if distance < cohesion_radius:
                    cohesion += other.position

        num_pedestrians = len(pedestrians)
        if num_pedestrians > 1:
            if alignment.length() > 0:
                alignment /= (num_pedestrians - 1)
                alignment.scale_to_length(MAX_SPEED)

            cohesion /= (num_pedestrians - 1)
            cohesion = (cohesion - self.position)
            cohesion.scale_to_length(MAX_SPEED)

        self.velocity += separation + alignment + cohesion
        self.velocity.scale_to_length(MAX_SPEED)
        self.position += self.velocity

        self.rect.center = self.position

# Inicialização do Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Formação de Faixas de Pedestres")
clock = pygame.time.Clock()

# Criação dos pedestres
all_pedestrians = pygame.sprite.Group()
for _ in range(NUM_PEDESTRIANS):
    position = (random.randint(RADIUS, WIDTH - RADIUS), random.randint(RADIUS, HEIGHT - RADIUS))
    pedestrian = Pedestrian(position)
    all_pedestrians.add(pedestrian)

# Loop principal do jogo
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_pedestrians.update(all_pedestrians)

    # Desenho na tela
    screen.fill(BG_COLOR)
    for pedestrian in all_pedestrians:
        pygame.draw.circle(screen, PEDESTRIAN_COLOR, pedestrian.rect.center, RADIUS)
    pygame.draw.line(screen, LANE_COLOR, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 2)

    pygame.display.flip()
    clock.tick(60)

# Encerramento do Pygame
pygame.quit()
