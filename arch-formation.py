import pygame
import sys
import random
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
DECELERATION_RADIUS = 100


class Agent:
    def __init__(self):
        self.position = Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.max_speed = 3
        self.max_force = 0.1
        self.heading = 0  # Ângulo de rotação do triângulo

    def seek(self, target):
        desired = target - self.position

        # Calcula a distância até o alvo
        distance = desired.length()

        if distance > 0:
            # Verifica se o agente está dentro da zona de desaceleração
            if distance < DECELERATION_RADIUS:
                # Calcula a velocidade proporcional à distância, diminuindo gradualmente
                speed = self.max_speed * (distance / DECELERATION_RADIUS)
            else:
                speed = self.max_speed

            desired = desired.normalize() * speed

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

    def collide(self, other_agent):
        # Calcula a distância entre os agentes
        distance = self.position.distance_to(other_agent.position)
        combined_radius = AGENT_RADIUS * 2

        # Verifica se ocorre colisão com base na distância e no raio dos agentes
        if distance < combined_radius:
            return True
        else:
            return False


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    agents = []
    for _ in range(NUMBER_AGENTS):
        agent = Agent()
        agents.append(agent)

    target = Vector2(WIDTH // 2, HEIGHT // 2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pos = pygame.mouse.get_pos()
        target = Vector2(pos[0], pos[1])
        screen.fill(WHITE)

        for agent in agents:
            agent.update(target, agents)

            # Verifica colisões com outros agentes
            for other_agent in agents:
                if agent != other_agent and agent.collide(other_agent):
                    # Ajusta a posição do agente para formar um arco
                    agent.position = agent.position.rotate(0.2)



                    

            agent.draw(screen)

        pygame.draw.circle(screen, RED, (int(target.x), int(target.y)), 5)

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
