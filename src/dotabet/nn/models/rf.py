# rf.py
import dotabet
from sklearn.ensemble import RandomForestClassifier
import torch
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
import joblib

def get_random_forest_model(n_estimators, max_depth, random_state,min_samples_leaf,min_samples_split):
    rfc = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        min_samples_leaf=min_samples_leaf,
        min_samples_split=min_samples_split,
    )
    return rfc

def train_random_forest(rfc, train_loader):
    train_features, train_labels = [], []
    for data, labels in train_loader:
        train_features.append(data)
        train_labels.append(labels)
    train_features = torch.cat(train_features).numpy()
    train_labels = torch.cat(train_labels).numpy()
    rfc.fit(train_features, train_labels)
    save_model(rfc, dotabet.nn.config.rf_path)

def evaluate_random_forest(rfc, test_loader):
    test_features, test_labels = [], []
    for data, labels in test_loader:
        test_features.append(data)
        test_labels.append(labels)
    test_features = torch.cat(test_features).numpy()
    test_labels = torch.cat(test_labels).numpy()
    predictions = rfc.predict(test_features)
    accuracy = accuracy_score(test_labels, predictions)
    print(f'Random Forest Model Test Accuracy: {accuracy:.4f}')
    return accuracy

def save_model(rfc, file_path):
    print(f"Random Forest saved to {file_path}")
    joblib.dump(rfc, file_path)

def load_model(file_path):
    print(f"Random Forest loaded from {file_path}")
    return joblib.load(file_path)

def grid_search_rfc(param_grid, train_loader):
    train_features, train_labels = [], []
    for data, labels in train_loader:
        train_features.append(data)
        train_labels.append(labels)
    train_features = torch.cat(train_features).numpy()
    train_labels = torch.cat(train_labels).numpy()

    rfc = RandomForestClassifier()
    grid_search = GridSearchCV(estimator=rfc, param_grid=param_grid, cv=3, n_jobs=-1, scoring='accuracy')
    grid_search.fit(train_features, train_labels)

    return grid_search.best_estimator_, grid_search.best_params_, grid_search.best_score_
