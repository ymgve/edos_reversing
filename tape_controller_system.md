# EDOS tape controller system

## Hardware
(everything here is best guesses based on analyzing the C64 tape code, since I have not actually seen the hardware)
- 6809 CPU, exact clock frequency uknown
- 6522 CIA at `0xc000` for tape communication, maybe clocked at half frequency of 6809
   - output register B is connected to some hardware
      - upper bit is output pulses to tape
   - input register A connected to some hardware
      - status bit `0x08` set at start means code returns with error code 1
      - status bit `0x20` cleared at start means code returns with error code 2
      - status bit `0x10` cleared means ready for write?
- possibly second 6522 CIA at `0xc010` for communication with the host system
   - reading from `0xc011` returns bytes sent from the host system

## CDUPALL.BIN
Contains code snippets for writing various types of formats to tape

    offset  size
    0x0000  4       EC BD 0B 51 - magic bytes?
    0x0004  4       "1.00" - version number? (Same on both known CDs)
    0x0008  4       00 18 00 00 - maybe offset to start of table at 0x0018
    0x000c  4       00 18 07 00 - maybe offset to start of code snippets at 0x0718
    0x0010  4       00 02 05 6F - maybe limits (lo/hi `system_id` then hi `format_id`)
    0x0014  4       00 1F 00 00 - maybe size of metadata + code size
    0x0018  4*0x70*4    table of formats for 4 different systems, 0x70 reserved entries for each system
    0x0718  *       headers and code for writers

The table at `0x0018` consists of 4-byte entries for each writer. To find the correct writer ID, take the `tape system ID` and `format ID` from the block header in the game data file:

    index = (system_id - 2) * 0x70 + format_id
    entry = 0x0018 + index * 4

Format of entries:

    offset  size
    0       1       type: 0 - unused, 1 - offset, 3 - redirect
    1       2       data
    3       1       unused, always 0

Type 1 means `data` is a little endian direct offset to the start of the writer code snippet
Type 3 means the first byte of `data` is a new `system_id` and second byte is a new `format_id` that redirects to another Type 1 entry
Type 2 and others have not been observed

Each code snippet is *prepended* with a 0x1d bytes metadata header, the code snippet offset points to the *end* of this metadata

Format of code snippet (all values little endian):

    offset  size
    -0x1d   1       system_id
    -0x1c   1       format_id
    -0x1b   1       always 0
    -0x1a   4       timestamp in MS-DOS FAT format
    -0x16   0x14    always 0s
    -0x02   2       XMODEM CRC16 checksum of the code snippet
     0x00   2       size of code snippet
     0x02   *       code snippet

## WRTIMING.BIN
Contains write timings for various tape write code snippets (maybe disk too?)
File is a table of entries of size `0x18`, format depended on the writer code currently being used. How to find the specific entry:

    index = (system_id - 1) * 0x70 + format_id
    offset = index * 0x18

## Write procedure
- Host system reads and parses file containing game data, and for each block gets `system_id` and `format_id`
- Host system reads timings from `WRTIMING.BIN` for the corresponding ids
- Host system concatenates timing data and block header into a buffer
- Host system places block data into another buffer
- Host system reads code snippet from `CDUPALL.BIN` and transfers it to the 6809
- 6809 starts executing the code snippet
   - if the 6809 calls `0xf030` (code NOT present in snippets, so inferred), it sequentially gets bytes of timing data + header
   - if the 6809 reads from `0xc011`, it sequentially gets bytes of block data
   - the code snippet communicates with the tape drive and writes pulses, returns with a status code when done

