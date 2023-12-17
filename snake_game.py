import pygame
from collections import namedtuple
import random

pygame.init()


Point = namedtuple('Point', 'x, y')
font = pygame.font.SysFont('arial', 25)


class snake:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.blocksize = 20
        self.speed = 20
        self.Clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.w, self.h))
        

        #state
        self.direction = 'right'
        self.head= Point(self.w/2 , self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-self.blocksize, self.head.y),
                      Point(self.head.x-(2*self.blocksize), self.head.y)]
        self.food = None
        self.score = 0
        self._place_food()


    def _place_food(self):
        x = random.randint(0, (self.w - self.blocksize)//self.blocksize)*self.blocksize
        y = random.randint(0, (self.h - self.blocksize)//self.blocksize)*self.blocksize
        self.food = Point(x,y)
        if self.food in self.snake:
            self._place_food()


    def play(self):

        #Taking Input from the user
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_LEFT:
                    self.direction = 'left'
                elif event.key==pygame.K_RIGHT:
                    self.direction = 'right'
                elif event.key==pygame.K_UP:
                    self.direction = 'up'
                elif event.key==pygame.K_DOWN:
                    self.direction = 'down'      

        # snake_movement
        self.change_direction(self.direction)
        self.snake.insert(0, self.head)

        #Collision Detection
        game_over = False
        if self.collide():
            game_over = True
            return game_over, self.score

        # food placement
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        # Updating
        self.update()
        self.Clock.tick(self.speed)

        #Returnig the final score and the game condition
        return game_over, self.score

    
    def update(self):
        self.screen.fill("black")
        for pt in self.snake:
            pygame.draw.rect(self.screen,"green",pygame.Rect(pt.x, pt.y,self.blocksize,self.blocksize))
            pygame.draw.rect(self.screen,"darkgreen",pygame.Rect(pt.x+4, pt.y+4, self.blocksize-8, self.blocksize-8))
        pygame.draw.rect(self.screen, "yellow", pygame.Rect(self.food.x, self.food.y,self.blocksize,self.blocksize))
        text = font.render("Score: " + str(self.score), True, "white")
        self.screen.blit(text, [0, 0])
        pygame.display.flip()

    def change_direction(self, direction):
        x = self.head.x
        y = self.head.y
        if direction=='left':
            x -= self.blocksize
        elif direction=='right':
            x += self.blocksize
        elif direction=='up':
            y -= self.blocksize
        elif direction=='down':
            y += self.blocksize

        self.head = Point(x,y)
    
    def collide(self):
        if self.head in self.snake[1:]:
            print(self.head)
            return True
        if self.head.x > self.w - self.blocksize or self.head.x < 0 or self.head.y > self.h - self.blocksize or self.head.y < 0:
            return True
        else:
            return False



if __name__ == '__main__':
    game = snake()
    
    # game loop
    while True:
        game_over, score = game.play()
        
        if game_over == True:
            break
        
    print('Final Score', score)
        
        
    pygame.quit()