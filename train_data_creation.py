import sqlite3
import pandas as pd

database_list = ['2009-09'] #provide the name of databases

for database in database_list:
    connection = sqlite3.connect('{}.db'.format(database))
    c  = connection.cursor()
    limit = 5000          # number of rows to pull at a time from database
    last_unix = 0
    rows_pulled = limit
    counter = 0
    while rows_pulled == limit:
        data = pd.read_sql("select * from reddit_data_table where unix > {} and parent not null and score >0 order by unix asc limit {}".format(last_unix,limit),connection)
        last_unix = data.tail(1)['unix'].values[0]
        rows_pulled = len(data)
        with open("train_data_context.from",'a',encoding = 'utf8') as f:
            for text in data['parent'].values:
                f.write(text + '\n')
        with open("train_data_reply.to",'a',encoding = 'utf8') as f:
            for text in data['comment'].values:
                f.write(text + '\n')
        counter +=1
    print(counter*limit,'rows processed from',database)
