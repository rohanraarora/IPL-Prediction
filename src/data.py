import pandas as pd
import numpy as np

#Source Data
bbbsDF = pd.read_csv('../data/Ball_by_Ball.csv')
bbbsDF = bbbsDF.convert_objects(convert_numeric=True)
matchesDF = pd.read_csv('../data/Match.csv')
playerMatchesDF = pd.read_csv('../data/Player_Match.csv')
playersDF = pd.read_csv('../data/Player.csv')
seasonsDF = pd.read_csv('../data/Season.csv')
teamsDF = pd.read_csv('../data/Team.csv')

def getMatchesForTeam(id):
    return matchesDF[(matchesDF["Team_Name_Id"] == id) | (matchesDF["Opponent_Team_Id"] == id)]

def getMatchesWonByTeam(id):
    return matchesDF[matchesDF["Match_Winner_Id"] == id]

def getTeamWinPercentage(id):
    result = 0
    totalMatches = len(getMatchesForTeam(id))
    matchesWon = len(getMatchesWonByTeam(id))
    if(totalMatches>0):
        result = (matchesWon*100)/totalMatches
    return result

def getMatchesForTeamAgainstTeam(team_id,against_id):
    return matchesDF[((matchesDF["Team_Name_Id"] == team_id) & (matchesDF["Opponent_Team_Id"] == against_id)) | ((matchesDF["Team_Name_Id"] == against_id) & (matchesDF["Opponent_Team_Id"] == team_id))]

def getMatchWonByTeamAgainstTeam(team_id,against_id):
    totalMatchesDF = getMatchesForTeamAgainstTeam(team_id,against_id)
    return totalMatchesDF[totalMatchesDF["Match_Winner_Id"] == team_id]

def getMatchWonPercentageForTeamAgainstTeam(team_id,against_id):
    result = 0
    totalMatchesDF = getMatchesForTeamAgainstTeam(team_id,against_id)
    matchesWon = len(totalMatchesDF[totalMatchesDF["Match_Winner_Id"] == team_id])
    totalMatches = len(totalMatchesDF)
    if(totalMatches>0):
        result = (matchesWon*100)/totalMatches
    return result

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

def geneareWinPercentageSheet():
    print("Generating WinPercent Data")
    data = pd.DataFrame( columns=('team_id','opponent_id','win_percentage'))
    pos = 0
    for index, row in teamsDF.iterrows():
        teamId = row["Team_Id"]
        for i, r in teamsDF.iterrows():
            ti = r["Team_Id"]
            if(ti != teamId):
                win_percent = np.nan
                matchesAgainst = len(getMatchesForTeamAgainstTeam(teamId,ti))
                matchesWonAgainst = len(getMatchWonByTeamAgainstTeam(teamId,ti))
                if(matchesAgainst > 0):
                    win_percent = (matchesWonAgainst*100)/matchesAgainst
                data.loc[pos,"team_id"] = teamId
                data.loc[pos,"opponent_id"] = ti
                data.loc[pos,"win_percentage"] = win_percent
                pos = pos + 1
    data.to_csv("../data/gen/win_percent.csv",sep=',')
    print("Done")

def calculateBatsmanScore(row):
    PAR_AVG = 122.84
    score = 0
    runs = row["Runs"]
    fifties = row["Fifties"]
    hundreds = row["Hundreds"]
    bowlsPlayed = row["Bowls_Played"]
    out = row["Out"]
    average = 0
    if(bowlsPlayed>0):
        average = (runs*100)/bowlsPlayed
    wicketsAsFielder = row["Wickets_As_Fielder"]
    if(runs > 0):
        score = score + runs
        score = score + fifties*25
        score = score + hundreds*50
        if(out == 0):
            score = score + 10
        relative_avg = average/PAR_AVG
        score = score*relative_avg
    else:
        if(out == 1):
            score = score - 15
    if(wicketsAsFielder > 0):
        score = score + 10*wicketsAsFielder
    return score

def calculateBowlerScore(row):
    score = 0
    wickets = row["Wickets"]
    runsConceded = row["Runs_Conceded"]
    economy = 0
    extras = row["Extras"]
    overs = row["Overs"]
    maidenOvers = row["Maiden_Overs"]
    wicketsAsFielder = row["Wickets_As_Fielder"]
    if(overs>0):
        economy = runsConceded/overs
    if(wickets > 0):
        score = score + 22.5*wickets
        if(wickets >= 4 ):
            score = score + 10*wickets
    if(extras >= 10):
        score = score - 10
    elif(extras >= 5):
        score = score - 5
    elif(extras > 0):
        score = score -2
    if(maidenOvers > 0):
        score = score + maidenOvers*10
    if(wicketsAsFielder > 0):
        score = score + 10*wicketsAsFielder
    return score

