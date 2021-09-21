import pygame
import neat
import os
import time
import random
pygame.font.init()

Screen_height = 800
Screen_width = 500

STAT_FONT = pygame.font.SysFont("comicsans", 50)

GEN = 0

Bird_Imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
Pipe_Img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
Base_Img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_Img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

class Bird:
    imgs = Bird_Imgs
    max_rotation = 25                 #degrees
    rotation_speed = 20
    animation_time = 5

    def __init__(self, x, y):
        self.x = x                    #starting position of bird (x & y)
        self.y = y
        self.tilt = 0                 #how much  the image is tilted in the screen. intially tilt = 0 moving flat until we move it
        self.tick_count = 0  
        self.speed = 0
        self.height = self.y
        self.img_count = 0            #which image of bird currently showing
        self.img = self.imgs[0]

    def jump(self):
        self.speed = -10.5
        self.tick_count = 0           #to keep track of when we last jumped
        self.height = self.y          #where the bird started moving/jump from

    def move(self):                   #used to call when every single frame to move our bird
        self.tick_count += 1

        dis = self.speed*self.tick_count + 1.5*self.tick_count**2       #how many pixels we've have moved upward or dowmward by changing y position

        if dis >= 16:                                                   #taking 16 as terminal velocity
            dis = 16

        if dis < 0:
            dis -= 2                                                    #to move upward a lil bit more

        self.y = self.y + dis

        if dis < 0 or self.y < self.height + 50:           #if moving upward
            if self.tilt < self.max_rotation:
                self.tilt = self.max_rotation
        else:                                              #if moving downward
            if self.tilt > -90:
                self.tilt -= self.rotation_speed

    def draw(self, window):

        self.img_count += 1                                #how many times we've shown one image

        if self.img_count <= self.animation_time:
            self.img = self.imgs[0]
        elif self.img_count <= self.animation_time*2:
            self.img = self.imgs[1]
        elif self.img_count <= self.animation_time*3:
            self.img = self.imgs[2]
        elif self.img_count <= self.animation_time*4:
            self.img = self.imgs[1]
        elif self.img_count == self.animation_time*4 + 1:
            self.img = self.imgs[0]
            self.img_count = 0

        if self.tilt <= -80:                             #when diving straight downward
            self.img = self.imgs[1]                      #making it flat
            self.img_count = self.animation_time*2       #when jump back up its where it should be   

        #to roate the birc around the center based on its current tilt
        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y) ).center )
        window.blit(rotated_img, new_rect.topleft)

    def get_mask(self):                                  #due to collision
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200 
    VEL = 5
    #height or y will be random everytime

    def __init__(self, x):
        self.x = x
        self.height = 0
        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(Pipe_Img, False, True)
        self.PIPE_BOTTOM = Pipe_Img

        self.passed = False                                    #if the bird is already passed by the pipe & collision purposes
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()    #bujhi nai kichu watch the video again
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -=self.VEL                                      #mainly the background moves in negative x direction

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()         #check in pygame
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        #offset is how far away these masks are from each other
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)  #point will return if the masks collide or not 
        t_point = bird_mask.overlap(top_mask,top_offset)         #if they dont collied will return none

        if b_point or t_point:                                   #this if means means they are not None
            return True

        return False

class Base:
    VEL = 5                                                     #velocity must be same as the pipe
    WIDTH = Base_Img.get_width()
    IMG = Base_Img

    def __init__(self, y):                                      #dont need x as parameter since it will be moving
        self.y = y
        self.x1 = 0                                             #iniatially in the screen       
        self.x2 = self.WIDTH                                    #stays behind the width and comes in the screen after x1 passes by 

    def move(self):                                             #in oeder to move in circular pattern
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:                            #if x1 is off the screen
            self.x1 = self.x2 + self.WIDTH                      #x1 recycles back

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(window, birds, pipes, base, score, gen):

    window.blit(BG_Img, (0,0))

    for pipe in pipes:
        pipe.draw(window)

    score_text = STAT_FONT.render( "Score: " + str(score), 1, (255,255,255) )
    window.blit(score_text, (Screen_width - score_text.get_width(), 10))

    gen_text = STAT_FONT.render( "Generation: " + str(gen), 1, (255,255,255) )
    window.blit(gen_text, (10, 10))

    base.draw(window)

    for bird in birds:
        bird.draw(window)

    pygame.display.update()

def main(genomes, config):
    global GEN
    GEN += 1

    nets = []   #to keep track of neural network that controls to keep track of the where that position is in the screen
    ge = []     #keeoing ytrack of genomes to change their fitness according to need
    birds = []  #for multiple birds at a time

    for g_id,g in genomes:                                       #genomes come in touples
        net = neat.nn.FeedForwardNetwork.create(g, config)       #setting up neural network for each genome
        nets.append(net)                                         #appending that to the list
        birds.append(Bird(230,350))                              #appending bird object
        g.fitness = 0
        ge.append(g)


    base = Base(730)
    pipes = [Pipe(600)]
    window = pygame.display.set_mode((Screen_width, Screen_height))

    clock = pygame.time.Clock()
    
    score = 0

    run = True

    while run:

        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_idx = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():   # determining whether to use the first or second
                pipe_idx = 1                                                                 # pipe on the screen for neural network input
        else:
            run = False
            break
        
        for x, bird in enumerate(birds):  
            ge[x].fitness += 0.1              # give each bird a fitness 0.1 for each frame to encourage to stay alive
            bird.move()

            # send bird location, top pipe location and bottom pipe location to neural network and determine from network whether to jump or not
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_idx].height), abs(bird.y - pipes[pipe_idx].bottom)))     #this output is a list

            if output[0] > 0.5:                # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()




        #a list to keep the removed pipes which passes off the screen
        rem = []  
        add_pipe = False    

        for pipe in pipes:
            for x,bird in enumerate(birds):       #x is to know the postion of the bird in the list 
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    
                if not pipe.passed and pipe.x < bird.x:       #if bird is already passed a pipe
                    pipe.passed = True
                    add_pipe = True         
                
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:       #if pipe is off the screen append it in the rem list
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))                          #another pipe to arrive in the screen

        for r in rem:
            pipes.remove(r)

        for x,bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:        #if bird hits ground
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()

        draw_window(window, birds, pipes, base, score, GEN)


def run(config_path):
    #load in the configuration file and runs the NEAT algorithm to train a neural network to play flappy bird    
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # setting the population p based on whatever we have in the congif file
    p = neat.Population(config)

    #the output we gonna see
    p.add_reporter(neat.StdOutReporter(True))     #this stdout reporter shows detailed statistics about progress of each generation and about best fitness
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    #50 is how many generations and main is the fitness function which is called 50 times and pass all of the genomes like population,
    #current gen population, and the congif file also
    winner = p.run(main, 50) 

    #fitness function is determined by how far the bird moves in the game

if __name__ == "__main__":
   
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'confi-feedforward.txt')
    run(config_path)