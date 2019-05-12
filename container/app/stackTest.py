from stackapi import StackAPI
from pprint import pprint
from lxml import html
from lxml.etree import HTMLParser

whitespace_parser = HTMLParser(remove_blank_text=True)

stackOverflowConnection = StackAPI('stackoverflow')

stackOverflowSearch = stackOverflowConnection.fetch(
    'search/excerpts', q="", tagged="python", sort='votes', accepted=True, page=1, pagesize=2)

questionID = [items['question_id']
              for items in stackOverflowSearch['items']][0:10]

returnedAnswers = stackOverflowConnection.fetch(
    'questions/{ids}/answers', ids=questionID, sort='votes')

answerID = [items['answer_id'] for items in returnedAnswers['items']][0:20]

answers = stackOverflowConnection.fetch(
    'answers/{ids}', ids=answerID, sort='votes', filter="withbody")

answers = []
for answer in answers['items']:
    answers.append({accepted: answer['is_accepted'], votes: answer['score'],
                    author: answer['owner']['display_name'], source: "stackoverflow",
                    url: "https://stackoverflow.com/a/{}/{}".format(answer['answer_id'], answer['owner']['user_id'])})
