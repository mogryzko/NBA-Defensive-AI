import argparse
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import random
from model import LSTM
import time, math
import matplotlib.pyplot as plt
import matplotlib.animation as anim


parser = argparse.ArgumentParser()
parser.add_argument("player_w_underscore")
parser.add_argument("speed", nargs='?')
parser.add_argument('train', nargs='?')
args = parser.parse_args()
init_speed = False
init_train = False
if args.speed: init_speed = True
if args.train: init_train = True


########################

# Load data

#######################

input_tensors = []
gold_values = []



dfs = []

hardcoded_ids = [args.player_w_underscore]
for id in hardcoded_ids:
    df1 = pd.read_csv('data/csv/' + id + '.csv')
    dfs.append(df1)



for df in dfs:
    df_list = np.split(df, df[df.isnull().all(1)].index)[:-1] # split into moments through splitting by empty rows
    if init_speed:
        for df in df_list:
            df.drop(df.index[0], inplace=True)  # drop first row, which will be empty
            df = df[df.index % 3 == 0]
            input_numpy = df.values[:,:-2]
            gold_numpy = df.values[1:, :2]
            input_numpy = input_numpy[:-1, :]

            temp1, temp2 = np.zeros_like(input_numpy), np.zeros_like(gold_numpy)
            temp1[:], temp2[:] = input_numpy, gold_numpy
            input_numpy, gold_numpy = temp1, temp2

            input_numpy.resize(input_numpy.shape[0],1,input_numpy.shape[1])
            gold_numpy.resize(gold_numpy.shape[0],1,gold_numpy.shape[1])

            input_tensor = torch.from_numpy(input_numpy).float()
            gold_value = torch.from_numpy(gold_numpy).float()

            input_tensors.append(input_tensor)
            gold_values.append(gold_value)
    else:
        for df in df_list:
            df.drop(df.index[0], inplace=True)  # drop first row, which will be empty
            input_numpy = df.values[:, :-2]
            input_numpy.resize(input_numpy.shape[0], 1, input_numpy.shape[1])
            gold_numpy = df.values[:, -2:]
            gold_numpy.resize(gold_numpy.shape[0], 1, gold_numpy.shape[1])

            input_tensor = torch.from_numpy(input_numpy).float()
            gold_value = torch.from_numpy(gold_numpy).float()

            input_tensors.append(input_tensor)
            gold_values.append(gold_value)




assert(len(input_tensors) == len(gold_values))


def randomTrainingExample():
    rand = random.randint(0, len(input_tensors) - 1)
    return input_tensors[rand], gold_values[rand]


########################

# Helper functions

#######################


def train(input_tensor, gold_value):
    hidden = rnn.initHidden()

    rnn.zero_grad()

    loss = 0

    for i in range(input_tensor.size(0)):
        output, hidden = rnn(input_tensor[i], hidden)
        l = criterion(output, gold_value[i])


        # testing additions to loss function: punish no movement, moving off screen
        piq_x_gold,piq_y_gold = float(gold_value[i][0,0]), float(gold_value[i][0,1])
        bh_x,bh_y = float(input_tensor[i][0,6]),float(input_tensor[i][0,7])

        if torch.all(torch.eq(input_tensor[i][0,:2],output[0])):
            # no movement
            l *= 10
        if 0 > float(output[0,0]) > 47 or 0 > float(output[0,1]) > 50:
            # moving off screen
            l*=1000
        '''
        if distanceFromHoop(float(output[0,0]),float(output[0,1])) > float(input_tensor[i][0,11]):
            # further from basket than ball handler
            l *= 10
        '''

        loss += l

    loss.backward()
    torch.nn.utils.clip_grad_norm(rnn.parameters(), 0.25)

    for p in rnn.parameters():
        p.data.add_(-learning_rate, p.grad.data)

    return output, loss.item() / input_tensor.size(0)


def timeSince(since):
    now = time.time()
    s = now - since
    m = math.floor(s / 60)
    s -= m * 60
    return '%dm %ds' % (m, s)


def velocity(x1,y1,x2,y2,time):
    v = 1000*distance(x1,x2,y1,y2)/time
    return v


