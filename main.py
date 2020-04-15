# -*- coding: utf-8 -*-

from jira import JIRA
import datetime
import pandas as pd
import json
from config import SERVER_URL, JIRA_PASS, JIRA_USER


def estimateStartDate(offset):
    dateNow = datetime.datetime.now().date()
    return dateNow - datetime.timedelta(offset)


def strToDate(DateInString: str):
    return datetime.datetime.strptime(DateInString[:10], '%Y-%m-%d').date()


def ifNone(valueToTest, alterValue):
    result = None
    if valueToTest is None:
        result = alterValue
    else:
        result = valueToTest
    return result


def readAllProjects():
    jira_options = {
        'server': SERVER_URL
    }

    jac = JIRA(options=jira_options, basic_auth=(JIRA_USER, JIRA_PASS))
    projNames = []
    projects = jac.projects()
    for proj in projects:
        projNames.append(proj.name)
    return json.dumps(projNames)


def downloadTimeLogs(projectName):
    # connecting to jira server
    jira_options = {
        'server': SERVER_URL
    }
    jac = JIRA(options=jira_options, basic_auth=(JIRA_USER, JIRA_PASS))
    block_size = 100
    block_num = 0
    while True:
        start_idx = block_num * block_size
        issues_in_project = jac.search_issues(
            'project='+projectName, start_idx, block_size)
        if len(issues_in_project) == 0:
            break
        else:
            # iterating through issues to get all timelogs
            for issue in issues_in_project:
                auth = list()
                wlDt = list()
                wlTS = list()
                summ = list()
                iKey = list()
                pKey = list()
                pDesc = list()
                wrkl = jac.worklogs(issue.key)
                if len(wrkl) > 0:
                    for wrk in wrkl:
                        try:
                            pKey.append(issue.fields.parent.key)
                            pDesc.append(issue.fields.parent.fields.summary)
                        except AttributeError:
                            pKey.append(issue.key)
                            pDesc.append(issue.fields.summary)
                        finally:
                            summ.append(issue.fields.summary)
                            iKey.append(issue.key)
                            auth.append(wrk.author)
                            wlTS.append(wrk.timeSpentSeconds/3600)
                            wlDt.append(wrk.started[:10])
                    preFrame = {
                        'Parent Key': pKey,
                        'Parent Description': pDesc,
                        'Key': iKey,
                        'Summary': summ,
                        'Author': auth,
                        'TimeSpent': wlTS,
                        'Date': wlDt
                    }
                    result = pd.DataFrame(preFrame)
                    result.to_csv(
                        'final/' + projectName + '.csv',
                        mode='a',
                        header=False,
                        sep='|')
        print(block_num)
        block_num += 1

    print("Done")


def listNextSprintIssues(sprintName):
    jira_options = {
        'server': SERVER_URL
    }
    jac = JIRA(options=jira_options, basic_auth=(JIRA_USER, JIRA_PASS))
    nextSprintWorkload = jac.search_issues(
        'project = BP AND Sprint = ' +
        sprintName +
        'ORDER BY Rank ASC')
    for issue in nextSprintWorkload:
        try:
            print(str(issue)+" - " + issue.fields.summary +
                  '('+issue.fields.timetracking.originalEstimate+')')
        except AttributeError as ae:
            print(str(issue)+" - " + issue.fields.summary)
            print(ae)


if __name__ == "__main__":
    print(datetime.datetime.now())
    dtStart = datetime.datetime.now()
    # listNextSprintIssues('"BP Sprint 46"')
    # readAllProjects()
    downloadTimeLogs("BP")
    print(datetime.datetime.now())
    print(datetime.datetime.now() - dtStart)
