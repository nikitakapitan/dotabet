# plot.py
import matplotlib.pyplot as plt
from IPython.display import clear_output, display

def plot_loss_curve(train_losses, val_losses, val_acc, current_epoch):
    clear_output(wait=True)
    plt.figure(figsize=(10, 5))
    plt.plot(range(1, current_epoch + 1), train_losses, label='Training Loss')
    plt.plot(range(1, current_epoch + 1), val_losses, label='Validation Loss')
    plt.plot(range(1, current_epoch + 1), val_acc, label='Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss Curve')
    plt.legend()
    plt.grid(True)
    display(plt.gcf())  # Display the current figure
    plt.close()  # Close the plot to prevent it from showing up multiple times