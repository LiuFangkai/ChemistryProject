def param(a,**y):
    sum=a
    # for x in y:
    #     if(len(y)==1):
    #         if(x=='b'):
    #             sum=sum+y[x]
    #         elif(x=='c'):
    #             sum=sum-y[x]
    #         else:
    #             sum=sum*y[x]
    #     elif(len(y)==0):
    #         pass
    #     else:
    #         sum=sum+y[x]
    if('b' in y and 'c' in y):
        sum=sum+y['b']
    elif('c' in y and 'b' not in y):
        sum=sum-y['c']
    else:
        sum=10*sum
    return sum

def result(a,**y):
    return 10*param(a,**y)

if __name__ == '__main__':
    dict={'b':2,'c':1,'d':0.0}
    # sum=param(1,**dict)
    # print(sum)

    dels=[]
    for key in dict.keys():
        if(dict[key]==0):
           dels.append(key)
        else:
            pass

    for key in dels:
        del dict[key]
    print(dict)