''' cnv_eval - Model evaluation tools for Conversa '''

import numpy as np
import pandas as pd
from copy import copy, deepcopy
from sklearn.model_selection import StratifiedKFold

__author__ = 'Shayaan Syed Ali'
# __copyright__ = ''
__credits__ = ['Shayaan Syed Ali']
__maintainer__ = 'Shayaan Syed Ali'
__email__ = 'shayaan.syed.ali@gmail.com'
__status__ = 'Development'
# __license__ = ''
# __version__ = ''

# TODO: Add functions to write to file
# TODO: In doc add function guide/map
# TODO: Add vprint and verbose flags

# Constants

# Header strings
_PID_H_STR = 'pid'
_CAM_H_STR = 'cam'
_BEHAV_H_STR = 'behaviour'
_MODEL_H_STR = 'model'
_FOLD_H_STR = 'fold_no'
_ACCURACY_H_STR = 'accuracy'

HEADER_STRINGS = [  # TODO: Convert to dict and use as such in code
    _PID_H_STR,
    _CAM_H_STR,
    _BEHAV_H_STR,
    _MODEL_H_STR,
    _FOLD_H_STR,
    _ACCURACY_H_STR,
]


# Only works when elements in prediction and actual are in range [0, 1]
# TODO: Make more general - parameterize range?
def accuracy(predicted, true):
    '''
    Determines the accuracy of a predicted value against an actual value
    Requires that the predicted and true values are numpy arrays (or of classes that work with numpy functions) and that
    they are of the same shape
    :param predicted: The predicted value(s) as a numpy array, same shape as true
    :param true: The actual value(s) as a numpy array, same shape as predicted
    :return: The accuracy of the prediction against the true value, specifically the 
    '''
    if not predicted.shape == true.shape:
        raise RuntimeError('Prediction shape is ' + str(predicted.shape) + ' while true has shape ' + str(true.shape))
    abs_err = np.absolute(np.round(predicted.values) - true.values)
    return 1 - np.mean(abs_err)


# TODO: Doc and implement in eval_models
def evaluate(model, predictors, labels, eval_func=accuracy):
    predicted_labels = model.predict(predictors)
    return eval_func(predicted_labels, labels)


# In each epoch of training, all data is used
# The batch size specifies how many data points are given to the model at once
# E.g. with 135 data points, n_epochs = 10, and batch_sz = 20, you get 7 batches per epoch where 6 of the batches are of
# size 20 and one is of size 15 (so every data point is used once). The model trains on this data 10 times (10 epochs)
# and each time it divides the data into 7 batches

def eval_models(models, predictors, labels, n_folds=5, return_data_frame=True, verbose=0):  # TODO: Implement verbose
    '''
    Evaluates nn_models given predictor and label data to train and test the nn_models on
    :param models: The nn_models to evaluate
    :param predictors: Predictors to test the nn_models on
    :param labels: Labels to test the nn_models on
    :param n_folds: The number of folds to test the data on, defaults to 5
    :param return_data_frame: Whether to return the evaluation data in a pandas DataFrame or a Python dict
    :param verbose: The verbosity level of model training and testing - note that model console output often conflicts
    with outputs from cnv_eval - defaults to 0 (not verbose)
    :return: A pandas DataFrame with columns fold_no, model_no, and accuracy or a dict if return_data_frame=False
    '''

    # folds = k_folds(predictors, labels, n_folds)

    # Set up eval_results as dict and convert to pd dataframe if return_data_frame is True
    # It is significantly faster (and more straightforward) to work this way
    eval_results = dict([
        (_FOLD_H_STR, []),
        (_MODEL_H_STR, []),
        (_ACCURACY_H_STR, [])
    ])

    for model_no in range(0, len(models)):

        # Select model
        model = models[model_no]
        print('Model: ' + str(model_no+1) + '/' + str(len(models)) + ', ' + str(model))
        # model = deepcopy(nn_models[model_no])  # Resets model on each fold
        # TODO: Determine applicable behaviour or parameterize

        k_fold = StratifiedKFold(n_splits=n_folds)

        fold_no = 0

        for train_index, test_index in k_fold.split(
                np.ravel(np.zeros(
                    (predictors.shape[0], 1)
                )),
                np.ravel(np.zeros(
                    (labels.shape[0], 1)
                ))):

            # Select fold
            print('\tFold: ' + str(fold_no+1) + '/' + str(n_folds))

            print('Train index: ' + str(train_index))
            print('Test index: ' + str(test_index))

            # Unpack data from fold
            train_predictors = predictors.iloc[train_index]
            train_labels = labels.iloc[train_index]
            test_predictors = predictors.iloc[test_index]
            test_labels = labels.iloc[test_index]

            # Train
            print('\t\tTraining')
            # print(train_predictors)
            model.learn(train_predictors, train_labels)

            # Test
            print('\t\tEvaluating')
            acc = accuracy(predicted=model.predict(test_predictors), true=test_labels)
            print('\t\t\tAccuracy: ' + str(acc))

            # Set accuracy
            eval_results[_MODEL_H_STR].append(model_no + 1)
            eval_results[_FOLD_H_STR].append(fold_no + 1)
            eval_results[_ACCURACY_H_STR].append(acc)

            fold_no = fold_no + 1

    # Return applicable DataFrame or dict
    # TODO: Test
    # return eval_results if return_data_frame else pd.DataFrame(eval_results).sort_values(_MODEL_H_STR)
    return eval_results if return_data_frame else order_fields(pd.DataFrame(eval_results).sort_values(_MODEL_H_STR), [_MODEL_H_STR])


