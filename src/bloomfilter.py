
import array
import hashlib
from random import Random


class BitArray(object):

    def __init__(self, size):
        self.bits= array.array('B',[0 for i in range((size+7)//8)] )
    
    def __set__(self, bit, value):
        if value != 1 or value != 0:
            raise ValueError('Only 0 or 1 is accepted as BitArray\'s cells values')
        b = self.bits[bit//8]
        #self.bits[bit//8] = b | 1 << (bit % 8)
        self.bits[bit//8] = b | value << (bit % 8)
    
    def __get__( self, bit):
        b = self.bits[bit//8]
        return (b >> (bit % 8)) & 1


class BloomFilter(object):
    
    def __init__(self, n=None, m=None, k=None, p=None):
        self.m = m
        if k > 128: 
            raise Exception('k value should be lower that 128')
        self.k = k
        self.bits = BitArray(size=m)
        # switch between hashing techniques
        self.__indexes = self.__rand_indexes
        #self.__indexes = self.__hash_indexes

    def __contains__(self, key):
        for i in self.__indexes(key): 
            if not self.bits[i]:
                return False    
        return True 

    def add(self, key):
        dupe = True 
        bits = []
        for i in self.__indexes(key): 
            if dupe and not self.bits[i]:
                dupe = False
            self.bits[i] = 1
            bits.append(i)
        return dupe

    def __and__(self, filter):
        if (self.k != filter.k) or (self.m != filter.m): 
            raise Exception('Must use bloom filters created with equal k / m paramters for bitwise AND')
        return BloomFilter(m=self.m,k=self.k,bits=(self.bits & filter.bits))

    def __or__(self, filter):
        if (self.k != filter.k) or (self.m != filter.m): 
            raise Exception('Must use bloom filters created with equal k / m paramters for bitwise OR')
        return BloomFilter(m=self.m,k=self.k,bits=(self.bits | filter.bits))

    def __hash_indexes(self,key):
        ret = []
        for i in range(self.k):
            ret.append(self.hashes[i](key) % self.m)
        return ret

    def __rand_indexes(self,key):
        self.rand.seed(hash(key))
        ret = []
        for i in range(self.k):
            ret.append(self.rand.randint(0,self.m-1))
        return ret
        
    def __url_hash(self, url):
        """DUEUnit__url_hash():
            Hash function for digesting the URL and URI to fixed size codes for very fast comparison.
            In addition it offers a level of transparency in case the code/hash function will be changed.
            Currently Hash function used is MD5.
        """
        if url:
            hash = hashlib.sh128()
            hash.update(url)
            #using hexdigest() and not digest() because we have to write the hash codes on utf8 files
            hashkey = hash.hexdigest()
            return hashkey
        return None
    
if __name__ == '__main__':
    e = BloomFilter(m=100, k=4)
    e.add('one')
    e.add('two')
    e.add('three')
    e.add('four')
    e.add('five')        

    f = BloomFilter(m=100, k=4)
    f.add('three')
    f.add('four')
    f.add('five')
    f.add('six')
    f.add('seven')
    f.add('eight')
    f.add('nine')
    f.add("ten")        

    # test check for dupe on add
    assert not f.add('eleven') 
    assert f.add('eleven') 

    # test membership operations
    assert 'ten' in f 
    assert 'one' in e 
    assert 'ten' not in e 
    assert 'one' not in f         

    # test set based operations
    union = f | e
    intersection = f & e

    assert 'ten' in union
    assert 'one' in union 
    assert 'three' in intersection
    assert 'ten' not in intersection
    assert 'one' not in intersection