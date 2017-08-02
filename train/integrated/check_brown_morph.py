import sys

'''
Script to check if the unmorphed words are in the output of the brown list
'''

def get_morph_mapping(morph_file):
	mapping = {}
	f = open(morph_file, "r")
	for line in f.readlines():
		sent = line.strip("\n")
		word_pair = sent.split("\t")
		if(word_pair[0] in mapping.keys()):
			print(word_pair[0], word_pair[1])
			#with open("morphed-words.txt", "a+") as f_out:
			#	f_out.write(word_pair[0] + "\t" + word_pair[1]  + "\n")
		else:
			mapping[word_pair[0]] = word_pair[1]
	f.close()
	return mapping

def morph(morph_mapping, morph_words, words_to_check):
	morphed_words = []
	unmorphed_words = []
	for word in words_to_check:
		if word in morph_words:
			morphed_words.append((word, morph_mapping[word]))
		else:
			unmorphed_words.append(word)
	return morphed_words, unmorphed_words
	

morph_analysed_file = sys.argv[1]
unmorphed_words_file = sys.argv[2]

morph_mapping = get_morph_mapping(morph_analysed_file)
morph_words = morph_mapping.keys()

words_to_check = []
with open(unmorphed_words_file, "r") as f_in:
	lines = f_in.readlines()
	for word in lines:
		words_to_check.append(word.strip())

morphed_words, unmorphed_words = morph(morph_mapping, morph_words, words_to_check)


with open("morphed-words2.txt", "w") as f_out:
	for pair in morphed_words:
		f_out.write(pair[0] + "\t" + pair[1]  + "\n")

with open("unmorphed-words2.txt", "w") as f_out:
	for word in unmorphed_words:
		f_out.write(word + "\n")
