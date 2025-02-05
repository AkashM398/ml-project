#! /usr/bin/python2
import pandas as pd #used for DATAFrames and DataFrames can hold different types data of multidimensional arrays. 
import numpy as np#Numpy provides robust data structures for efficient computation of multi-dimensional arrays & matrices.
import _pickle as cPickle
import sklearn.ensemble as ske
from sklearn import linear_model
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectFromModel
from sklearn.externals import joblib
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix

data = pd.read_csv('data.csv', sep='|') #generate df as data
X = data.drop(['Name', 'md5', 'legitimate'], axis=1).values #now droping some coloumns as axis 1(mean coloumn) and will show the values in the rows
y = data['legitimate'].values #values of legitimate data

print('Researching important feature based on %i total features\n' % X.shape[1])# shape() is use in pandas to give number of row/column

# Feature selection using Trees Classifier
fsel = ske.ExtraTreesClassifier().fit(X, y)
model = SelectFromModel(fsel, prefit=True)
X_new = model.transform(X)#now features are only 9 :)
nb_features = X_new.shape[1]#will save value 13 as shape is (138047, 13) :}



X_train, X_test, y_train, y_test = train_test_split(X_new, y ,test_size=0.2)#now converting in training and testing data in 20% range hahhahaha ! as total x is 138047 and testing is 138047*0.2=27610 :)
features = []

print('%i features identified as important:' % nb_features) #as mentioned above


#important features sored
indices = np.argsort(fsel.feature_importances_)[::-1][:nb_features]
for f in range(nb_features):
    print("%d. feature %s (%f)" % (f + 1, data.columns[2+indices[f]], fsel.feature_importances_[indices[f]]))

# mean adding to the empty 'features' array the 'important features'
for f in sorted(np.argsort(fsel.feature_importances_)[::-1][:nb_features]):#[::-1] mean start with last towards first 
    features.append(data.columns[2+f])

#Algorithm comparison
algorithms = {
        "DecisionTree": tree.DecisionTreeClassifier(max_depth=10),
        #The max_depth parameter denotes maximum depth of the tree.
    
        "RandomForest": ske.RandomForestClassifier(n_estimators=50),#In case, of random forest, these ensemble classifiers are            the randomly created decision trees. Each decision tree is a single classifier and the target prediction is based on            the majority voting method.
         #n_estimators ==The number of trees in the forest.
    
        "GradientBoosting": ske.GradientBoostingClassifier(n_estimators=50),
        "AdaBoost": ske.AdaBoostClassifier(n_estimators=100),
         #Ada mean Adaptive
         #Both are boosting algorithms which means that they convert a set of weak learners into a single strong learner. They            both initialize a strong learner (usually a decision tree) and iteratively create a weak learner that is added to the            strong learner. They differ on how they create the weak learners during the iterative process.
    
        "GNB": GaussianNB()
        #Bayes theorem is based on conditional probability. The conditional probability helps us calculating the probability             that something will happen
    }

results = {}
print("\nNow testing algorithms")
for algo in algorithms:
    clf = algorithms[algo]
    clf.fit(X_train, y_train)#fit may be called as 'trained'
    score = clf.score(X_test, y_test)
    print("%s : %f %%" % (algo, score*100))
    results[algo] = score

winner = max(results, key=results.get)
print('\nWinner algorithm is %s with a %f %% success' % (winner, results[winner]*100))

# Save the algorithm and the feature list for later predictions
print('Saving algorithm and feature list in classifier directory...')
joblib.dump(algorithms[winner], 'classifier/classifier.pkl')#Persist an arbitrary Python object into one file.
open('classifier/features.pkl', 'wb').write(cPickle.dumps(features))
#joblib works especially well with NumPy arrays which are used by sklearn so depending on the classifier type you use you might have performance and size benefits using joblib.Otherwise pickle does work correctly so saving a trained classifier and loading it again will produce the same results no matter which of the serialization libraries you use
print('Saved')

# Identify false and true positive rates
clf = algorithms[winner]
res = clf.predict(X_test)
mt = confusion_matrix(y_test, res)
#A confusion matrix, also known as an error matrix,[4] is a specific table layout that allows visualization of the performance of an algorithm, typically a supervised learning.
print("False positive rate : %f %%" % ((mt[0][1] / float(sum(mt[0])))*100))
print('False negative rate : %f %%' % ( (mt[1][0] / float(sum(mt[1]))*100)))
