#python-hashes

Interesting (non-cryptographic) hashes implemented in pure Python. Included so far:

 * Bloom filters
 * Charikar similarity hashes 
 * Nilsimsa signatures
 * geohashes

Each hash is implemented as its own type extended from the base class `hashtype`.

Official repository and latest version: https://github.com/sangelone/python-hashes

To install the latest version, you can either do `easy_install python-hashes` or
`pip install python-hashes`. You may need to use `sudo`, depending on your environment.

---

###simhash

Charikar similarity is most useful for creating 'fingerprints' of
documents or metadata so you can quickly find duplicates or cluster
items. It operates on lists of strings, treating each word as its
own token (order does not matter, as in the bag-of-words model).

Here is a quick example session showing off similarity hashes:

    >>> from hashes.simhash import simhash
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

    >>> hash3 = simhash('this is yet another test', hashbits=8)
    >>> hash3.hex()
    '0x18'
    >>> hash4 = simhash('extremely long hash bitlength', hashbits=2048)
    >>> hash4.hex()
    '0xf00020585012016060260443bab0f7d76fde5549a6857ecL'

But be careful; it only makes sense to compare equal-length hashes!

    >>> hash3.similarity(hash4)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "hashes/simhash.py", line 63, in similarity
        raise Exception('Hashes must be of equal size to find similarity')
    Exception: Hashes must be of equal size to find similarity


###bloom

The Bloom filter is a space-efficient probabilistic data structure that is
used to test whether an element is a member of a set. False positives are
possible, but false negatives are not. Elements can be added to the set but
not removed.

Uses SHA-1 from Python's hashlib, but you can swap that out with any other
160-bit hash function. Also keep in mind that it starts off very sparse and
become more dense (and false-positive-prone) as you add more elements.

Here is the basic use case:

    >>> from hashes.bloom import bloomfilter
    >>> hash1 = bloomfilter('test')
    >>> hash1.hashbits, hash1.num_hashes     # default values (see below)
    (28756, 7)
    >>> hash1.add('test string')
    >>> 'test string' in hash1
    True
    >>> 'holy diver' in hash1
    False
    >>> for word in 'these are some tokens to add to the filter'.split():
    ...     hash1.add(word)
    >>> 'these' in hash1
    True

The hash length and number of internal hashes used for the digest are automatically
determined using your input values `capacity` and `false_positive_rate`. The capacity
is the upper bound on the number of items you wish to add. A lower false-positive
rate will create a larger, but more accurate, filter.

    >>> hash2 = bloomfilter(capacity=100, false_positive_rate=0.01)
    >>> hash2.hashbits, hash2.num_hashes
    (959, 7)
    >>> hash3 = bloomfilter(capacity=1000000, false_positive_rate=0.01)
    >>> hash3.hashbits, hash3.num_hashes
    (9585059, 7)
    >>> hash4 = bloomfilter(capacity=1000000, false_positive_rate=0.0001)
    >>> hash4.hashbits, hash4.num_hashes
    (19170117, 14)

The hash grows in size to accommodate the number of items you wish to add,
but remains sparse until you are done adding the projected number of items:

    >>> import zlib
    >>> len(hash4.hex())
    250899
    >>> len(zlib.compress(hash4.hex()))
    1068


###geohash

Geohash is a latitude/longitude geocode system invented by
Gustavo Niemeyer when writing the web service at geohash.org, and put
into the public domain.

It is a hierarchical spatial data structure which subdivides space
into buckets of grid shape. Geohashes offer properties like
arbitrary precision and the possibility of gradually removing
characters from the end of the code to reduce its size (and
gradually lose precision). As a consequence of the gradual
precision degradation, nearby places will often (but not always)
present similar prefixes. On the other side, the longer a shared
prefix is, the closer the two places are. For this implementation,
the default precision is 12 (base32) characters long.

It's very easy to use:

    >>> from hashes.geohash import geohash
    >>> here = geohash(33.0505, -1.024, precision=4)
    >>> there = geohash(34.5, -2.5, precision=4)
    >>> here.hash, there.hash
    ('evzs', 'eynk')
    >>> here.distance_in_miles(there)
    131.24743425050551

    >>> # The longer the hash, the more accurate it is
    >>> here.encode(33.0505, -1.024, precision=8)
    >>> here.hash
    'evzk08wt'
    >>> here.decode()
    (33.050565719604492, -1.0236167907714844)

    >>> # Now try with 20 characters
    >>> here.encode(33.0505, -1.024, precision=20)
    >>> here.hash
    'evzk08wm55drbqbww0j7'
    >>> here.decode()
    (33.050499999999936, -1.0239999999998339)


###nilsimsa

Most useful for filtering spam by creating signatures of documents to
find near-duplicates. Charikar similarity hashes can be used on any
datastream, whereas Nilsimsa is a digest ideal for documents (language
doesn't matter) because it uses histograms of *rolling* trigraphs instead
of the usual bag-of-words model where order doesn't matter.

[Related paper](http://spdp.dti.unimi.it/papers/pdcs04.pdf) and [original reference](http://ixazon.dynip.com/~cmeclax/nilsimsa.html).

*The Nilsimsa hash does not output the same data as the
reference implementation.* **Use at your own risk.**
