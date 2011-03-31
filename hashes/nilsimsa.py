"""
Implementation of Nilsimsa hashes (signatures) in Python.

Most useful for filtering spam by creating signatures of documents to 
find near-duplicates. Charikar similarity hashes can be used on any 
datastream, whereas Nilsimsa is a digest ideal for documents (written 
in any language) because it uses histograms of [rolling] trigraphs 
instead of the usual bag-of-words model where order doesn't matter.

Related paper: http://spdp.dti.unimi.it/papers/pdcs04.pdf

Part of python-hashes by sangelone. See README and LICENSE.
"""

from hashtype import hashtype

TRAN = [ord(x) for x in 
    "\x02\xD6\x9E\x6F\xF9\x1D\x04\xAB\xD0\x22\x16\x1F\xD8\x73\xA1\xAC"\
    "\x3B\x70\x62\x96\x1E\x6E\x8F\x39\x9D\x05\x14\x4A\xA6\xBE\xAE\x0E"\
    "\xCF\xB9\x9C\x9A\xC7\x68\x13\xE1\x2D\xA4\xEB\x51\x8D\x64\x6B\x50"\
    "\x23\x80\x03\x41\xEC\xBB\x71\xCC\x7A\x86\x7F\x98\xF2\x36\x5E\xEE"\
    "\x8E\xCE\x4F\xB8\x32\xB6\x5F\x59\xDC\x1B\x31\x4C\x7B\xF0\x63\x01"\
    "\x6C\xBA\x07\xE8\x12\x77\x49\x3C\xDA\x46\xFE\x2F\x79\x1C\x9B\x30"\
    "\xE3\x00\x06\x7E\x2E\x0F\x38\x33\x21\xAD\xA5\x54\xCA\xA7\x29\xFC"\
    "\x5A\x47\x69\x7D\xC5\x95\xB5\xF4\x0B\x90\xA3\x81\x6D\x25\x55\x35"\
    "\xF5\x75\x74\x0A\x26\xBF\x19\x5C\x1A\xC6\xFF\x99\x5D\x84\xAA\x66"\
    "\x3E\xAF\x78\xB3\x20\x43\xC1\xED\x24\xEA\xE6\x3F\x18\xF3\xA0\x42"\
    "\x57\x08\x53\x60\xC3\xC0\x83\x40\x82\xD7\x09\xBD\x44\x2A\x67\xA8"\
    "\x93\xE0\xC2\x56\x9F\xD9\xDD\x85\x15\xB4\x8A\x27\x28\x92\x76\xDE"\
    "\xEF\xF8\xB2\xB7\xC9\x3D\x45\x94\x4B\x11\x0D\x65\xD5\x34\x8B\x91"\
    "\x0C\xFA\x87\xE9\x7C\x5B\xB1\x4D\xE5\xD4\xCB\x10\xA2\x17\x89\xBC"\
    "\xDB\xB0\xE2\x97\x88\x52\xF7\x48\xD3\x61\x2C\x3A\x2B\xD1\x8C\xFB"\
    "\xF1\xCD\xE4\x6A\xE7\xA9\xFD\xC4\x37\xC8\xD2\xF6\xDF\x58\x72\x4E"]


class nilsimsa(hashtype):
    def __init__(self, value='', hashbits=256):
        self.hashbits = hashbits
        self.count = 0          # num characters seen
        self.acc = [0]*256      # accumulators for computing digest
        self.lastch = [-1]*4    # last four seen characters (-1 until set)
        self.create_hash(value)

    def create_hash(self, data):
        """Calculates a Nilsimsa signature with appropriate bitlength.        
        Input must be a string. Returns nothing.
        Reference: http://ixazon.dynip.com/~cmeclax/nilsimsa.html
        """
        if type(data) != str:
            raise Exception('Nilsimsa hashes can only be created on strings')
        self.hash = 0L
        self.add(data)

    def add(self, data):
        """Add data to running digest, increasing the accumulators for 0-8
           triplets formed by this char and the previous 0-3 chars."""
        for character in data:
            ch = ord(character)
            self.count += 1

            # incr accumulators for triplets
            if self.lastch[1] > -1:
                self.acc[self._tran3(ch, self.lastch[0], self.lastch[1], 0)] +=1
            if self.lastch[2] > -1:
                self.acc[self._tran3(ch, self.lastch[0], self.lastch[2], 1)] +=1
                self.acc[self._tran3(ch, self.lastch[1], self.lastch[2], 2)] +=1
            if self.lastch[3] > -1:
                self.acc[self._tran3(ch, self.lastch[0], self.lastch[3], 3)] +=1
                self.acc[self._tran3(ch, self.lastch[1], self.lastch[3], 4)] +=1
                self.acc[self._tran3(ch, self.lastch[2], self.lastch[3], 5)] +=1
                self.acc[self._tran3(self.lastch[3], self.lastch[0], ch, 6)] +=1
                self.acc[self._tran3(self.lastch[3], self.lastch[2], ch, 7)] +=1

            # adjust last seen chars
            self.lastch = [ch] + self.lastch[:3]
        self.hash = self._digest()

    def _tran3(self, a, b, c, n):
        """Get accumulator for a transition n between chars a, b, c."""
        return (((TRAN[(a+n)&255]^TRAN[b]*(n+n+1))+TRAN[(c)^TRAN[n]])&255)

    def _digest(self):
        """Get digest of data seen thus far as a list of bytes."""
        total = 0                           # number of triplets seen
        if self.count == 3:                 # 3 chars = 1 triplet
            total = 1
        elif self.count == 4:               # 4 chars = 4 triplets
            total = 4
        elif self.count > 4:                # otherwise 8 triplets/char less
            total = 8 * self.count - 28     # 28 'missed' during 'ramp-up'

        threshold = total / 256             # threshold for accumulators

        code = [0]*self.hashbits            # start with all zero bits
        for i in range(256):                # for all 256 accumulators
            if self.acc[i] > threshold:     # if it meets the threshold
                code[i >> 3] += 1 << (i&7)  # set corresponding digest bit

        code = code[::-1]                   # reverse the byte order

        out = 0
        for i in xrange(self.hashbits):     # turn bit list into real bits
            if code[i] :
                out += 1 << i

        return out
                            
    def similarity(self, other_hash):
        """Calculate how different this hash is from another Nilsimsa.
        Returns a float from 0.0 to 1.0 (inclusive)
        """
        if type(other_hash) != nilsimsa:
            raise Exception('Hashes must be of same type to find similarity')
        b = self.hashbits
        if b != other_hash.hashbits:
            raise Exception('Hashes must be of equal size to find similarity')
        return float(b - self.hamming_distance(other_hash)) / b
