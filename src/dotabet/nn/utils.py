import torch.optim.lr_scheduler as lr_scheduler

def get_scheduler(optimizer, scheduler_type, scheduler_params):
    if scheduler_type == 'StepLR':
        step_size = scheduler_params.get('step_size', 30)
        gamma = scheduler_params.get('gamma', 0.1)
        return lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=gamma)
    elif scheduler_type == 'ReduceLROnPlateau':
        mode = scheduler_params.get('mode', 'min')
        factor = scheduler_params.get('factor', 0.1)
        patience = scheduler_params.get('patience', 10)
        return lr_scheduler.ReduceLROnPlateau(optimizer, mode=mode, factor=factor, patience=patience)
    # Add more scheduler types as needed
    else:
        raise ValueError(f"Unknown scheduler type: {scheduler_type}")
