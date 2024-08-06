import torch
import torch.nn.functional as F
import dotabet

# sklearn
from sklearn.metrics import accuracy_score

# Neural Network
from dotabet.nn.utils import load_model as load_neural_network
from dotabet.nn.test import evaluate_model

# Random Forest
from sklearn.ensemble import RandomForestClassifier
from dotabet.nn.models.rf import evaluate_random_forest
from dotabet.nn.models.rf import load_model as load_random_forest
from dotabet.nn.config import rf_path

class ModelEnsemble(torch.nn.Module):
    def __init__(self):
        super(ModelEnsemble, self).__init__()
        
        rfc = load_random_forest(rf_path)
        neural_network = load_neural_network(dotabet.nn.config.neural_network_path)
        
        self.models = [neural_network, neural_network, neural_network, rfc]

    @torch.no_grad()
    def forward(self, x):
        assert x.dim() != 1, f"ensemble.py: x.dim() == 1. No BatchNorm dimension"
        predictions = []
        model_predictions = {}
        
        for i, model in enumerate(self.models, start=1):
            model_key = i
            if isinstance(model, torch.nn.Module):
                model.eval()
                with torch.no_grad():
                    output = model(x).squeeze()
                    predictions.append(output)
                    model_predictions[model_key] = output
            else:
                # Assume non-PyTorch models accept numpy arrays and return numpy arrays
                output = torch.tensor(model.predict(x.cpu().numpy())).float()
                predictions.append(output)
                model_predictions[model_key] = output
        
        avg_prediction = torch.mean(torch.stack(predictions), dim=0) 
        return avg_prediction, model_predictions

    @torch.no_grad()
    def evaluate_ensemble(self, test_loader, train_loader=None):

        correct = 0
        total = 0
        model_accuracies = {i: 0 for i in range(1, len(self.models) + 1)}

        test_features, test_labels = [], []
        for inputs, targets in test_loader:
            test_features.append(inputs)
            test_labels.append(targets)

        test_features = torch.cat(test_features)
        test_labels = torch.cat(test_labels)

        ensemble_output, model_predictions = self(test_features)
        predicted = (ensemble_output >= 0.5).float()
        total = test_labels.size(0)
        correct = (predicted == test_labels).sum().item()

        for model_key, prediction in model_predictions.items():
            if isinstance(self.models[model_key - 1], torch.nn.Module):
                individual_pred = (prediction >= 0.5).float()
                model_accuracies[model_key] = (individual_pred == test_labels).sum().item() / total
            elif isinstance(self.models[model_key - 1], RandomForestClassifier):
                individual_pred = (prediction >= 0.5).numpy()
                model_accuracies[model_key] = accuracy_score(test_labels.numpy(), individual_pred)
    
        ensemble_accuracy = correct / total
        print(f'Ensemble Model Test Accuracy: {ensemble_accuracy:.4f}')
        for k, v in model_accuracies.items():
            print(f'Model {k} Test Accuracy: {v:.4f}')
        
        return ensemble_accuracy, model_accuracies
