
import sys
import math
import copy


import pygame
from pygame.locals import *
import random

global vec2
vec2 = pygame.math.Vector2

visualTraing = True
if __name__ == "__main__" or visualTraing:
    pygame.init()

    fps = 60
    fpsClock = pygame.time.Clock()

    width, height = 1000, 700
    gameDisplay = pygame.display.set_mode((width, height))



    bg = pygame.image.load("Images/background.png")
    player_image = pygame.image.load("Images/car.png")
    top_player_image = pygame.image.load("Images/car2.png")

class Player:
    def __init__(self, extinc_value):
        self.pos = [800, 400]
        self.fitness = 0
        self.alive = True
        self.angle = 270
        self.width, self.height = 30, 15
        # self.color = (200, 150, 100)
        self.rotatedFrame = []
        self.sights = [180, 225, 270, 315, 360]
        self.intersectionPoints = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]

        #Making the game more smooth
        self.acceleration = 0.1
        self.velocity = 0
        self.time = 0

        self.timeTillExtintcion = extinc_value

        self.img_length = player_image.get_rect().size

    def get_rotated_hitbox(self):
        """
        Gets the edges of the car even after rotaton

        :return: list of 4 (x,y) tuples
        """

        posX, posY = self.pos[0] - 15, self.pos[1] - 8
        rect = [[[posX, posY], [posX + self.width - 15, posY]],
                [[posX + self.width, posY], [posX + self.width, posY + self.height - 5]],
                [[posX + self.width - 15, posY + self.height], [posX, posY + self.height]],
                [[posX, posY + self.height - 5], [posX, posY]]]

        for i, line in enumerate(rect):
            # Find the midpointd

            # midpoint = [(line[0][0]+line[1][0])/2, (line[0][1]+line[1][1])/2]

            midpoint = [self.pos[0] - self.img_length[0] / 2, self.pos[1] - self.img_length[1] / 2]

            # Make the midpoint the origin
            point1Mid = [
                line[0][0] - midpoint[0],
                line[0][1] - midpoint[1]
            ]

            point2Mid = [
                line[1][0] - midpoint[0],
                line[1][1] - midpoint[1]
            ]

            # Rotation matrix
            point1_rotated = [
                math.cos(math.radians(-self.angle)) * point1Mid[0] - math.sin(math.radians(-self.angle)) * point1Mid[1],
                math.sin(math.radians(-self.angle)) * point1Mid[0] + math.cos(math.radians(-self.angle)) * point1Mid[1]
            ]

            point2_rotated = [
                math.cos(math.radians(-self.angle)) * point2Mid[0] - math.sin(math.radians(-self.angle)) * point2Mid[1],
                math.sin(math.radians(-self.angle)) * point2Mid[0] + math.cos(math.radians(-self.angle)) * point2Mid[1]
            ]

            # Add midpoint back

            point1_rotated[0] += midpoint[0]
            point1_rotated[1] += midpoint[1]
            point2_rotated[0] += midpoint[0]
            point2_rotated[1] += midpoint[1]

            point1_rotated[0] += self.pos[0] - point2_rotated[0]
            point1_rotated[1] += self.pos[1] - point2_rotated[1]
            point2_rotated[0] += self.pos[0] - point2_rotated[0]
            point2_rotated[1] += self.pos[1] - point2_rotated[1]

            rect[i] = [point1_rotated, point2_rotated]

        return rect