# TODO: Test
def order_fields(df, priority_fields):
    '''
    Re-orders the columns of a pandas DataFrame according to column_names
    Refactored from https://stackoverflow.com/a/25023460/7195043
    :param df: The DataFrame whose columns are to be reordered
    :param priority_fields: The fields to bring to the left in order, does not need to include all columns - others will
    be added at the back
    :return: The DataFrame with reordered columns
    '''
    remaining_fields = [col for col in df.columns if col not in priority_fields]
    df = df[priority_fields + remaining_fields]
    return df

# # TODO: Implement
# def k_folds(predictors, labels, n_folds):
#     '''
#     Splits predictors and labels into a number of testing groups
#     :param predictors: All of the predictors data to be split
#     :param labels: All of the label data to be split
#     :param n_folds: The number of folds to split the data into
#     :return: Each fold is a nested tuple, of (train_data, test_data) where
#     train_data = (train_predictors, train_labels) and test_data = (test_predictors, test_labels)
#     '''
#
#     pass
#
#     folds = list()
#     for i in range(0, n_folds):
#
#         # Test data
#         test_predictors = None
#         test_labels = None
#         test_data = (test_predictors, test_labels)
#
#         # Train data
#         train_predictors = None
#         train_labels = None
#         train_data = (train_predictors, train_labels)
#
#         folds.append((train_data, test_data))
#
#     return folds


# Subjects are tuples of (pid, cam), where pid and cam are numbers, like (2024, 2)
# Set behavs to None for all behavs being trained on, otherwise provide iterable of strings
# TODO: Documentation
def eval_models_on_subjects(models, subjects, behaviours=None, timesteps=30, n_folds=5, verbose=0):

    eval_results = dict([
        (_PID_H_STR, []),
        (_CAM_H_STR, []),
        (_BEHAV_H_STR, []),
        (_MODEL_H_STR, []),
        (_FOLD_H_STR, []),
        (_ACCURACY_H_STR, []),
    ])

    try:
        from cnv_data import load_subject, add_dim, to_subseqs
    except ImportError:
        print('Unable to import cnv_data functions')

    for (pid, cam) in subjects:
        print('Subject: pid' + str(pid) + 'cam' + str(cam))
        (predicts, labels) = load_subject(pid, cam)

        # Set behavs if not provided
        if behaviours is None:
            behaviours = labels.columns.tolist()

        for behav_name in behaviours:

            print('Behaviour: ' + str(behav_name))

            # TODO: Determine best behaviour and ask about preferred implementation
            # models_copy = copy(models)  # These nn_models specialize for each subject and behaviour

            behav_labels = pd.DataFrame(labels[behav_name], columns=[behav_name])  # DataFrame of single behaviour
            sub_eval_results = eval_models(models, predicts, behav_labels, return_data_frame=False, n_folds=n_folds, verbose=verbose)

            # Add results to over evaluation results
            n_rows = len(sub_eval_results[_ACCURACY_H_STR])
            eval_results[_PID_H_STR].extend([pid] * n_rows)
            eval_results[_CAM_H_STR].extend([cam] * n_rows)
            eval_results[_BEHAV_H_STR].extend([behav_name] * n_rows)
            eval_results[_MODEL_H_STR].extend(sub_eval_results[_MODEL_H_STR])
            eval_results[_FOLD_H_STR].extend(sub_eval_results[_FOLD_H_STR])
            eval_results[_ACCURACY_H_STR].extend(sub_eval_results[_ACCURACY_H_STR])

    # print(eval_results)

    eval_df = order_fields(pd.DataFrame(eval_results), [_PID_H_STR, _CAM_H_STR, _BEHAV_H_STR, _MODEL_H_STR, _FOLD_H_STR, _ACCURACY_H_STR])
    eval_df.sort_values([_MODEL_H_STR, _BEHAV_H_STR])

    print('Models evaluated on subjects')
    return eval_df


def summary(eval_results, drop_fields=_FOLD_H_STR):
    '''
    Returns a summarized version of model evaluations which averages the accuracy of models across folds
    :param eval_results: The DataFrame to summarize
    :return: A summary DataFrame
    '''
    # Future TODO: Include and implement optional param for field to average over
    # Future TODO - Add compatibility with eval_models dfs where pid and cam columns do not exist
    summary_df = eval_results.drop(_FOLD_H_STR, 1)  # Drop fold string
    summary_df = (summary_df.groupby([_PID_H_STR, _CAM_H_STR, _BEHAV_H_STR, _MODEL_H_STR]).mean())
    return summary_df


print('Imported cnv_eval')