def generatePlayerMatchScoreData():
    playersMatchesCompleteDF = pd.read_csv("../data/gen/player_match_complete.csv")
    playersMatchesCompleteDF = playersMatchesCompleteDF.convert_objects(convert_numeric=True)
    print("Generating PlayerMatchesComplete Data")
    data = pd.DataFrame(columns=('Match_Id','Player_Id','Team_Id','Is_Batsman','Is_Bowler','Is_Allrounder','Score'))
    pos = 0
    totalSize = len(playersMatchesCompleteDF)
    for index,row in playersMatchesCompleteDF.iterrows():
        print("Processing data...( %d %% done)" % int(pos*100/totalSize) )
        isBatsman = 0
        isBowler = 0
        isAllRounder = 0
        score = 0
        matchId = row["Match_Id"]
        playerId = row['Player_Id']
        teamId = row["Team_Id"]
        playerMatchesCompleteDF = playersMatchesCompleteDF[(playersMatchesCompleteDF["Player_Id"] == playerId)]
        totalMatches = len(playerMatchesCompleteDF)
        battedMatchedDF = playerMatchesCompleteDF[playerMatchesCompleteDF["Batted"] == 1]
        bowledMatchesDF = playerMatchesCompleteDF[playerMatchesCompleteDF["Bowled"] == 1]
        bothMatchesDF = playerMatchesCompleteDF[(playerMatchesCompleteDF["Batted"] == 1)&(playerMatchesCompleteDF["Bowled"] == 1)]
        battedMatches = len(battedMatchedDF)
        bowledMatches = len(bowledMatchesDF)
        bothMatches = len(bothMatchesDF)
        if(((bothMatches*100)/totalMatches) > 66):
            isAllRounder = 1
            isBatsman = 0
            isBowler = 0
            score = calculateBatsmanScore(row) + calculateBowlerScore(row)
        elif(battedMatches > bowledMatches):
            isBatsman = 1
            isAllRounder = 0
            isBowler = 0
            score = calculateBatsmanScore(row)
        else:
            isBowler = 1
            isBatsman = 0
            isAllRounder = 0
            score = calculateBowlerScore(row)
        data.loc[pos,'Match_Id'] = matchId
        data.loc[pos,'Player_Id'] = playerId
        data.loc[pos,"Team_Id"] = teamId
        data.loc[pos,'Is_Batsman'] = isBatsman
        data.loc[pos,'Is_Bowler'] = isBowler
        data.loc[pos,'Is_Allrounder'] = isAllRounder
        data.loc[pos,'Score'] = score
        pos = pos + 1
    data.to_csv("../data/gen/player_match_score.csv",sep=',')
    print("Done")

def generatePlayerScoreData():
    print("Generating PlayerScore Data")
    data = pd.DataFrame(columns=('Player_Id','Player_Name','Total_Score','Avg_Score'))
    playersMatchesScoreDF = pd.read_csv("../data/gen/player_match_score.csv")
    pos = 0
    for index,row in playersDF.iterrows():
        score = 0
        totalScore = 0
        playerId = row["Player_Id"]
        name = row["Player_Name"]
        playerMatchesDF = playersMatchesScoreDF[playersMatchesScoreDF["Player_Id"] == playerId]
        totalMatches = len(playerMatchesDF)
        if(totalMatches>0):
            totalScore = playerMatchesDF["Score"].sum()
            score = totalScore/totalMatches
        data.loc[pos,"Player_Id"] = playerId
        data.loc[pos,"Player_Name"] = name
        data.loc[pos,"Total_Score"] = totalScore
        data.loc[pos,"Avg_Score"] = score
        pos = pos + 1
    data.to_csv("../data/gen/player_score.csv",sep=',')
    print("Done")

