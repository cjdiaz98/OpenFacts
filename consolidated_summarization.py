# from gensim.summarization import keywords
# from gensim.summarization import summarize
# import sentence_vetting
from collections import defaultdict
import nltk
import TreeToList as listGen
import bookparse as parser
import random
from bookparse import parse_into_tree

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim.summarization import summarize


bio_book = "biology_raw.xhtml"
bio_tree = parse_into_tree(bio_book)

######## TreeToList

def pull_sentences(terms, tree):
    """
    Used to be makeFile

    Input: tree --the xhtml book in tree form
           terms --the glossary terms you are searching for (list)

    Output: dictionary where each term is mapped to all of its nodes
    """
	# genereates a list of all glossary terms
	# terms = parser.find_book_terms(book)
	# takes the xhtml tree and simplifies it into a more readible tree
	# tree = parser.parse_into_tree(book)
	# finds all sentences where the term appears in the sentnece
    term_sentences = {}
    for term in terms:
        appearances = []
        for node in tree:

            if node == appearances[-1]:
                continue

            if node.cargo is None:
                continue

            elif term in node.cargo.lower():
                appearances.append(node)

                ### NEW --> ONLY IF WE DECIDE WE WANT TO ADD NEIGHBORS
                # if node.sibling_prev != appearances[-2] and node.sibling_prev != None:
                #     appearances.append(node.sibling_prev)
                #
                # if node != appearances[-1]:
                #     appearances.append(node)
                #
                # if node.sibling_next != None:
                #     appearances.append(node.sibling_next)

        term_sentences[term] = appearances
	return term_sentences


def term_list_sentences(node_dict):
    """
    Input: node_dict -- dictionary where each node is mapped to list of nodes

    Output: dictionary where each term is mapped to list of sentences
    (each sentence in list form)
    """
    sentence_dict = defaultdict(list)
    for term in node_dict:
        for node in node_dict[term]:
            cargo_sentence = node.cargo # remove the punctuation
            sentence_dict[term].append(cargo_sentence.split())
    return sentence_dict


def listToString(sentence_list):
    """
    Takes a list of lists (type str) and converts to a list of strings
    """
    result = []
    for sentence in fileList:
        string = " ".join(sentence)
        result.append(string)
    return result

def run_vetting(terms,tree):
    """
    Helper Functions:
    -pull_sentencese()
    -term_list_sentences()
    -listToString
    -findDefSentences

    Pulls all the sentences relevant to the terms.
    For each term and its sentences, finds the definitional sentences
    and the term is mapped to each

    :param terms: list of terms
    :param tree: book in tree form
    :return:
    """
    node_dict = pull_sentences(terms,tree)
    sentence_dict = term_list_sentences(node_dict)
    def_sentence_dict = {}

    for term in sentence_dict:
        term_string = listToString(sentence_dict[term])
        def_sentences = findDefSentences(term_string,term)
        def_sentence_dict[term] = def_sentences
    return def_sentence_dict


######## SENTENCE VETTING
def findDefSentences(df, key):
    """
    Finds all the useful sentences in a dictionary where the
    keys are the full sentences and values are parsed info
    about the sentences.

    Input--DF: dictionary w/ keys = sentences and values = parsed info about that sentence # PARSED INFO?
            LIST
    	   key: glossary term

    Output--result: list of relevant sentences (each in list form)
    """
    sentences = df
    tagged_sentences = []
    for sent in sentences:
        print(sent)
        token = nltk.word_tokenize(sent)
        print(token)
        sentences.append(nltk.pos_tag_sents(nltk.word_tokenize(sent)))

    # tagged_sentences = nltk.pos_tag_sents(nltk.word_tokenize(sent) for sent in sentences)

    # checks if the key has multiple words
    if len(key.split(' ')) > 1:
        result = set()
        # iterates through each word of the key to find sentences related to it
        for w in key.split(' '):
            tagged = iterTaggedSentences(w, tagged_sentences, sentences)

    else:
        tagged = iterTaggedSentences(key, tagged_sentences, sentences)
    return tagged


