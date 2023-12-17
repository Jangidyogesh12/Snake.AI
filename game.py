import pygame
from collections import namedtuple
import random
import numpy as np

pygame.init()


Point = namedtuple('Point', 'x, y')
font = pygame.font.SysFont('arial', 25)


class snakeAI:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.blocksize = 20
        self.speed = 20
        self.Clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.reset()
        

    def reset(self):
        self.direction = 'right'
        self.head= Point(self.w/2 , self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-self.blocksize, self.head.y),
                      Point(self.head.x-(2*self.blocksize), self.head.y)]
        self.food = None
        self.score = 0
        self._place_food()
        self.frame_iteration = 0;

    def _place_food(self):
        x = random.randint(0, (self.w - self.blocksize)//self.blocksize)*self.blocksize
        y = random.randint(0, (self.h - self.blocksize)//self.blocksize)*self.blocksize
        self.food = Point(x,y)
        if self.food in self.snake:
            self._place_food()


    def play(self, action):
        # Taking action input from the modelAgent
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()      

        # snake_movement
        self.change_direction(action)
        self.snake.insert(0, self.head)

        #Collision Detection
        reward = 0
        game_over = False
        if self.collide()  or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # food placement
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        # Updating
        self.update()
        self.Clock.tick(self.speed)

        #Returnig the final score and the game condition
        return reward, game_over, self.score

    
    def collide(self, pt = None):
        if pt is None:
            pt = self.head
        if pt in self.snake[1:]:
            return True
        if pt.x > self.w - self.blocksize or pt.x < 0 or pt.y > self.h - self.blocksize or pt.y < 0:
            return True
        else:
            return False
        

    def update(self):
        self.screen.fill("black") 

        for pt in self.snake:
            pygame.draw.rect(self.screen,"green",pygame.Rect(pt.x, pt.y,self.blocksize,self.blocksize))
            pygame.draw.rect(self.screen,"darkgreen",pygame.Rect(pt.x+4, pt.y+4, self.blocksize-8, self.blocksize-8))

        pygame.draw.rect(self.screen, "yellow", pygame.Rect(self.food.x, self.food.y,self.blocksize,self.blocksize))

        text = font.render("Score: " + str(self.score), True, "white")
        self.screen.blit(text, [0, 0])
        
        pygame.display.flip()

    
    def change_direction(self, action):
        # [straight, right, left] and this id denoted by an array of [1,0,0], [0,1,0] and [0,0,1]
        clock_wise = ['right', 'down', 'left', 'up']
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1,0,0]):
            new_dir = clock_wise[idx] # NO chage in the direction
        elif np.array_equal(action, [0,1,0]):
            next_idx = (idx+1)%4
            new_dir = clock_wise[next_idx] # right turn 
        else: #[0,0,1]
            next_idx = (idx-1)%4
            new_dir = clock_wise[next_idx] #left turn
        
        self.direction = new_dir
    
        x = self.head.x
        y = self.head.y
        if self.direction=='left':
            x -= self.blocksize
        elif self.direction=='right':
            x += self.blocksize
        elif self.direction=='up':
            y -= self.blocksize
        elif self.direction=='down':
            y += self.blocksize

        self.head = Point(x,y)