class Wall:
    def __init__(self, pos1, pos2):
        self.pos1, self.pos2 = pos1, pos2


    def draw(self):
        pygame.draw.line(gameDisplay, (255, 255, 0), self.pos1, self.pos2, 5)

    # On two line segments s0 and s1, check if they intersect through dot product
    # Found on https://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect
    def intersects(self, s0, s1):
        dx0 = s0[1][0] - s0[0][0]
        dx1 = s1[1][0] - s1[0][0]
        dy0 = s0[1][1] - s0[0][1]
        dy1 = s1[1][1] - s1[0][1]
        p0 = dy1 * (s1[1][0] - s0[0][0]) - dx1 * (s1[1][1] - s0[0][1])
        p1 = dy1 * (s1[1][0] - s0[1][0]) - dx1 * (s1[1][1] - s0[1][1])
        p2 = dy0 * (s0[1][0] - s1[0][0]) - dx0 * (s0[1][1] - s1[0][1])
        p3 = dy0 * (s0[1][0] - s1[1][0]) - dx0 * (s0[1][1] - s1[1][1])
        return (p0 * p1 <= 0) & (p2 * p3 <= 0)


    #https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines
    def findIntersection(self, x1, y1, x2, y2, x3, y3, x4, y4):
        global vec2
        uA = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
        uB = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
        if 0 <= uA <= 1 and 0 <= uB <= 1:
            intersectionX = x1 + (uA * (x2 - x1))
            intersectionY = y1 + (uA * (y2 - y1))
            return vec2(intersectionX, intersectionY)
        return None


    def check_collision(self, frame):
        for line in frame:
            if self.intersects(line, [self.pos1, self.pos2]):
                return True
        return False

class Gate:
    def __init__(self, pos1, pos2, requirements):
        self.pos1, self.pos2, = pos1, pos2
        self.requirements = requirements

    def intersects(self, s0, s1):
        dx0 = s0[1][0] - s0[0][0]
        dx1 = s1[1][0] - s1[0][0]
        dy0 = s0[1][1] - s0[0][1]
        dy1 = s1[1][1] - s1[0][1]
        p0 = dy1 * (s1[1][0] - s0[0][0]) - dx1 * (s1[1][1] - s0[0][1])
        p1 = dy1 * (s1[1][0] - s0[1][0]) - dx1 * (s1[1][1] - s0[1][1])
        p2 = dy0 * (s0[1][0] - s1[0][0]) - dx0 * (s0[1][1] - s1[0][1])
        p3 = dy0 * (s0[1][0] - s1[1][0]) - dx0 * (s0[1][1] - s1[1][1])
        return (p0 * p1 <= 0) & (p2 * p3 <= 0)

    def check_collision(self, frame, score):
        for line in frame:
            if self.intersects(line, [self.pos1, self.pos2]) and score in self.requirements:
                return score+1
        return score


