import torch
import torch.optim as optim
import torch.nn as nn
import matplotlib.pyplot as plt
from dotabet.nn.vizual import plot_loss_curve
import dotabet

def l1_penalty(model, l1_lambda):
    l1_norm = sum(p.abs().sum() for p in model.parameters())
    return l1_lambda * l1_norm

def train_model(model, train_loader, val_loader, optimizer, num_epochs, scheduler=None, l1_lambda=None):
    criterion = nn.BCELoss()
    train_losses = []
    val_losses = []
    val_acc = []
    
    
    plt.ion()  # Turn on interactive mode for live updates
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for inputs, targets in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs.squeeze(), targets)
            if l1_lambda:
                loss += l1_penalty(model, l1_lambda)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        
        if scheduler:
            if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                scheduler.step(running_loss / len(train_loader))
            else:
                scheduler.step()
        
        val_loss = 0.0
        model.eval()
        with torch.no_grad():
            for inputs, targets in val_loader:
                outputs = model(inputs)
                loss = criterion(outputs.squeeze(), targets)
                val_loss += loss.item()
        
        train_losses.append(running_loss / len(train_loader))
        val_losses.append(val_loss / len(val_loader))
        val_acc.append(dotabet.nn.test.evaluate_model(model, val_loader))
        
        if (epoch + 1) % 5 == 0 or epoch == num_epochs - 1:
            plot_loss_curve(train_losses, val_losses, val_acc, epoch + 1)
    
    plt.ioff()  # Turn off interactive mode
    print(f"Train Loss: {train_losses[-1]}. Val Loss: {val_losses[-1]}, Val Accuracy: {val_accs[-1]}")
    dotabet.nn.utils.save_model(neural_network, dotabet.nn.config.neural_network_path)
    return train_losses, val_losses, val_acc

