import pygame
import pygame.locals as locals
import random
import AI
import os
import numpy as np



class Game(object):
    SIZE = (300, 400)
    FPS = 50

    def __init__(self):
        self.surface = pygame.display.set_mode(Game.SIZE)
        self.clock = pygame.time.Clock()
        self.ai=AI.ArtificialIntelligence()

    def init(self):
        self.background = Background()
        #self.bird = Bird()
        self.birds=[]
        networks=self.birds.next_generation_networks()
        for network in networks:
            self.birds.append(Bird(network))
        self.score_obj = Score()
        self.pipes = []
        self.pipes.append(Pipe())
        self.time = 0
        self.is_running = True
        self.score = 0

    def start(self):
        self.init()
        while self.is_running:
            self.time += 1
            if self.time == 100000000:
                self.time = 0
            self.control()
            self.update()
            self.draw()
            pygame.display.update()
            print("存活："+str(len())+',第几代：'+str(self.gen)+',分数：'+str(self.score))
            if self.score>50000 and not os.path.exists('neuro_model.csv'):
                layers=np.array(self.birds[0].network.get_data()['layers'])
                weights=np.array(self.birds[0].network.get_data()['weights'])
                np.savetxt('neuro_model.csv',weights,delimiter=",")

            self.clock.tick(Game.FPS)
            #pygame.mixer_music.load('C:\Users\Administrator\Downloads')

    def control(self):
        for event in pygame.event.get():
            if event.type == locals.QUIT:
                exit()
            if event.type == locals.KEYDOWN:
                if event.key == locals.K_SPACE:
                    self.bird.fly()

    def create_pipe(self):
        if self.time % 50 == 0:
            self.pipes.append(Pipe())

    def update_pipes(self):
        index = len(self.pipes) - 1
        while index >= 0:
            if self.pipes[index].need_remove():
                del (self.pipes[index])
            else:
                self.pipes[index].update()
            index -= 1

    def draw_pipes(self, surface):
        for pipe in self.pipes:
            pipe.draw(surface)


    def update_birds(self):
        index=len(self.birds)-1
        while index>=0:
            if self.birds[index].is_dead(self.pipes):
                self.ai.gather_score(self.birds[index].network,self.time)
                del (self.birds[index])
            else:
                inputs=self.birds[index].get_inputs(self.pipes)
                ret=self.birds[index].network.get_result(inputs)
                if ret[0]>0.5:
                    self.birds[index].fly()
                self.birds[index].update()
            index=-1
        if len(self.birds)==0:
            self.start()

    def draw_birds(self,surface):
        for pipe in self.birds:
            pipe.draw(surface)

    def update(self):
        if self.bird.is_dead(self.pipes):
            self.is_running = False
        for pipe in self.pipes:
            if pipe.need_add_score(self.bird):
                self.score += 1
        self.create_pipe()
        self.background.update()
        self.bird.update()
        self.update_pipes()
        self.score_obj.update(self.score)

    def draw(self):
        self.background.draw(self.surface)
        self.bird.draw(self.surface)
        self.draw_pipes(self.surface)
        self.score_obj.draw(self.surface)


class Background(object):
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self, surface):
        surface.fill((200, 200, 200))


class Bird(object):
    IMG = pygame.image.load("./res/bird.png")

    def __init__(self,network):
        self.x = 50
        self.y = 180
        self.width = Bird.IMG.get_width()
        self.height = Bird.IMG.get_height()
        self.speed = 0
        self.network=network

    def update(self):
        self.y += self.speed
        if self.speed < 8:
            self.speed += 1

    def draw(self, surface):
        surface.blit(Bird.IMG, (self.x, self.y))

    def fly(self):
        self.speed = -8

    def is_dead(self, pipes):
        if self.y < 0:
            return True
        if self.y + self.height > Game.SIZE[1]:
            return True
        for pipe in pipes:
            if self.x + self.width > pipe.x \
                    and self.x < pipe.x + pipe.width:
                if self.y < pipe.up_y or self.y + self.height > pipe.down_y:
                    return True
        return False

    def get_inputs(self,pipes):
        inputs=[self.y,0.0,0.0,0.0,0.0]
        for pipe in pipes:
            if not pipe.x<self.x-pipe.width:
                inputs[1]=(self.x+self.width)-pipe.x
                inputs[2]=self.x-(pipe.x+pipe.width)
                inputs[3]=self.y-pipe.up_y
                inputs[4]=(self.y+self.height)-pipe.down_y
                break
        return inputs


class Pipe(object):
    DOWN_PIPE = pygame.image.load("./res/pipe.png")
    UP_PIPE = pygame.transform.rotate(DOWN_PIPE, 180)
    GAP_SIZE = 100  # 上下管道之间的间隙
    MIN_SIZE = 80  # 管道在窗口中最小的长度

    def __init__(self):
        self.x = Game.SIZE[0]
        self.up_y = random.randint(Pipe.MIN_SIZE, Game.SIZE[1] - (Pipe.MIN_SIZE + Pipe.GAP_SIZE))  # 上管道管口的坐标
        self.down_y = self.up_y + Pipe.GAP_SIZE  # 下管道管口的坐标
        self.width = Pipe.DOWN_PIPE.get_width()
        self.height = Pipe.DOWN_PIPE.get_height()
        self.speed = 4
        self.score_flag = True

    def need_remove(self):
        if self.x <= -self.width:
            return True
        return False

    def update(self):
        self.x -= self.speed

    def draw(self, surface):
        surface.blit(Pipe.UP_PIPE, (self.x, self.up_y - self.height))
        surface.blit(Pipe.DOWN_PIPE, (self.x, self.down_y))

    def need_add_score(self, bird):
        if self.score_flag:
            if self.x + self.width < bird.x:
                self.score_flag = False
                return True
        return False


class Score(object):
    def __init__(self):
        self.y = 40

    def update(self, score):
        self.imgs = []
        for num in str(score):
            self.imgs.append(pygame.image.load("./res/" + num + ".png"))
        width = 0
        for img in self.imgs:
            width += img.get_width()
        self.x = Game.SIZE[0] / 2 - width / 2

    def draw(self, surface):
        for i in range(len(self.imgs)):
            surface.blit(self.imgs[i], (self.x, self.y))
            self.x += self.imgs[i].get_width()


if __name__ == '__main__':
    game = Game()
    while True:
        game.start()
