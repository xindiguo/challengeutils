import os
import synapseclient
import pandas as pd
from synapseclient import Evaluation


def createEvaluationQueue(syn, name, description, status, parentId, submissionInstructionsMessage):
	queue = syn.store(Evaluation(
	  name=name,
	  description=description,
	  status=status,
	  contentSource=parentId,
	  submissionInstructionsMessage=submissionInstructionsMessage,
	  submissionReceiptMessage="Thanks for submitting to %s!" % name))
	return(queue)

def rescore(syn,evalID):
	bundle = syn.getSubmissionBundles(evalID,status='SCORED')
	for (i,(item,status)) in enumerate(bundle):
		status.status = 'VALIDATED'
		syn.store(status)
		print(i)

# {u'firstRoundStart': u'2017-01-03T00:00:00.000Z',
#   u'numberOfRounds': 1,
#   u'roundDurationMillis': 3139200000,
#   u'submissionLimit': 6}
def setQuota(syn,evalID,quota=3):
	quota1 = dict(submissionLimit = quota)
	e = syn.getEvaluation(evalID)
	e.quota = quota1
	e = syn.store(e)

def reNameSubmissionFiles(syn,evalID,downloadLocation="./",stat="SCORED"):
	bundle = syn.getSubmissionBundles(evalID,status=stat)
	for (i,(item,status)) in enumerate(bundle):
		if status.get("annotations") is not None:
			team = annots['stringAnnos'][0]['value']
		else:
			if item.get("teamId") is not None:
				team = syn.getTeam(item.get("teamId")).name
			else:
				user = syn.getUserProfile(item.userId).userName
		date = item.createdOn
		fileEnt = syn.getSubmission(item.id,downloadLocation=downloadLocation)
		fileName = os.path.basename(fileEnt.filePath)
		newName = team+"___"+date+"___"+fileName
		newName = newName.replace(' ','_')
		os.rename(fileName,newName)
		print(i)


def create_team_wikis(syn, synid, templateid, tracker_table_synid):
	"""
	Function that creates wiki pages from a template by looking at teams that
	are registered for a challenge.  The teams that have a wiki made for them
	Are stored into a trackerTable that has columns wikiSynId, and teamId

	params:
		synId: Synapse id of challenge project
		templateId:  Synapse id of the template
		trackerTableSynId: Synapse id of Table that tracks if wiki pages have been made per team
	"""
	

	challenge_ent = syn.get(synid)
	challenge_obj = getChallengeId(challenge_ent)
	registered_teams = syn._GET_paginated("/challenge/%s/challengeTeam" % challenge_obj['id'])
	for i in registered_teams:
		submitted_teams = syn.tableQuery("SELECT * FROM %s where teamId = '%s'" % (tracker_table_synid, i['teamId']))
		if len(submitted_teams.asDataFrame()) == 0:
			team = syn.getTeam(i['teamId'])
			#The project name is the challenge project name and team name
			project = syn.store(synapseclient.Project("%s %s" % (challenge_ent.name, team.name)))
			#Give admin access to the team
			syn.setPermissions(project, i['teamId'], accessType=['DELETE','CHANGE_SETTINGS','MODERATE','CREATE','READ','DOWNLOAD','UPDATE','CHANGE_PERMISSIONS'])
			wiki_copy = synu.copy(syn,templateid,project.id)
			#syn.sendMessage(i[])
			#Store copied synId to tracking table
			syn.store(synapseclient.Table(tracker_table_synid,[[wiki_copy[templateid],i['teamId']]]))