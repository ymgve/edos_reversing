
# EDOS CD-ROM overview

## EDOS background
EDOS was an attempt at an alternative method of distributing software back in the late 80s/early 90s in Europe.
Instead of stores having a backroom full of individual games on tape and floppy, they instead had a collection
of blank tapes and floppies, and a custom computer that could write the games to tape/floppy while you waited.

The participating stores with the system got periodic updates with new games on CD-ROMs, and this is an attempt
at reverse engineering the formats on those CD-ROMs without having the rest of the hardware for the system.

At the moment I have found two different CD-ROMs, both from late 1992. If anyone has any other CDs from this system,
or even parts of the hardware that the system used, I'd love to get in touch with you.

Websites with more info about the system:

https://blog.amigaguru.com/edos-the-software-on-demand-of-the-80s/

https://www.cpc-power.com/cpcarchives/index.php?page=articles&num=318

https://amiga.abime.net/publishers/view/edos-software-on-demand

https://cpcrulez.fr/games-company-british_telecom_buys_edos_firm.htm


## CD-ROM content
Game data files: numbered folders, containing files with filenames `Pxxxxxxx.Ayy` where `xxxxxxx` is the title ID and `yy` is the platform ID (see platform ID list)
 - example: `P0001099.A42` is title ID 1099 and platform ID 42
 - each file contains the data for one game for one platform, one file can contain data for multiple destination floppies/tapes

Catalog files: filenames `xxxxyyyy.zzZ`

Duplication data file: `DUPLDATA.Z99`

### Platform list
    ID      Platform                Physical format          # known titles
    A02     AMSTRAD 464/6128        3 INCH DISK                         150
    A35     ATARI ST                3.5 INCH DISK                       268
    A36     AMIGA                   3.5 INCH DISK                       245
    A37     PC COMPATIBLE           3.5 INCH DISK                       218
    A42     AMSTRAD 464/6128        CASSETTE / K7                       414
    A43     SPECTRUM 48K/128K/+     CASSETTE / K7                       425
    A44     COMMODORE 64/128        CASSETTE / K7                       373
    A48     MSX                     CASSETTE / K7                        11
    A54     COMMODORE 64/128        5.25 INCH DISK                       94
    A57     PC COMPATIBLE           5.25 INCH DISK                      216
    A60     maybe SEGA console? TODO
    A70     maybe SEGA console? TODO

## Catalog files
- filenames `xxxxyyyy.zzZ` where `xxxx`, `yyyy` and `zz` are numbers of currently unknown meaning, example `00070401.04Z`
- best guess: `xxxx` is the issue number of the CD, 7 on the CD from September 1992 and 8 on the CD from November 1992. `yyyy` and `zz` might be country codes (different prices in different currencies and different catalog selections in each market)
- PKZIP files, password protected, the password is `SAMSON`
- Each zip file contains null-separated list of text lines, 17 lines per entry

### Example entry
    000000935                       title ID
    COUNT DUCKULA                   title name
    ALTERNATIVE SOFTWARE            publisher
    ATARI ST                        platform
    3.5 INCH DISK                   media format
    00000000000799                  retail price
    00000000000391                  gross price?
    N                               always N
                                    developer
    000                             compatibility flags?
    003                             003 when `xxxx` is 7, 004 when it is 8
    01                              number of disks?
    0                               always 0, except for two titles
                                    always empty
    270892                          some date, last time entry updated?
    N                               always N
                                    always empty

## Game data files
- Three types of files, tape files, disk files, and Sega files (TODO)
- Tape and disk files start with a 512 byte encrypted metadata section, containing much of the same data as the catalog files


