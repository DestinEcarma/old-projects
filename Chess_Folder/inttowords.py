from lib2to3.pytree import Node


class Solution(object):
    def addTwoNumbers(self, l1, l2):
        str(l1)
        for i in range(len(l1)//2):
            j = len(l1) - i - 1
            l1[i], l1[j] = l1[j], l1[i]
        
        for i in range(len(l2)//2):
            j = len(l2) - i - 1
            l2[i], l2[j] = l2[j], l2[i]

        s1 = ""
        s2 = ""
        
        for i in l1:
            s1 += str(i)
        
        for i in l2:
            s2 += str(i)
        
        num3 = str(int(s1) + int(s2))
        return list(reversed(num3))

print(Solution().addTwoNumbers([2,4,3], [5,6,4]))