# -*- coding: utf-8 -*-

from jira import JIRA
import pandas as pd

def downloadTimeLogs(serverURL, projectName):
    jira_options = {
            'server':serverURL
            }
    jira_user = 'marcin.wroblewski@scalac.io'
    jira_pass = 'k1T27hk7HhuYlM2tmOIf6AFB'
    jac = JIRA(options=jira_options, basic_auth=(jira_user, jira_pass))

    block_size =100
    block_num = 0

    auth = pd.Series()
    wlDt = pd.Series()
    wlTS = pd.Series()
    summ = pd.Series()
    iKey = pd.Series()

    while True:
        start_idx = block_num * block_size
        issues_in_project = jac.search_issues('project='+ projectName, start_idx, block_size)
        if len(issues_in_project) == 0:
            break
        block_num += 1


        for issue in issues_in_project:
            wrkl = jac.worklogs(issue.key)
            for wrk in wrkl:
                summ.add(issue.fields.summary)
                iKey.add(issue.key)
                auth.add(wrk.author)
                wlTS.add(wrk.timeSpent)
                wlDt.add(wrk.started)
    preFrame = {
        'Summary':summ,
        'Key':iKey,
        'Author':auth,
        'TimeSpent':wlTS,
        'Date':wlDt
    }
    result = pd.DataFrame(preFrame)
    result.to_excel('final/'+ projectName + '.xlsx')
    return "Done"

print(
    downloadTimeLogs(serverURL='http://prp.atlassian.net', projectName='PRP')
    )