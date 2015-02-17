# wordChain
wordChain takes in two words of equal length, and returns a sequence of words, going from the first to the second, changing only one letter at a time, where each word is found in a dictionary.

This problem was in the book "Cracking the Coding Interview, 5th Edition" (problem 18.10, page 476) by Gayle Laakmann McDowell. My solution pre-processes the dictionary to create a graph. This takes up some hard drive space, and it takes some time the first time the program is run, but subsequent searches are very fast. Unlike the solution in the book, mine works for all words, even if they contain non-English letters.