def distance(x1,x2,y1,y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def distanceFromHoop(x,y):
    return math.sqrt((x - 5) ** 2 + (y - 25) ** 2)


def createInput(piq_x_loc, piq_y_loc, prev_piq_x_loc, prev_piq_y_loc, x_loc, y_loc, prev_x_loc, prev_y_loc):
    input = torch.ones(12,)
    input[0], input[1] = piq_x_loc,piq_y_loc
    input[2] = velocity(piq_x_loc,piq_y_loc,prev_piq_x_loc,prev_piq_y_loc,40)
    input[3], input[4] = (piq_x_loc - prev_piq_x_loc), (piq_y_loc - prev_piq_y_loc)
    input[5] = distanceFromHoop(piq_x_loc,piq_y_loc)
    input[6], input[7] = x_loc, y_loc
    input[8] = velocity(x_loc,y_loc,prev_x_loc,prev_y_loc,40)
    input[9], input[10] = (x_loc - prev_x_loc), (y_loc - prev_y_loc)
    input[11] = distanceFromHoop(x_loc,y_loc)
    input.unsqueeze_(0)
    return input


def predict(input_tensors, gold_values):
    with torch.no_grad():  # no need to track history when predicting
        input = input_tensors[0]
        hidden = rnn.initHidden()

        diff = 0

        prev_x_loc, prev_y_loc = input[0,6], input[0,7]
        x_loc, y_loc = input[0,6], input[0,7]
        prev_piq_x_loc, prev_piq_y_loc = input[0,0], input[0,1]
        piq_x_loc, piq_y_loc = input[0,0], input[0,1]

        # for animation:

        bh_xy = []
        piq_xy = []
        piq_gold = [(float(gold_values[i][0,0]),float(gold_values[i][0,1])) for i in range(len(input_tensors))]

        for i in range(len(input_tensors)):
            output, hidden = rnn(input, hidden)

            # for new input vector
            prev_x_loc, prev_y_loc = x_loc, y_loc
            prev_piq_x_loc, prev_piq_y_loc = piq_x_loc, piq_y_loc
            piq_x_loc, piq_y_loc = output[0,0], output[0,1]
            x_loc, y_loc = input_tensors[i][0,6], input_tensors[i][0,7]

            # for animation
            piq_xy.append((float(piq_x_loc),float(piq_y_loc)))
            bh_xy.append((float(x_loc),float(y_loc)))

            if i == len(input_tensors)-1:
                diff = output - gold_values[i]
                x_diff,y_diff = float(diff[0,0]), float(diff[0,1])
                diff = (math.fabs(x_diff) + math.fabs(y_diff))/2

            input = createInput(piq_x_loc, piq_y_loc, prev_piq_x_loc, prev_piq_y_loc, x_loc, y_loc, prev_x_loc, prev_y_loc)

        return diff, len(input_tensors), bh_xy, piq_xy, piq_gold

def init():
    line.set_offsets([])
    return line,

def animate(i, num_frames):
    colors = []
    x_positions = []
    y_positions = []
    count = 0
    for player_coord in player_coords:
        x = player_coord[i][0]
        y = player_coord[i][1]
        x_positions.append(x)
        y_positions.append(y)
        if count == 0:
            colors.append('black')
        elif count == 1:
            colors.append('red')
        elif count == 2:
            colors.append('gold')
        count += 1
    x_positions = np.asarray(x_positions)
    y_positions = np.asarray(y_positions)
    positions = np.vstack((x_positions, y_positions)).T
    line.set_offsets(positions)
    line.set_color(c=colors)
    if i == num_frames-1:
        plt.close()
    return line,


########################

# Train or evaluate

#######################


if init_train:

    rnn = LSTM(12, 300, 2)

    criterion = nn.MSELoss()

    learning_rate = 0.0005
    #learning_rate = 0.0001

    n_iters = 25000
    print_every = 5000
    plot_every = 100
    all_losses = []
    total_loss = 0 # Reset every plot_every iters

    start = time.time()

    plt.ion()
    ax = plt.gca()
    ax.set_xlim([0, 5])
    ax.set_ylim([0, 300])
    plt.title("Loss over time")
    plt.xlabel("(100x) Num Iterations")
    plt.ylabel("Loss")

    for iter in range(1, n_iters + 1):
        output, loss = train(*randomTrainingExample())
        total_loss += loss

        if iter % print_every == 0:
            print('%s (%d %d%%) %.4f' % (timeSince(start), iter, iter / n_iters * 100, loss))

        if iter % plot_every == 0:
            all_losses.append(total_loss / plot_every)
            print(total_loss / plot_every)
            total_loss = 0
            ax.set_xlim([0, len(all_losses) + 10])
            ax.plot(all_losses)
            plt.draw()
            plt.pause(0.0001)

    torch.save(rnn.state_dict(), './data/' + args.player_w_underscore + '.model')

else:

    rnn = LSTM(12, 300, 2)
    rnn.load_state_dict(torch.load('./data/' + args.player_w_underscore + '.model'))

    num_test_examples = 100


    for i in range(3):
        court = plt.imread('halfcourt.png')
        fig = plt.figure(figsize=(15, 11.5))
        ax = plt.axes(xlim=(-10, 60), ylim=(-10, 60))
        line = ax.scatter([], [], s=50)
        colors = []

        with torch.no_grad():
            ex_input, ex_gold = torch.tensor([0]),torch.tensor([0])
            while float(ex_input.size()[0]) < num_test_examples:
                ex_input, ex_gold = randomTrainingExample()
            diff, num_frames, bh_xy, piq_xy, piq_gold = predict(ex_input, ex_gold)

        assert(len(bh_xy) == len(piq_xy) == len(piq_gold))

        player_coords = [bh_xy,piq_xy,piq_gold]


        animation = anim.FuncAnimation(fig, animate, init_func=init, frames=num_frames, fargs=[num_frames], interval=50, repeat=False, blit=True)

        plt.imshow(court, zorder=0, extent=[0, 47, 50, 0])
        plt.show()



























