import numpy
import pandas
import random

from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

sw_factory = StopWordRemoverFactory()
# stopwords = sw_factory.get_stop_words()
sw_remover = sw_factory.create_stop_word_remover()

stemmer = StemmerFactory().create_stemmer()
rsp_list = pandas.read_csv("response.csv")
snt_list = pandas.read_csv("sentence.csv")
syn_list = pandas.read_csv("sinonim.csv")



def empty(lists):
  if len(lists) == 0:
    return True

  return False


def add_respon(responses, key):
  # mencari intent yang isinya seperti key pada dataframe lalu jadikan record
  getResponse = rsp_list[rsp_list["Intent"] == key].to_records(index=False)
  # jika getResponse tidak kosong maka tambahkan satu respon
  if not empty(getResponse):
    responses += [ random.choice(getResponse)[1] ]

  return responses


def inside(haystack, needlestack):
  for item in needlestack:
    if item in haystack:
      return True

  return False


def get_similarity_index(lists):
  lens = len(lists)
  list_index = list(range(0, lens))

  for x in range(lens):
    for y in range(lens):
      if lists[list_index[x]] > lists[list_index][y]:
        swap = list_index[x]
        list_index[x] = list_index[y]
        list_index[y] = swap

  return list_index


def synonymize(words):
  sinonim_list = syn_list.to_records(index=False)
  result = words.lower()

  for sinonims in sinonim_list:
    for item in str(sinonims[1]).split(','):
      result = result.replace(item, f"{sinonims[0]} ", 1)    

  return result


def get_covid_info(user_input):
  response = None
  article = open("article.txt", "r")

  paragraph = article.read().split("\n\n\n")
  tokens = [ stemmer.stem(sw_remover.remove(synonymize(token))) for token in paragraph ]

  tokens.append(user_input)
  vectorized = CountVectorizer().fit_transform(tokens)
  similarity = cosine_similarity(vectorized[-1], vectorized)
  similarity_list = similarity.flatten()
  index = get_similarity_index(similarity_list)
  index = index[1:]

  # print(similarity_list)

  for x in range(len(index)):
    if similarity_list[index[x]] > 0.2:
      response = f"{paragraph[index[x]]}\n\n"
      break

  tokens.remove(user_input)

  return [ response ]