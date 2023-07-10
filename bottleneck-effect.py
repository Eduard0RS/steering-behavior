import pygame
from pygame.math import Vector2
import random

# Constantes
SCREEN_SIZE = [800, 600]
BG_COLOR = (255, 255, 255)
RADIUS = 5
MAX_SPEED = 2

class Pedestrian(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.position = Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        self.target = Vector2(0, 0)
        self.image = pygame.Surface((RADIUS * 2, RADIUS * 2))
        self.image.fill((0, 0, 0))
        self.triangle_points = [
            Vector2(self.position[0], self.position[1] - RADIUS),
            Vector2(self.position[0] - RADIUS, self.position[1] + RADIUS),
            Vector2(self.position[0] + RADIUS, self.position[1] + RADIUS)
        ]

    def update(self):
        avoidance_radius =35
        alignment_radius = 15
        cohesion_radius = 25

        separation = Vector2(0, 0)
        alignment = Vector2(0, 0)
        cohesion = Vector2(0, 0)



        for other in pedestrians:
            direction= self.target - self.position
            direction.scale_to_length(MAX_SPEED)
            self.velocity = direction
            if other != self:
                distance = self.position.distance_to(other.position)

                if distance < avoidance_radius:
                    diff = self.position - other.position
                    if diff.length() > 0:
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

        if self.velocity.length() > 0:
            self.velocity.scale_to_length(MAX_SPEED)
            self.position += self.velocity
        else:
            self.velocity = Vector2(0, 0)

        self.triangle_points = [
            Vector2(self.position[0], self.position[1] - 5),
            Vector2(self.position[0] - 5, self.position[1] + 5),
            Vector2(self.position[0] + 5, self.position[1] + 5)
        ]

    def draw(self, screen):
        pygame.draw.polygon(screen, (0, 0, 0), self.triangle_points)




pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Bottleneck Effect")

pedestrians = pygame.sprite.Group()


for i in range(1):
    pedestrian = Pedestrian()
    pedestrian.position = Vector2(random.randint(0,100),550)
    pedestrian.target = Vector2(700,300)
    pedestrian.velocity = Vector2(0, 0)
    pedestrians.add(pedestrian)

running = True
clock = pygame.time.Clock()
while running:
    screen .fill(BG_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type==pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                for i in pedestrians:
                    i.target = Vector2(0,300)
            if event.key == pygame.K_RIGHT:
                for i in pedestrians:
                    i.target = Vector2(700,300)
        if event.type == pygame.MOUSEBUTTONUP:
            pos=pygame.mouse.get_pos()
            for i in pedestrians:
                i.target = Vector2(pos[0],pos[1])
  
           
            
    # Atualizar os pedestres
    pedestrians.update()
    for i in pedestrians:
        i.velocity= i.target - i.position
        i.velocity.scale_to_length(1) 
        i.draw(screen)   

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
