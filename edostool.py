import os, sys

from edoslib import *

def extract(filename, destdir):
    ef = EdosFile(filename)
    
    for line in ef.get_metadata():
        print(line)
    
    side_number = 1
    for block in ef.iter_blocks():
        if block.format_id in (0x7e, 0x7f):
            side_number += 1
        else:
            if ef.type == "disk":
                outname = "block_side%02d_track%03d_head%1d_format%02x.bin" % (side_number, block.trackno, block.head, block.format_id)
                
                open(os.path.join(destdir, outname), "wb").write(block.data)
                
                print("Wrote block to disk, side %d track %3d head %d format %02x" % (side_number, block.trackno, block.head, block.format_id))
        
def pulsestats(srcdir, ext):
    for filename in os.listdir(srcdir):
        if filename.split(".")[1].lower() == ext.lower():
            ef = EdosFile(os.path.join(srcdir, filename))
            metadata = ef.get_metadata()
            
            stats = []
            for block in ef.iter_blocks():
                if ef.type == "disk" and block.format_id == 0x60:
                    statline = ["."] * 64
                    total = 0
                    for c in block.data:
                        statline[c // 4] = "*"
                        total += c - 1
                    
                    stats.append(("".join(statline), block.trackno, block.head, total))
                    
            if len(stats) != 0:
                print("Filename: " + filename + " Title: " + metadata[0])
                
                for statline, trackno, head, total in stats:
                    print("%s %2d %1d %10d" % (statline, trackno, head, total))
                    
                print()
        
def bitstats(srcdir, ext):
    for filename in os.listdir(srcdir):
        if filename.split(".")[1].lower() == ext.lower():
            ef = EdosFile(os.path.join(srcdir, filename))
            metadata = ef.get_metadata()
            
            stats = []
            for block in ef.iter_blocks():
                if ef.type == "disk" and block.format_id == 0xe0:
                    total = 0
                    short = 0
                    med = 0
                    long = 0
                    bs = Bitstream(block.data)
                    while True:
                        a = bs.get_bit()
                        if a == None:
                            break
                            
                        if a == 1:
                            total += 2
                            short += 1
                            
                        else:
                            b = bs.get_bit()
                            if b == None:
                                break
                                
                            if b == 0:
                                total += 3
                                med += 1
                            else:
                                total += 4
                                long += 1
                    
                    stats.append((block.trackno, block.head, total, short, med, long))
                    
            if len(stats) != 0:
                print("Filename: " + filename + " Title: " + metadata[0])
                
                for trackno, head, total, short, med, long in stats:
                    print("%2d %1d %10d %10d %10d %10d" % (trackno, head, total, short, med, long))
                    
                print()

def main():
    cmd = sys.argv[1]
    if cmd == "extract":
        filename = sys.argv[2]
        destdir = sys.argv[3]
        extract(filename, destdir)
        
    elif cmd == "pulsestats":
        srcdir = sys.argv[2]
        ext = sys.argv[3]
        pulsestats(srcdir, ext)
        
    elif cmd == "bitstats":
        srcdir = sys.argv[2]
        ext = sys.argv[3]
        bitstats(srcdir, ext)
        
    else:
        raise Exception("unknown command", cmd)

if __name__ == "__main__":
    main()