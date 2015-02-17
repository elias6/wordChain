#! /usr/bin/env python3

import argparse
import pickle
import random
from collections import deque
from itertools import chain
from multiprocessing import Pool


def load_word_list(filename):
    with open(filename) as word_file:
        print("Adding words from {}. Please wait.".format(filename))
        return set(word_file.read().splitlines())


def load_word_graph(filename):
    with open(filename, "rb") as word_graph_file:
        print("Loading word graph from {}.".format(filename))
        return pickle.load(word_graph_file)


def save_word_graph(word_graph, filename):
    with open(filename, "wb") as word_graph_file:
        print("Saving word graph to {}.".format(filename))
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


def demo(word_graph):
    for word_length in range(3, 8):
        words = [w for w in word_graph if len(w) == word_length]
        for _ in range(3):
            initial, goal = random.sample(words, 2)
            print_word_chain(initial, goal, word_graph)
            print()


def print_word_chain(initial, goal, word_graph):
    print('Finding shortest path from "{}" to "{}"'.format(initial, goal))
    path = find_word_chain(initial, goal, word_graph)
    print(path or 'No path found between "{}" and "{}"'.format(initial, goal))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "initial_word",
        nargs="?",
        help="Initial word.")
    parser.add_argument(
        "goal_word",
        nargs="?",
        help="Goal word. This must be given if the initial word is given. It must be exactly as "
            "long as the initial word.")
    parser.add_argument(
        "-d",
        "--demo_mode",
        action="store_true",
        help="Demonstrate this program's functionality by finding paths between some randomly "
            "chosen words.")
    parser.add_argument(
        "-w",
        "--word_list_files",
        help="Files containing words to be used. Each word must be on a separate line. "
            "Multiple files can be specified. "
            "Example: `%(prog)s -w /usr/share/dict/words -w /usr/share/dict/propernames`. "
            "If no word list files are specified and no word graph files are found, "
            "/usr/share/dict/words will be used as the word list file.",
        action="append")
    parser.add_argument(
        "-g",
        "--word_graph_input",
        help="Pickle file containing word graph with connections between words. "
            "This usually does not need to be explicitly specified.",
        default="wordGraph.pickle")
    parser.add_argument(
        "-o",
        "--word_graph_output",
        help="Name for pickle file used to save word graph so subsequent searches will be much "
            "faster. This usually does not need to be explicitly specified. To disable saving "
            "word graphs, specify /dev/null or your operating system's equivalent.",
        default="wordGraph.pickle"
    )
    args = parser.parse_args()

    if len([x for x in (args.initial_word, args.goal_word) if x is not None]) == 1:
        parser.error("Initial word and goal word must be given together.")

    if args.word_list_files:
        all_words = set()
        for filename in args.word_list_files:
            all_words.update(load_word_list(filename))
        word_graph = make_word_graph(all_words)
    else:
        try:
            word_graph = load_word_graph(args.word_graph_input)
        except FileNotFoundError:
            all_words = load_word_list("/usr/share/dict/words")
            word_graph = make_word_graph(all_words)
    if "all_words" in locals():
        # Save word graph if it may contain new words
        save_word_graph(word_graph, args.word_graph_output)

    if args.demo_mode:
        demo(word_graph)
    elif args.initial_word and args.goal_word:
        print_word_chain(args.initial_word, args.goal_word, word_graph)
    else:
        parser.print_help()
