import argparse
import re
import datetime
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import json

SKIP_WORD_LESS = 5

alphanum_only_pattern = re.compile('[\W_]+')
freq_dict = {}


def generate_cloud(words, maxwords):
    word_freq = {k: v for k, v in sorted(words.items(), reverse=True, key=lambda item: item[1])}

    wc = WordCloud(background_color="white", width=1000, height=1000, max_words=maxwords, relative_scaling=0.5,
                   normalize_plurals=False).generate_from_frequencies(word_freq)

    plt.imshow(wc, interpolation='bilInear')
    plt.axis('off')
    plt.show()


def calculate_freq(word):
    word = word.strip().lower()
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


time_format = '%Y-%m-%dT%H:%M:%S'


def parse_simple_chat(export, start_date):
    for entry in (elem for elem in export['messages'] if not isinstance(elem['text'], list)):
        msg_date = datetime.datetime.strptime(entry['date'], time_format)
        if start_date and msg_date < start_date:
            continue

        tokenize_line(entry['text'])

def parse_super_chat(export, start_date):
    for chat in export['chats']['list']:
        parse_simple_chat(chat, start_date)


def parse_telegram_chat(file_name, start_date):
    with open(file_name, encoding='utf-8') as chat_export:
        export = json.load(chat_export)
        if 'chats' in export:
            return parse_super_chat(export, start_date)

        if not 'messages' in export:
            print("There is no 'messages' field in your chat export")
            exit(1)

        parse_simple_chat(export, start_date)


def remove_slurs(words):
    with open('slur.txt', encoding='utf-8') as f:
        slur = f.read().splitlines()
        for key in list(words.keys()):
            if key in slur:
                del words[key]

        return words

def remove_function_words(words):
    with open('conjunctions.txt', encoding='utf-8') as f:
        conjunctions = f.read().splitlines()

    with open('pronouns.txt', encoding='utf-8') as f:
        pronouns = f.read().splitlines()

    with open('prepositions.txt', encoding='utf-8') as f:
        prepositions = f.read().splitlines()

    with open('particles.txt', encoding='utf-8') as f:
        particles = f.read().splitlines()

    with open('interjections.txt', encoding='utf-8') as f:
        interjections = f.read().splitlines()

    with open('exclusions.txt', encoding='utf-8') as f:
        exclusions = f.read().splitlines()

    function_words = prepositions + particles + interjections + pronouns + conjunctions + exclusions
    for key in list(words.keys()):
        if key in function_words:
            del words[key]

    return words


def cmd_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d', '--days', nargs=1, required=False, help='Max date from now to take into an account.')
    parser.add_argument('-c', '--chat', nargs=1, required=True, help='A path to a telegram chat export in JSON.')
    parser.add_argument('-m', '--max', nargs=1, required=False, help='Max number of words to use.')
    parser.add_argument('-ns', '--notshorter', nargs=1, required=False, help='Skip words shorter than N characters.')
    parser.add_argument('-rs', '--noslure', required=False, action='store_true',
                        help='Filter slur out.')
    parser.add_argument('-f', '--leavefunc', required=False, action='store_true',
                        help='Leave function words, like pronouns.')

    processed_args = parser.parse_args()
    return processed_args


def main():
    args = cmd_args()

    if args.notshorter:
        try:
            global SKIP_WORD_LESS
            SKIP_WORD_LESS = int(args.notshorter[0])
        except ValueError as e:
            print(e)
            exit(1)

    max_words = 100
    if args.max:
        try:
            max_words = int(args.max[0])
        except ValueError as e:
            print(e)
            exit(1)

    start_date = None
    if args.days:
        start_date = datetime.datetime.now() - datetime.timedelta(int(args.days[0]))

    parse_telegram_chat(args.chat[0], start_date)
    global freq_dict

    if not args.leavefunc:
        freq_dict = remove_function_words(freq_dict)

    if args.noslure:
        freq_dict = remove_slurs(freq_dict)

    if len(freq_dict) < 1:
        print("History is empty, cannot generate anything useful.")
        return

    generate_cloud(freq_dict, max_words)


if __name__ == '__main__':
    main()
