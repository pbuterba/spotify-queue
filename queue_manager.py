total_seconds = 0

while total_seconds / 60 < 110:
    duration = input('Enter duration: ')
    minutes = int(duration.split(':')[0])
    seconds = int(duration.split(':')[1])
    add_seconds = (minutes * 60) + seconds
    total_seconds = total_seconds + add_seconds
    print(f'{total_seconds // 60}:{total_seconds - ((total_seconds // 60)*60)}')

print('STOP - Add song here')
