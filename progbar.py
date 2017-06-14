# encoding=utf8

import sys

def print_bar (iteration, total, prefix = 'Progress: ', suffix = '', decimals = 1, length = 30, fill = '█'):
  percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
  filledLength = int(length * iteration // total)
  bar = fill * filledLength + ' ' * (length - filledLength)
  sys.stdout.write('\r %s |%s| %s%% %s' % (prefix, bar, percent, suffix))
  sys.stdout.flush()
  if iteration == total:
    print ""
  