'''
Based on PyTorch's tutorial for a RNN:

https://pytorch.org/tutorials/intermediate/char_rnn_generation_tutorial.html

'''


import torch
import torch.nn as nn
import torch.nn.functional as F

class LSTM(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(LSTM, self).__init__()
        self.hidden_size = hidden_size

        self.i2h = nn.Linear(input_size + hidden_size, hidden_size)
        self.i2o = nn.Linear(input_size + hidden_size, output_size)
        self.o2o = nn.Linear(hidden_size + output_size, output_size)
        self.o3o = nn.Linear(hidden_size + output_size, output_size)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, input, hidden):
        input_combined = torch.cat((input, hidden), 1)
        hidden = self.i2h(input_combined)
        output = F.relu(self.i2o(input_combined))
        output_combined = torch.cat((hidden, output), 1)
        output = F.relu(self.o2o(output_combined))
        output_combined = torch.cat((hidden, output), 1)
        output = self.o3o(output_combined)

        # We add a softmax layer to the output, which converts the output to be between 0 and 1. Because we know
        # that the player in question (piq) will not move more than one foot in the xy plane within each 40 millisecond
        # frame, we multiply that softmax value by 2, subtract 1 from the piq's initial position, and then add the
        # softmax output to the original piq's position. The goal is to substantially reduce the range in which the
        # network has to learn
        '''
        output = 16.0 * self.softmax(output)
        to_output = input[0,:2] - torch.tensor([8.0,8.0])
        output = to_output + output
        '''

        return output, hidden

    def initHidden(self):
        return torch.zeros(1, self.hidden_size)