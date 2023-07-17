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

class Agent:
    def __init__(self):
        self.position = Vector2(random.randint(0, 250), random.randint(0, HEIGHT))
        self.velocity = Vector2(0, 0)
        self.previous_position = self.position.copy()  # Armazena a posição anterior
        self.previous_velocity = self.velocity.copy()  # Armazena a velocidade anterior
        self.acceleration = Vector2(0, 0)
        self.max_speed = 3
        self.max_acceleration = 0.1
        self.heading = 0  # Ângulo de rotação do triângulo
        self.collision_distance = 20


    def seek(self, target):
        desired_velocity = target - self.position
        desired_distance = 300  # Distância de referência para definir a velocidade máxima
        if desired_velocity.length() > 0:
            desired_velocity = desired_velocity.normalize() * self.max_speed * (desired_velocity.length() / desired_distance)

            # Verifica se a velocidade desejada está abaixo do limite mínimo
            min_speed = 1  # Velocidade mínima desejada
            if desired_velocity.length() < min_speed:
                desired_velocity = desired_velocity.normalize() * min_speed

        steering_force = desired_velocity - self.velocity
        return steering_force
    
    def avoid_other_agents(self, agents):
        avoidance_force = Vector2(0, 0)
        detection_radius = 60

        for other_agent in agents:
            if other_agent != self:
                to_other_agent = other_agent.position - self.position
                agent_distance = to_other_agent.length()

                # Verifica se o agente está dentro do raio de detecção do outro agente
                if 0 < agent_distance < detection_radius:
                    # Calcula a força de desvio proporcional à distância e direção do outro agente
                    avoidance_force += -to_other_agent.normalize() * (detection_radius - agent_distance) / detection_radius

        return avoidance_force
    
    
    def avoid_obstacles(self, obstacles):
        avoidance_force = Vector2(0, 0)
        detection_radius = 50

        for obstacle in obstacles:
            to_obstacle = obstacle.position - self.position
            obstacle_distance = to_obstacle.length()

            # Verifica se o agente está dentro do raio de detecção do obstáculo
            if 0 < obstacle_distance < detection_radius:
                # Calcula a força de desvio proporcional à distância e direção do obstáculo
                avoidance_force += -to_obstacle.normalize() * (detection_radius - obstacle_distance) / detection_radius

        return avoidance_force
    
    def collides_with(self, obstacle):
        # Calcula a distância entre o centro do agente e o obstáculo
        distance = self.position.distance_to(obstacle.position)

        # Verifica se ocorre colisão com base na distância e no raio do obstáculo
        if distance < 20:  # Raio do agente = 10
            return True
        else:
            return False

    def collides_with_any(self, obstacles):
        for obstacle in obstacles:
            if self.collides_with(obstacle):
                return True
        return False
    
    def check_collision_ahead(self, obstacles, num_frames):
        future_velocity = self.velocity.copy()  # Cria uma cópia temporária da velocidade atual
        future_position = self.position.copy()

        for _ in range(num_frames):
            future_velocity += self.acceleration
            future_velocity = future_velocity.normalize() * self.max_speed
            future_position += future_velocity
            self.previous_position = self.position.copy()

            for obstacle in obstacles:
                to_obstacle = obstacle.position - future_position
                obstacle_distance = to_obstacle.length()

                if obstacle_distance < self.collision_distance:
                    # Se houver uma possível colisão, muda o ângulo de direção do agente
                    self.heading += 90
                    self.heading %= 360
                    return

            if self.collides_with_any(obstacles):
                # Armazena a posição atual como posição anterior
                self.previous_position = self.position.copy()
                
             

                # Define uma nova direção aleatória para desviar do obstáculo
                self.velocity = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.max_speed

                # Volta para a posição anterior
                self.position = self.previous_position.copy()

                # Muda o ângulo de direção do agente
                self.heading += 90
                self.heading %= 360

                return


    def update(self, target, obstacles, agents):
        # Calcula a força resultante das ações de busca e desvio de obstáculos
        seek_force = self.seek(target)
        avoidance_force = self.avoid_obstacles(obstacles)
        other_agents_avoidance_force = self.avoid_other_agents(agents)
        steering_force = seek_force + avoidance_force + other_agents_avoidance_force

        # Adiciona a força de direção atual à aceleração
        self.acceleration += steering_force

        # Limita a aceleração à magnitude máxima
        if self.acceleration.length() > self.max_acceleration:
            self.acceleration = self.acceleration.normalize() * self.max_acceleration

        # Atualiza a velocidade com base na aceleração
        self.velocity += self.acceleration

        # Limita a velocidade à magnitude máxima
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed

        # Verifica a colisão antecipada nos próximos 10 frames
        self.check_collision_ahead(obstacles, 10)

        # Aplica o movimento
        self.previous_position = self.position.copy()  # Armazena a posição anterior

        # Atualiza a posição com base na velocidade
        self.position += self.velocity

        # Verifica se o agente está dentro do obstáculo após o movimento
        for obstacle in obstacles:
            if self.collides_with(obstacle):
                # Desfaz o movimento
                self.position = self.previous_position.copy()

                # Define uma nova direção aleatória para desviar do obstáculo
                self.velocity = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.max_speed

                # Muda o ângulo de direção do agente
                self.heading += 90
                self.heading %= 360

                break

        # Zera a aceleração a cada atualização
        self.acceleration *= 0

        # Calcula o ângulo de rotação com base na direção atual da velocidade
        self.heading = self.velocity.angle_to(Vector2(1, 0))

    def draw(self, screen):
        # Calcula os vértices do triângulo
        v1 = self.position + self.velocity.normalize() * 10
        v2 = self.position + self.velocity.normalize().rotate(120) * 10
        v3 = self.position + self.velocity.normalize().rotate(-120) * 10

        # Desenha o triângulo na tela
        pygame.draw.polygon(screen, BLACK, [v1, v2, v3])

class Obstacle:
    def __init__(self, position):
        self.position = position

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.position.x), int(self.position.y)), 10)

def create_obstacles():
    obstacles = []

    # Posição e tamanho do gargalo
    bottleneck_x = WIDTH // 2
    bottleneck_y = HEIGHT // 2
    bottleneck_width = 0
    bottleneck_height = 45

    # Espaçamento entre os obstáculos
    spacing = 10

    # Criação dos obstáculos acima do gargalo
    for y in range(0, bottleneck_y - bottleneck_height // 2, spacing):
        obstacles.append(Obstacle(Vector2(bottleneck_x - bottleneck_width // 2 , y)))

    # Criação dos obstáculos abaixo do gargalo
    for y in range(bottleneck_y + bottleneck_height // 2, HEIGHT, spacing):
        obstacles.append(Obstacle(Vector2(bottleneck_x - bottleneck_width // 2 , y)))

    return obstacles

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    agents = []  # Lista para armazenar os agentes
    for _ in range(NUMBER_AGENTS):
        agent = Agent()
        agents.append(agent)

    bottleneck_center = Vector2(WIDTH // 2, HEIGHT // 2)
    target = bottleneck_center

    obstacles = create_obstacles()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(WHITE)

        for agent in agents:
            # Ajusta a velocidade máxima com base na quantidade de agentes
            if len(agents) < NUMBER_AGENTS // 2:
                agent.max_speed = 6
            else:
                agent.max_speed = 2

            agent.update(target, obstacles, agents)
            agent.draw(screen)

            if agent.position.distance_to(target) < 10:
                agents.remove(agent)

        pygame.draw.circle(screen, RED, (int(target.x), int(target.y)), 5)
        for obstacle in obstacles:
            obstacle.draw(screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