### Metadata decryption algorithm
    def decryptmetadata(data):
        sbox_i = [126, 64, 19, 187, 247, 222, 80, 197, 245, 163, 169, 189, 193, 28, 143, 161, 182, 116, 145, 18, 70, 156, 178, 218, 148, 219, 39, 147, 229, 77, 48, 158, 127, 96, 216, 61, 160, 231, 49, 190, 107, 0, 35, 238, 29, 71, 121, 117, 85, 8, 78, 202, 241, 146, 214, 150, 184, 2, 76, 20, 164, 138, 86, 68, 3, 93, 13, 38, 246, 170, 152, 5, 135, 242, 133, 69, 103, 207, 82, 172, 59, 154, 209, 58, 253, 132, 129, 221, 115, 217, 66, 235, 185, 100, 255, 168, 237, 249, 4, 7, 94, 244, 124, 205, 114, 102, 21, 130, 191, 165, 42, 63, 142, 113, 41, 65, 16, 12, 118, 120, 125, 83, 180, 79, 112, 72, 24, 43, 149, 25, 95, 233, 227, 228, 141, 234, 192, 203, 62, 47, 105, 131, 111, 239, 14, 232, 87, 208, 155, 92, 136, 22, 140, 6, 27, 212, 26, 40, 55, 37, 188, 199, 123, 162, 52, 201, 99, 215, 195, 176, 32, 196, 15, 250, 53, 81, 60, 194, 10, 84, 122, 31, 119, 75, 98, 179, 134, 1, 34, 128, 88, 89, 45, 109, 151, 252, 226, 240, 17, 139, 175, 67, 166, 224, 91, 230, 36, 213, 159, 211, 198, 137, 200, 44, 57, 171, 206, 248, 254, 51, 108, 11, 74, 9, 73, 174, 186, 104, 251, 144, 220, 153, 181, 173, 157, 23, 54, 50, 110, 210, 33, 243, 236, 204, 97,30, 106, 101, 223, 167, 183, 90, 177, 225, 56, 46]
        key1 = [0, 63, 120, 63, 63, 168, 167, 216, 31, 250, 55, 201, 190, 202, 45, 170, 216]
        key2 = [64, 63, 248, 198, 162, 188, 71, 114, 158, 38, 202, 22, 188, 53, 249, 194, 9, 232, 211]
        
        res = ""
        for i in xrange(len(data)):
            t = ord(data[i])
            t = sbox_i[t] ^ key1[i % len(key1)] ^ key2[i % len(key2)]
            res += chr(t)
            
        return res

### Tape file format
After the encrypted metadata, tape files are a sequence of blocks, each block starting with a 10 byte header: (All values are big endian)
    
    offset  size        
    00      2       gap size before data (maybe multiplies of 156.25 ms)
    02      2       tape system ID (mostly matches last digit of platform ID)
    04      2       number of header syncs (loader specific?)
    06      2       lower 16 bits of data size
    08      1       format ID
    09      1       upper bits of data size if above 64K, can also be 0xff
    0a      sz      data block (loader specific, generally pulse lengths)

Tape system ID and format ID together indicates which custom function should be used to write data to tape. A few IDs are special:

    ff      native format for system (Example: KERNAL loader for C64)
    7e      not actually a data block, but a special indicator that the system
            operator should insert a new tape
    7f      not actually a data block, but a special indicator that the system
            operator should flip the tape
    
For more detailed description of formats, look in the DUPLDATA section (todo)

### Disk file format
Disk files are slightly different from tape files. After the encrypted metadata, a halfword specifies the size of the full header. Then follows all the headers for the file in sequence. After that, data blocks follow, one for each header. Header description: (All values are big endian)

    offset  size
    00      1       track number
    01      1       head number
    02      2       disk system ID
    04      2       always either 0x000a or 0x1000 (purpose not known)
    06      2       data size
    08      1       format ID
    09      1       always 0 (maybe upper bits of data size?)

In contrast with tapes, there are only a few format IDs:

    14      unknown, only used in Interphase for Amiga (TODO)
    60      data contains raw flux lengths for the track
    e0      data contains compressed bits (MFM or GCR) for the track
    7e      not actually a data block, but a special indicator that the system
            operator should insert a new disk
    7f      not actually a data block, but a special indicator that the system
            operator should flip the disk (Only used for Amstrad)
    
#### Disk format type 0x60 for Amiga
Data block starts at hole sync. Each byte represents the distance to the next flux transtition, measured in approx `byteval` * 35ns

TODO get more precise measurement, this works for most games but not all
TODO see how very large distances are handled

#### Disk format type 0xe0 for Amiga
Data block starts at hole sync. To get the raw MFM bits, read the data block as a MSB bit stream and translate, then write with standard 2us bitcell size

    src     dst
    1       01
    00      001
    01      0001

## Duplication data files
This is a PKZIP file that seems to contain files with various parameters and functions for the writing process.

### CDUPALL.BIN
Machine code for the 6809 tape controller. See separate document for format/assumed hardware specs

### INCOMPAT.DAT
Text file containing some platform descriptions, according to file name related to incompatibilities

### PDC.0xx, UDC.0xx
TODO

### WRTIMING.BIN
Timing data for the 6809 tape controller. Se separate document for format
