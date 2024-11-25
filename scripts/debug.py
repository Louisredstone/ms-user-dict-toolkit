import argparse
import datetime

def hex_str(data, new_line=16, large_space=4):
    assert new_line > large_space
    result = ''
    for i in range(len(data)):
        result += f'{data[i]:02X} '
        if new_line not in [-1, None] and (i+1) % new_line == 0:
            result += '\n'
        if large_space not in [-1, None] and ((i+1) % new_line) % large_space == 0:
            result += ' '
    return result.strip()

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
    # assert v1 == 0x40+28*n
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
        assert item_bytes[0:4] ==  bytes([0x10, 0x00, 0x10, 0x00])
        pinyin_start = 16
        phrase_start = item_bytes[4]
        assert item_bytes[5] == 0x00
        i_candidate = item_bytes[6]
        assert item_bytes[7] == 0x06
        assert item_bytes[8:12] == bytes([0x00]*4)
        SQL_key = item_bytes[12:16]
        assert len(item_bytes) % 2 == 0
        assert len(item_bytes) >= 24
        pinyin_bytes = item_bytes[pinyin_start:phrase_start]
        phrase_bytes = item_bytes[phrase_start:]
        pinyin = pinyin_bytes.decode('utf-16')
        phrase = phrase_bytes.decode('utf-16')
        print(f'\tpinyin: {pinyin}')
        print(f'\ti_candidate: {i_candidate}')
        print(f'\tphrase: {phrase}')
        print(f'\tSQL_key (unimportant): {hex_str(SQL_key)}')

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