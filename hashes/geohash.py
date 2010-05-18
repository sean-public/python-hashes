"""
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
prefix is, the closer the two places are.

Part of python-hashes by sangelone. See README and LICENSE.
Based on code by Hiroaki Kawai <kawai@iij.ad.jp> and geohash.org
"""

from hashtype import hashtype


class geohash(hashtype):
    _base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
    _base32_map = {}
    for i in range(len(_base32)):
        _base32_map[_base32[i]] = i

    def _encode_i2c(self,lat,lon,lat_length,lon_length):
        precision=(lat_length+lon_length)/5
        a, b = lat, lon
        if lat_length < lon_length:
            a, b = lon, lat
        
        boost = (0,1,4,5,16,17,20,21)
        ret = ''
        for i in range(precision):
                ret += self._base32[(boost[a&7]+(boost[b&3]<<1))&0x1F]
                t = a>>3
                a = b>>2
                b = t
        
        return ret[::-1]

    def encode(self, latitude, longitude, precision):
        if latitude >= 90.0 or latitude < -90.0:
                raise Exception("invalid latitude")
        while longitude < -180.0:
                longitude += 360.0
        while longitude >= 180.0:
                longitude -= 360.0
        
        lat = latitude/180.0
        lon = longitude/360.0
        
        lat_length=lon_length=precision*5/2
        if precision%2==1:
                lon_length+=1
        
        if lat>0:
                lat = int((1<<lat_length)*lat)+(1<<(lat_length-1))
        else:
                lat = (1<<lat_length-1)-int((1<<lat_length)*(-lat))
        
        if lon>0:
                lon = int((1<<lon_length)*lon)+(1<<(lon_length-1))
        else:
                lon = (1<<lon_length-1)-int((1<<lon_length)*(-lon))
        
        self.hash = self._encode_i2c(lat,lon,lat_length,lon_length)

    def _decode_c2i(self, hashcode):
        lon = 0
        lat = 0
        bit_length = 0
        lat_length = 0
        lon_length = 0

        # Unrolled for speed
        for i in hashcode:
                t = self._base32_map[i]
                if bit_length%2==0:
                        lon = lon<<3
                        lat = lat<<2
                        lon += (t>>2)&4
                        lat += (t>>2)&2
                        lon += (t>>1)&2
                        lat += (t>>1)&1
                        lon += t&1
                        lon_length+=3
                        lat_length+=2
                else:
                        lon = lon<<2
                        lat = lat<<3
                        lat += (t>>2)&4
                        lon += (t>>2)&2
                        lat += (t>>1)&2
                        lon += (t>>1)&1
                        lat += t&1
                        lon_length+=2
                        lat_length+=3
                
                bit_length+=5
        
        return (lat,lon,lat_length,lon_length)

    def decode(self):
        (lat,lon,lat_length,lon_length) = self._decode_c2i(self.hash)
        
        lat = (lat<<1) + 1
        lon = (lon<<1) + 1
        lat_length += 1
        lon_length += 1
        
        latitude  = 180.0*(lat-(1<<(lat_length-1)))/(1<<lat_length)
        longitude = 360.0*(lon-(1<<(lon_length-1)))/(1<<lon_length)
        
        return latitude, longitude

    def __init__(self, lat=0.0, long=0.0, precision=12):
        self.encode(lat, long, precision)
