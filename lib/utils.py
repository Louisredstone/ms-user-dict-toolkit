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