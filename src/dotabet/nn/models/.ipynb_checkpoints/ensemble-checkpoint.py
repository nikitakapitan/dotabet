import torch
import torch.nn.functional as F

class ModelEnsemble(torch.nn.Module):
    def __init__(self, models):
        super(ModelEnsemble, self).__init__()
        self.models = models

    def forward(self, x):
        assert x.dim() !=1, f"ensemble.py: x.dim() == 1"
        predictions = [model(x) for model in self.models]
        # Average the predictions
        avg_prediction = torch.mean(torch.stack(predictions), dim=0)
        return avg_prediction

def create_ensemble(input_size, config):
    models = []
    for _ in range(config['num_models']):
        model = NeuralNetwork(
            input_size,
            use_batch_norm=config['use_batch_norm'],
            use_dropout=config['use_dropout'],
            dropout_prob=config['dropout_prob']
        )
        models.append(model)
    return ModelEnsemble(models)
