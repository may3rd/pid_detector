

with open('custom.txt') as f:
    content = f.readlines()

content = [x.strip() for x in content]

try:
    index_of = content.index('test') + 1
except ValueError:
    index_of = -1

print(index_of)