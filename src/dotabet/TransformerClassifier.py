
import torch.nn as nn
import torch

class TransformerClassifier(nn.Module):
    def __init__(self, vocab_size, embedding_dim, num_heads, num_layers, d_ff):
        super(TransformerClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        encoder_layer = nn.TransformerEncoderLayer(d_model=embedding_dim, nhead=num_heads,dim_feedforward=d_ff)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(embedding_dim, 1)
    
    def forward(self, x):
        x = self.embedding(x)  # (batch_size, seq_len, embedding_dim)
        x = x.permute(1, 0, 2)  # (seq_len, batch_size, embedding_dim) for PyTorch Transformer
        x = self.transformer_encoder(x)
        x = x.mean(dim=0)  # Global average pooling over the sequence dimension
        x = self.fc(x)
        x = torch.sigmoid(x)
        return x.squeeze()