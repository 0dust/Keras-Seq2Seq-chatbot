import sqlite3
import json
from datetime import datetime

time_period = '2009-09' # the data being used is from september 2009.
global transaction = []

connection = sqlite3.connect('{}.db'.format(time_period))
c = connection.cursor()


# database table creation
def create_table():
    c.execute(
        """CREATE TABLE IF NOT EXISTS reddit_database(parent_id TEXT PRIMARY KEY,
    comment_id TEXT UNIQUE,
    parent TEXT,
    comment TEXT,
    subreddit TEXT,
    unix INT,
    score INT)"""
    )
    
  

# replace newlines with some other string 
def format_data(data):
    data = data.replace("\n"," newlinechar ")
    data = data.replace("\r"," newlinechar ")
    data = data.replace('"',"'")
    return data



#return score of the entry with  parent_id = pid
def find_existing_score(pid):
    try:
        sql = "SELECT score from reddit_database where parent_id = '{}' limit 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else:
            return False
    except Exception as e:
        return False
 


#collect the queries and executes them together when number of total queries exceed 2000.
#any number can be set,bigger number speeds up the entry.
def transactions_in_bulk(sql):
    transaction.append(sql)      #append the query in list
    if len(transaction)>2000:
        c.execute('BEGIN TRANSACTION')
        for s in transaction:
            try:
                c.execute(s)
            except:
                pass
        connection.commit()          #save the changes in database
        transaction = []            #empty the list to store further
 



def sql_insert_replace_comment(commentid,parentid,parent,comment,subreddit,time,score):
    try:
        sql = """update reddit_database set parent_id = ?, comment_id= ?,parent = ?,
        comment = ?,subreddit = ?,unix=?,score=? where
        parent_id = ?; """.format(parentid,commentid,parent,comment,subreddit,int(time),score,parentid)
        
        transactions_in_bulk(sql)
       
    except Exception as e:
        print('update insertion',str(e))
  



def sql_insert_has_parent(commentid,parentid,parent,comment,subreddit,time,score):
    try:
        sql = """insert into parent_reply (parent_id, comment_id,parent,
        comment,subreddit,unix,score) values
        ("{}","{}","{}","{}","{}",{},{}); """.format(parentid,commentid,parent,comment,subreddit,int(time),score)
        transactions_in_bulk(sql)
    except Exception as e:
        print('parent insertion',str(e))
 



def sql_insert_no_parent(commentid,parentid,comment,subreddit,time,score):
    try:
        sql = """insert into parent_reply (parent_id, comment_id,
        comment,subreddit,unix,score) values
        ("{}","{}","{}","{}",{},{}); """.format(parentid,commentid,comment,subreddit,int(time),score)
        transactions_in_bulk(sql)
       
    except Exception as e:
        print('noparent insertion',str(e))        
 



#check data being entered in database for length specifications.        
def acceptable(data):
    if len(data.split(' '))>50 or len(data)<1:
        return False
    elif len(data) >1000:
        return False
    elif data == '[deleted]' or data == '[removed]':
        return False
    else:
        return True
  



#return comment whose comment id is pid, 
#the comment being returned is parent of another comment(child comment) 
#hence its comment_id = parent_id of child comment.         
def find_parent(pid):
    try:
        sql = "SELECT comment FROM reddit_database WHERE comment_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else:
            return False
    except Exception as e:
        return False
   




if __name__ == "__main__":
    create_table()
    row_count = 0                 #count number of rows read.
    paired_rows_count = 0          #count number of comments which got their parent from database using find_parent.
    
    with open("projects/RC_2009/RC_2009",buffering = 1000) as f:

        for row in f:

            row = json.loads(row)
            row_count += 1
            parent_id = row['parent_id']
            body = format_data(row['body'])
            created_utc = row['created_utc']
            score = row['score']
            subreddit = row['subreddit']
            comment_id = row['name']
            parent_data = find_parent(parent_id)

            if score>=3:                #set score depending on choice

                if acceptable(body):         #checking body to be of suitable length
                    existing_comment_score = find_existing_score(parent_id)

                    if existing_comment_score:
                        if score> existing_comment_score:
                           #comment with low score replaced by comment with higher score. 
                            sql_insert_replace_comment(comment_id,parent_id,parent_data,body,subreddit,created_utc,score)

                    else:
                        if parent_data:

                            sql_insert_has_parent(comment_id,parent_id,parent_data,body,subreddit,created_utc,score)
                            paired_rows_count +=1
                        else:
                            #comment without parent is inserted because it may be a parent of some other comment 
                            #find_parent will associate it with its child if it encounters one.
                            sql_insert_no_parent(comment_id,parent_id,body,subreddit,created_utc,score)

            #print the log after every 1000 rows.
            if row_count % 1000 ==0:
                print("total rows read : {}, paired rows: {},time:{}".format(row_count,paired_rows_count,str(datetime.now())))

