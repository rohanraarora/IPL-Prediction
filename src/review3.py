import pandas as pd
import numpy as np
import sklearn
from sklearn import preprocessing, cross_validation, svm, neighbors
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier


bbbDF = pd.read_csv('../data/Ball_by_Ball.csv')
matchesDF = pd.read_csv('../data/Match.csv')
pmDf = pd.read_csv('../data/Player_Match.csv')
playerDF = pd.read_csv('../data/Player.csv')
seasonDF = pd.read_csv('../data/Season.csv')
teamsDF = pd.read_csv('../data/Team.csv')
winPercentDf = pd.read_csv('../data/gen/win_percent.csv')

modifiedMatchDf = matchesDF

modifiedTeamDf = teamsDF
modifiedTeamDf['Win_Percentage'] = 0

# Removing Matches which do not have a result.
modifiedMatchDf = matchesDF[matchesDF.IS_Result != 0]
# Removing all NA Values
modifiedMatchDf.dropna(inplace=True)

# Final DF To be fitted
modifiedMatchDf = modifiedMatchDf[['Match_Id','Team_Name_Id', 'Opponent_Team_Id', 'Toss_Winner_Id','Toss_Decision', 'Match_Winner_Id']]


totalTeams = len(teamsDF)

def getMatchesForTeam(id):
	return matchesDF[(matchesDF["Team_Name_Id"] == id) | (matchesDF["Opponent_Team_Id"] == id)]

def getMatchesWonByTeam(id):
	return matchesDF[matchesDF["Match_Winner_Id"] == id]

def getMatchesForTeamAgainstTeam(team_id,against_id):
	return matchesDF[((matchesDF["Team_Name_Id"] == team_id) & (matchesDF["Opponent_Team_Id"] == against_id)) | ((matchesDF["Team_Name_Id"] == against_id) & (matchesDF["Opponent_Team_Id"] == team_id))]

def getMatchWonByTeamAgainstTeam(team_id,against_id):
	totalMatchesDF = getMatchesForTeamAgainstTeam(team_id,against_id)
	return totalMatchesDF[totalMatchesDF["Match_Winner_Id"] == team_id]

def getMatchWonPercentWhenTossWonForTeam(id):
	tossWonDF = matchesDF[matchesDF["Toss_Winner_Id"] == id]
	matchWonDF = tossWonDF[tossWonDF["Match_Winner_Id"] == id]
	return (len(matchWonDF)*100)/(len(tossWonDF))

def getFirstBatWonPercentage(id):
	totalMatchesDF = getMatchesForTeam(id)
	batFirstMatchesDF = totalMatchesDF[((totalMatchesDF["Toss_Winner_Id"]==id) & (totalMatchesDF["Toss_Decision"] == 'bat')) | ((totalMatchesDF["Toss_Winner_Id"]!=id) & (totalMatchesDF["Toss_Decision"] == 'field'))]
	matchesWonDF = batFirstMatchesDF[batFirstMatchesDF["Match_Winner_Id"] == id]
	batFirstMatches = len(batFirstMatchesDF)
	if(batFirstMatches>0):
		matchesWon = len(matchesWonDF)
		return (matchesWon*100)/batFirstMatches
	return 0


# Add Columns for each team in any match for their Win Percentage in modifiedMatchDf
modifiedMatchDf['Team_Win_Percentage'] = 0
modifiedMatchDf['Opponent_Team_Win_Percentage'] = 0
modifiedMatchDf['Team_Won_Against_Opponent_Percentage'] = 0
modifiedMatchDf['Team_Toss_Decision_Match_Won'] = 0
modifiedMatchDf['Opponent_Toss_Decision_Match_Won'] = 0
modifiedMatchDf['Team_Bat_Decision_Match_Won'] = 0
modifiedMatchDf['Opponent_Bat_Decision_Match_Won'] = 0


def saveWinPercentageInTeamsDf():
	for teamId in teamsDF.Team_Id.unique():
		matchesWonDF = getMatchesWonByTeam(teamId)
		totalMatchesDF = getMatchesForTeam(teamId)
		totalMatches = len(totalMatchesDF)
		matchesWon = len(matchesWonDF)
		modifiedTeamDf.loc[(modifiedTeamDf.Team_Id == teamId), 'Win_Percentage'] = ((matchesWon*100)/totalMatches)

saveWinPercentageInTeamsDf()

def getTeamWonAgainstOpponentPercentage(teamId, opponentId):
	return float(winPercentDf[(winPercentDf.team_id == teamId) & (winPercentDf.opponent_id == opponentId)].win_percentage)

