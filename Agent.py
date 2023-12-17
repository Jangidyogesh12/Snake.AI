import torch
import random
from game import snakeAI, Point
from collections import deque
from model import Q_Trainer, Linear_QNet
import numpy as np
from utils import plot

max_memory = 100_000
lr = 0.001
batch_size = 100

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9 #discount rate
        self.memory = deque(maxlen = max_memory)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = Q_Trainer(self.model, lr=lr, gamma=self.gamma)



    def get_state(self, game):
        head = game.snake[0]
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)
        
        dir_l = game.direction == 'left'
        dir_r = game.direction == 'right'
        dir_u = game.direction == 'up'
        dir_d = game.direction == 'down'

        state = [
            # Danger straight
            (dir_r and game.collide(point_r)) or 
            (dir_l and game.collide(point_l)) or 
            (dir_u and game.collide(point_u)) or 
            (dir_d and game.collide(point_d)),

            # Danger right
            (dir_u and game.collide(point_r)) or 
            (dir_d and game.collide(point_l)) or 
            (dir_l and game.collide(point_u)) or 
            (dir_r and game.collide(point_d)),

            # Danger left
            (dir_d and game.collide(point_r)) or 
            (dir_u and game.collide(point_l)) or 
            (dir_r and game.collide(point_u)) or 
            (dir_l and game.collide(point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
            ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory)>batch_size:
            mini_sample = random.sample(self.memory, batch_size)
        
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, done = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
    
    def get_action(self, state):

        '''
           Before doing any move we want our snake(agent) to rondomely move on the canvas

           to explore it and when it gets the knowledge about its environment it will start 

           to exploit the game ie. to make less randome moves. 
           
           THIS PROCESS IS CALLED TRADEOFF EXPLORATION VS EXPLOITATION

        '''

        self.epsilon = 80 - (self.n_games)
        action = [0,0,0] #[straight, left, right]

        if random.randint(0,200)<self.epsilon:
            move = random.randint(0,2)
            action[move] = 1

        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            action[move] = 1
        
        return action

def train():

    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = snakeAI()

    while True:
        #get the old state of the game 
        old_state = agent.get_state(game)

        #geting the action from the agent according to the old state
        action = agent.get_action(old_state)

        #performing the new moves and getting the new state from the new game
        reward, done , score = game.play(action)
        new_state = agent.get_state(game)

        #now we will train the short memory 
        agent.train_short_memory(old_state, action, reward, new_state, done)

        #remember
        agent.remember(old_state, action, reward, new_state, done)

        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score>record:
                record = score
                agent.model.save()
            
            print('Game:', agent.n_games, 'Score:', score, 'Record:',record)

            #PLOTINGS 
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)





if __name__ == '__main__':
    train()

