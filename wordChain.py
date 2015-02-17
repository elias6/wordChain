#! /usr/bin/env python3

import argparse
import pickle
import random
from collections import deque
from itertools import chain
from multiprocessing import Pool

def load_word_list(filename="/usr/share/dict/words"):
    with open(filename) as word_file:
        return set(word_file.read().splitlines())

def load_word_graph(filename="wordGraph.pickle"):
    with open(filename, "rb") as word_graph_file:
        return pickle.load(word_graph_file)

def save_word_graph(word_graph, filename="wordGraph.pickle"):
    with open(filename, "wb") as word_graph_file:
        pickle.dump(word_graph, word_graph_file)

def get_close_words(word, all_words, all_chars):
    result = set()
    for pos in range(len(word)):
        prefix = word[:pos]
        suffix = word[pos + 1:]
        for char in all_chars:
            test_word = prefix + char + suffix
            if test_word != word and test_word in all_words:
                result.add(test_word)
    return result

def make_word_graph(all_words):
    all_chars = set(chain(*all_words))
    word_list = list(all_words)
    argument_generator = ((w, all_words, all_chars) for w in word_list)
    with Pool() as pool:
        word_sets = pool.starmap(get_close_words, argument_generator)
    return dict(zip(word_list, word_sets))

def make_word_graph_simple(all_words):
    all_chars = set(chain(*all_words))
    return {w: get_close_words(w, all_words, all_chars) for w in all_words}

def find_word_chain(initial, goal, word_graph):
    if len(initial) != len(goal):
        return None
    word_queue = deque([initial])
    predecessors = {}

    while word_queue:
        word = word_queue.popleft()
        for neighbor in word_graph[word]:
            if neighbor not in predecessors:
                word_queue.append(neighbor)
                predecessors[neighbor] = word
                if neighbor == goal:
                    result = [goal]
                    while result[-1] != initial:
                        result.append(predecessors[result[-1]])
                    return list(reversed(result))
    return None

def test(word_graph):
    for word_length in range(3, 8):
        words = [w for w in word_graph if len(w) == word_length]
        for _ in range(3):
            initial, goal = random.sample(words, 2)
            print("Finding shortest path from \"{}\" to \"{}\"".format(initial, goal))
            result = find_word_chain(initial, goal, word_graph)
            print(result)
            print()

if __name__ == "__main__":
    try:
        word_graph = load_word_graph()
    except FileNotFoundError:
        all_words = load_word_list()
        word_graph = make_word_graph(all_words)
        save_word_graph(word_graph)
    test(word_graph)
