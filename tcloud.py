import argparse
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import multidict as multidict
import json

SKIP_WORD_LESS = 5

alphanum_only_pattern = re.compile('[\W_]+')
freq_dict = {}


def generate_cloud(words):
    word_freq = {k: v for k, v in sorted(words.items(),reverse=True, key=lambda item: item[1])}


    wc = WordCloud(background_color="white", width=1000, height=1000, max_words=10, relative_scaling=0.5,
                   normalize_plurals=False).generate_from_frequencies(word_freq)

    plt.imshow(wc, interpolation='bilInear')
    plt.axis('off')
    plt.show()


def calculate_freq(word):
    word = word.strip()
    if not word: return
    if len(word) <= SKIP_WORD_LESS: return
    global freq_dict
    if word not in freq_dict:
        freq_dict[word] = 1
    else:
        freq_dict[word] = freq_dict[word] + 1


def tokenize_line(line):
    words = line.rstrip().split(' ')
    for word in words:
        word = alphanum_only_pattern.sub('', word)
        calculate_freq(word)


def parse_telegram_chat(file_name):
    with open(file_name, encoding='utf-8') as chat_export:
        chat = json.load(chat_export)
        for entry in (elem for elem in chat['messages'] if not isinstance(elem['text'], list)):
            tokenize_line(entry['text'])


def remove_function_words(words):
    conjunctions = []
    with open('conjunctions.txt', encoding='utf-8') as f:
        conjunctions = f.read().splitlines()

    pronouns = []
    with open('pronouns.txt', encoding='utf-8') as f:
        pronouns = f.read().splitlines()

    prepositions = []
    with open('prepositions.txt', encoding='utf-8') as f:
        prepositions = f.read().splitlines()

    particles = []
    with open('particles.txt', encoding='utf-8') as f:
        particles = f.read().splitlines()

    interjections = []
    with open('interjections.txt', encoding='utf-8') as f:
        interjections = f.read().splitlines()

    function_words = prepositions + particles + interjections + pronouns + conjunctions
    for key in list(words.keys()):
        if key in function_words:
            del words[key]

    return words


def cmd_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c', '--chat', nargs=1, required=True, help='A path to telegram char export in JSON.')
    processed_args = parser.parse_args()
    return processed_args


def main():
    args = cmd_args()
    parse_telegram_chat(args.chat[0])
    global freq_dict
    freq_dict = remove_function_words(freq_dict)
    generate_cloud(freq_dict)


if __name__ == '__main__':
    main()