def generatePlayerMatchesCompleteData():
    print("Generating PlayerMatchesComplete Data")
    data = pd.DataFrame(columns=('Match_Id','Player_Id','Team_Id','Batted','Bowls_Played','Runs','Fifties','Hundreds','Out','Bowled','Wickets','Runs_Conceded','Overs','Maiden_Overs','Extras','Wickets_As_Fielder'))
    pos = 0
    totalSize = len(playerMatchesDF)
    for index,row in playerMatchesDF.iterrows():
        print("Processing data...( %d %% done)" % int(pos*100/totalSize) )
        runsScored = np.nan
        fifties = np.nan
        hundreds = np.nan
        out = np.nan
        bowlsPlayed = np.nan
        bowled = 0
        batted = 0
        wickets = np.nan
        runsConceded = np.nan
        overs = np.nan
        maidenOvers = np.nan
        extras = np.nan
        matchId = row["Match_Id"]
        bbbMatchDF = bbbsDF[bbbsDF["Match_Id"] == matchId]
        playerId = row['Player_Id']
        teamId = row["Team_Id"]
        playerAsStrikerDF = bbbMatchDF[bbbMatchDF["Striker_Id"] == playerId]
        playerAsBatsmanDF = bbbMatchDF[(bbbMatchDF["Striker_Id"] == playerId) | (bbbMatchDF["Non_Striker_Id"] == playerId) ]
        wicketsAsFielder = len(bbbMatchDF[bbbMatchDF["Fielder_Id"] == playerId])
        if(len(playerAsBatsmanDF)>0):
            batted = 1
        if(len(playerAsStrikerDF) > 0):
            bowlsPlayed = len(playerAsStrikerDF)
            runsScored = playerAsStrikerDF["Batsman_Scored"].sum()
            out = len(playerAsBatsmanDF[playerAsBatsmanDF["Player_dissimal_Id"] == playerId])
            if(runsScored > 0):
                if(runsScored > 100):
                    hundreds = int(runsScored/100)
                    fifties = int((runsScored - hundreds*100)/50)
                else:
                    hundreds = 0
                    fifties = int(runsScored/50)

        playerAsBowlerDF = bbbMatchDF[bbbMatchDF["Bowler_Id"] == playerId]
        bowlsThrowed = len(playerAsBowlerDF)
        if(bowlsThrowed > 0):
            bowled = 1
            runsConceded = playerAsBowlerDF["Batsman_Scored"].sum()
            wicketsDF = playerAsBowlerDF[playerAsBowlerDF["Player_dissimal_Id"] > 0]
            wickets = len(wicketsDF)
            extras = playerAsBowlerDF["Extra_Runs"].sum()
            oversGroup = playerAsBowlerDF.groupby(["Over_Id"])["Batsman_Scored"].sum().reset_index("score")
            overs = len(oversGroup)
            maidenOvers = len(oversGroup[oversGroup["Batsman_Scored"] == 0])

        data.loc[pos,"Match_Id"] = matchId
        data.loc[pos,"Player_Id"] = playerId
        data.loc[pos,"Batted"] = batted
        data.loc[pos,"Bowls_Played"] = bowlsPlayed
        data.loc[pos,"Runs"] = runsScored
        data.loc[pos,"Fifties"] = fifties
        data.loc[pos,"Hundreds"] = hundreds
        data.loc[pos,"Out"] = out
        data.loc[pos,"Bowled"] = bowled
        data.loc[pos,"Wickets"] = wickets
        data.loc[pos,"Runs_Conceded"] = runsConceded
        data.loc[pos,"Overs"] = overs
        data.loc[pos,"Maiden_Overs"] = maidenOvers
        data.loc[pos,"Extras"] = extras
        data.loc[pos,"Team_Id"] = teamId
        data.loc[pos,"Wickets_As_Fielder"] = wicketsAsFielder
        pos = pos + 1

    data.to_csv("../data/gen/player_match_complete.csv",sep=',')
    print("Done")

def generatePredictData(teamId,opponentId,tossWon,batFirst):
    data = pd.DataFrame(columns=('Match_Id','Team_Id','Toss_Won','Bat_First','Win_Percenetage','Opponent_Win_Percentage','Win_Percenetage_Against','Toss_Decision_Win_Percentage','Bat_Decision_Win_Percentage','Match_Won'))
    pos = 0
    matchId = 1
    teamTossWon = 0
    teamBatFirst = 0
    teamWinPercentage = getTeamWinPercentage(teamId)
    opponentTeamWinPercentage = getTeamWinPercentage(opponentId)
    teamMatchWinPercentAgainstOpponent = getMatchWonPercentageForTeamAgainstTeam(teamId,opponentId)
    teamTossDescionWinPercentage = getMatchWonPercentWhenTossWonForTeam(teamId)
    teamBatDecisionWonPercentage = getFirstBatWonPercentage(teamId)
    if(tossWon == teamId):
        teamTossWon = 1
    else:
        teamTossDescionWinPercentage = 100 - teamTossDescionWinPercentage

    if(batFirst == teamId):
        teamBatFirst = 1
    else:
        teamBatDecisionWonPercentage = 100 - teamBatDecisionWonPercentage
    data.loc[pos,"Match_Id"] = matchId
    data.loc[pos,"Team_Id"] = teamId
    data.loc[pos,"Toss_Won"] = teamTossWon
    data.loc[pos,"Bat_First"] = teamBatFirst
    data.loc[pos,"Win_Percenetage"] = teamWinPercentage
    data.loc[pos,"Opponent_Win_Percentage"] = opponentTeamWinPercentage
    data.loc[pos,"Win_Percenetage_Against"] = teamMatchWinPercentAgainstOpponent
    data.loc[pos,"Toss_Decision_Win_Percentage"] = teamTossDescionWinPercentage
    data.loc[pos,"Bat_Decision_Win_Percentage"] = teamBatDecisionWonPercentage
    data.loc[pos,"Match_Won"] = 0
    return data




