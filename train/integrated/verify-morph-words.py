import sys

def get_dataset_keys(dataset_file):
	dataset_keys = set()
	f = open(dataset_file, "r")
	for line in f.readlines():
		words = line.strip("\n").split("\t")
		x = words[0]
		y = words[1]
            	if (x.startswith('in') or x.startswith('un') or x.startswith('anti') or x.startswith('de') or x.startswith('im') or x.startswith('non') or x.startswith('dis')):
			dataset_keys.add(x)
            	if (y.startswith('in') or y.startswith('un') or y.startswith('anti') or y.startswith('de') or y.startswith('im') or y.startswith('non') or y.startswith('dis')):
			dataset_keys.add(y)
	f.close()
	return dataset_keys

def get_morph_mapping(morph_file):
	mapping = {}
	f = open(morph_file, "r")
	for line in f.readlines():
		sent = line.strip("\n")
		word_pair = sent.split("\t")
		mapping[word_pair[0]] = word_pair[1]
	f.close()
	return mapping

def morph(dataset_keys, morph_mapping, morph_words):
	morphed_words = []
	unmorphed_words = []
	for word in dataset_keys:
		if word in morph_words:
			morphed_words.append((word, morph_mapping[word]))
		else:
			unmorphed_words.append(word)
	return morphed_words, unmorphed_words

morph_analysed_file = sys.argv[1]
dataset_file = sys.argv[2]

dataset_keys = get_dataset_keys(dataset_file)

morph_mapping = get_morph_mapping(morph_analysed_file)
morph_words = morph_mapping.keys()

morphed_words, unmorphed_words = morph(dataset_keys, morph_mapping, morph_words)

with open("morphed-words.txt", "w") as f_out:
	for pair in morphed_words:
		f_out.write(pair[0] + "\t" + pair[1]  + "\n")

with open("unmorphed-words.txt", "w") as f_out:
	for word in unmorphed_words:
		f_out.write(word + "\n")