def iterTaggedSentences(w, tagged_sentences, sentences):
    """
    Iterates through all tagged sentences and determines if it is considered relevant or not.
    Finds the idx of w and compares to the idx of the first verb. A sentence is relevant if w
    index is before verb index

    Input-- w: the key term, tagged_sentences: a list of parsed and tagged sentences, sentences:
        the original list of sentences that tagged_sentences came from

    Output-- result: a sublist of sentences that were deemed relevant, backup: a testing list
        used in debugging that can be ignored
    """
    result = []
    backup = []
    if len(tagged_sentences) < 7:
        return (sentences, backup)

    # Find relevant sentences
    for s in tagged_sentences:
        # Finds index of verb and key
        vIdx = findVIndex(s)
        nIdx = findNIndex(s, w)
        sIdx = tagged_sentences.index(s)

        '''
        if nIdx != -1 and vIdx != -1 or len(s) < 6:
            result.append(sentences[sIdx])
        elif nIdx != -1 or len(sentences) < 6:
        elif nIdx != -1 or len(s) < 6:
            backup.append(sentences[sIdx])
        print(len(s), len(tagged_sentences), len(sentences))
        '''

        if nIdx != -1:
            result.append(sentences[sIdx])

    return (result, backup)

def findNIndex(sentence,  key):
    """
    Gives a parsed sentence, finds the index of the first key that appears in the sentence.

    Input--sentence: a list of (word, tag) tuples
           key: the term we are trying to find in the sentence

    Output--index: the index of the verb if present (-1 if not present)
    """
    #find the first key word in the sentence
    for word in sentence:
        tag = word[0].lower()
        if tag == key:
            return sentence.index(word)
    return -1

def findVIndex(sentence):
    """
    Gives a parsed sentence, finds the index of the first verb that appears in the sentence.

    Input--sentence: a list of (word, tag) tuples

    Output--index: the index of the verb if present (-1 if not present)
    """
    #find the first VB word in the sentence
    for word in sentence:
        tag = word[1]
        if tag == "VB" or tag == "VBD" or tag == "VBG" or tag == "VBN" or tag == "VBP" or tag == "VBZ":

            return sentence.index(word)

    return -1

def genForTermsList(terms,tree):
    """
    Finds all relevant sentences to a given list of terms. Can be used
    if you want to pick and choose what terms to search
    input:
    terms - list of terms
    tree - book in tree form
    """
    termDict = defaultdict(list)

    for term in terms:
        pull_sentences()
        fileList = listGen.genSentences('output_file.txt')
        sentences = listGen.listToString(fileList)
        importantSentences = findDefSentences(sentences, term)

        termDict[term] += importantSentences[0]



######### HEAT MAPPING SECTION

def locate_sections(tree):
  """
  Makes dictionary where each section number is mapped
  to its position and title
  :param tree: Tree object
  :return:
  Mapping where every section number is mapped to a tuple.
  The tuple carries position of the node and the cargo
  of the node
  """
  num_sections = 0 # section numbers start from 0
  section_locations = {}
  for node in tree:
    if node.node_type == parser.NodeType.SECTION:
     section_locations[num_sections] = [node.position,node.cargo]
     num_sections += 1
  return section_locations