def addNewColumnDataInModifiedMatchDf():
	for matchId in modifiedMatchDf.Match_Id.unique():

		teamNameId = int(modifiedMatchDf[modifiedMatchDf.Match_Id == matchId].Team_Name_Id)
		opponentTeamId = int(modifiedMatchDf[modifiedMatchDf.Match_Id == matchId].Opponent_Team_Id)

		# Adding Team Won and Opponent Team Won Percentage
		modifiedMatchDf.loc[(modifiedMatchDf.Match_Id == matchId), 'Team_Win_Percentage'] = float(modifiedTeamDf[modifiedTeamDf.Team_Id == teamNameId].Win_Percentage)
		modifiedMatchDf.loc[(modifiedMatchDf.Match_Id == matchId), 'Opponent_Team_Win_Percentage'] = float(modifiedTeamDf[modifiedTeamDf.Team_Id == opponentTeamId].Win_Percentage)
		modifiedMatchDf.loc[(modifiedMatchDf.Match_Id == matchId), 'Team_Won_Against_Opponent_Percentage'] = float(getTeamWonAgainstOpponentPercentage(teamNameId, opponentTeamId))
		if int(modifiedMatchDf[modifiedMatchDf.Match_Id == matchId].Toss_Winner_Id) == teamNameId:
			modifiedMatchDf.loc[(modifiedMatchDf.Match_Id == matchId), 'Team_Toss_Decision_Match_Won'] = float(getMatchWonPercentWhenTossWonForTeam(teamNameId))
			modifiedMatchDf.loc[(modifiedMatchDf.Match_Id == matchId), 'Opponent_Toss_Decision_Match_Won'] = float(100) - float(getMatchWonPercentWhenTossWonForTeam(opponentTeamId))
		else:
			modifiedMatchDf.loc[(modifiedMatchDf.Match_Id == matchId), 'Team_Toss_Decision_Match_Won'] = float(100) - float(getMatchWonPercentWhenTossWonForTeam(teamNameId))
			modifiedMatchDf.loc[(modifiedMatchDf.Match_Id == matchId), 'Opponent_Toss_Decision_Match_Won'] = float(getMatchWonPercentWhenTossWonForTeam(opponentTeamId))

		if (int(modifiedMatchDf[modifiedMatchDf.Match_Id == matchId].Toss_Winner_Id) == teamNameId and modifiedMatchDf[modifiedMatchDf.Match_Id == matchId].Toss_Decision.str.contains('bat').any()) or (int(modifiedMatchDf[modifiedMatchDf.Match_Id == matchId].Toss_Winner_Id) != teamNameId and modifiedMatchDf[modifiedMatchDf.Match_Id == matchId].Toss_Decision.str.contains('field').any()):
			modifiedMatchDf.loc[(modifiedMatchDf.Match_Id == matchId), 'Team_Bat_Decision_Match_Won'] = float(getFirstBatWonPercentage(teamNameId))
			modifiedMatchDf.loc[(modifiedMatchDf.Match_Id == matchId), 'Opponent_Bat_Decision_Match_Won'] = float(100) - float(getFirstBatWonPercentage(opponentTeamId))
		else:
				modifiedMatchDf.loc[(modifiedMatchDf.Match_Id == matchId), 'Opponent_Bat_Decision_Match_Won'] = float(getFirstBatWonPercentage(opponentTeamId))
				modifiedMatchDf.loc[(modifiedMatchDf.Match_Id == matchId), 'Team_Bat_Decision_Match_Won'] = float(100) - float(getFirstBatWonPercentage(teamNameId))




addNewColumnDataInModifiedMatchDf()

modifiedMatchDf = modifiedMatchDf.drop(['Toss_Decision'],1)

modifiedMatchDf = modifiedMatchDf.drop(['Match_Id'],1)
X = modifiedMatchDf.drop(['Match_Winner_Id'],1)
Y = modifiedMatchDf['Match_Winner_Id']

X = preprocessing.scale(X)

X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, Y, test_size = 0.25)

print("Linear SVM")
lr = LinearRegression()
lr.fit(X_train, y_train)
accu = lr.score(X_test,y_test)
print(accu)


# print("Linear SVM")
# lin_clf = svm.LinearSVC()
# lin_clf.fit(X_train, y_train)
# accu = lin_clf.score(X_test,y_test)
# print(accu)

print("SVC SVM")
clf = svm.SVC()
clf.fit(X_train, y_train)
accu = clf.score(X_test,y_test)
print(accu)

print("SVR SVM")
clf = svm.SVR()
clf.fit(X_train, y_train)
accu = clf.score(X_test,y_test)
print(accu)

from sklearn.naive_bayes import GaussianNB
gnb = GaussianNB()
print("Naive Bayes")
gnb.fit(X_train, y_train)
accu = gnb.score(X_test,y_test)
print(accu)



print("Random Forest")
rf = RandomForestClassifier()
rf.fit(X_train, y_train)
accu = rf.score(X_test,y_test)
print(accu)

# print(modifiedTeamDf.head())
# print(X_train)
# X = preprocessing.scale(X)modifiedMatchDf.to_csv("./mainDF.csv",sep=',')
