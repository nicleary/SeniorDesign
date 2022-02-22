from sqlalchemy import asc, and_, or_
from tasks.task_initializer import CELERY
from celery import group

from util.cred_handler import get_secret
from db.database_connection import create_session
from db.db_utils import create_single_object, get_or_create, get_single_object
from db.models import KeyRateLimit, SearchPhraseDates, TaskError, Tweet, SearchPhrase, TwitterUser, Bill, CommitteeCodes, SubcommitteeCodes, Task, twitter_api_token_type
from datetime import datetime, timedelta
from pytz import timezone
import more_itertools as mit
from tasks.twitter_tasks import run_tweet_puller_archive

TIME_BEFORE_IRRELEVANT = timedelta(days=30)

###
### Process individual bill request
###

@CELERY.task()
def run_process_bill_request(bill_id, user_id):
    session = create_session()
    task = process_bill_request(bill_id, user_id)
    session.add(task)
    session.commit()
    res = task.run()
    session.commit()
    return res

@CELERY.task()
def rerun_process_bill_request(task: Task, user_id):
    session = create_session()
    task = process_bill_request(task.parameters['bill_id'], user_id)
    session.add(task)
    session.commit()
    res = task.run()
    session.commit()
    return res

class process_bill_request(Task):
    def __init__(self, bill_id, user_id):
        super().__init__(complete=False, error=False, launched_by_id=user_id, type='process_bill_request', parameters={'bill_id':bill_id})

    def run(self):
        session = create_session()
        try:
            return self.process_bill_request(self.parameters['bill_id'], self.launched_by_id)
        except Exception as e: 
            self.error = True
            error_object = create_single_object(session, TaskError, defaults={'description': str(e), 'task_id': self.id})
            session.commit()
            return str(e)

    def process_bill_request(self, bill_id, user_id):
        session = create_session()
        ### Get bill object
        bill = session.query(Bill).where(Bill.bill_id == bill_id).first()
        actions = bill.actions
        active = bill.active
        # If we don't have actions, return
        if actions == []:
            session.close()
            return 'Bill does not have actions, try again later!'
        # otherwise sort asc by date
        actions = sorted(actions, key=lambda x: x.datetime)
        ### Get bill active times
        if active or len(actions) == 1:
            start = actions[0].datetime
            end = actions[-1].datetime + TIME_BEFORE_IRRELEVANT
        else:
            start = actions[0].datetime
            end = actions[-1].datetime

        ### Get bill phrases
        phrases = [kw for kw in bill.keywords if not kw.type == 3]

        ### Determine ranges that need to be pulled
        jobs = group([get_needed_date_ranges.s(phrase.id, start, end) for phrase in phrases])
        async_res = jobs.apply_async()
        result = async_res.get()

        ### Flatten result
        ranges = []
        for subarr in result:
            for elem in subarr:
                ranges.append(elem)

        ### Spawn tweet pullers
        for r in ranges:
            run_tweet_puller_archive.apply_async(r[0], None, r[1][0], r[1][1], user_id)
            phrase_date = SearchPhraseDates(search_phrase_id = r[0], start_date=r[1][0], end_date=r[1][1])
            session.add(phrase_date)
            session.commit()
        
        return 'Tasks Started Successfully'

@CELERY.task
def get_needed_date_ranges(phrase_id, start, end):
    #For a given phrase id, find when it has not yet been called in the given range
    session = create_session()
    #Get dates we have currently pulled for:
    initial_range = range(0, (end-start).days) #+1 for inclusivity
    existing = session.query(SearchPhraseDates).where(and_(SearchPhraseDates.search_phrase_id == phrase_id, or_(and_(end > SearchPhraseDates.start_date, end < SearchPhraseDates.end_date), and_(start > SearchPhraseDates.start_date, start < SearchPhraseDates.end_date)))).all()
    # Find int ranges
    print(existing)
    ex_ranges = [range((ex.start_date - start).days, (ex.end_date - start).days) for ex in existing]
    print(ex_ranges)
    # Removing items from ranges using set differences
    out_ranges = set(initial_range)
    for sub_range in ex_ranges: #for each sub range
        out_ranges = out_ranges - set(sub_range)
    it = list(out_ranges)
    continuous = [list(group) for group in mit.consecutive_groups(it)]
    # Turn the ranges back into start/stop dates
    bounds = [[start + timedelta(days=c[0]),start + timedelta(days=c[1])] for c in continuous]
    
    return (phrase_id, bounds)