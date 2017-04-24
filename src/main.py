import pandas as pd
import numpy as np
import sklearn
from sklearn import preprocessing, cross_validation, svm, neighbors
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
import data as d

teamsDF = pd.read_csv('../data/Team.csv')

matchesTeamsDF = pd.read_csv("../data/gen/match_team.csv")
data = matchesTeamsDF.drop(['Match_Id'],1)
data = data.drop(['Unnamed: 0'],1)
X = data.drop(['Match_Won'],1)
Y = data['Match_Won']

X = preprocessing.scale(X)

X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, Y, test_size = 0.25)

def predict():
    print("Enter Team A Id")
    teamId = input()
    while(len(teamsDF[teamsDF["Team_Id"] == int(teamId)]) == 0):
        print("Please Enter valid Team Id")
        teamId = input()
    print("Enter Team B Id")
    opponentId = input()
    while(len(teamsDF[teamsDF["Team_Id"] == int(opponentId)]) == 0):
        print("Please Enter valid Team Id")
        opponentId = input()
    print("Which team won the toss?Enter Id")
    tossWon = input()
    while((tossWon != teamId) & (tossWon != opponentId)):
        print("Please Enter valid Team Id. %s or %s" % (teamId,opponentId))
        tossWon = input()
    print("Which team bat first?Enter Id")
    batFirst = input()
    while((batFirst != teamId) & (batFirst != opponentId)):
        print("Please Enter valid Team Id. %s or %s" % (teamId,opponentId))
        batFirst = input()
    px = d.generatePredictData(int(teamId),int(opponentId),int(tossWon),int(batFirst))
    px = px.drop(['Match_Id'],1)
    px = px.drop(['Match_Won'],1)

    px = preprocessing.scale(px)

    lin_svm = svm.LinearSVC()
    lin_svm.fit(X_train, y_train)
    pred = lin_svm.predict(px)
    if(pred[0] == 1):
        print("Team A Wins")
    else:
        print("Team B Wins")



def fitModels():

    print("Linear SVM")
    lin_svm = svm.LinearSVC()
    lin_svm.fit(X_train, y_train)
    accu = lin_svm.score(X_test,y_test)
    print(accu)

    print("SVC SVM")
    svc_svm = svm.SVC()
    svc_svm.fit(X_train, y_train)
    accu = svc_svm.score(X_test,y_test)
    print(accu)

    print("Naive Bayes")
    gnb = GaussianNB()
    gnb.fit(X_train, y_train)
    accu = gnb.score(X_test,y_test)
    print(accu)

    print("Random Forest")
    rf = RandomForestClassifier()
    rf.fit(X_train, y_train)
    accu = rf.score(X_test,y_test)
    print(accu)

#fitModels()
predict()
