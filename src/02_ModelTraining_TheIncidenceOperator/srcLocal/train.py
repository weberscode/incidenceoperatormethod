# %% Import libraries
import time
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
import optuna
from optuna.samplers import TPESampler

# %% Define functions and classes
def objective_dtree(trial, X_train, X_val, X_test, y_train, y_val, y_test):
    # suggest hyperparameters
    #criterion = trial.suggest_categorical('criterion', ['squared_error', 'friedman_mse', 'absolute_error', 'poisson'])
    criterion = 'squared_error'
    #splitter = trial.suggest_categorical('splitter', ['best', 'random'])
    splitter = 'best'
    #max_depth = trial.suggest_int('max_depth', 1, 40)
    max_depth = trial.suggest_int('max_depth', 1, 40)
    #min_samples_split = trial.suggest_int('min_samples_split', 2, 5)
    min_samples_split = 2
    #min_samples_leaf = trial.suggest_int('min_samples_leaf', 1, 5)
    min_samples_leaf = 1
    # create model
    model, training_time_min = train_model_dtree(X_train, y_train, criterion, splitter, max_depth, min_samples_split, min_samples_leaf)

    # evaluate normalized mean absolute error
    nMAE_val = nMAE(y_val, model.predict(X_val))
    nMAE_test = nMAE(y_test, model.predict(X_test))

    # add additional info to trial
    trial.set_user_attr('nMAE_test', nMAE_test)
    trial.set_user_attr('training_time_min', training_time_min)

    return nMAE_val

def train_model_dtree(X_train, y_train, criterion, splitter, max_depth, min_samples_split, min_samples_leaf):
    # create modelpipeline
    model = make_pipeline(
        StandardScaler(),
        DecisionTreeRegressor(
            criterion = criterion,
            splitter = splitter,
            max_depth = max_depth,
            min_samples_split = min_samples_split,
            min_samples_leaf = min_samples_leaf,
            random_state = 42
        )
    )

    # train model
    time0 = time.time()
    model.fit(X_train, y_train)
    time1 = time.time()
    training_time_min = (time1 - time0) / 60

    return model, training_time_min

def nMAE(true,pred):
    return np.mean(np.abs(true - pred)) / np.mean(true) * 100

def hyperparameter_optimization(X_train, X_val, X_test, y_train, y_val, y_test):
    n_startup_trials = 20
    n_trials=50
    # do study
    study = optuna.create_study(direction="minimize", sampler=TPESampler(n_startup_trials=n_startup_trials))
    study.optimize(lambda trial: objective_dtree(trial, X_train, X_val, X_test, y_train, y_val, y_test), n_trials=n_trials)

    # print best trial
    print("Best trial:")
    trial = study.best_trial
    print(f"  Value: {trial.value}")
    print("  Params: ")
    for key, value in trial.params.items():
        print(f"    {key}: {value}")
    print("  User attrs: ")
    for key, value in trial.user_attrs.items():
        print(f"    {key}: {value}")
