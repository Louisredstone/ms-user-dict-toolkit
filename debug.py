import argparse
import datetime

def print_hex(data):
    for i in range(len(data)):
        print(f'{data[i]:02X}', end=' ')
        if (i+1) % 4 == 0: print(' ', end='')
        if (i+1) % 16 == 0: print('')
    if len(data) % 16 != 0:
        print('')

def process_file(input_file):
    print(f'Processing file: {input_file}')
    # read binary data from input file
    with open(input_file, 'rb') as f:
        data = f.read()

    # process binary data
    # get first 64 bytes
    fixed_header = data[:64]
    
    assert fixed_header[:20] == bytes([
        0x6D, 0x73, 0x63, 0x68, 
        0x78, 0x75, 0x64, 0x70, 
        0x02, 0x00, 0x60, 0x00, 
        0x01, 0x00, 0x00, 0x00,
        0x40, 0x00, 0x00, 0x00
    ])
    v0 = int.from_bytes(fixed_header[20:24], byteorder='little')
    v1 = int.from_bytes(fixed_header[24:28], byteorder='little')
    v2 = int.from_bytes(fixed_header[28:32], byteorder='little')
    v3 = int.from_bytes(fixed_header[32:36], byteorder='little')
    assert fixed_header[36:] == bytes([0x00]*28)
    n = v2
    assert v0 == 0x40+4*n
    assert v1 == 0x40+28*n
    print('Header info:')
    print(f'\titems count: {n}')
    print(f'\theader length: {v0} bytes')
    assert v1 == len(data)
    print(f'\tfile length: {v1} bytes')
    timestamp = v3
    print(f'\ttimestamp: (UTC) {datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}')
    
    offset_bytes = data[64:v0]
    offsets = [int.from_bytes(offset_bytes[i*4:i*4+4], byteorder='little') for i in range(n)]
    items_bytes = data[v0:]
    
    def process_item(item_bytes):
        if len(item_bytes) != 24:
            raise NotImplementedError(f'Item length is {len(item_bytes)}, expected 24')
        x0 = int.from_bytes(item_bytes[0:4], byteorder='little')
        x1 = int.from_bytes(item_bytes[4:8], byteorder='little')
        x2 = int.from_bytes(item_bytes[8:12], byteorder='little')
        x3 = int.from_bytes(item_bytes[12:16], byteorder='little')
        x4 = int.from_bytes(item_bytes[16:20], byteorder='little')
        x5 = int.from_bytes(item_bytes[20:24], byteorder='little')
        assert x0 == 0x00100010, f'Unexpected x0 value: {x0}'
        assert 0x06000014 < x1 < 0x06FF0014, f'Unexpected x1 value: {x1}'
        i_candidate = (x1 - 0x06000014) >> 16
        print(f'\ti_candidate: {i_candidate}')
        assert x2 == 0x00000000, f'Unexpected x2 value: {x2}'
        print(f'\tx3: {x3:08X}')
        pinyin = item_bytes[16:20].decode('utf-16')
        print(f'\tpinyin: {pinyin}')
        phrase = item_bytes[20:24].decode('utf-16')
        print(f'\tphrase: {phrase}')

    for i in range(n):
        start = offsets[i]
        end = offsets[i+1] if i < n-1 else None
        item_bytes = items_bytes[start:end]
        print(f'Item {i+1}:')
        process_item(item_bytes)
        print('')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, help='Input file path')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    process_file(args.input)