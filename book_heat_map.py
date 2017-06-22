# MAYBE SOME KIND OF STANDARD DEVIATION TYPE THING?
# use find_terms_in_tree() to get the locations of term nodes


from bookparse import *
# from statistics import stdev
from collections import defaultdict
from random import choice

# QUESTIONS:
# NODE TYPE ISN'T GIVING ME ACTUAL TYPES --> IT'S GIVING ME NUMBERS!
# I THINK THIS IS SCREWING MY FUNCTIONS UP!
# CHECK LOCATE_SECTIONS


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
    if node.node_type == NodeType.SECTION:
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
    to the nodes in which the word appears

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

    term_node_appearances = find_terms_in_tree(terms,tree)
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

def get_sentences_per_sections(original_heat,sorted_heat,max_sent,max_num_sect,percent_sections=None):
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

            # print 'term',term
            ### SEE IF YOU CAN CHANGE THIS TO TAKE A PERCENTAGE OF SENTENCES FOR THE MORE POPULAR TERMS
            mentions,sections = zip(*sorted_heat[term][0:term_num_sect]) # unzips lists containing mentions and section
            # print 'mentions',mentions
            # print 'sections',sections
            total_mentions = sum(mentions) # number times word mentioned within sample that we're given
            term_num_sentences = max_sent
            if total_mentions < max_sent:
               term_num_sentences = total_mentions # if we don't have enough mentions here to even meet the given
                                                 # quota max_sent, then we lower the quota

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

def build_sentences(original_heat,max_sent,max_sections):
    """
    CALLS:
    sort_heat_map()
    get_sentences_per_sections()

    Experiment: sees
    :param original_heat: original heat map
    :param max_sent: number of sentences that we want to use in summarization.
                Actually number may be less depending on how many sentences are actually available
    :param max_num_sect: number of sections that'll be considered as the pool of
                        text we can draw from. May be less depending on number of section available
    :return:
    Dictionary with each term mapped to a body of text that was built on the basis of the
    number of mentions per section
    """
    heat_map_sorted = sort_heat_map(original_heat)
    term_sentence_per_section = get_sentences_per_sections(original_heat,heat_map_sorted,
                                                           max_sent,max_sections)
    summary_dict = {}
    for term in term_sentence_per_section:
        term_summary = '' # you'll be adding to this
        for section in term_sentence_per_section[term]:
            section_nodes = list(original_heat[term][section]) # gets all the relevant nodes in that section
            for i in range(term_sentence_per_section[term][section]):
                rand_node = choice(section_nodes)
                section_nodes.remove(rand_node) # remove node from sample
                term_summary += rand_node.cargo + ' '
        summary_dict[term] = term_summary
    return summary_dict


max_sent = 10
max_sections = 6
bio_tree = parse_into_tree('biology_raw.xhtml')
# bio_terms = ['biome','anaerobic','respiration',
#                                 'lipids','biomass','fungi','apoptosis']

bio_terms2 = ['anaerobic', 'renal capsule', 'diabetes insipidus', 'Apoda',
              'transitional epithelia', 'follicle stimulating hormone (FSH)',
              'septa', 'loam', 'lipid', 'capillary', 'progesterone', 'testes',
              'hypothyroidism', 'beta cell', 'compliance']

#
# original_heat = build_heat_map(bio_terms2,bio_tree)
# sorted_heat = sort_heat_map(original_heat)
# sent_dict = build_sentences(original_heat,max_sent,max_sections)




####################################################################################
# WAYS THIS CODE CAN BE CHANGED:
# -Instead of feeding in a number of sections and sentences, you can merely just
# have it decide based on the number available
# -Don't randomly select sentences from within build_sentences()
# -Only allow build_heat_map to take nodes of a particular type, or fitting particular criteria
# -Introduce new measures (as shown below), like mention density, or standard deviation to
# expand the culling down process


####################################################################################
# sort_by_mention(
# IDEAS:
# Use variance somewhere. Maybe relative to something else, you can use it to determine the difference
# in mentions between different sections --> the higher this measure, the more you discriminate towards certain
# sections

# mention density --> take the section with the top mentions. Add up the distance from this section of th
# the next ten or so sections. Divide by total sections. The smaller this number is, the more dense it is



def section_density(sorted_heat_map,num_sections_per):
    """
    :param sorted_heat_map:
    :param num_sections_per:
    :return:
    Takes designate n first sections, calculates how far from most populated section they all
    are and divides the sum of their distances by the number of sections total
    """
    term_section_density = {}
    for term in sorted_heat_map:
        sections_total = len(sorted_heat_map[term])
        relevant_sections = sorted_heat_map[term][:num_sections_per]
        dist_from_first_section = 0
        for i in range(len(relevant_sections)):
            dist_from_first_section += abs(relevant_sections[0][1]-relevant_sections[i][1])
        term_section_density[term] = len(dist_from_first_section / sections_total)
    return term_section_density


# OR..
# Take standard deviation. Go through each of the sections and tally how many mentions of the
# word were made
# Then where
# S = no. of mentions in that section,
# x = no. of standard deviation
# Avg = avg mentions
# if S - Avg < -x stdev then it doesn't make it'
