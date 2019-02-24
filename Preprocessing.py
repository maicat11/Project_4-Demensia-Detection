import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import nltk

import string
import os
import regex as re
from collections import defaultdict


punct = set(string.punctuation.replace('\\','').replace('|','').replace("'",''))

pos_punct_info = open("data/processed/output_POS.txt", 'a')

#check avg sent size
pos_punct_info.write("book_name|total_words|avg_sentence_size|"
                     + "!|#|\"|%|$|&|(|)|+|*|-|,|/|.|;|:|=|<|?|>|"
                     + "@|[|]|_|^|`|{|}|~|neg|neu|pos|compound|"
                     + "Title|Author|CC|CD|DT|EX|FW|IN|JJ|JJR|JJS|"
                     + "LS|MD|NN|NNP|NNPS|NNS|PDT|PRP|PRP$|RB|RBR|"
                     + "RBS|RP|VB|VBD|VBG|VBP|VBN|WDT|VBZ|WRB|WP$|WP|")
pos_punct_info.write('\n')


def punct_and_words(character_list):
    """
    Iterate through all characters. Count periods, punctuation frequencies.
    word_count = words in sentence (resets to zero after a period).
    total_words is the book's total word count.
    """
    punctuation_dict = defaultdict(int)
    sentence_count = 0
    word_count = 0
    period_count = 0
    avg_sent_size = 0
    total_words = 0
    punct_count = 0

    # sentence count
    for i in range(1, len(character_list)):
        # if letter followed by space or punct, then word count +=1
        if ((character_list[i] == " " or str(character_list[i]) in punct) and
                str(character_list[i - 1]) in string.ascii_letters):
            total_words += 1
        # count periods
        if character_list[i] == ".":
            period_count += 1
        if character_list[i] in punct:
            punct_count += 1
            punctuation_dict[character_list[i]] += 1

    avg_sent_size = (total_words / period_count)
    # put together output, bar delimited
    pos_punct_info.write(str(total_words) + "|")
    pos_punct_info.write(str(avg_sent_size) + "|")

    for p in punct:
        s = ""
        if p in punctuation_dict:
            s = s + str(punctuation_dict[p] / punct_count) + "|"  # ratio of punct that is [x]
        else:
            s = s + str(0) + "|"  # 0 if unused
        pos_punct_info.write(s)


def get_sentiment(temp):
    temp = temp.replace('\n', '')
    temp = temp.replace('\r', '')
    # tokenize sentences
    content = tokenize.sent_tokenize(temp)

    # get author and title now that content is split by sentence
    sid = SentimentIntensityAnalyzer()
    booksent = []
    for sentence in content:
        ss = sid.polarity_scores(sentence)
        ssarray = [ss['neg'], ss['neu'], ss['pos'], ss['compound']]
        booksent.append(ssarray)
    valuearray = np.array(booksent)
    # mean negative, neutral, positive, compound score for all lines in book
    values = np.mean(valuearray, axis=0)
    return values, booksent


def get_author(book_title):
    book_list = {'Agatha Christie': ['AndThenThereWereNone',
                                     'DestinationUnknown',
                                     'ElephantsCanRemember'],
                 'Iris Murdoch': ['TheSandcastle',
                                  'TheBlackPrince',
                                  'JacksonsDilemma'],
                 'P.D. James': ['DevicesAndDesires',
                                'DeathComesToPemberley',
                                'CoverHerFace']
                 }

    for author, books in book_list.items():
        if book_title in books:
            return author


def pos_tagging(content):
    parts = ["CC", "CD", "DT", "EX", "FW", "IN", "JJ",
             "JJR", "JJS", "LS", "MD", "NN", "NNP", "NNPS",
             "NNS", "PDT", "PRP", "PRP$", "RB", "RBR",
             "RBS", "RP", "VB", "VBD", "VBG", "VBP",
             "VBN", "WDT", "VBZ", "WRB", "WP$", "WP"]
    # tokenize first
    text = nltk.word_tokenize(content)
    results = nltk.pos_tag(text)

    # dict of {POS: count}
    results_dict = defaultdict(int)
    counter = 0
    for tag in results:
        token = tag[0]
        pos = tag[1]
        counter += 1
        results_dict[pos] += 1

    # write to file
    for part_of_sp in parts:
        s = ""
        if part_of_sp in results_dict:
            # percent of POS
            s = s + str(results_dict[part_of_sp] / float(counter)) + "|"
        else:
            s = s + str(0) + "|"  # 0 if unused
        pos_punct_info.write(s)


def preprocessing():
    '''
    read file as a list of words
    set lowercase, stem, remove stopwords???
    get punctuation string for later feature extraction
    save local wordcount dict???
    save global word dict after finished looping through docs???
    '''
    for book in os.listdir("data/interim"):
        book_file = str(book)
        book_name = re.sub(r'(James_|Murdoch_|Christie_|\.txt)*', '', book_file)
        title = re.sub("([a-z])([A-Z])", "\g<1> \g<2>", book_name)
        pos_punct_info.write(book_name + "|")

        with open("data/interim/" + book_file, 'r') as f:
            content = f.read().rstrip('\n')

        punct_and_words(content)
        sentiment_values, _ = get_sentiment(content)
        neg = sentiment_values[0]
        neu = sentiment_values[1]
        pos = sentiment_values[2]
        compound = sentiment_values[3]
        pos_punct_info.write(str(neg) + "|"
                             + str(neu) + "|"
                             + str(pos) + "|"
                             + str(compound) + "|")

        title = re.sub("([a-z])([A-Z])", "\g<1> \g<2>", book_name)
        author = get_author(book_name)
        pos_punct_info.write(title + "|" + author + "|")
        pos_tagging(content)
        pos_punct_info.write('\n')
        print(f'Done processing: {title}')
        f.close()
        pos_punct_info.close()