def generateMatchTeamData():
    data = pd.DataFrame(columns=('Match_Id','Team_Id','Toss_Won','Bat_First','Win_Percenetage','Opponent_Win_Percentage','Win_Percenetage_Against','Toss_Decision_Win_Percentage','Bat_Decision_Win_Percentage','Match_Won'))
    pos = 0
    for index,row in matchesDF.iterrows():
        matchId = row["Match_Id"]
        teamId = row["Team_Name_Id"]
        opponentTeamId = row["Opponent_Team_Id"]
        teamWinPercentage = getTeamWinPercentage(teamId)
        opponentTeamWinPercentage = getTeamWinPercentage(opponentTeamId)
        teamMatchWinPercentAgainstOpponent = getMatchWonPercentageForTeamAgainstTeam(teamId,opponentTeamId)
        teamTossWon = 0
        opponentTossWon = 0
        teamBatFirst = 0
        opponentBatFirst = 0
        tossWinTeamId = row["Toss_Winner_Id"]
        batDecision = row["Toss_Decision"]
        teamTossDescionWinPercentage = getMatchWonPercentWhenTossWonForTeam(teamId)
        opponentTeamTossDescionWinPercentage = getMatchWonPercentWhenTossWonForTeam(opponentTeamId)
        teamBatDecisionWonPercentage = getFirstBatWonPercentage(teamId)
        opponentBatDecisionWonPercentage = getFirstBatWonPercentage(opponentTeamId)
        if(teamTossWon == teamId):
            teamTossWon = 1
            opponentTeamTossDescionWinPercentage = 100 - opponentTeamTossDescionWinPercentage
            if(batDecision == 'bat'):
                teamBatFirst = 1
                opponentBatDecisionWonPercentage = 100 - opponentBatDecisionWonPercentage
            else:
                opponentBatFirst = 1
                teamBatDecisionWonPercentage = 100 - teamBatDecisionWonPercentage
        else:
            opponentTossWon = 1
            teamTossDescionWinPercentage = 100 - teamTossDescionWinPercentage
            if(batDecision == 'bat'):
                opponentBatFirst = 1
                teamBatDecisionWonPercentage = 100 - teamBatDecisionWonPercentage
            else:
                teamBatFirst = 1
                opponentBatDecisionWonPercentage = 100 - opponentBatDecisionWonPercentage
        matchWon = row["Match_Winner_Id"]
        teamMatchWon = 0
        opponentMatchWon = 0
        if(matchWon == teamId):
            teamMatchWon = 1
        else:
            opponentMatchWon = 1

        data.loc[pos,"Match_Id"] = matchId
        data.loc[pos,"Team_Id"] = teamId
        data.loc[pos,"Toss_Won"] = teamTossWon
        data.loc[pos,"Bat_First"] = teamBatFirst
        data.loc[pos,"Win_Percenetage"] = teamWinPercentage
        data.loc[pos,"Opponent_Win_Percentage"] = opponentTeamWinPercentage
        data.loc[pos,"Win_Percenetage_Against"] = teamMatchWinPercentAgainstOpponent
        data.loc[pos,"Toss_Decision_Win_Percentage"] = teamTossDescionWinPercentage
        data.loc[pos,"Bat_Decision_Win_Percentage"] = teamBatDecisionWonPercentage
        data.loc[pos,"Match_Won"] = teamMatchWon
        pos = pos + 1

        data.loc[pos,"Match_Id"] = matchId
        data.loc[pos,"Team_Id"] = opponentTeamId
        data.loc[pos,"Toss_Won"] = opponentTossWon
        data.loc[pos,"Bat_First"] = opponentBatFirst
        data.loc[pos,"Win_Percenetage"] = opponentTeamWinPercentage
        data.loc[pos,"Opponent_Win_Percentage"] = teamWinPercentage
        data.loc[pos,"Win_Percenetage_Against"] = 100 - teamMatchWinPercentAgainstOpponent
        data.loc[pos,"Toss_Decision_Win_Percentage"] = opponentTeamTossDescionWinPercentage
        data.loc[pos,"Bat_Decision_Win_Percentage"] = opponentBatDecisionWonPercentage
        data.loc[pos,"Match_Won"] = opponentMatchWon
        pos = pos + 1

    data.to_csv("../data/gen/match_team.csv",sep=',')
    print("Done")


#eneratePlayerMatchesCompleteData()
#geneareWinPercentageSheet()
#generatePlayerMatchScoreData()
#generatePlayerScoreData()
#generateMatchTeamData()
