# Installation
- Clone or copy this repo in the directory of your choosing
- Download an raw HTML CTE book and put it in the same directory
- Done!

# How to use
- Open either a python file or a python shell in the same directory
- Write `import bookparse`
- Now the functions in bookparse are available to use!

# Functions
- `find_book_terms(book_file)`
  - Finds all glossary terms in the given html file
  - Input: 
    - `book_file`: the string of the full path to the book file, including the extension (e.g. 'biology.xhtml')
  - Output:
    - A list of all the glossary terms as strings
- `parse_into_tree(file_name)`
  - Parses the given book file into a simplified tree of nodes
  - Input: 
    - `book_file`: the string of the full path to the book file, including the extension (e.g. 'biology.xhtml')
  - Output: 
    - A BookTree object (a tree data structure) consisting of BookTreeNode objects
- `find_terms_in_tree(terms, tree)`
  - Searches for a list of terms inside a BookTree
  - Input:
    - `terms`: a list of string search terms
    - `tree`: a BookTree object
  - Output:
    - A dict representing the appearances of each term in the book
      - keys: each string in `terms` will be a key of the returned dict
      - values: a list of BookTreeNodes that the key is found in
- `parse_book_file(file_name, [search_term], [flag_print_tree], [flag_print_terms])`
  - Example of the usage of the above functions
  - Serves no actual practical purpose other than demonstration
  - Takes a book file and parses into a tree, then displays all appearances of an optional search term and a histogram of its frequency throughtout the book
  - Input:
    - `book_file`: the string of the full path to the book file, including the extension (e.g. 'biology.xhtml')
    - `search_term`: a single term to search the tree for. Can be a glossary term or just an arbitrary string
    - `flag_print_tree`: whether or not to print the full parsed tree. Great for grepping!
    - `flag_print_terms`: whether or not to print a list of all terms found in the tree

# Objects
  - `BookTreeNode`
    - Properties
      - parent (BookTreeNode): the parent node
      - children ([BookTreeNode]): a list of all children nodes
      - sibling_next (BookTreeNode): the node's preceding sibling
      - sibling_prev (BookTreeNode): the node's postceding sibling
      - node_type (NodeType): the type of node
      - cargo (string): a string associated with a node
      - position (int): the node's position in the tree (e.g. node 10 in a tree of size 20)
    - Methods
      - `add_child(node)`: 
        - Input: (BookTreeNode) the node to be added as a child to the node
      - `rm_child(node)`: 
        - Input: (BookTreeNode) the node to be removed from the nodes list of children
      - `print_as_root()`:
        - Prints the tree as if the current node were root
    - Types of Nodes:
      - 'BOOK': Reserved for the root node of the tree
        - cargo: the title of the book
        - children: pages, units, chapters
      - 'UNIT': A unit of the book
        - cargo: the title of the unit
      - 'CHAPTER': A chapter of the book
        - cargo: the title of the chapter
      - 'PAGE': A page/module of the book (e.g. Preface, Appendix, Section 1.3, etc...)
        - cargo: the title of the page/module
      - 'SECTION': A section of the book
        - cargo: the title of the section
      - 'ABSTRACT': The learning objectives of a chapter or module
        - cargo: empty
      - 'FEATURE': A feature of the book (e.g. Collaborative Activity, Lab, etc...)
        - cargo: empty
      - 'TEXT': A sentence in the book
        - cargo: the sentence
        - children: none
      - 'IMG': An image in the book
        - cargo: the partial url to the image
        - children: text nodes representing the alt-text of the image and the caption of the image
  - `BookTree`
    - Iterable
      - Example: `for nodes in tree` will loop through all nodes in the tree
    - Size
      - Example: `len(tree)` returns the number of nodes in the tree
    - Properties
      - root (BookTreeNode): the root node of the tree
    - Methods
      - `get_nodes()` 
        - Output: ([BookTreeNode]) list of all nodes in the tree
