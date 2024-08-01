nums = [1, 2, 3, 4, 5, 6, 7]
k = 3

for i in range(1, k + 1):
    tableTemp = []

    for j in range(len(nums)):
        v = j - i
        tableTemp.append(nums[v])

    print(str.format("rotate {index} steps to the right: {table}", index = i, table = tableTemp))