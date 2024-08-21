import pygame
import neat
import time
import os
import random
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

bird_img = [pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'bird1.png'))),pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'bird2.png'))),pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'bird3.png')))]
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'pipe.png')))
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'base.png')))
bg_img = pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'bg.png')))

STAT_FONT = pygame.font.SysFont('Consolas', 40)

# classes --------------------------------------------------------
class Bird:
    IMG = bird_img
    MAX_ROTATION = 25
    ROT_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMG[0]

    def jump(self):
        self.velocity = -10.5 #in pygame upper left corner is [0,0]... to move up need negative velocity
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        # for downward acceleration arc
        displacement = self.velocity * self.tick_count + 1.5 * self.tick_count**2

        # terminal velocity
        if displacement >= 16:
            displacement = 16

        #fine tune jump
        if displacement < 0:
            displacement -= 2

        self.y += displacement

        if displacement < 0 or self.y < self.height + 50: # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else: # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VELOCITY

    def draw(self, win):
        self.img_count += 1

        # bird animation
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMG[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMG[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMG[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMG[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMG[0]
            self.img_count = 0

        # so when bird is nose diving, it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMG[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_img, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False


class Base:
    VELOCITY = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        # background cycle
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


# window ---------------------------------------------------------
def draw_window(win, birds, pipes, base, score):
    win.blit(bg_img, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render('Score: ' + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - text.get_width() - 10, 10))

    base.draw(win)

    for bird in birds:
        bird.draw(win)

    pygame.display.update()


# main game loop -------------------------------------------------------
def main(genomes, config):
    nets = []
    ge = []
    birds = []

    for _, g in genomes: #(_, g) because it's a tuple
        net  = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:
        clock.tick(30) # 30fps
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        #what pipe are we looking at (if pipe passed, change to next in the list)
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        # move the bird
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1 # small amount because loop is running 30 times a second

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        remove = []
        add_pipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove.append(pipe)
            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5 #encourage the birds to actually go through the pipes
            pipes.append(Pipe(700))
        for r in remove:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        if score > 50: # fitness threshold
            break

        base.move()

        draw_window(win, birds, pipes, base, score)


# NEAT -----------------------------------------------------------
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # create the population, which is top-level object for NEAT run
    p = neat.Population(config)

    # show progress in terminal
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # run for up to 50 generations
    # because fitness criteria is who ever makes it farthest -> use main() as fitness function
    winner = p.run(main,50)

if __name__ == '__main__':
    # determine path to config so script will run successfully regardless of current working directory
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-neat.txt')
    run(config_path)