import MySQLdb as mysql
from faker import Faker
from random import choice, randint
import json



db = mysql.connect(host="localhost",user="root",
                  passwd="toor",db="codesnippets", port=3306)


fk = Faker()


items = []

for x in range(10):
    title = fk.name()
    tags = "python"
    votes = randint(1, 1000)
    answer_num = randint(1, 1000)
    answered = choice([0, 1])
    source = choice(["codesnippets", "stackoverflow"])
    author = fk.name()
    url = ""
    items.append([title, tags, votes, answer_num, answered, source, url])

# # Adding col query
query = "INSERT INTO questions (title, tags, votes, answers_num, answered, source, url) VALUES (%s, %s, %s, %s, %s, %s, %s)"

db.commit()

with db.cursor() as cur:
    cur.execute("TRUNCATE TABLE questions")
    cur.executemany(query, items)


db.commit()