def build_heat_map(terms,tree):
    """
    Inputs:
    -terms, a list of terms that you want a heatmap for (ALL LOWERCASE)
    -tree, of class BookTree

    CALLS:
    find_terms_in_tree
    locate_sections

    Steps:
    -Gets list of nodes in which the term appears
    -For each node, it checks which chapter/section the mention falls in (by looking at its location)
    and adds one tally to that section
    - (optional) add an extra tally or two to a section in which the key word is mentioned
    - In order to keep track of which section we're in, make a while loop that
    re-assigns the current section by checking the location of the node that we're at
    :return:
    -2nd degree mapping. Each word mapped to dictionary. Dictionaries map section
    to a list of nodes in which the word appears

    """
    section_locations = locate_sections(tree)
    all_sections = section_locations.keys()
    section_info = section_locations.values() # contains positions and titles
    # print 'section info',section_info
    # print len(all_sections)

    # take all of the compound terms out of the terms list and put in their constituents
    compound_term_dict = {}
    for term in terms:
        component_terms = term.split()
        if len(component_terms) > 1:
            compound_term_dict[term] = component_terms
            terms.remove(term)
            for sub_term in component_terms:
                terms.append(sub_term)

    term_node_appearances = parser.find_terms_in_tree(terms,tree)
    total_heat = {}

    for compound_term in compound_term_dict:
        term_node_appearances[compound_term] = []
        for sub_term in compound_term_dict[compound_term]:
            term_node_appearances[compound_term] = term_node_appearances[compound_term] \
                                                   + term_node_appearances[sub_term]
            term_node_appearances.pop(sub_term,None)
    # Deal with all compound words by removing their sub terms and
    # adding all mentions to the compound term value

    for term in term_node_appearances:
        curr_section = 0  # pick first section for the current section
        next_section_position = section_info[curr_section + 1][0]  # position where next section starts
        term_heat_map = defaultdict(list)
        for node in term_node_appearances[term]:
            while node.position > next_section_position and curr_section != len(all_sections)-1:
                curr_section += 1
                next_section_position = section_info[curr_section + 1][0]
            # print term,next_section_position,node.position

            term_heat_map[curr_section].append(node)

                # if term in section_info[curr_section][1]:
                    # term_heat_map[curr_section].append(SOMETHING) ### OPTIONAL: ADD EXTRA POINTS FOR MENTION IN SECTION TITLE
            # term_heat_map[curr_section] += 1

        total_heat[term] = term_heat_map
    return total_heat

def sort_heat_map(total_heat):
    """
    :param terms: list of terms that you calculated the heat map for
    :param total_heat: dictionary of dictionaries as returned by the function
    build_heat_map()

    :return:
    A dictionary, where each terms is mapped to a list of lists.
    Each of the inner lists contains (x,section) format where x is the number of mentions
    in the section
    The list is sorted by decreasing number of mentions
    """
    terms = total_heat.keys()
    term_mentions = {}

    for term in terms:
        sections = total_heat[term].keys() # get list of all sections
        num_mentions = []
        for section in sections:
            num_mentions.append(len(total_heat[term][section]))

        section_mention_sorted = zip(num_mentions,sections)
        section_mention_sorted = sorted(section_mention_sorted,reverse = True)
        term_mentions[term] = section_mention_sorted
    return term_mentions

def get_sentences_per_sections(original_heat,sorted_heat,max_sent=None,max_num_sect=None,
                               percent_sect=None,percent_sent=None):
