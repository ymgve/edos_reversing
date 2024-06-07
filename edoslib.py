import struct, sys

    
class Bitstream(object):
    def __init__(self, data):
        self.data = data
        self.idx = 0
        self.limit = len(data) * 8
        
    def get_bit(self):
        if self.idx == self.limit:
            return None
            
        c = self.data[self.idx >> 3]
        b = (c >> (7 - (self.idx & 7))) & 1
        self.idx += 1
        return b
        
def decryptmetadata(data):
    sbox_i = [126, 64, 19, 187, 247, 222, 80, 197, 245, 163, 169, 189, 193, 28, 143, 161, 182, 116, 145, 18, 70, 156, 178, 218, 148, 219, 39, 147, 229, 77, 48, 158, 127, 96, 216, 61, 160, 231, 49, 190, 107, 0, 35, 238, 29, 71, 121, 117, 85, 8, 78, 202, 241, 146, 214, 150, 184, 2, 76, 20, 164, 138, 86, 68, 3, 93, 13, 38, 246, 170, 152, 5, 135, 242, 133, 69, 103, 207, 82, 172, 59, 154, 209, 58, 253, 132, 129, 221, 115, 217, 66, 235, 185, 100, 255, 168, 237, 249, 4, 7, 94, 244, 124, 205, 114, 102, 21, 130, 191, 165, 42, 63, 142, 113, 41, 65, 16, 12, 118, 120, 125, 83, 180, 79, 112, 72, 24, 43, 149, 25, 95, 233, 227, 228, 141, 234, 192, 203, 62, 47, 105, 131, 111, 239, 14, 232, 87, 208, 155, 92, 136, 22, 140, 6, 27, 212, 26, 40, 55, 37, 188, 199, 123, 162, 52, 201, 99, 215, 195, 176, 32, 196, 15, 250, 53, 81, 60, 194, 10, 84, 122, 31, 119, 75, 98, 179, 134, 1, 34, 128, 88, 89, 45, 109, 151, 252, 226, 240, 17, 139, 175, 67, 166, 224, 91, 230, 36, 213, 159, 211, 198, 137, 200, 44, 57, 171, 206, 248, 254, 51, 108, 11, 74, 9, 73, 174, 186, 104, 251, 144, 220, 153, 181, 173, 157, 23, 54, 50, 110, 210, 33, 243, 236, 204, 97,30, 106, 101, 223, 167, 183, 90, 177, 225, 56, 46]
    key1 = [0, 63, 120, 63, 63, 168, 167, 216, 31, 250, 55, 201, 190, 202, 45, 170, 216]
    key2 = [64, 63, 248, 198, 162, 188, 71, 114, 158, 38, 202, 22, 188, 53, 249, 194, 9, 232, 211]
    
    res = bytearray()
    for i in range(len(data)):
        t = data[i]
        t = sbox_i[t] ^ key1[i % len(key1)] ^ key2[i % len(key2)]
        res.append(t)
        
    return res

class EdosDiskBlock:
    def __init__(self, headerdata):
        (self.trackno,
         self.head,
         self.system_id,
         self.unknown1,
         self.size,
         self.format_id,
         self.unknown2) = struct.unpack(">BBHHHBB", headerdata)
         
class EdosFile:
    def __init__(self, filename):
        self.filename = filename
        self.base, self.ext = filename.split(".")
        
        if self.ext.upper() in ("A42", "A43", "A44", "A48"):
            self.type = "tape"

        elif self.ext.upper() in ("A02", "A35", "A36", "A37", "A54", "A57"):
            self.type = "disk"
            
        else:
            raise Exception("Unsupported file extension " + self.ext)
        
            
        self.f = open(filename, "rb")
        self.ct = self.f.read(0x200)

    def get_metadata(self):
        pt = decryptmetadata(self.ct)
        
        res = []
        for line in pt.split(b"\xf7"):
            res.append(line.decode("ascii"))
            
        return res
        
    def iter_blocks(self):
        if self.type == "disk":
            headersize = struct.unpack("<H", self.f.read(2))[0]
            headerdata = self.f.read(headersize)

            for i in range(0, headersize, 10):
                block = EdosDiskBlock(headerdata[i:i+10])
                block.data = self.f.read(block.size)
            
                yield block
        
if __name__ == "__main__":
    ef = EdosFile(sys.argv[1])
    for line in ef.get_metadata():
        print(line)
