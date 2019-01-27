# NBA Defensive AI

An attempt to train an AI on actual NBA game data so that it can play defense against a human user. I took SportVU tracking data for NBA games from the 2015-16 season, made a rule based algorithm that finds when an inputted player is in defensive situations, then trained an LSTM neural network on each situation.

### Prerequisites

```
pip install -r requirements.txt
```

### To create features for a specific player

Open /Features/createfeatures.py and add the filepath of where you saved the repo where it is specified in the file

```
python Features/createfeatures.py [Player_Name] [Teamid (BOS, WAS, etc.)]

```
new csv will be saved as data/csvs/Player_Name.csv

### To train LSTM on new features

```
python main.py [Player_Name] ['train'] ['speed' (optional, increases speed of training by skipping lines of csv)] 
```

### To visualize accuracy of trained AI

```
python main.py [Player_Name]
```
an animation plotting an actual defensive event will pop up. AI is in red, offensive ball handler is in black, and real life defensive player is in gold

For example:

![Alt Text](https://raw.githubusercontent.com/mogryzko/NBA-Defensive-AI/master/gif1.gif)

![Alt Text](https://raw.githubusercontent.com/mogryzko/NBA-Defensive-AI/master/gif2.gif)

### To play against AI

```
python game.py [Player_Name]
```

use arrow keys to play!
