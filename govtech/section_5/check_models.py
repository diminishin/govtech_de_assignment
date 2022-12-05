import pyforest
import warnings
warnings.filterwarnings("ignore")
from sklearn import metrics
from sklearn.metrics import accuracy_score
import lazypredict
from lazypredict.Supervised import LazyClassifier
import pandas
from pandas import read_csv
from pandas.plotting import scatter_matrix
from matplotlib import pyplot
import seaborn as sns

from sklearn.preprocessing import PowerTransformer, QuantileTransformer
from sklearn.preprocessing import FunctionTransformer
from sklearn.compose import ColumnTransformer

def get_data():
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/car/car.data"
    names = ['buying', 'maint', 'doors', 'persons', 'lug_boot', 'safety', 'class']
    df = pd.read_csv(url, names=names)
    df = df.drop('persons',axis=1)

    labels = {}
    for col in df:
        if col != 'class':
            labels[col] = { ni: n for n,ni in enumerate(set(df[col]),1) }
            df[col] = df[col].map(labels[col])
        else:
            df[col] = df[col].map({'good': 1, 'unacc': 2, 'acc': 3, 'vgood': 4})

    # Skew before
    print(f"Skewness before: \n{df.skew()}\n")
    return df

df = get_data()

df["class"] = df["class"].map({1: -2.8678881, 2: -0.36623292 , 3: 1.25076241, 4: 2.47282076})

# Skew after
print(f"Skewness after: \n{df.skew()}\n")

features = ['maint', 'doors', 'lug_boot', 'safety', 'class']
x_features = df[features]
y_labels = df['buying']

x_train, x_test, y_train, y_test = train_test_split(x_features, y_labels, random_state = 42)

clf = LazyClassifier(verbose=0,ignore_warnings=True)

models, predictions = clf.fit(x_train, x_test, y_train, y_test)

print(models)


