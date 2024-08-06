rf_path = r"D:\WORKSPACE\dotabet\data\weights\random_forest_model.joblib"
neural_network_path = r"D:\WORKSPACE\dotabet\data\weights\neural_network.pth"

data_config = {
    'batch_size' : 32,
}

neural_network_config = {
    'use_batch_norm': True,
    'use_dropout': True,
    'dropout_prob': 0.5,
    'use_scheduler': True,
    'scheduler_type': 'StepLR',
    'scheduler_params': {
        'step_size': 10,
        'gamma': 0.1
    },
    'learning_rate': 0.001,
    'num_epochs': 50,
    'batch_size': 32,
    'weight_decay': 0.01,  # L2 regularization parameter
    'l1_lambda' : None,
}

rfc_config = {
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42,
        'min_samples_leaf': 4,
        'min_samples_split': 5,
    }