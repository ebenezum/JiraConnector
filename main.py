# -*- coding: utf-8 -*-

from jira import JIRA
import pandas as pd
import numpy as np


def downloadTimeLogs(serverURL, projectName):
    jira_options = {
            'server':serverURL
            }
    jira_user = 'marcin.wroblewski@scalac.io'
    jira_pass = 'k1T27hk7HhuYlM2tmOIf6AFB'
    jac = JIRA(options=jira_options, basic_auth=(jira_user, jira_pass))

    block_size =100
    block_num = 0
    auth = list()
    wlDt = list()
    wlTS = list()
    summ = list()
    iKey = list()

    while True:
        start_idx = block_num * block_size
        issues_in_project = jac.search_issues('project='+projectName, start_idx, block_size)
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
        'Summary':summ,
        'Key':iKey,
        'Author':auth,
        'TimeSpent':wlTS,
        'Date':wlDt
    }
    result = pd.DataFrame(preFrame)
    # pivot = pd.pivot_table(result, values='TimeSpent',index=['Date','Summary'], columns='Author',aggfunc=np.sum)
    with pd.ExcelWriter('final/'+ projectName + '.xlsx') as writer:
        result.to_excel(writer, sheet_name='Raw Data')
        # pivot.to_excel(writer, sheet_name='Pivot')
    return "Done"

print(
    downloadTimeLogs(serverURL='http://prp.atlassian.net', projectName='PRP')
    )