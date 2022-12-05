## Section 5: Machine Learning

#
As the distribution of 'class' is extremely skewed, I attempted to resolve the skewness of the 'class' column first. 
Run check_skew.py and below is the result. Box-cox transformation gives the best transformation.

Box-cox values = [unacc = -0.36623292  acc = 1.25076241 v-good = 2.47282076 good = -2.8678881 ]
#
Skewness was -0.98 before & is -1.6 after Log transformation.

Skewness was -0.98 before & is -0.1 after Square transformation.

Skewness was -0.98 before & is 0.86 after cube transformation.

Skewness was -0.98 before & is 0.03 after Box-cox transformation.

Skewness was -0.98 before & is 0.07 after Yeo-johnson transformation.


Next, I used lazypredict to attempt and find out which model give the best score for this dataset.
From the results below, seems like GaussianNB had the best result with 0.33 accuracy. Although its still a low score, it is the best I can do with for now.

 Accuracy  ...  Time Taken
 
Model                                    ...            
GaussianNB                         0.33  ...        0.00
QuadraticDiscriminantAnalysis      0.31  ...        0.00
AdaBoostClassifier                 0.29  ...        0.06
BernoulliNB                        0.29  ...        0.00
SGDClassifier                      0.27  ...        0.01
SVC                                0.27  ...        0.06
Perceptron                         0.27  ...        0.00
DummyClassifier                    0.23  ...        0.00
CalibratedClassifierCV             0.22  ...        0.23
NuSVC                              0.23  ...        0.19
LogisticRegression                 0.22  ...        0.01
RidgeClassifierCV                  0.22  ...        0.00
RidgeClassifier                    0.22  ...        0.00
LinearSVC                          0.22  ...        0.07
LinearDiscriminantAnalysis         0.22  ...        0.00
PassiveAggressiveClassifier        0.24  ...        0.01
NearestCentroid                    0.20  ...        0.01
KNeighborsClassifier               0.17  ...        0.01
BaggingClassifier                  0.17  ...        0.01
LGBMClassifier                     0.16  ...        0.09
LabelSpreading                     0.14  ...        0.05
LabelPropagation                   0.14  ...        0.04
RandomForestClassifier             0.12  ...        0.08
ExtraTreesClassifier               0.12  ...        0.07
DecisionTreeClassifier             0.12  ...        0.00
ExtraTreeClassifier                0.12  ...        0.00

Next, I run model.py to train GaussianNB model.
The results as follows:
Probability of buying with the requirement input parameters
low - 0.75
not low - 0.25
