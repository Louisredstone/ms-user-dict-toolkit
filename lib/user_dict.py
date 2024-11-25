import yaml
from .utils import hex_str

class UserDict:
    def __init__(self, data=None):
        self.utctimestamp = -1
        self.items = []
        if data: self._init_from_bytes(data)
        
    def add_item(self, pinyin: str, phrase: str, i_candidate: int=1, sql_key: int=0xbeefcafe):
        assert isinstance(pinyin, str), "pinyin should be a string"
        assert isinstance(phrase, str), "phrase should be a string"
        assert isinstance(i_candidate, int) and 1 <= i_candidate <= 9, "i_candidate should be an integer"
        assert isinstance(sql_key, int), "sql_key should be an integer"
        self.items.append(dict(
            pinyin=pinyin,
            i_candidate=i_candidate,
            phrase=phrase,
            sql_key=sql_key
        ))
        
    def to_bytes(self):
        # fixed header
        result = bytes([
            0x6D, 0x73, 0x63, 0x68, 
            0x78, 0x75, 0x64, 0x70, 
            0x02, 0x00, 0x60, 0x00, 
            0x01, 0x00, 0x00, 0x00,
            0x40, 0x00, 0x00, 0x00
        ])
        n = len(self.items)
        items_start = 0x40+4*n
        # data_length = 0x40+4*n+sum((len(item['pinyin'])+len(item['phrase'])+2)*2+16 for item in self.items)
        items_bytes = [
            bytes([0x10, 0x00, 0x10, 0x00])
            + bytes([(len(item['pinyin'])+1)*2+16, 0x00, item['i_candidate'], 0x06])
            + bytes([0x00]*4)
            + item['sql_key'].to_bytes(4, byteorder='little')
            + item['pinyin'].encode('utf-16-le') + bytes([0x00]*2)
            + item['phrase'].encode('utf-16-le') + bytes([0x00]*2)
            for item in self.items
        ]
        data_length = 0x40+4*n+sum(len(item_bytes) for item_bytes in items_bytes)
        offset_bytes = []
        acc = 0
        for item_bytes in items_bytes:
            offset_bytes.append(int.to_bytes(acc, 4, byteorder='little'))
            acc += len(item_bytes)
        result += int.to_bytes(items_start, 4, byteorder='little') # items_start
        result += int.to_bytes(data_length, 4, byteorder='little') # data_length
        result += int.to_bytes(n, 4, byteorder='little') # n
        result += int.to_bytes(self.utctimestamp, 4, byteorder='little') # utctimestamp
        result += bytes([0x00]*28) # reserved
        result += b''.join(offset_bytes)
        result += b''.join(items_bytes)
        return result
    
    def to_dat_file(self, file_path):
        with open(file_path, 'wb') as f:
            f.write(self.to_bytes())
    
    @staticmethod
    def from_dat_file(file_path):
        with open(file_path, 'rb') as f:
            data = f.read()
        return UserDict(data)
    
    def _init_from_bytes(self, data):
        assert self.utctimestamp == -1
        assert len(self.items) == 0
        # get first 64 bytes
        fixed_header = data[:64]
        assert fixed_header[:20] == bytes([
            0x6D, 0x73, 0x63, 0x68, 
            0x78, 0x75, 0x64, 0x70, 
            0x02, 0x00, 0x60, 0x00, 
            0x01, 0x00, 0x00, 0x00,
            0x40, 0x00, 0x00, 0x00
        ])
        items_start = int.from_bytes(fixed_header[20:24], byteorder='little')
        data_length = int.from_bytes(fixed_header[24:28], byteorder='little')
        n = int.from_bytes(fixed_header[28:32], byteorder='little')
        utctimestamp = int.from_bytes(fixed_header[32:36], byteorder='little')
        assert fixed_header[36:] == bytes([0x00]*28)
        assert items_start == 0x40+4*n
        assert data_length == len(data)
        self.utctimestamp = utctimestamp
        offset_bytes = data[64:items_start]
        offsets = [int.from_bytes(offset_bytes[i*4:i*4+4], byteorder='little') for i in range(n)]
        items_bytes = data[items_start:]
        
        def parse_item(item_bytes):
            assert item_bytes[0:4] ==  bytes([0x10, 0x00, 0x10, 0x00])
            pinyin_start = 16
            phrase_start = item_bytes[4]
            assert item_bytes[5] == 0x00
            i_candidate = item_bytes[6]
            assert item_bytes[7] == 0x06
            assert item_bytes[8:12] == bytes([0x00]*4)
            sql_key=int.from_bytes(item_bytes[12:16], byteorder='little')
            assert len(item_bytes) % 2 == 0
            assert len(item_bytes) >= 24
            pinyin_bytes = item_bytes[pinyin_start:phrase_start]
            phrase_bytes = item_bytes[phrase_start:]
            pinyin = pinyin_bytes.decode('utf-16-le')
            phrase = phrase_bytes.decode('utf-16-le')
            return dict(
                pinyin=pinyin,
                i_candidate=i_candidate,
                phrase=phrase,
                sql_key=sql_key
            )
            
        for i in range(n):
            start = offsets[i]
            end = offsets[i+1] if i < n-1 else None
            item_bytes = items_bytes[start:end]
            item = parse_item(item_bytes)
            self.items.append(item)
    
    def __str__(self):
        return yaml.dump(self.items)
        
