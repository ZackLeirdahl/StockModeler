import schedule, time
from multiprocessing import Queue
from consumer import Consumer
from generator import TaskGenerator

def populate_queue(q, task):
    q.put(task)

def populate_schedule(q, task_type, test=False):
    for task in TaskGenerator().get_tasks(task_type, test=test):
        for runtime in task['runtimes']:
            schedule.every().day.at(runtime).do(populate_queue, q, task['task'])

if __name__ == '__main__':
    process_queue = Queue()
    consumers = [Consumer(process_queue) for i in range(2)]
    populate_schedule(process_queue, 'daily', True)
    print(schedule.jobs)
    while True:
        schedule.run_pending()
        #time.sleep(5)
        

""" TO DO
- create test methods
- add a task_type to update fundamentals data
    - gets symbols from collection: 'company' where nextEarningsDate was yesterday
    - adds task named fundamentals to process_queue
    - checks if new results were added
    - if yes:
        - post blob, update 'company' collection to set new nextEarningsDate
    - if no:
        - kill task
- Firebridege.flush will compare the downloaded file vs. the uploaded file to mark differences and add to artifacts collection
- add artifacts collection
    - key = symbol
    - fields = 
        - uri
            - create_date
            - update_date
            - next_update --> datetime
            - next_purge --> datetime
            - last_purge --> datetime
- create a collection for historical artifact data for artifacts that take up a lot of memory
    - EX: 10 day historical options volume
- add quotes to schedule
    - need to rethink what the purpose is of quotes
"""