import random


def pick_random_word():
    word_list = open('wordlist.txt', 'r').read().split('\n')
    return random.choice(word_list)
