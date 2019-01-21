"""
 Pygame base template

 Sample Python/Pygame Programs
 Simpson College Computer Science
 http://programarcadegames.com/
 http://simpson.edu/computer-science/

"""

import pygame
from model import LSTM
import torch
import argparse
import time
import math

parser = argparse.ArgumentParser()
parser.add_argument("playerid")
args = parser.parse_args()

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

UP = 273
DOWN = 274
RIGHT = 275
LEFT = 276


reset_hidden = 0


pygame.init()

# Set the width and height of the screen [width, height]
size = (470, 498)
screen = pygame.display.set_mode(size)
prev_x_loc,prev_y_loc = 30,25
x_loc,y_loc = 30,25
prev_piq_x_loc, prev_piq_y_loc = 20,25
piq_x_loc, piq_y_loc = 20,25
prev_time = time.time()


pygame.display.set_caption("NBA MAdness")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # --- Game logic
    class Background(pygame.sprite.Sprite):
        def __init__(self, image_file, location):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load(image_file)
            self.rect = self.image.get_rect()
            self.rect.left, self.rect.top = location

    BackGround = Background('halfcourt.png', [0, 0])


    def timeSince(since):
        now = time.time()
        s = now - since
        return s

    def velocity(x1,y1,x2,y2,time):
        v = 1000 * math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)/40
        return v

    def distanceFromHoop(x,y):
        return math.sqrt((x - 5) ** 2 + (y - 25) ** 2)

    def createInput():
        input = torch.ones(12,)
        input[0], input[1] = piq_x_loc,piq_y_loc
        input[2] = velocity(piq_x_loc,piq_y_loc,prev_piq_x_loc,prev_piq_y_loc,timeSince(prev_time))
        input[3], input[4] = (piq_x_loc - prev_piq_x_loc), -1*(piq_y_loc - prev_piq_y_loc)
        input[5] = distanceFromHoop(piq_x_loc,piq_y_loc)
        input[6], input[7] = x_loc, y_loc
        input[8] = velocity(x_loc,y_loc,prev_x_loc,prev_y_loc,timeSince(prev_time))
        input[9], input[10] = (x_loc - prev_x_loc), -1*(y_loc - prev_y_loc)
        input[11] = distanceFromHoop(x_loc,y_loc)
        input.unsqueeze_(0)
        return input


    rnn = LSTM(12, 300, 2)
    rnn.load_state_dict(torch.load('./data/' + args.playerid  + "test"+'.model'))



    # --- Screen-clearing code
    screen.fill(WHITE)
    screen.blit(BackGround.image, BackGround.rect)

    # --- Drawing code
    pressed = pygame.key.get_pressed()
    inc = [(0,0.25),(0,-0.25),(0.4,0),(-0.4,0)]
    # update x,y coordinates based on keys pressed
    for i in range(273, 277):
        if pressed[i] == 1:
            prev_x_loc = x_loc
            prev_y_loc = y_loc
            x_loc += inc[i-273][0]
            y_loc += inc[i-273][1]
            prev_time = time.time()

    #if reset_hidden % 100 == 0:
    if reset_hidden == 0:
        hidden = rnn.initHidden()
    input = createInput()
    output, hidden = rnn(input, hidden)


    prev_piq_x_loc, prev_piq_y_loc = piq_x_loc, piq_y_loc
    piq_x_loc, piq_y_loc = float(output[0,0]), float(output[0,1])

    # gameboard dim: 470 x 498

    game_x_loc = int((470/47) * x_loc)
    game_y_loc = int(498 - ((498/50) * y_loc))
    game_piq_x_loc = int((470/47) * piq_x_loc)
    game_piq_y_loc = int(498 - ((498/50) * piq_y_loc))

    pygame.draw.circle(screen, BLACK, (game_x_loc, game_y_loc), 8)
    pygame.draw.circle(screen, GREEN, (game_piq_x_loc, game_piq_y_loc), 8)


    reset_hidden += 1

    # --- Update the screen with what we've drawn.
    pygame.display.flip()

    # --- Limit to 60 frames per second
    clock.tick(30)

# Close the window and quit.
pygame.quit()