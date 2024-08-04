config = {
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
    'data_file': 'your_file.csv'
}