# >>>>>>> b18e81de41ec2c97237ba6177794feb986fbce96
    """
    :param total_heat_map: passed from heat map
    :param sorted_heat: passed from sort_heat_map
    :param max_sent: number of sentences that we want to use in summarization.
                Actually number may be less depending on how many sentences are actually available
    :param max_num_sect: number of sections that'll be considered as the pool of
                        text we can draw from. May be less depending on number of section available
    :param percent_sections: percent of total sections we'll take from each term (not implemented right now)

    :return:
    A dict of dicts: Each term mapped to dictionary. Internal dict
    contains section mapped to number of sentences that'll be
    pulled from that section
    """
    term_sentence_per_sect = {}
    for term in sorted_heat:
        term_num_sect = max_num_sect # so we avoid changing num_sect

        try:
            if len(sorted_heat[term]) < max_num_sect:
                term_num_sect = len(sorted_heat[term])
                # this is only a preliminary deciding method on how many
                # sections to use
            # term_num_sect = round(len(sorted_heat[term]) * percent_sections)

            ### SEE IF YOU CAN CHANGE THIS TO TAKE A PERCENTAGE OF SENTENCES FOR THE MORE POPULAR TERMS
            mentions,sections = zip(*sorted_heat[term][0:term_num_sect]) # unzips lists containing mentions and section
            # print 'mentions',mentions
            # print 'sections',sections
            total_mentions = sum(mentions) # number times word mentioned within sample that we're given
            term_num_sentences = max_sent
            if total_mentions < max_sent:
               term_num_sentences = total_mentions # if we don't have enough mentions here to even meet the given
                                                 # quota max_sent, then we lower the quota
            if percent_sent != None:
                term_num_sentences = round(total_mentions*percent_sent)

            sentence_per_sect = {} # internal dictionary

            for s in range(len(sections)): # here we calculate the share of the total sentences that each section gets
                fraction_total = float(mentions[s] * 1.0 / total_mentions)
                num_sentences = int(round(fraction_total * term_num_sentences)) #round to nearest int
                sentence_per_sect[sections[s]] = num_sentences
                # round down need to have integer number of sentences
            term_sentence_per_sect[term] = sentence_per_sect
        except:
            term_sentence_per_sect[term] = defaultdict(int)
    return term_sentence_per_sect

def which_sect(sorted_heat):
    """
    For term in sorted_heat, determines which sections we're going to end up pulling sentences from.
    Does this by taking the average number of mentions per section, and seeing which
    sections are above average in this

    :param sorted_heat: heated sort map
    :return:
    """
    pull_dict = {}
    for term in sorted_heat:
        pull_sections = []  # sections we're going to pull from
        count = 0
        for section in sorted_heat[term]:
            count += section[0]
        average_mention = float(count/len(sorted_heat[term]))
        for section in sorted_heat[term]:
            if section[0] > average_mention:
                pull_sections.append(section[1])

        pull_dict[term] = pull_sections
    return pull_dict

def heat_map_vetting(tree,bio_terms,max_num_sent,percent_sect=None):
    """
    Similar output to pull sentences, except the nodes are more culled down

    :param tree: book in tree form
    :param bio_terms: list of terms
    :param max_num_sent: maximum number of sentences that we want
    :param percent_sect: percent of the total sections that we want to use
    :return:
    Mapping of terms to a list of all the nodes relevant to that term
    """
    original_heat = build_heat_map(bio_terms, bio_tree)
    sorted_heat = sort_heat_map(original_heat)
    # sentences_per_sect = get_sentences_per_sections(original_heat,sorted_heat,
    #                                                 max_num_sent=max_num_sent,percent_sect=percent_sect)
    relevant_node_dict = defaultdict(list)
    which_sections = which_sect(sorted_heat)

    for term in original_heat:
        for section in which_sections[term]:
            if len(relevant_node_dict[term])>max_num_sent:
                break
            relevant_node_dict[term].extend(original_heat[term][section])

    return relevant_node_dict



def prepare_for_summ(node_dict):
    """
    takes in dictionary where each term is mapped to lsit of nodes

    returns dictionary where each term is mapped to the string of
    concatenated node cargo
    """
    preliminary_dict = {}
    for term in node_dict:
        preliminary_dict[term] = ''

    for term in node_dict:
        for node in node_dict[term]:
            preliminary_dict[term] += ' ' + node.cargo
    return preliminary_dict

def gensim_sum(node_dict):
    pre_summ_dict = prepare_for_summ(node_dict)
    # print 'pre summ dict', pre_summ_dict
    post_summ_dict = {}

    for term in pre_summ_dict:
        print 'THIS TERM',term
        try:
            term_sentences = pre_summ_dict[term].split('.')
            print 'lengthhhh', str(len(term_sentences))
            post_summ_dict[term] = summarize(pre_summ_dict[term])
            post_summ_dict[term] = summarize(post_summ_dict[term])
        except:
            pass
    return post_summ_dict


