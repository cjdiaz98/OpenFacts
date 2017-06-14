# encoding=utf8
import sys

reload(sys)
sys.setdefaultencoding('utf8')

from HTMLParser import HTMLParser
import re
import termrelate
import progbar

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

# Need support for figures
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
  def __init__(self, parent, sibling_prev, node_type, cargo):
    self.parent = parent
    self.children = []
    self.sibling_prev = sibling_prev
    self.sibling_next = None
    self.node_type = node_type
    self.cargo = cargo
    
    # A position is not received until a tree containing the BookTreeNode is iterated over
    # Can't do it on first walk because of how text nodes are grouped
    # Might lead to some unexpected behavior but... oh well
    self.position = -1

    if parent is not None:
      parent.add_child(self)
    self.sibling_prev = sibling_prev
    if sibling_prev is not None:
      sibling_prev.sibling_next = self

  def add_child(self, child):
    self.children.append(child)

  def rm_child(self, child):
    self.children.remove(child)

  def print_as_root(self, level=0):
    # This method is really only useful for grepping
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
    node_list = []
    node = self.root
    node_list.append(node)
    pos_count = [0]
    pos_count[0] += 1
    node.position = pos_count[0]
    for child in node.children:
      self._get_nodes_append(node_list, child, pos_count)
    return node_list

  def _get_nodes_append(self, node_list, node, pos_count):
    node_list.append(node)
    pos_count[0] += 1
    node.position = pos_count[0]
    for child in node.children:
      self._get_nodes_append(node_list, child, pos_count)

  def __iter__(self):
    return iter(self.get_nodes())

  def __len__(self):
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
      progbar.print_bar(self.getpos()[0], self.file_lines)

  def handle_data(self, data):
    if self.open_term and not data.isspace() and data is not None:
      self.buffer += data


class BookTreeParser(HTMLParser):
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

              # Resolve previous sentences first before adding current object to the tree for ordering purposes
              if self.last_sibling is not None and self.last_sibling.node_type == NodeType.TEXT:
                common_parent = self.last_sibling.parent
                sentences = re.findall('[^?.]*?[.?]', self.last_sibling.cargo)
                prev_it_sibling = self.last_sibling.sibling_prev
                for nth_sent in sentences:
                  current_sentence = BookTreeNode(common_parent, prev_it_sibling, NodeType.TEXT, nth_sent)
                  prev_it_sibling = current_sentence
                common_parent.rm_child(self.last_sibling)

              self.relevant_levels.append(self.full_parent_level)
              node_type = node_type_assign[data_type]
              opened_node = BookTreeNode(self.tree_parent_stack.peek(), self.last_sibling, node_type, None)
              self.tree_parent_stack.push(opened_node)

              # Show progress
              progbar.print_bar(self.getpos()[0], self.file_lines)

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
    # TODO: Include figcaption in img branches of tree
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
            # progbar.print_bar(self.getpos()[0], self.file_lines)
  
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

def find_book_terms(file_name):
  with open(file_name) as xhtml_lines:
    num_lines = sum(1 for line in xhtml_lines)

  print "Searching for terms in " + file_name + "..."
  term_parser = BookTermParser(num_lines)
  with open(file_name) as xhtml_terms:
    term_parser.feed(xhtml_terms.read())
  progbar.print_bar(term_parser.file_lines, term_parser.file_lines)
  return term_parser.terms

def parse_into_tree(file_name):
  with open(file_name) as xhtml_lines:
    num_lines = sum(1 for line in xhtml_lines)
  
  print "Parsing " + file_name + " into a tree..."
  tree_parser = BookTreeParser(num_lines)
  with open(file_name) as xhtml_tree:
    tree_parser.feed(xhtml_tree.read())
  progbar.print_bar(tree_parser.file_lines, tree_parser.file_lines)

  return BookTree(tree_parser.root)

def find_terms_in_tree(terms, tree):
  num_nodes = len(tree)
  num_terms = len(terms)

  print "Finding terms in tree..."
  term_nodes = {term : [] for term in terms}
  for node in tree:
    text = node.cargo
    if text is not None:
      text = text.lower()
      for term in terms:
        if term in text:
          term_nodes[term].append(node)
    progbar.print_bar(node.position, num_nodes)
  return term_nodes

# Usage Example
def parse_book_file(file_name, search_term=None, flag_print_tree=False, flag_print_terms=False):

  terms = find_book_terms(file_name)
  tree = parse_into_tree(file_name)

  term_nodes = find_terms_in_tree(terms, tree)

  num_nodes = len(tree)
  num_terms = len(terms)

  if search_term is not None:
    if search_term in terms:
      term_locs = []
      appearances = term_nodes[search_term]
      for node in appearances:
        print re.sub('('+search_term+')', bcolors.OKGREEN+r'\1'+bcolors.ENDC, node.__repr__(), flags=re.I)
        term_locs.append(float(node.position)/num_nodes)
      histo = termrelate.pdf_hist(term_locs, 10)
      # print term_locs
      termrelate.graph_hist(histo)
    else:
      for node in tree:
        text = node.cargo
        if text is not None:
          if search_term in text:
            print re.sub('('+search_term+')', bcolors.OKGREEN+r'\1'+bcolors.ENDC, node.__repr__(), flags=re.I)
      print "\'" + search_term + "\' is not a glossary term, but returned the above results!"

  if flag_print_terms:
    print terms

  if flag_print_tree:
    tree.root.print_as_root()

  print "DONE"
