# encoding=utf8
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import random

def pdf_hist(locations, buckets):
  pdf = [0]*buckets
  for loc in locations:
    pdf[int(loc*buckets)] += 1.0
  for x in range(buckets):
    pdf[x] /= len(locations)
  return pdf

def pdf_diff(pdf_1, pdf_2):
  buckets = len(pdf_1)
  total = 0.0
  if len(pdf_2) == buckets:
    for x in range(buckets):
      total += abs(pdf_1[x]-pdf_2[x])
  return 1.0 - total/2.0

def graph_hist(hist):
  print '-' * 50
  for val in hist:
    print '|' + '█'*int(50*val)
  print '-' * 50

# list_1 = [0.3, 0.3, 0.2, 0.3]
# list_2 = [0.1, 0.1, 0.2, 0.3, 0.2]
# pdf_1 =  pdf_hist(list_1, 10)
# pdf_2 =  pdf_hist(list_2, 10)

# graph_hist(pdf_1)
# graph_hist(pdf_2)
# print pdf_diff(pdf_1, pdf_2)
