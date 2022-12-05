# Load libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.svm import SVC

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold

from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

from pandas import read_csv
from pandas.plotting import scatter_matrix

from sklearn.neural_network import MLPClassifier
import joblib

import lime, lime.lime_tabular

def get_data():
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/car/car.data"
    names = ['buying', 'maint', 'doors', 'persons', 'lug_boot', 'safety', 'class']
    df = pd.read_csv(url, names=names)
    df = df.drop('persons',axis=1)

    for col in df:
        if col != 'class':
            labels[col] = { ni: n for n,ni in enumerate(set(df[col]),1) }
            df[col] = df[col].map(labels[col])
        else:
            df[col] = df[col].map({'good': 1, 'unacc': 2, 'acc': 3, 'vgood': 4})

    # Skew before
    print(f"Skewness before: \n{df.skew()}\n")
    return df

labels = {}
df = get_data()

df["class"] = df["class"].map({1: -2.8678881, 2: -0.36623292 , 3: 1.25076241, 4: 2.47282076})

# Skew after
print(f"Skewness after: \n{df.skew()}\n")

features = ['maint', 'doors', 'lug_boot', 'safety', 'class']
x_features = df[features]
y_labels = df['buying']

x_train, x_test, y_train, y_test = train_test_split(x_features, y_labels, random_state = 42)
nb = GaussianNB()
nb.fit(x_train,y_train)
print("score: ", accuracy_score(y_test, nb.predict(x_test)))

# prediction df with the parameters we want to predict
predict_df = pd.DataFrame(columns=features)
predict_df.loc[0] = [ labels['maint']['high'], labels['doors']['4'], labels['lug_boot']['big'], labels['safety']['high'], -2.8678881 ]

explainer = lime.lime_tabular.LimeTabularExplainer(x_train.values, feature_names=features, class_names=labels['buying'], discretize_continuous=True)
exp = explainer.explain_instance(predict_df.iloc[0], nb.predict_proba, num_features=6, top_labels=1)
exp.save_to_file('exp.html')


