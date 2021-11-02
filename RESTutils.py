import praw
from datetime import datetime
from praw.models import MoreComments
from utils import getTimeDifference
import requests
import json

import sys
import time

def getCommentsForSubmission(submission_id):
    request_string = "https://api.pushshift.io/reddit/submission/comment_ids/"
    request_string += submission_id

    # The request fails randomly sometimes; I haven't been able to figure out why. For now,
    # just sleep 5 seconds and try again.
    success = False
    while not success:
        try:
            response = requests.get(request_string)
            response_json = response.json()
            success = True
        except ValueError:
            print("Unexpected error:", sys.exc_info()[0])
            print("JSON responded with empty for some reason.... trying again")
            time.sleep(5)

    print(len(response_json["data"]))
    return response_json["data"]

# Returns a (submission_id, author_name, timestamp) tuple
def getSubmissionsBetweenTimes(beforeTime, afterTime):
    num_results = 1
    curBeforeTime = beforeTime
    results = []
    while num_results != 0:
        request_string = getRequestString(curBeforeTime, afterTime)
        # print(request_string)
        response = requests.get(request_string)
        response_json = response.json()
        for entry in response_json["data"]:
            author_id = ""
            if "author_fullname" in entry:
                author_id = entry["author_fullname"][3:]
            results.append((entry["id"], author_id, entry["author"], entry["created_utc"], entry["num_comments"]))
        num_results = response_json["metadata"]["results_returned"]
        length = len(response_json["data"])
        if length > 0:
            curBeforeTime = response_json["data"][length-1]["created_utc"]

        print(response_json["metadata"]["total_results"])
    return results

def getRequestString(beforeTime, afterTime):
    responseString = "https://api.pushshift.io/reddit/search/submission/?subreddit=politics&sort=desc&size=50000&metadata=true"
    responseString += "&before="
    responseString += str(beforeTime)
    responseString += "&after="
    responseString += str(afterTime)
    print(responseString)
    return responseString