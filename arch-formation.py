import pygame
import sys
import random
import math
from pygame.math import Vector2

# Configurações da tela
WIDTH = 800
HEIGHT = 600

# Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Constantes
NUMBER_AGENTS = 30
AGENT_RADIUS = 10
ARC_RADIUS = 200
ARC_ANGLE = 90

class Agent:
    def __init__(self, position):
        self.position = position
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.max_speed = 3
        self.max_force = 0.1
        self.heading = 0  # Ângulo de rotação do triângulo

    def seek(self, target):
        desired = target - self.position
        desired = desired.normalize() * self.max_speed
        steering = desired - self.velocity
        steering = self.limit_vector(steering, self.max_force)
        return steering

    def avoid_collision(self, agents):
        avoidance_force = Vector2(0, 0)
        detection_radius = 2 * AGENT_RADIUS

        for other_agent in agents:
            if other_agent != self:
                to_other_agent = other_agent.position - self.position
                distance = to_other_agent.length()

                if 0 < distance < detection_radius:
                    avoidance_force -= to_other_agent.normalize() / distance

        avoidance_force = self.limit_vector(avoidance_force, self.max_force)
        return avoidance_force

    def update(self, target, agents):
        avoidance_force = self.avoid_collision(agents)
        seek_force = self.seek(target)

        self.acceleration = avoidance_force + seek_force
        self.velocity += self.acceleration
        self.velocity = self.limit_vector(self.velocity, self.max_speed)
        self.position += self.velocity

        self.heading = self.velocity.angle_to(Vector2(1, 0))

    def limit_vector(self, vector, max_value):
        if vector.length() > max_value:
            vector = vector.normalize() * max_value
        return vector

    def draw(self, screen):
        v1 = self.position + self.velocity.normalize() * AGENT_RADIUS
        v2 = self.position + self.velocity.normalize().rotate(135) * AGENT_RADIUS
        v3 = self.position + self.velocity.normalize().rotate(-135) * AGENT_RADIUS

        pygame.draw.polygon(screen, BLACK, [v1, v2, v3])


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    agents = []
    target = Vector2(WIDTH // 2, HEIGHT // 2)

    # Posição central do arco
    arc_center = Vector2(WIDTH // 2, HEIGHT // 2)

    # Criação dos agentes em uma formação de arco
    for i in range(NUMBER_AGENTS):
        angle = math.radians(i / (NUMBER_AGENTS - 1) * ARC_ANGLE - ARC_ANGLE / 2)
        position = Vector2(arc_center.x + ARC_RADIUS * math.cos(angle),
                           arc_center.y + ARC_RADIUS * math.sin(angle))
        agent = Agent(position)
        agents.append(agent)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(WHITE)
        position = pygame.mouse.get_pos()
        target = Vector2(position[0], position[1])
        for agent in agents:
            agent.update(target, agents)
            agent.draw(screen)

        pygame.draw.circle(screen, RED, (int(target.x), int(target.y)), 5)

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
