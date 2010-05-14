#python-hashes

Interesting (non-cryptographic) hashes implemented in pure Python. Included so far:

 * Bloom filters
 * Charikar similarity hashes 
 * Nilsimsa signatures

Each hash is implemented as its own type extended from the base class `hashtype`.

---

###simhash

Charikar similarity is most useful for creating 'fingerprints' of
documents or metadata so you can quickly find duplicates or cluster
items. It operates on lists of strings, treating each word as its
own token (order does not matter, as in the bag-of-words model).

Here is a quick example session showing off similarity hashes:

    >>> import simhash
    >>> from simhash import simhash
    >>> hash1 = simhash('This is a test string one.')
    >>> hash2 = simhash('This is a test string TWO.')
    >>> hash1
    <simhash.simhash object at 0x7f1f93070c90>
    >>> print hash1, hash2
    10203485745788768176630988232 10749932022170787621889701832
    >>> hash1.hex()
    '0x20f82026a01daffae45cfdc8L'
    >>> hash1.similarity(hash2)
    0.875                   # % of differing bits
    >>> long(hash1) - long(hash2)
    -546446276382019445258713600L
    >>> hash1 < hash2       # Hashes of the same type can be compared
    True
    >>> a_list = [hash2, hash1, 4.2]
    >>> for item in a_list: print item
    10749932022170787621889701832
    10203485745788768176630988232
    4.2
    >>> a_list.sort()       # Because comparisons work, so does sorting
    >>> for item in a_list: print item
    4.2
    10203485745788768176630988232
    10749932022170787621889701832

It can be extended to any bitlength using the `hashbits` parameter.

    >>> hash3 = simhash('this is yet another test', hashbits=12)
    >>> print hash3
    1816

###bloom

The Bloom filter is a space-efficient probabilistic data structure that is
used to test whether an element is a member of a set. False positives are
possible, but false negatives are not. Elements can be added to the set, but
not removed. The more elements that are added to the set, the larger the
probability of false positives.

Uses SHA-1 from Python's hashlib, but you can swap that out with any other
160-bit hash function. Also keep in mind that it starts off very sparse and
become more dense (and false-positive-prone) as you add more elements.

###nilsimsa

Most useful for filtering spam by creating signatures of documents to
find near-duplicates. Charikar similarity hashes can be used on any
datastream, whereas Nilsimsa is a digest ideal for documents (language
doesn't matter) because it uses histograms of *rolling* trigraphs instead
of the usual bag-of-words model where order doesn't matter.

[Related paper](http://spdp.dti.unimi.it/papers/pdcs04.pdf) and [original reference](http://ixazon.dynip.com/~cmeclax/nilsimsa.html).

