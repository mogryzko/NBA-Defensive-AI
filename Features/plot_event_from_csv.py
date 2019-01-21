import pandas as pd
import numpy as np

import matplotlib.animation as anim
import matplotlib.pyplot as plt
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument("playerid")
args = parser.parse_args()




bh_xy = []
piq_xy = []

df = pd.read_csv('../data/csv/' + args.playerid + '.csv')
df_list = np.split(df, df[df.isnull().all(1)].index)[:-1] # split into moments through splitting by empty rows
for df in df_list:
    df.drop(df.index[0], inplace=True)  # drop empty rows
    input_numpy = df.values[:,:-2]
    bh_xy.append((input_numpy[:,6],input_numpy[:,7]))
    piq_xy.append((input_numpy[:,0],input_numpy[:,1]))




assert(len(bh_xy) == len(piq_xy))


def randomTrainingExample():
    rand = random.randint(0, len(bh_xy) - 1)
    return bh_xy[rand], piq_xy[rand]


court = plt.imread('../halfcourt.png')
fig = plt.figure(figsize=(15, 11.5))
ax = plt.axes(xlim=(-10, 60), ylim=(-10, 60))
line = ax.scatter([], [], s=50)
colors = []

ex_bh_xy, ex_piq_xy = randomTrainingExample()


player_coords = [ex_bh_xy, ex_piq_xy]
num_frames = len(ex_bh_xy[0])




def init():
    line.set_offsets([])
    return line,


def animate(i):
    colors = []
    x_positions = []
    y_positions = []
    count = 0
    for player_coord in player_coords:
        x = player_coord[0][i]
        y = player_coord[1][i]
        x_positions.append(x)
        y_positions.append(y)
        if count == 0:
            colors.append('black')
        elif count == 1:
            colors.append('gold')
        count += 1
    x_positions = np.asarray(x_positions)
    y_positions = np.asarray(y_positions)
    positions = np.vstack((x_positions, y_positions)).T
    line.set_offsets(positions)
    line.set_color(c=colors)
    return line,


animation = anim.FuncAnimation(fig, animate, init_func=init, frames=num_frames, interval=10, blit=True)

plt.imshow(court, zorder=0, extent=[0, 47, 50, 0])
plt.show()








