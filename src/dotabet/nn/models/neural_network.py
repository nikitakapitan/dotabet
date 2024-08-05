import torch
import torch.nn as nn

class NeuralNetwork(nn.Module):
    def __init__(self, input_size, use_batch_norm=False, use_dropout=False, dropout_prob=0.5):
        super(NeuralNetwork, self).__init__()
        self.use_batch_norm = use_batch_norm
        self.use_dropout = use_dropout
        
        self.fc1 = nn.Linear(input_size, 128)
        self.bn1 = nn.BatchNorm1d(128) if use_batch_norm else nn.Identity()
        self.dropout1 = nn.Dropout(dropout_prob) if use_dropout else nn.Identity()
        
        self.fc2 = nn.Linear(128, 64)
        self.bn2 = nn.BatchNorm1d(64) if use_batch_norm else nn.Identity()
        self.dropout2 = nn.Dropout(dropout_prob) if use_dropout else nn.Identity()
        
        self.fc3 = nn.Linear(64, 32)
        self.bn3 = nn.BatchNorm1d(32) if use_batch_norm else nn.Identity()
        self.dropout3 = nn.Dropout(dropout_prob) if use_dropout else nn.Identity()
        
        self.fc4 = nn.Linear(32, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        x = torch.relu(self.bn1(self.fc1(x)))
        x = self.dropout1(x)
        x = torch.relu(self.bn2(self.fc2(x)))
        x = self.dropout2(x)
        x = torch.relu(self.bn3(self.fc3(x)))
        x = self.dropout3(x)
        x = self.fc4(x)
        x = self.sigmoid(x)
        return x
