import sys
from itertools import chain , combinations
from collections import defaultdict
from optparse import OptionParser

def subsets(arr):
    #returns nonempty subsets of arr
    return chain(*[combinations(arr , i+1) for i , a in enumerate(arr)])

def returnItemsWithMinSupport(itemSet , transactionList , minSupport , freqSet):
    #calculates the support for items in the itemSet and retutns a subset of the itemSet each of whose elements satisfies the minSupport
    _itemSet = set()
    localSet = defaultdict(int)

    for item in itemSet:
        for transaction in transactionList:
            if item.issubset(transaction) :
                freqSet[item] += 1
                localSet[item] += 1
    for item, count in localSet.items():
        support = float(count)/len(transaction)
        if support >= minSupport:
            _itemSet.add(item)
    return _itemSet

def joinSet(itemSet , length):
    #join a set with itself and returns the n-element itemsets
    return  set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])

def getItemSetTranactionList(data_iterator):
    transactionList = list()
    itemSet = set()
    for record in data_iterator :
        transaction = frozenset(record)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(frozenset([item]))
    return itemSet , transactionList

def runApriori(data_iter , minSupport , minConfidence):
    #run the apriori algorithm, data_iter is a record iterator
    #return both : items(tuple , support)
    #              rules((pretuple , posttuple) , confidence)
    itemSet, transactionList = getItemSetTranactionList(data_iter)
    freqSet = defaultdict(int)
    largeSet = dict()
    #global dictionary which stores (key = n-itemSet , value = support)
    #which satisfy minSupport
    oneCSet = returnItemsWithMinSupport(itemSet , transactionList ,minSupport , freqSet)
    currentLSet = oneCSet
    k = 2
    while(currentLSet != set([])):
        largeSet[k-1] = currentLSet
        currentLSet = joinSet(currentLSet , k)
        currentCSet = returnItemsWithMinSupport(currentLSet , transactionList, minSupport ,freqSet)
        currentLSet = currentCSet
        k = k + 1

    def getSupport(item):
        #returns the support of an item
        return float(freqSet[item])/len(transactionList)

    toRetItems = []
    largest = []
    max = 0
    for key ,  value in largeSet.items():
        for item in value :
            if getSupport(item) > minSupport :
                if len(item) > max:
                    max = len(item)
    print('\n----------Largest Frequent Itemsets --------------\n')
    for key ,  value in largeSet.items():
        toRetItems.extend([(tuple(item), getSupport(item)) for item in value if getSupport(item) >= minSupport])
        largest.extend([(tuple(item), getSupport(item)) for item in value if getSupport(item) >= minSupport and len(item) == max])
    for i in range(len(largest)):
        print(largest[i])
    toRetRules = []
    print('\n-----------All Frequent Itemsets------------------\n')
    for key , value in largeSet.items():
        for item in value :
            _subsets = map(frozenset, [x for x in subsets(item) if getSupport(item) >= minSupport])
            for element in _subsets:
                remain = item.difference(element)
                if len(remain) > 0 :
                    confidence = getSupport(item)/getSupport(element)
                    if confidence >= minConfidence :
                        toRetRules.append(((tuple(element) , tuple(remain)), confidence))
    return toRetItems , toRetRules

def printResults(items ,  rules):
    for item , support in sorted(items , key =lambda support: support):
        print("item: " , str(item) , " , support : " , support)

    print("\n ---------Association Rules--------------\n")

    for rule , confidence in sorted(rules , key=lambda confidence: confidence):
        pre , post = rule
        print("Rule: " , str(pre) , " ==> " , str(post), " , confidence : " , confidence)

def dataFromFile(fname):
    file_iter = open(fname , 'rU')
    for line in file_iter:
        line = line.strip().rstrip(',')
        record = frozenset(line.split(','))
        yield record

if __name__ == "__main__":
    inFile1 = dataFromFile('Market_Basket_Optimisation.csv')
    minSupport = 0.5
    minConfidence = 0.3
    items , rules = runApriori(inFile1 , minSupport , minConfidence)
    printResults(items , rules)