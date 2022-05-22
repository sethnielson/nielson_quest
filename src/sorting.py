import random
import sys
import time
import matplotlib.pyplot as plt

def rand_numb(size, mini, maxi):
    final_list = []
    for i in range(size):
        final_list.append(random.randint(mini,maxi))
    return final_list
    
def swap(list, x, y):
    vari = list[x]
    list[x] = list[y]
    list[y] = vari
    
class bubble_sort:
    def sort(self, list):
        for i in range(len(list)-1):
            for j in range(len(list)-1):
                if list[j] > list[j+1]:
                    swap(list, j, j+1)
                

max_size = sys.argv[1]
max_size = int(max_size)
sorty = bubble_sort()
timing = []
for current_size in range(max_size):
    l = rand_numb(current_size + 1, 0, 30)
    time_1 = time.time()
    sorty.sort(l)
    time_2 = time.time()
    time_f = time_2 - time_1
    "print(l)"
    print("It took ", time_f, "seconds to sort your size: ", current_size, " list")
    timing.append(time_f)

plt.plot(range(1,max_size+1),timing)
plt.show()
    
    
"""list = rand_numb(4, 0, 10)
print(list)
swap(list, 0, 1)
print(list)  


sorty.sort(list)
print(list)"""

