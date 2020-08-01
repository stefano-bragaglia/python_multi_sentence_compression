Multi-Sentence Compression
====
_Multi-Sentence Compression, in Python 3!_

Compressing a cluster of related sentences into a single sentence that retains the most relevant non-redundant concepts from the original cluster and is grammatically sound is a complex task.

This project implements the method suggested in ["Multi-Sentence Compressing: Finding Shortest Paths in Word Graphs"](http://www.aclweb.org/anthology/C10-1037) (**Katja Filippova.** Google Inc. _In Proc of 23rd Intl Conf COLING, 2010._) which is based upon shortest paths in word graphs.

Specifically, we use:
* [Spacy](https://spacy.io) for basic sentence detection, tokenisation and POD tagging

The procedure consists in:
* generating a `word graph`
* weighting the **edges** between _words_
* compressing the graph into a _meaningful summary_.

Word graph
----

A `word graph` (or `adjacency text graph`) is a directed graph where:
* _words_ become **nodes** (punctuation is ignored)
* _adjacent words_ are connected by **edges** (type: _FOLLOWS_)
* _frequencies_ of words and adjacencies are saved on both **nodes** and **edges**.

The **lower case text**, **POS tag** and the **stop_word** flag of each _word_ act as key, so that words with the same grammatical usage are unique in the graph.
If more words have a similar key, the key with most similar context (words before and after it) or higher frequency is considered a mapping.
The only exception to this rule is for [stop-words](https://en.wikipedia.org/wiki/Most_common_words_in_English) which are duplicated if the context is empty to keep their _frequencies_ (and importance in the graph) low.

The identifier of the originating sentence and the offset position of each mapped word are maintained in a separate **lookup table**.
The chain of _words_ of each sentence is also preceded by a _START_ **node** and followed by an _END_ **node**.

Given the following cluster of related sentences:

1. _The wife of a former U.S. president Bill Clinton, Hillary Clinton, visited China last Monday._
2. _Hillary Clinton wanted to visit China last month but postponed her plans till Monday last week._
3. _Hillary Clinton paid a visit to the People Republic of China on Monday._
4. _Last week the Secretary State Ms. Clinton visited Chinese officials._

the resulting `word graph` is presented below.

   {
        "<START>": {
            "the:DT:*:0": 1,
            "hillary:NNP:_:9": 2,
            "last:JJ:*:12": 1
        },
        "the:DT:*:0": {
            "wife:NN:_:1": 1,
            "people:NNP:_:27": 1,
            "secretary:NNP:_:30": 1
        },
        "wife:NN:_:1": {
            "of:IN:*:2": 1
        },
        "of:IN:*:2": {
            "a:DT:*:3": 1,
            "china:NNP:_:11": 1
        },
        "a:DT:*:3": {
            "former:JJ:*:4": 1,
            "visit:NN:_:25": 1
        },
        "former:JJ:*:4": {
            "u.s.:NNP:_:5": 1
        },
        "u.s.:NNP:_:5": {
            "president:NN:_:6": 1
        },
        "president:NN:_:6": {
            "bill:NNP:_:7": 1
        },
        "bill:NNP:_:7": {
            "clinton:NNP:_:8": 1
        },
        "clinton:NNP:_:8": {
            "hillary:NNP:_:9": 1,
            "visited:VBD:_:10": 2,
            "wanted:VBD:_:14": 1,
            "paid:VBD:_:24": 1
        },
        "hillary:NNP:_:9": {
            "clinton:NNP:_:8": 3
        },    
        "visited:VBD:_:10": {
            "china:NNP:_:11": 1,
            "chinese:JJ:_:33": 1
        },
        "china:NNP:_:11": {
            "last:JJ:*:12": 2,
            "on:IN:*:29": 1
        },
        "last:JJ:*:12": {
            "monday:NNP:_:13": 1,
            "month:NN:_:17": 1,
            "week:NN:_:23": 2
        },
        "monday:NNP:_:13": {
            "<END>": 2,
            "last:JJ:*:12": 1
        },
        "wanted:VBD:_:14": {
            "to:TO:*:15": 1
        },
        "to:TO:*:15": {
            "visit:VB:_:16": 1
        },
        "visit:VB:_:16": {
            "china:NNP:_:11": 1
        },
        "month:NN:_:17": {
            "but:CC:*:18": 1
        },
        "but:CC:*:18": {
            "postponed:VBD:_:19": 1
        },
        "postponed:VBD:_:19": {
            "her:PRP$:*:20": 1
        },
        "her:PRP$:*:20": {
            "plans:NNS:_:21": 1
        },    
        "plans:NNS:_:21": {
            "till:IN:_:22": 1
        },
        "till:IN:_:22": {
            "monday:NNP:_:13": 1
        },
        "week:NN:_:23": {
            "<END>": 1,
            "the:DT:*:0": 1
        },
        "paid:VBD:_:24": {
            "a:DT:*:3": 1
        },
        "visit:NN:_:25": {
            "to:IN:*:26": 1
        },
        "to:IN:*:26": {
            "the:DT:*:0": 1
        },
        "people:NNP:_:27": {
            "republic:NNP:_:28": 1
        },
        "republic:NNP:_:28": {
            "of:IN:*:2": 1
        },
        "on:IN:*:29": {
            "monday:NNP:_:13": 1
        },
        "secretary:NNP:_:30": {
            "state:NNP:_:31": 1
        },
        "state:NNP:_:31": {
            "ms.:NNP:_:32": 1
        },
        "ms.:NNP:_:32": {
            "clinton:NNP:_:8": 1
        },
        "chinese:JJ:_:33": {
            "officials:NNS:_:34": 1
        },
        "officials:NNS:_:34": {
            "<END>": 1
        }
    }


Weights
----

Both weight methods discussed in the [original paper](http://www.aclweb.org/anthology/C10-1037) have been implemented.

The **naive** method simply considers the inverse of the _frequency_ of each _FOLLOWS_ **edge**.

The **advanced** method is more sophisticated as it keeps into account **sintagmatic associations** scaled by 
the relative distance of the terms in their enclosing sentences.
 
In particular:
 
                            freq(i) + freq(j)
    w'(edge(i, j)) = ------------------------------
                      SUM(s in S) diff(s, i, j)^-1 

                    | pos(s, j) - pos(s, i)    if pos(s, i) < pos(s, j)
    diff(s, i, j) = | 
                    | 0                        otherwise

                       w'(edge(i, j))
    w"(edge(i, j) = -------------------
                     freq(i) x freq(j)

Notice that these weights are costs: the lower, the better.

Compression
----

The goal of this step is to generalise the input sentences by generating an appropriate compression (inductive task).
All the **paths** from _START_ to _END_ describe all the possible _worlds_ that can be reached upon summarisation.

In order to obtain sound summaries, we require paths to be at least **8 words** long and to contain **at least a verb**.
The remaining paths are ranked by **increasing cost**, which is the sum of the weights on their **edges** normalised by **path length**.

By visiting the _words_ in the **minimal cost path** (if any), the desired compression summary is generated.

Results
----

The project is organised as a [PyBuilder Project](https://pybuilder.io), 
therefore it is sufficient to issue the following command on the terminal in the root folder of the project 
(provided that [PyBuilder]() is installed locally):

    pyb execute
    
Alternatively, just try:

    python3 /src/main/script/main.py

The example introduced above, for instance, produces the following output:

    hillary clinton visited china last week

which corresponds to the following summary: 

    Hillary Clinton visited China last week.

The algorithm has been successfully applied to English and Spanish by using an _ad-hoc_ **stop-word list** of 600 term ca.
The experimental results are discussed in the [original paper](http://www.aclweb.org/anthology/C10-1037).