bio_terms1 = ['biomass','respiration','meiosis']
vetted_nodes = heat_map_vetting(bio_tree, bio_terms1, 100)
print gensim_sum(vetted_nodes)

# print gensim_sum(vetted_nodes)

# test_body = ' A good example of this connection is the exchange of carbon between autotrophs and heterotrophs within and between ecosystems by way of atmospheric carbon dioxide. Heterotrophs and autotrophs are partners in biological carbon exchange (especially the primary consumers, largely herbivores).  Heterotrophs acquire the high-energy carbon compounds from the autotrophs by consuming them, and breaking them down by respiration to obtain cellular energy, such as ATP.  Thus, there is a constant exchange of oxygen and carbon dioxide between the autotrophs (which need the carbon) and the heterotrophs (which need the oxygen).  Other protists are heterotrophic and consume organic materials (such as other organisms) to obtain nutrition.  Amoebas and some other heterotrophic protist species ingest particles by a process called phagocytosis, in which the cell membrane engulfs a food particle and brings it inward, pinching off an intracellular membranous sac, or vesicle, called a food vacuole ([link]). Subtypes of heterotrophs, called saprobes, absorb nutrients from dead organisms or their organic wastes.  Some protists can function as mixotrophs, obtaining nutrition by photoautotrophic or heterotrophic routes, depending on whether sunlight or organic nutrients are available.  All animals require a source of food and are therefore heterotrophic, ingesting other living or dead organisms; this feature distinguishes them from autotrophic organisms, such as most plants, which synthesize their own nutrients through photosynthesis.  As heterotrophs, animals may be carnivores, herbivores, omnivores, or parasites ([link]ab). All animals are heterotrophs that derive energy from food.  Plastids are derived from cyanobacteria that lived inside the cells of an ancestral, aerobic, heterotrophic eukaryote.  In a primary endosymbiotic event, a heterotrophic eukaryote consumed a cyanobacterium.  In the first event, a cyanobacterium was engulfed by a heterotrophic eukaryote.  In contrast, heterotrophic prokaryotes obtain carbon from organic compounds.  Thus, photoautotrophs use energy from sunlight, and carbon from carbon dioxide and water, whereas chemoheterotrophs obtain energy and carbon from an organic chemical source.  Other organisms, such as animals, fungi, and most other bacteria, are termed heterotrophs, because they must rely on the sugars produced by photosynthetic organisms for their energy needs.  Those carbohydrates are the energy source that heterotrophs use to power the synthesis of ATP via respiration.'
# test_body1 = "particular trophic level incorporate the energy they receive into biomass; it is calculated using the following formula. Net consumer productivity is the energy content available to the organisms of the next trophic level.  Assimilation is the biomass (energy content generated per unit area) of the present trop"
test_body2 = "Glycolysis is a metabolic pathway that takes place in the cytosol of cells in all living organisms. This pathway can function with or without the presence of oxygen. In humans, aerobic conditions produce pyruvate and anaerobic conditions produce lactate. In aerobic conditions, the process converts one molecule of glucose into two molecules of pyruvate (pyruvic acid), generating energy in the form of two net molecules of ATP. Four molecules of ATP per glucose are actually produced, however, two are consumed as part of the preparatory phase. The initial phosphorylation of glucose is required to increase the reactivity (decrease its stability) in order for the molecule to be cleaved into two pyruvate molecules by the enzyme aldolase. During the pay-off phase of glycolysis, four phosphate groups are transferred to ADP by substrate-level phosphorylation to make four ATP, and two NADH are produced when the pyruvate are oxidized. The overall reaction can be expressed this way:"
# print 'yoooo', summarize(test_body4)

    ########### IDEAS TO POSSIBLY IMPLEMENT

# Possibly at the end of each node's cargo add a little set of
    # parentheses indicating which section we got each that sentence from
    # for reference by the reader
