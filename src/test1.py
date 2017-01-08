import test2

test2.init()
print "Global variable from test 1: ", test2.globvar

list = [1,2,3,4,5]
print list

while list:
    del(list[0])
    print list