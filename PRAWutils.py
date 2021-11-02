import praw
from datetime import datetime
from praw.models import MoreComments
from utils import getTimeDifference

# Comment is a reddit comment object (not just a comment id).
# Comment_associations is a dict from {comment_id -> (submission_id, submission_created_utc)}
def getCommentInfo(reddit, comment_associations, comment):
    time_difference = comment.created_utc - comment_associations[comment.id][1]
    comment_author_name = ""
    comment_author_id = ""
    if comment.author != None:
        comment_author_name = comment.author.name
        comment_author_id = comment.author_fullname[3:]

    print((comment.id, comment_author_id, comment_author_name, comment.created_utc, time_difference, comment_associations[comment.id][0]))
    return (comment.id, comment_author_id, comment_author_name, comment.created_utc, time_difference, comment_associations[comment.id][0])