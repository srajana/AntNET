import codecs
import itertools
import preprocess_dataset as preprocess
import numpy as np
np.random.seed(133)


def vectorize_path(path, x, y, lemma_index, pos_index, dep_index, dir_index):
    """
    Return a vector representation of the path
    :param path: the string representation of a path
    :param lemma_index: index to lemma dictionary
    :param pos_index: index to POS dictionary
    :param dep_index: index to dependency label dictionary
    :param dir_index: index to edge direction dictionary
    :return:
    """
    path_edges = []
    edges = path.split('_')
    for edge_index,edge in enumerate(edges):
        path_edges.append(vectorize_edge(edge, x, y, lemma_index , pos_index, dep_index, dir_index, edge_index, len(edges)))

    if None in path_edges:
        return None

    return tuple(path_edges)

def get_morph_mapping(morph_file):
	mapping = {}
	f = open(morph_file, "r")
	for line in f.readlines():
		sent = line.strip("\n")
		word_pair = sent.split("\t")
		mapping[word_pair[0]] = word_pair[1]
	f.close()
	return mapping

def vectorize_edge(edge, x, y, lemma_index, pos_index, dep_index, dir_index, edge_index, len_edges):
    """
    Return a vector representation of the edge: concatenate lemma/pos/dep and add direction symbols
    :param edge: the string representation of an edge
    :param lemma_index: index to lemma dictionary
    :param pos_index: index to POS dictionary
    :param dep_index: index to dependency label dictionary
    :param dir_index: index to edge direction dictionary
    :param edge_index: index of the edge in the path
    :param len_edges: Number of edges in the path
    :return:
    """
    morph_mapping = get_morph_mapping("morph-analyzed-pairs.txt")
    negation_marker = 0
    try:
        lemma_orig, pos, dep, direction = edge.split('/')
        lemma, pos, dep, direction = lemma_index.get(lemma_orig, 0), pos_index[pos], dep_index[dep], dir_index[direction]
    except:
        return None

    if (edge_index == 0):
	negation_marker = 1
        if len(x.split()) > 1:
            if x.split()[0]=="not":
                negation_marker = 2
		base_lemma = x.split()[1]
		lemma = lemma_index.get(base_lemma, 0)
        else:
	    if x in morph_mapping.keys():
		if morph_mapping[x] != x:
			negation_marker = 2
			base_lemma = morph_mapping[x]
			lemma = lemma_index.get(base_lemma, 0)
            else:
		if x.startswith('in') or x.startswith('un') or x.startswith('de') or x.startswith('im'):
                	negation_marker = 2
			base_lemma = x[2:]	
			lemma = lemma_index.get(base_lemma, 0)
            	elif x.startswith('anti') or x.startswith('non') or x.startswith('dis'):
                	negation_marker = 2
			base_lemma = x[3:]
			lemma = lemma_index.get(base_lemma, 0)
    elif (edge_index == len_edges -1):
	negation_marker = 1
        if len(y.split()) > 1:
            if y.split()[0]=="not":
                negation_marker = 2
		base_lemma = y.split()[1]
		lemma = lemma_index.get(base_lemma, 0)
        else:
	    if (y in morph_mapping.keys()):
		if morph_mapping[y] != y:
			negation_marker = 2
			base_lemma = morph_mapping[y]
			lemma = lemma_index.get(base_lemma, 0)
	    else:
		if y.startswith('in') or y.startswith('un') or y.startswith('de') or y.startswith('im'):
                	negation_marker = 2
			base_lemma = y[2:]	
			lemma = lemma_index.get(base_lemma, 0)
            	elif y.startswith('anti') or y.startswith('non') or y.startswith('dis'):
                	negation_marker = 2
			base_lemma = y[3:]
			lemma = lemma_index.get(base_lemma, 0)

    return tuple([lemma, pos, dep, direction, negation_marker])
        

def reconstruct_edge((lemma, pos, dep, direction, negation_marker),
                     lemma_inverted_index, pos_inverted_index, dep_inverted_index, dir_inverted_index):
    """
    Return a string representation of the edge
    :param lemma_inverted_index: lemma to index dictionary
    :param pos_inverted_index: POS to index dictionary
    :param dep_inverted_index: dependency label to index dictionary
    :param dir_inverted_index: edge direction to index dictionary
    :return: The string representation of the edge
    """
    recon_edge = '/'.join([lemma_inverted_index[lemma], pos_inverted_index[pos], dep_inverted_index[dep],
                     dir_inverted_index[direction], str(negation_marker)])
    return recon_edge


def load_embeddings(file_name, vocabulary):
    """
    Load the pre-trained embeddings from a file
    :param file_name: the embeddings file
    :param vocabulary: limited vocabulary to load vectors for
    :return: the vocabulary and the word vectors
    """
    with codecs.open(file_name, 'r', 'utf-8') as f_in:
        words, vectors = zip(*[line.strip().split(' ', 1) for line in f_in])
    wv = np.loadtxt(vectors)

    # Add the unknown words
    word_set = set(words)
    unknown_vector = np.random.random_sample((wv.shape[1],))
    unknown_words = list(set(vocabulary).difference(set(words)))

    # Create vectors for MWEs - sum of word embeddings, and OOV words
    unknown_word_vectors = [np.add.reduce([wv[words.index(w)] if w in word_set else unknown_vector
                                           for w in word.split(' ')])
                            for word in unknown_words]

    wv = np.vstack((wv, unknown_word_vectors))
    words = list(words) + unknown_words

    print 'Known lemmas:', len(vocabulary) - len(unknown_words), '/', len(vocabulary)

    # Normalize each row (word vector) in the matrix to sum-up to 1
    row_norm = np.sum(np.abs(wv)**2, axis=-1)**(1./2)
    wv /= row_norm[:, np.newaxis]

    word_index = { w : i for i, w in enumerate(words) }

    return wv, word_index


def load_dataset(dataset_file, relations):
    """
    Loads a dataset file
    :param dataset_file: the file path
    :return: a list of dataset instances, (x, y, relation)
    """
    with codecs.open(dataset_file, 'r', 'utf-8') as f_in:
        dataset = [tuple(line.strip().split('\t')) for line in f_in]
        dataset = preprocess.preprocess(dataset)
        dataset = { (x, y) : relation for (x, y, relation) in dataset if relation in relations }
    return dataset


def unique(lst):
    """
    :param lst: a list of lists
    :return: a unique list of items appearing in those lists
    """
    indices = sorted(range(len(lst)), key=lst.__getitem__)
    indices = set(next(it) for k, it in
                  itertools.groupby(indices, key=lst.__getitem__))
    return [x for i, x in enumerate(lst) if i in indices]


def get_paths(corpus, x, y):
    """
    Get the paths that connect x and y in the corpus
    :param corpus: the corpus' resource object
    :param x: x
    :param y: y
    :return:
    """
    x_to_y_paths = corpus.get_relations(x, y)
    y_to_x_paths = corpus.get_relations(y, x)
    paths = { corpus.get_path_by_id(path) : count for (path, count) in x_to_y_paths.iteritems() }
    paths.update({ corpus.get_path_by_id(path).replace('X/', '@@@').replace('Y/', 'X/').replace('@@@', 'Y/') : count
                   for (path, count) in y_to_x_paths.iteritems() })
    return paths
