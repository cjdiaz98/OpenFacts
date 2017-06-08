# encoding=utf8
import sys

reload(sys)
sys.setdefaultencoding('utf8')

from HTMLParser import HTMLParser
import re

def printProgressBar (iteration, total, prefix = 'Progress: ', suffix = '', decimals = 1, length = 50, fill = '█'):
  percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
  filledLength = int(length * iteration // total)
  bar = fill * filledLength + ' ' * (length - filledLength)
  sys.stdout.write('\r %s |%s| %s%% %s' % (prefix, bar, percent, suffix))
  sys.stdout.flush()
  if iteration == total:
    print()

class Stack(object):
  def __init__(self):
    self.items = []

  def is_empty(self):
    return self.items == []

  def push(self, item):
    self.items.append(item)

  def pop(self):
    return self.items.pop()

  def pop_quiet(self):
    del self.items[-1]

  def peek(self):
    return self.items[-1]

  def clear(self):
    self.items == []

  def size(self):
    return len(self.items)

  def count(self, item):
    return self.items.count(item)

  def __repr__(self):
    return str(self.items)

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  reverse = dict((value, key) for key, value in enums.iteritems())
  enums['to_string'] = reverse
  return type('Enum', (), enums)

NodeType = enum('BOOK', 'UNIT', 'CHAPTER', 'PAGE', 'SECTION', 'ABSTRACT', 'FEATURE', 'TEXT', 'IMG')
node_type_assign = {
  'img' : NodeType.IMG,
  'note' : NodeType.FEATURE,
  'abstract' : NodeType.ABSTRACT,
  'section' : NodeType.SECTION,
  'page' : NodeType.PAGE,
  'chapter' : NodeType.CHAPTER,
  'unit' : NodeType.UNIT
}

class BookTreeNode(object):
  # count = 0

  def __init__(self, parent, sibling_prev, node_type, cargo):
    self.parent = parent
    self.children = []
    self.sibling_prev = sibling_prev
    self.sibling_next = None
    self.node_type = node_type
    self.cargo = cargo

    # BookTreeNode.count += 1

    if parent is not None:
      parent.add_child(self)
    self.sibling_prev = sibling_prev
    if sibling_prev is not None:
      sibling_prev.sibling_next = self

  def add_child(self, child):
    self.children.append(child)

  def rm_child(self, child):
    self.children.remove(child)
    # BookTreeNode.count -= 1

  def print_as_root(self, level=0):
    if self.node_type != NodeType.TEXT:
      print "#",
      for _ in range(level):
        print "|",
      print self
      for child in self.children:
        child.print_as_root(level + 1)

  def __repr__(self):
    return "<BOOK_NODE node_type=" + NodeType.to_string[self.node_type] + " cargo=" + str(self.cargo) + ">"

class BookTree(object):
  def __init__(self, root):
    self.root = root

  def get_nodes(self):
    nodes = []
    node = self.root
    nodes.append(node)
    for child in node.children:
      self._get_nodes_append(nodes, child)
    return nodes

  def _get_nodes_append(self, nodes, node):
    nodes.append(node)
    for child in node.children:
      self._get_nodes_append(nodes, child)

  def __iter__(self):
    return iter(self.get_nodes())

  def size(self):
    return len(self.get_nodes())

class BookTermParser(HTMLParser):
  def __init__(self, file_lines):
    HTMLParser.__init__(self)
    self.terms = []
    self.file_lines = file_lines
    self.open_term = False
    self.buffer = ''

  def handle_starttag(self, tag, attrs):
    if tag == 'dt':
      self.open_term = True
  def handle_endtag(self, tag):
    if tag == 'dt':
      term_text = self.buffer
      # Don't add duplicates
      if term_text not in self.terms:
        self.terms.append(term_text)
      self.buffer = ''
      self.open_term = False
      # Show progress
      printProgressBar(self.getpos()[0], self.file_lines)

  def handle_data(self, data):
    if self.open_term and not data.isspace() and data is not None:
      self.buffer += data


class BookTreeParser(HTMLParser):
  # TODO: Instead of a group of connected nodes, form a tree object with actual properties and methods
  def __init__(self, file_lines):
    HTMLParser.__init__(self)
    self.full_parent_level = 0
    self.relevant_levels = [0]
    self.tree_parent_stack = Stack()
    self.titling = False
    self.within_metadata = False
    self.last_sibling = None

    #for progress tracking
    self.file_lines = file_lines

    book_root = BookTreeNode(None, None, NodeType.BOOK, None)
    self.root = book_root
    self.tree_parent_stack.push(book_root)

  def handle_starttag(self, tag, attrs):
    self.full_parent_level += 1
    if not self.within_metadata:
      if tag in ('div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'section', 'img', 'nav'):
        if tag == 'section':
          attrs.append(('data-type', 'section'))
        elif tag == 'nav':
          self.within_metadata = True
          self.relevant_levels.append(self.full_parent_level)
        for attr_pair in attrs:
          if attr_pair[0] == 'data-type':
            data_type = attr_pair[1]
            if data_type == 'metadata':
              self.within_metadata = True
              self.relevant_levels.append(self.full_parent_level)
            elif data_type in node_type_assign:

              # Just in case
              self.titling = False

              self.relevant_levels.append(self.full_parent_level)
              node_type = node_type_assign[data_type]
              opened_node = BookTreeNode(self.tree_parent_stack.peek(), self.last_sibling, node_type, None)
              self.tree_parent_stack.push(opened_node)

              # Show progress
              printProgressBar(self.getpos()[0], self.file_lines)

              if self.last_sibling is not None and self.last_sibling.node_type == NodeType.TEXT:
                common_parent = self.last_sibling.parent
                sentences = re.findall('[^?.]*?[.?]', self.last_sibling.cargo)
                prev_it_sibling = self.last_sibling.sibling_prev
                for nth_sent in sentences:
                  current_sentence = BookTreeNode(common_parent, prev_it_sibling, NodeType.TEXT, nth_sent)
                  prev_it_sibling = current_sentence
                common_parent.rm_child(self.last_sibling)

              self.last_sibling = None
            elif data_type in ('document-title', 'title'):
              self.titling = True
      elif tag == 'title':
        self.titling = True


  def handle_endtag(self, tag):
    if self.full_parent_level == self.relevant_levels[-1]:
      if self.within_metadata:
        self.within_metadata = False
      else:
        if self.last_sibling is not None and self.last_sibling.node_type == NodeType.TEXT:
          common_parent = self.last_sibling.parent
          sentences = re.findall('[^?.]*?[.?]', self.last_sibling.cargo)
          prev_it_sibling = self.last_sibling.sibling_prev
          for nth_sent in sentences:
            current_sentence = BookTreeNode(common_parent, prev_it_sibling, NodeType.TEXT, nth_sent)
            prev_it_sibling = current_sentence
          common_parent.rm_child(self.last_sibling)
        self.last_sibling = self.tree_parent_stack.pop()
      del self.relevant_levels[-1]
    self.full_parent_level -= 1

  def handle_startendtag(self, tag, attrs):
    if tag == 'img':

      if self.last_sibling is not None and self.last_sibling.node_type == NodeType.TEXT:
        common_parent = self.last_sibling.parent
        sentences = re.findall('[^?.]*?[.?]', self.last_sibling.cargo)
        prev_it_sibling = self.last_sibling.sibling_prev
        for nth_sent in sentences:
          current_sentence = BookTreeNode(common_parent, prev_it_sibling, NodeType.TEXT, nth_sent)
          prev_it_sibling = current_sentence
        common_parent.rm_child(self.last_sibling)

      # Just in case
      self.titling = False
      img_node = None
      for attr_pair in attrs:
        if attr_pair[0] == 'src':
          img_src = attr_pair[1]
          img_node = BookTreeNode(self.tree_parent_stack.peek(), self.last_sibling, NodeType.IMG, img_src)
          self.last_sibling = img_node
      if img_node is not None:
        for attr_pair in attrs:
          if attr_pair[0] == 'alt':
            img_alt = attr_pair[1]
            # Seperate image alt text into sentences...
            # Not sure if this is entirely necessary
            sentences = re.findall('[^?.]*?[.?]', img_alt)
            prev_it_sibling = None
            for nth_sent in sentences:
              current_sentence = BookTreeNode(img_node, prev_it_sibling, NodeType.TEXT, nth_sent)
              prev_it_sibling = current_sentence
      else:
        print "Warning: Image is without a source!"

  def handle_data(self, data):
    if not self.within_metadata:
      if not data.isspace():
        text = re.sub( '\s+', ' ', data)
        parent = self.tree_parent_stack.peek()
        if self.titling:
          if parent.cargo is None:
            parent.cargo = text
            self.titling = False
        else:
          if self.last_sibling is not None and self.last_sibling.node_type == NodeType.TEXT and parent.node_type != NodeType.ABSTRACT:
            self.last_sibling.cargo += text
          else:
            current_node = BookTreeNode(parent, self.last_sibling, NodeType.TEXT, text)
            self.last_sibling = current_node

            # Show progress
            # printProgressBar(self.getpos()[0], self.file_lines)
  
  def handle_entityref(self, data):
    # TODO: Convert to unicode and append into surrounding text
    # Note: Converting to unicode seems to slow everything down...?
    # self.handle_data(self.unescape('&'+data+';'))
    # self.handle_data('&'+data+';')
    pass

  def handle_charref(self, name):
    pass
  def handle_comment(self, data):
    pass
  def handle_decl(self, decl):
    pass
  def unknown_decl(self,data):
    pass
  def handle_pi(self, data):
    pass

def print_help():
  usage_help = "Usage: python BookTreeParser.py -help"
  usage = "Usage: python BookTreeParser.py [-p] file_name [search_term]"
  print usage
  print usage_help

# Just copy-pasted, we may want different colors for testing and whatnot
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

args = sys.argv

flag_print_tree = False
if '-p' in args:
  flag_print_tree = True
  args.remove('-p')

flag_print_terms = False
if '-t' in args:
  flag_print_terms = True
  args.remove('-t')

flag_search_tree = False
for x in range(len(args)):
  if args[x] == '-s':
    flag_search_tree = True
    search_term = args[x + 1]
    del args[x]
    del args[x]
    break

flag_help = False
if '-help' in args:
  flag_help = True
  args.remove('-help')


if flag_help or len(args) != 2:
  print_help()
else:
  file_name = sys.argv[1]

  with open(file_name) as xhtml_lines:
    num_lines = sum(1 for line in xhtml_lines)

  print "Searching for terms in " + file_name + "..."
  term_parser = BookTermParser(num_lines)
  with open(file_name) as xhtml_terms:
    term_parser.feed(xhtml_terms.read())
  terms = term_parser.terms
  printProgressBar(term_parser.file_lines, term_parser.file_lines)
  

  print "Parsing " + file_name + " into a tree..."
  tree_parser = BookTreeParser(num_lines)
  with open(file_name) as xhtml_tree:
    tree_parser.feed(xhtml_tree.read())
  printProgressBar(tree_parser.file_lines, tree_parser.file_lines)

  tree = BookTree(tree_parser.root)
  tree_nodes = tree.get_nodes()
  num_nodes = len(tree_nodes)
  # print BookTreeNode.count

  # Search a single value
  # if flag_search_tree:
  #   for node in tree:
  #     text = node.cargo
  #     if text is not None:
  #       if search_term in text :
  #         print node.__repr__().replace(search_term, bcolors.OKGREEN + search_term + bcolors.ENDC)
  # print tree.size()

  print "Finding terms in tree..."
  term_sentences = {term : [] for term in terms}
  for x in range(num_nodes):
    node = tree_nodes[x]
    text = node.cargo
    if text is not None:
      text = text.lower()
      for term in terms:
        if term in text:
          term_sentences[term].append(node)
    printProgressBar(x, num_nodes)  
  printProgressBar(num_nodes, num_nodes)

  if flag_search_tree:
    appearances = term_sentences[search_term]
    for node in appearances:
      print re.sub('('+search_term+')', bcolors.OKGREEN+r'\1'+bcolors.ENDC, node.__repr__(), flags=re.I)

  if flag_print_terms:
    print terms

  if flag_print_tree:
    tree.root.print_as_root()

  print "DONE"
