#!/usr/bin/env python

# Implementation of Charikar simhashes in Python
# Reference used: http://dsrg.mff.cuni.cz/~holub/sw/shash

# This implementation by sangelone:
# http://github.com/sangelone/python-hashes

class simhash():
    def __init__(self, tokens='', hashbits=96):
        self.hashbits = hashbits
        self.hash = self.simhash(tokens)

    def __trunc__(self):
        return self.hash

    def __str__(self):
        return str(self.hash)
    
    def __long__(self):
        return long(self.hash)

    def __float__(self):
        return float(self.hash)
        
    def __cmp__(self, other):
        if self.hash < long(other): return -1
        if self.hash > long(other): return 1
        return 0
    
    def simhash(self, tokens):
        # Returns a Charikar simhash with appropriate bitlength
        v = [0]*self.hashbits
    
        for t in [self._string_hash(x) for x in tokens]:
            bitmask = 0
            for i in xrange(self.hashbits):
                bitmask = 1 << i
                if t & bitmask:
                    v[i] += 1
                else:
                    v[i] -= 1
    
        fingerprint = 0
        for i in xrange(self.hashbits):
            if v[i] >= 0:
                fingerprint += 1 << i
        
        return fingerprint

    def _string_hash(self, v):
        # A variable-length version of Python's builtin hash
        if v == "":
            return 0
        else:
            x = ord(v[0])<<7
            m = 1000003
            mask = 2**self.hashbits-1
            for c in v:
                x = ((x*m)^ord(c)) & mask
            x ^= len(v)
            if x == -1: 
                x = -2
            return x

    def hamming_distance(self, other_hash):
        x = (self.hash ^ other_hash.hash) & ((1 << self.hashbits) - 1)
        tot = 0
        while x:
            tot += 1
            x &= x-1
        return tot

    def similarity(self, other_hash):
        b = self.hashbits
        if b!= other_hash.hashbits:
            raise Exception('Hashes must be of equal size to find similarity!')
        return float(b - self.hamming_distance(other_hash)) / b


if __name__ == '__main__':
    s1 = 'This is a test string for tesing 12132131'
    s2 = 'PubMed comprises more than 19 million citations'
    #s2 = 'This is a test string for testing also!'

    for bits in xrange(16, 100, 16):
        hash1 = simhash(s1.split(), bits)
        hash2 = simhash(s2.split(), bits)

        print "%s\t[simhash = 0x%x]" % (s1, hash1)
        print "%s\t[simhash = 0x%x]" % (s2, hash2)
        print "%.3f%% similar because" % (hash1.similarity(hash2)*100),
        print hash1.hamming_distance(hash2), "bits differ out of", hash1.hashbits