class Game:
    def __init__(self, population_count, gui=False):
        self.gui = gui
        self.extinction_value = 75
        self.players = [Player(self.extinction_value) for i in range(population_count)]
        self.information = []
        self.population_alive = population_count
        self.running = False
        self.friction = 0.95


        # Race boundaries
        self.show_bounds = False
        self.walls = []
        for i, point in enumerate(
                [(891, 361), (873, 459), (847, 524), (763, 602), (632, 660), (511, 667), (350, 640), (239, 596),
                 (150, 571), (119, 543), (113, 516), (125, 486), (171, 450), (247, 422), (294, 376), (242, 317),
                 (176, 286), (86, 242), (75, 206), (94, 157), (168, 104), (283, 72), (514, 79), (653, 91), (759, 120),
                 (818, 156), (865, 234), (891, 361)]):
            if i != 0:
                self.walls.append(Wall(pastPoint, point))
            pastPoint = point

        for i, point in enumerate(
                [(763, 331), (752, 394), (742, 424), (725, 462), (696, 511), (658, 556), (558, 563), (481, 557),
                 (413, 547), (368, 516), (363, 504), (371, 481), (395, 452), (429, 430), (484, 411), (500, 393),
                 (499, 377), (490, 352), (475, 329), (442, 313), (308, 263), (292, 238), (301, 216), (329, 190),
                 (392, 157), (422, 164), (683, 238), (710, 256), (740, 279), (762, 331)]):
            if i != 0:
                self.walls.append(Wall(pastPoint, point))
            pastPoint = point

        #gates = [[(883, 312), (764, 322)], [(764, 322), (838, 193)], [(838, 193), (742, 278)], [(742, 278), (769, 127)], [(769, 127), (710, 249)], [(710, 249), (665, 99)], [(665, 99), (646, 222)], [(646, 222), (571, 89)], [(571, 89), (578, 198)], [(578, 198), (489, 86)], [(489, 86), (495, 175)], [(495, 175), (404, 78)], [(404, 78), (407, 156)], [(407, 156), (237, 84)], [(237, 84), (334, 185)], [(334, 185), (99, 153)], [(99, 153), (310, 208)], [(310, 208), (134, 267)], [(134, 267), (303, 259)], [(303, 259), (267, 334)], [(267, 334), (347, 285)], [(347, 285), (294, 378)], [(294, 378), (482, 345)], [(482, 345), (266, 411)], [(266, 411), (376, 465)], [(376, 465), (208, 440)], [(208, 440), (369, 520)], [(369, 520), (145, 566)], [(145, 566), (395, 537)], [(395, 537), (302, 624)], [(302, 624), (457, 556)], [(457, 556), (433, 656)], [(433, 656), (534, 567)], [(534, 567), (528, 671)], [(528, 671), (585, 566)], [(585, 566), (669, 646)], [(669, 646), (649, 555)], [(649, 555), (812, 567)], [(812, 567), (700, 502)], [(700, 502), (873, 472)], [(873, 472), (728, 445)]]
        gates = [[(883, 312), (764, 322)], [(838, 193), (742, 278)], [(769, 127), (710, 249)], [(665, 99), (646, 222)], [(571, 89), (578, 198)], [(489, 86), (495, 175)], [(404, 78), (407, 156)], [(237, 84), (334, 185)], [(99, 153), (310, 208)], [(134, 267), (303, 259)], [(267, 334), (347, 285)], [(294, 378), (482, 345)], [(266, 411), (376, 465)], [(208, 440), (369, 520)], [(113, 518), (383, 531)], [(145, 566), (395, 537)],[(257, 606), (413, 545)], [(302, 624), (457, 556)], [(391, 639), (481, 558)], [(433, 656), (534, 567)], [(528, 671), (585, 566)], [(669, 646), (649, 555)], [(812, 567), (700, 502)], [(873, 472), (728, 445)], [(890, 392), (758, 365)]]
        self.gates = []
        temp = []
        for i, gate in enumerate(gates):
            self.gates.append(Gate(gate[0], gate[1], [i, i+len(gates)]))




    def start(self):
        self.running = True

        return self.generate_observation()

    def generate_observation(self):
        information = []
        for player in self.players:
            information.append([
                (abs(player.intersectionPoints[0][0]-player.pos[0]) + abs(player.intersectionPoints[0][1]-player.pos[1]))/1000,
                (abs(player.intersectionPoints[1][0] - player.pos[0]) + abs(player.intersectionPoints[1][1] - player.pos[1]))/1000,
                (abs(player.intersectionPoints[2][0] - player.pos[0]) + abs(player.intersectionPoints[2][1] - player.pos[1]))/1000,
                (abs(player.intersectionPoints[3][0] - player.pos[0]) + abs(player.intersectionPoints[3][1] - player.pos[1]))/1000,
                (abs(player.intersectionPoints[4][0] - player.pos[0]) + abs(player.intersectionPoints[4][1] - player.pos[1]))/1000,
            ])

        return information  # What to pass: 5 rays for how close the car is to wall

    def run(self, step):

        if self.gui:
            self.draw()

        self.population_alive = [player.alive for player in self.players].count(True)
        if self.population_alive == 0:
            self.running = False

        self.movement(step)

        return self.generate_observation()

    def draw(self):

        gameDisplay.blit(bg, (0, 0))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # Draw player
        for i, player in enumerate(self.players):
            if player.alive:
                if i != 0 or __name__ == "__main__":
                    img = pygame.transform.rotate(
                        pygame.transform.scale(player_image, (player.width, player.height)), player.angle)
                    gameDisplay.blit(img,
                                     (player.pos[0] - img.get_rect().size[0] / 2, player.pos[1] - img.get_rect().size[1] / 2))
                else:
                    img = pygame.transform.rotate(
                        pygame.transform.scale(top_player_image, (player.width+20, player.height+10)), player.angle)
                    gameDisplay.blit(img,
                                     (player.pos[0] - img.get_rect().size[0] / 2,
                                      player.pos[1] - img.get_rect().size[1] / 2))


                if self.show_bounds:
                    for intersectionPoint in player.intersectionPoints:

                        width, height = player.pos[0] - img.get_rect().size[0] / 2 + 10, player.pos[1] - \
                                        img.get_rect().size[1] / 2 + 5

                        if intersectionPoint != -1:
                            pygame.draw.rect(gameDisplay, (255, 255, 0), (intersectionPoint[0], intersectionPoint[1], 10, 10), 0)

                            pygame.draw.line(gameDisplay, (255, 255, 0), (width, height), (intersectionPoint[0], intersectionPoint[1]), 5)

        if self.show_bounds:
            for line in self.players[0].rotatedFrame:
                pygame.draw.line(gameDisplay, (255, 255, 0), line[0], line[1], 2)

            for wall in self.walls:
                wall.draw()

            for gate in self.gates:
                pygame.draw.line(gameDisplay, (200, 200, 50), gate.pos1, gate.pos2, 2)

        pygame.display.flip()
        fpsClock.tick(180)

    def movement(self, steps):
        for i, step in enumerate(steps):



            if self.players[i].alive:

                self.players[i].rotatedFrame = self.players[i].get_rotated_hitbox()

                self.friction = 0.95
                if step == 0:
                    self.players[i].angle -= 1
                    self.friction = 0.99
                elif step == 2:
                    self.players[i].angle += 1
                    self.friction = 0.99
                elif step == 1:
                    self.players[i].velocity += self.players[i].acceleration



                self.players[i].velocity *= self.friction
                self.players[i].pos[0] += math.sin(math.radians(self.players[i].angle - 90))*self.players[i].velocity * (1.3 if self.friction == 0.99 else 1)
                self.players[i].pos[1] += math.cos(math.radians(self.players[i].angle - 90))*self.players[i].velocity * (1.3 if self.friction == 0.99 else 1)


                for wall in self.walls:
                    if wall.check_collision(self.players[i].rotatedFrame):
                        self.players[i].alive = False


                for gate in self.gates:
                    tempFit = self.players[i].fitness
                    self.players[i].fitness = gate.check_collision(self.players[i].rotatedFrame, self.players[i].fitness)

                    self.players[i].time += 1
                    if self.players[i].fitness > tempFit:
                        self.players[i].timeTillExtintcion = self.extinction_value

                    if self.players[i].fitness == 50:
                        self.players[i].alive = False
                        self.players[i].fitness += 1/self.players[i].time


                for _, sight in enumerate(self.players[i].sights):
                    width, height = self.players[i].pos[0]+10, self.players[i].pos[1]
                    points = [(width, height), (width+1000*math.sin(math.radians(sight+self.players[i].angle)), height+1000*math.cos(math.radians(sight+self.players[i].angle)))]

                    intersectionPoint = [-1,-1]
                    distance = 100000
                    for wall in self.walls:
                        point =  wall.findIntersection(points[0][0], points[0][1], points[1][0], points[1][1], wall.pos1[0], wall.pos1[1], wall.pos2[0], wall.pos2[1])

                        if point != None:
                            if abs(point[0]-self.players[i].pos[0]) + abs(point[1]-self.players[i].pos[1]) < distance:
                                distance = abs(point[0]-self.players[i].pos[0]) + abs(point[1]-self.players[i].pos[1])
                                intersectionPoint = point


                    self.players[i].intersectionPoints[_] = intersectionPoint

                self.players[i].timeTillExtintcion -= 1

                if self.players[i].timeTillExtintcion <= 0:
                    self.players[i].alive = False

                if not 0 <= self.players[i].pos[0] <= 1000 and not 0 <= self.players[i].pos[1] <= 700:
                    self.players[i].alive = False



if __name__ == "__main__":
    running = True
    while running:
        game = Game(1, True)
        game.start()

        stop = False

        lines = []
        while game.running:
            game.players[0].timeTillExtintcion = 10000
            state = -2
            keys = pygame.key.get_pressed()
            if keys[ord("w")]:
                state = 1
            if keys[ord("d")]:
                state = 0
            if keys[ord("a")]:
                state = 2

            observation = game.run([state])

            #print(observation)



            #boundaries maker
            pos = pygame.mouse.get_pos()
            pressed = pygame.mouse.get_pressed()
            if pressed[0] == 1 and not stop:
                stop = True
                lines.append(pos)
            if pressed[0] == 0:
                stop = False

            if keys[ord("n")]:
                print(lines)

        print(game.players[0].fitness)


