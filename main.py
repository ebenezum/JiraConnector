# -*- coding: utf-8 -*-

from jira import JIRA
import pandas as pd
import json
from config import SERVER_URL, JIRA_PASS, JIRA_USER


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
    jira_options = {
        'server': SERVER_URL
    }

    jac = JIRA(options=jira_options, basic_auth=(JIRA_USER, JIRA_PASS))

    block_size = 100
    block_num = 0
    auth = list()
    wlDt = list()
    wlTS = list()
    summ = list()
    iKey = list()

    while True:
        start_idx = block_num * block_size
        issues_in_project = jac.search_issues(
            'project='+projectName, start_idx, block_size)
        if len(issues_in_project) == 0:
            break
        block_num += 1

        for issue in issues_in_project:
            wrkl = jac.worklogs(issue.key)
            for wrk in wrkl:
                summ.append(issue.fields.summary)
                iKey.append(issue.key)
                auth.append(wrk.author)
                wlTS.append(wrk.timeSpentSeconds/3600)
                wlDt.append(wrk.started[:10])
    preFrame = {
        'Summary': summ,
        'Key': iKey,
        'Author': auth,
        'TimeSpent': wlTS,
        'Date': wlDt
    }
    result = pd.DataFrame(preFrame)
    with pd.ExcelWriter('final/' + projectName + '.xlsx') as writer:
        result.to_excel(writer, sheet_name='Raw Data')
        # pivot.to_excel(writer, sheet_name='Pivot')
    return "Done"


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
    # listNextSprintIssues('"BP Sprint 46"')
    # readAllProjects()
    downloadTimeLogs("BP")
