import SQLutils
import RESTutils
import PRAWutils
import utils

import sys


# this was to get and fill just the submissions table
def GetAndFillSubmissionsTable():
	beforeTime = 1615770384 # march 14 9pm EST (2021)
	afterTime = 1600218384 # sept 15 9pm EST (2020)

	# fill 'submissions' with a list of submission ids between the given times
	submissions = RESTutils.getSubmissionsBetweenTimes(beforeTime, afterTime)

	# submissions is a list of (submission_id, author_name, timestamp) tuple

	db = SQLutils.getSQLdb()
	for submission in submissions:
		SQLutils.insertSubmission(db, submission)


def main():
	hoursBack = 1
	while True:
		times = getBeforeAndAfterTimes(hoursBack)
		if times == -1:
			print("FINISHED!!!")
			break

		beforeTime = times[0]
		afterTime = times[1]

		result = getAndStoreComments(beforeTime, afterTime)
		if result == -1:
			hoursBack += 1
		else:
			hoursBack = 1

# Get the times between which we should search for comments. Get all times before the earliest
# time in the submission database, and search backwards for 'hoursBack' hours.
def getBeforeAndAfterTimes(hoursBack):
	db = SQLutils.getSQLdb()

	endTime = 1615856784 # march 15 9pm EST (2021)
	startTime = 1600218384 # sept 15 9pm EST (2020)

	beforeTime = SQLutils.getEarliestSubmissionTime(db)
	afterTime = beforeTime - (3600 * hoursBack) # 1 hour * hoursBack

	if beforeTime < startTime:
		return -1

	print (beforeTime, afterTime)
	return (beforeTime, afterTime)
	

def getAndStoreComments(beforeTime, afterTime):
	db = SQLutils.getSQLdb()

	submissions = SQLutils.getSubmissionsBetweenTimes(db, beforeTime, afterTime)
	if len(submissions) == 0:
		return -1 # there were no submissions, so go back another hour

	comment_ids = []
	comment_associations = {}
	for submission in submissions:
		submission_comment_ids = RESTutils.getCommentsForSubmission(submission[0])
		for comment_id in submission_comment_ids:
			comment_associations[comment_id] = (submission[0], submission[3])
		comment_ids += submission_comment_ids

	if len(comment_ids) == 0:
		return -1 # there were no comments, so go back another hour

	# prepend 't1_' to all comment ids
	for i in range(len(comment_ids)):
		comment_ids[i] = "t1_" + comment_ids[i]

	# for each comment, get the info to stick in the DB
	comment_infos = []
	reddit = utils.getReddit()
	for comment in reddit.info(fullnames = comment_ids):
		comment_infos.append(PRAWutils.getCommentInfo(reddit, comment_associations, comment))

	for comment_info in comment_infos:
		SQLutils.insertComment(db, comment_info)

	return 1 # ok

if __name__ == "__main__":
    main()