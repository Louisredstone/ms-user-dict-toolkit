import os, sys

def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)
        
add_path('.')

from lib.user_dict import UserDict
from lib.utils import hex_str

root, dirs, files = next(os.walk('analysis'))

passed = 0
failed = 0
for file in files:
    if file.endswith('.dat'):
        filepath = os.path.join(root, file)
        print(f"Testing on {filepath}.")
        with open(filepath, 'rb') as f:
            data = f.read()
        user_dict = UserDict(data)
        produced_data = user_dict.to_bytes()
        if data == produced_data:
            print(f'Test passed for {file}.')
            passed += 1
        else:
            print(f'Test failed for {file}.')
            print(f'Original file content:')
            print(hex_str(data))
            print(f'Produced file content:')
            print(hex_str(produced_data))
            failed += 1

print(f'Total: {passed+failed}, Passed: {passed}, Failed: {failed}')