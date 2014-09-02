"""
Implementation of a Bloom filter in Python.

The Bloom filter is a space-efficient probabilistic data structure that is
used to test whether an element is a member of a set. False positives are
possible, but false negatives are not. Elements can be added to the set, but 
not removed. The more elements that are added to the set, the larger the
probability of false positives.

Uses SHA-1 from Python's hashlib, but you can swap that out with any other
160-bit hash function. Also keep in mind that it starts off very sparse and
become more dense (and false-positive-prone) as you add more elements.

Part of python-hashes by sangelone. See README and LICENSE.
"""

import math
import hashlib
from hashtype import hashtype


class bloomfilter(hashtype):
    def __init__(self, value='', capacity=3000, false_positive_rate=0.01):
        """
        'value' is the initial string or list of strings to hash,
        'capacity' is the expected upper limit on items inserted, and
        'false_positive_rate' is self-explanatory but the smaller it is, the larger your hashes!
        """
        self.create_hash(value, capacity, false_positive_rate)

    def create_hash(self, initial, capacity, error):
        """
        Calculates a Bloom filter with the specified parameters.
        Initalizes with a string or list/set/tuple of strings. No output.

        Reference material: http://bitworking.org/news/380/bloom-filter-resources
        """
        self.hash = 0L
        self.hashbits, self.num_hashes = self._optimal_size(capacity, error)

        if len(initial):
            if type(initial) == str:
                self.add(initial)
            else:
                for t in initial:
                    self.add(t)
    
    def _hashes(self, item):
      """
      To create the hash functions we use the SHA-1 hash of the
      string and chop that up into 20 bit values and then
      mod down to the length of the Bloom filter.
      """
      m = hashlib.sha1()
      m.update(item)
      digits = m.hexdigest()

      # Add another 160 bits for every 8 (20-bit long) hashes we need
      for i in range(self.num_hashes / 8):
          m.update(str(i))
          digits += m.hexdigest()

      hashes = [int(digits[i*5:i*5+5], 16) % self.hashbits for i in range(self.num_hashes)]
      return hashes  

    def _optimal_size(self, capacity, error):
        """Calculates minimum number of bits in filter array and
        number of hash functions given a number of enteries (maximum)
        and the desired error rate (false positives).
        
        Example: m, k = self._optimal_size(3000, 0.01)   # m=28756, k=7
        
        Source: http://en.wikipedia.org/wiki/Bloom_filter#Optimal_number_of_hash_functions
        """
        m = math.ceil((capacity * math.log(error)) / math.log(1.0 / (math.pow(2.0, math.log(2.0)))))
        k = math.ceil(math.log(2.0) * m / capacity)
        return (int(m), int(k))

    
    def add(self, item):
        "Add an item (string) to the filter. Cannot be removed later!"
        for pos in self._hashes(item):
            self.hash |= (2 ** pos)

    def __contains__(self, name):
        "This function is used by the 'in' keyword"
        retval = True
        for pos in self._hashes(name):
            retval = retval and bool(self.hash & (2 ** pos))
        return retval
