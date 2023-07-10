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
        self.target = Vector2(0, 0)
        self.image = pygame.Surface((RADIUS * 2, RADIUS * 2))
        self.image.fill(BG_COLOR)
        self.rect = self.image.get_rect(center=position)
        self.position = Vector2(position)
        self.velocity = Vector2(0, random.uniform(-0.5, 0.5))
        self.triangle_points = [
            Vector2(position[0], position[1] - RADIUS),
            Vector2(position[0] - RADIUS, position[1] + RADIUS),
            Vector2(position[0] + RADIUS, position[1] + RADIUS)
        ]

        # Variável para controle da formação de vias
        self.lane_alignment_weight = 0.1

    def update(self, pedestrians):
        avoidance_radius = 50
        alignment_radius = 100
        cohesion_radius = 100

        separation = Vector2(0, 0)
        alignment = Vector2(0, 0)
        cohesion = Vector2(0, 0)

        lane_direction = Vector2(1, 0)

        for other in pedestrians:
            direction= self.target - self.position
            direction.scale_to_length(MAX_SPEED)
            self.velocity = direction
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
                
                lane_direction += other.velocity * self.lane_alignment_weight

        num_pedestrians = len(pedestrians)
        if num_pedestrians > 1:
            if alignment.length() > 0:
                alignment /= (num_pedestrians - 1)
                alignment.scale_to_length(MAX_SPEED)

            cohesion /= (num_pedestrians - 1)
            cohesion = (cohesion - self.position)
            cohesion.scale_to_length(MAX_SPEED)

        lane_direction.scale_to_length(1)

        alignment += lane_direction * MAX_SPEED

        self.velocity += separation + alignment + cohesion

        if self.velocity.length() > 0:
            self.velocity.scale_to_length(MAX_SPEED)

        self.position += self.velocity

        self.rect.center = self.position
        self.triangle_points = [
            Vector2(self.position[0], self.position[1] - RADIUS),
            Vector2(self.position[0] - RADIUS, self.position[1] + RADIUS),
            Vector2(self.position[0] + RADIUS, self.position[1] + RADIUS)
        ]

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
        mouse_pos = pygame.mouse.get_pos()

    all_pedestrians.update(all_pedestrians)

    # Desenho na tela
    screen.fill(BG_COLOR)
    for pedestrian in all_pedestrians:
        pedestrian.target = Vector2(mouse_pos[0], mouse_pos[1])
        pygame.draw.polygon(screen, PEDESTRIAN_COLOR, pedestrian.triangle_points)
    pygame.draw.line(screen, LANE_COLOR, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 2)

    pygame.display.flip()
    clock.tick(60)

# Encerramento do Pygame
pygame.quit()
