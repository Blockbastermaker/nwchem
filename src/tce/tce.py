# Tensor Contraction Engine v.1.0
# (c) All rights reserved by Battelle & Pacific Northwest Nat'l Lab (2002)
#
# $Id: tce.py,v 1.3 2002-10-23 01:38:52 sohirata Exp $
#

import string
import types
import copy

def readfromfile(filename):
   """Converts the content of a file to a list of tensor contractions"""
   newlist = ListTensorContractions()
   file = open(filename,"r")
   alwaystrue = 1
   while (alwaystrue):
      selfexpr = file.readline()
      if (selfexpr == ""):
         file.close()
         return newlist
      else:
         selfexpr = string.split(selfexpr)
         donewithfactors = 0
         pointer = 1
         coefficients = []
         permutations = []
         while (not donewithfactors):
            if (selfexpr[pointer] == "+"):
               parity = 1
               pointer = pointer + 1
            elif (selfexpr[pointer] == "-"):
               parity = -1
               pointer = pointer + 1
            else:
               # neither "+" or "-"; assume "+" and do not increment pointer
               parity = 1
            coefficients.append(string.atof(selfexpr[pointer]) * parity)
            pointer = pointer + 1
            if (selfexpr[pointer] == "]"):
               permutations.append([])
               donewithfactors = 1
            elif ((selfexpr[pointer] == "*") or (selfexpr[pointer] == "P") or (selfexpr[pointer] == "p")):
               if (selfexpr[pointer] == "*"): 
                  pointer = pointer + 1
               indexes = []
               while (selfexpr[pointer + 1] != ")"):
                  pointer = pointer + 1
                  if (selfexpr[pointer] != "=>"):
                     if (selfexpr[pointer][0] == "h"):
                        type = "hole"
                     elif (selfexpr[pointer][0] == "p"):
                        type = "particle"
                     else:
                        type = "general"
                     label = string.atoi(selfexpr[pointer][1:])
                     newindex = Index(type,label)
                     indexes.append(newindex)
               permutations.append(indexes)
               pointer = pointer + 2
               if (selfexpr[pointer] == "]"):
                  donewithfactors = 1
            else:
               permutations.append([])
         factor = Factor(coefficients,permutations)
         summation = []
         if ("Sum" in selfexpr):
            indexes = []
            pointer = selfexpr.index("Sum")
            while (selfexpr[pointer + 1] != ")"):
               pointer = pointer + 1
               if (selfexpr[pointer] != "("):
                  if (selfexpr[pointer][0] == "h"):
                     type = "hole"
                  elif (selfexpr[pointer][0] == "p"):
                     type = "particle"
                  else:
                     type = "general"
                  label = string.atoi(selfexpr[pointer][1:])
                  newindex = Index(type,label)
                  indexes.append(newindex)
            summation = Summation(indexes)
         tensors=[]
         ntensors = selfexpr[selfexpr.index("]"):].count("*")
         if (ntensors != selfexpr[selfexpr.index("]"):].count("(")):
            return "Wrong input format"
         if ("Sum" in selfexpr):
            ntensors = ntensors - 1
            offset = 2
         else:
            offset = 1
         if (ntensors > 0):
            for itensor in range(0,ntensors):
               counter = 0
               for pointer in range(selfexpr.index("]"),len(selfexpr)):
                  if (selfexpr[pointer] == "*"):
                     counter = counter + 1
                     if (counter == itensor + offset):
                        tensortype = selfexpr[pointer + 1]
                        tensorlabel = itensor + 1
                        anotherpointer = pointer + 2
                        indexes = []
                        while (selfexpr[anotherpointer + 1] != ")"):
                           anotherpointer = anotherpointer + 1
                           if (selfexpr[anotherpointer] != "("):
                              if (selfexpr[anotherpointer][0] == "h"):
                                  type = "hole"
                              elif (selfexpr[anotherpointer][0] == "p"):
                                  type = "particle"
                              else:
                                  type = "general"
                              label = string.atoi(selfexpr[anotherpointer][1:])
                              indexes.append(Index(type,label))
               tensors.append(Tensor(tensortype,indexes,tensorlabel))
      newlist.list.append(TensorContraction(factor,summation,tensors))

def factorial(n):
   """Returns a factorial of an integer n"""
   if (n == 0):
      return 1
   else:
      return n*factorial(n-1)

def permutation(n):
   """Returns a list of all permutation of n integers"""
   if (n == 1):
      result = [[1]]
      return result
   else:
      result = permutation(n-1)
      newresult = []
      for shorterpermutation in result:
         for position in range(0,n):
            newpermutation = copy.deepcopy(shorterpermutation)
            newpermutation.insert(position,n)
            newresult.append(newpermutation)
      return newresult

def permutationwithparity(n):
   """Returns a list of all permutation of n integers, with its first element being the parity"""
   if (n == 1):
      result = [[1,1]]
      return result
   else:
      result = permutationwithparity(n-1)
      newresult = []
      for shorterpermutation in result:
         for position in range(1,n+1):
            parity = shorterpermutation[0]
            for swaps in range(n-position):
               parity = - parity
            newpermutation = copy.deepcopy(shorterpermutation)
            newpermutation.insert(position,n)
            newpermutation[0] = parity
            newresult.append(newpermutation)
      return newresult

def restrictedpermutationwithparity(lista,listb,listc):
   """Returns all permutations of a combined list of three input lists of indexes except those change the orders among the input lists"""
   result = []
   combined = lista + listb + listc
   if (len(combined) < 2):
      return [[1,"empty"]]
   permutations = permutationwithparity(len(combined))
   for permutation in permutations:
      newpermutation = []
      newpermutation.append(permutation[0])
      for position in range(1,len(permutation)):
         newpermutation.append(combined[permutation[position]-1])
      rejected = 0
      for nindexa in range(1,len(newpermutation)):
         for nindexb in range(1,len(newpermutation)):
            if (nindexa < nindexb):
               indexa = newpermutation[nindexa]
               indexb = newpermutation[nindexb]
               if (indexa.type != indexb.type):
                  rejected = 1
               if (indexa.isin(lista) and indexb.isin(lista) and indexa.isgreaterthan(indexb)):
                  rejected = 1
               if (indexa.isin(listb) and indexb.isin(listb) and indexa.isgreaterthan(indexb)):
                  rejected = 1
               if (indexa.isin(listc) and indexb.isin(listc) and indexa.isgreaterthan(indexb)):
                  rejected = 1
      if (not rejected):
         result.append(newpermutation)

   if (not result):
      return [[1,"empty"]]
   else:
      return result

def arethesamepermutation(permutationa,permutationb):
   """Returns true if two permutations are identical"""
   # input parameters are lists of indexes objects
   # [a,b,c,c,a,b] means the permutation a -> c; b -> a ; c -> b
   # so, [a,b,c,c,a,b] == [b,c,a,a,b,c]
   if ((permutationa == []) and (permutationb == [])):
      return 1
   if (permutationa == []):
      for nindex in range(len(permutationb)/2):
         if (not permutationb[nindex].isidenticalto(permutationb[nindex+len(permutationb)/2])):
            return 0
      return 1
   if (permutationb == []):
      for nindex in range(len(permutationa)/2):
         if (not permutationa[nindex].isidenticalto(permutationa[nindex+len(permutationa)/2])):
            print permutationa[nindex].show(),permutationa[nindex+len(permutationa)/2].show()
            return 0
      return 1
   if (len(permutationa) != len(permutationb)):
      return 0
   for nindexa in range(len(permutationa)/2):
      indexa = permutationa[nindexa]
      indexx = permutationa[nindexa+len(permutationa)/2]
      found = 0
      for nindexb in range(len(permutationb)/2):
         indexb = permutationb[nindexb]
         indexy = permutationb[nindexb+len(permutationb)/2]
         if ((indexa.isidenticalto(indexb)) and (indexx.isidenticalto(indexy))):
            found = 1
      if (not found):
         return 0
   return 1
 
def combinepermutations(one,two):
   """Connects two permutations of indexes"""
   if (len(one) == 0):
      return two
   elif (len(two) == 0):
      return one
   elif (len(one) != len(two)):
      return "Internal error"
   three = []
   for n in range(len(one)/2):
      three.append(one[n])
   for n in range(len(one)/2,len(one)):
      for m in range(len(two)/2):
         if (one[n].isidenticalto(two[m])):
            three.append(two[m+len(two)/2])
   return three

def performpermutation(list,permutation,reverse=0):
   """Performs a permutation operation to a list of indexes"""
   result = []
   for indexa in list:
      exist = 0
      if (reverse):
         for nindexb in range(len(permutation)/2,len(permutation)):
            indexb = permutation[nindexb]
            if (indexa.isidenticalto(indexb)):
               result.append(permutation[nindexb-len(permutation)/2])
               exist = 1
      else:
         for nindexb in range(len(permutation)/2):
            indexb = permutation[nindexb]
            if (indexa.isidenticalto(indexb)):
               result.append(permutation[nindexb+len(permutation)/2])
               exist = 1
      if (not exist):
         result.append(indexa)

   return result

def arethesamelists(list1,list2):
   """Returns true if two lists of indexes are the same (permutation allowed)"""
   if (len(list1) != len(list2)):
      return 0
   copylist2 = copy.deepcopy(list2)
   for index in list1:
      exist = 0
      for nindex in range(len(copylist2)):
         if (index.isidenticalto(copylist2[nindex])):
            exist = 1
            del copylist2[nindex]
      if (not exist):
         return 0
   return 1

def picknfromlist(n,list):
   """Returns a list of all possible n choices from a given list"""
   integerlist = []
   for i in range(len(list)):
      integerlist.append(i)
   integerchoices = [[]]
   for i in range(n):
      integerchoices = pick1fromlist(integerchoices,integerlist)
   result = []
   for integerchoice in integerchoices:
      choice = []
      for i in integerchoice:
         choice.append(copy.deepcopy(list[i]))
      result.append(choice)
   return result

def pick1fromlist(choices,list):
   """Appends one additional non-overlapping choice of an integer from the list to the exisiting choices"""
   newchoices = []
   for choice in choices:
      for i in list:
         overlap = 0
         for j in choice:
            if (i <= j):
               overlap = 1
         if (not overlap):
            newchoice = copy.deepcopy(choice)
            newchoice.append(i)
            newchoices.append(newchoice)
          
   return newchoices

def sortindexes(self):
   """Sorts a list of indexes in an ascending order with no regard to parity"""
   selfcopy = copy.deepcopy(self)
   alwaystrue = 1
   while (alwaystrue):
      done = 1
      for nindexa in range(len(selfcopy)):
         indexa = selfcopy[nindexa]
         for nindexb in range(len(selfcopy)):
            if (nindexb <= nindexa):
               continue
            indexb = selfcopy[nindexb]
            if (indexa.isgreaterthan(indexb)):
               swap = copy.deepcopy(indexa)
               selfcopy[nindexa] = copy.deepcopy(indexb)
               selfcopy[nindexb] = swap
               done = 0
      if (done):
         return selfcopy

def printindexes(self):
   """Prints a list of indexes"""
   show = "("
   for index in self:
      show = string.join([show,index.show()])
   show = string.join([show,")"])
   print show

def printpermutation(self):
   """Prints a permutation of indexes"""
   show = "("
   for nindex in range(len(self)/2):
      index = self[nindex]
      show = string.join([show,index.show()])
   show = string.join([show,"=>"])
   for nindex in range(len(self)/2,len(self)):
      index = self[nindex]
      show = string.join([show,index.show()])
   show = string.join([show,")"])
   print show

def expand(nestedlist):
   """Expands a nested list into a non-nested list"""
   result = []
   if (nestedlist):
      for member in nestedlist:
         if (isinstance(member,types.ListType)):
            result = result + expand(member)
         else:
            result.append(member)
      return result
   else:
      return result

def createfactor(permutables,all):
   """Creates a factor object with all possible permutations of indexes in the given permutable list"""
   factor = Factor([0.0],[[]])
   permutations = permutationwithparity(len(permutables))
   for permutation in permutations:
      before = []
      after = []
      parity = permutation[0]
      permutation = permutation[1:len(permutation)]
      for index in all:
         before.append(index)
         replaced = 0
         for ianother in range(len(permutables)):
            another = permutables[ianother]
            if (another.isidenticalto(index)):
               replacedindex = copy.deepcopy(permutables[permutation[ianother]-1])
               replaced = 1
         if (replaced):
            after.append(replacedindex)
         else:
            after.append(index)
      beforeandafter = before + after
      factor.add(Factor([float(parity)/float(factorial(len(permutation)))],[beforeandafter]))
   return factor
 
def writetofile(list,filename):
   """Writes a list to a given file"""
   file = open(filename,"w")
   for n in list:
      file.write(n)
      file.write("\n")

class Index:

   def __init__(self,type="unknown",label=0):
      """Creates a hole/particle/general index of tensors"""
      self.type = type
      self.label = label

   def __str__(self):
      """Prints the content"""
      return self.show()

   def show(self):
      """Returns a human-friendly string of the content"""
      show = string.join([self.type[0], repr(self.label)], "")
      return show

   def isidenticalto(self,another):
      """Returns true if self and another indexes are identical"""
      if ((self.type == another.type) and (self.label == another.label)):
         return 1
      else:
         return 0
 
   def isin(self,list):
      """Returns true if an index is in the list"""
      for index in list:
         if (self.isidenticalto(index)):
            return 1
      return 0

   def isgeneral(self):
      """Returns true if self is a general (as opposed to particle/hole) index"""
      if (self.type == "general"):
         return 1
      else:
         return 0

   def ishole(self):
      """Returns true if self is a hole index"""
      if (self.type == "hole"):
         return 1
      else:
         return 0

   def isparticle(self):
      """Returns true if self is a particle index"""
      if (self.type == "particle"):
         return 1
      else:
         return 0
 
   def isgreaterthan(self,another):
      """Returns true if self should be to the right of another in the canonical order"""
 
      if ((self.type == 'hole') and (another.type == 'particle')):
         return 0
      elif ((self.type == 'hole') and (another.type == 'general')):
         return 0
      elif ((self.type == 'particle') and (another.type == 'hole')):
         return 1
      elif ((self.type == 'particle') and (another.type == 'general')):
         return 0
      elif ((self.type == 'general') and (another.type == 'hole')):
         return 1
      elif ((self.type == 'general') and (another.type == 'particle')):
         return 1
 
      # at this point self.type = another.type
      if (self.label > another.label):
         return 1
      else:
         return 0
 
      return 0

class Factor:

   def __init__(self,coefficients=[],permutations=[]):
      """Creates a numerical and permutation factor of an operator sequence"""
      self.coefficients = coefficients
      self.permutations = copy.deepcopy(permutations)

   def __str__(self):
      """Prints the content"""
      return self.show()

   def show(self,verbose=1):
      """Returns a human-friendly string of contests"""
      if (verbose):
         show = "["
         for n in range(len(self.coefficients)):
            coefficient = self.coefficients[n]
            if (coefficient >= 0.0):
               show = string.join([show,"+",repr(coefficient)])
            elif (coefficient < 0.0):
               show = string.join([show,"-",repr(-coefficient)])
            if (self.permutations[n]):
               show = string.join([show,"* P("])
               for nindex in range(len(self.permutations[n])/2):
                  index = self.permutations[n][nindex]
                  show = string.join([show,index.show()])
               show = string.join([show,"=>"])
               for nindex in range(len(self.permutations[n])/2,len(self.permutations[n])):
                  index = self.permutations[n][nindex]
                  show = string.join([show,index.show()])
               show = string.join([show,")"])
         show = string.join([show,"]"])
      else:
         show = repr(self.coefficients[0])
         if (len(self.coefficients) > 1):
            show = string.join([show,"* P(",repr(len(self.coefficients)),")"])
      return show

   def duplicate(self):
      """Returns a deepcopy"""
      duplicate = Factor(copy.deepcopy(self.coefficients),copy.deepcopy(self.permutations))
      return duplicate

   def multiply(self,factor):
      """Multiply a factor to all coefficients"""
      for n in range(len(self.coefficients)):
         self.coefficients[n] = self.coefficients[n] * factor

   def add(self,another,factor=1.0):
      """Add two Factors together"""
      for m in range(len(another.coefficients)):
         done = 0
         for n in range(len(self.coefficients)):
            if (arethesamepermutation(self.permutations[n],another.permutations[m])):
               self.coefficients[n] = self.coefficients[n] + another.coefficients[m] * factor
               done = 1
         if (not done):
            self.coefficients.append(another.coefficients[m] * factor)
            self.permutations.append(another.permutations[m])

   def isthesameas(self,another):
      """Returns true if two factors are the same to a common scalar multiplier"""
      if (len(self.coefficients) != len(another.coefficients)):
         return 0
      alreadyused = []
      for nself in range(len(self.coefficients)):
         selfpermutation = self.permutations[nself]
         selfcoefficient = self.coefficients[nself]
         found = 0
         for nanother in range(len(another.coefficients)):
            if (nanother in alreadyused):
               continue
            anotherpermutation = another.permutations[nanother]
            anothercoefficient = another.coefficients[nanother]
            if (arethesamepermutation(selfpermutation,anotherpermutation)):
               ratio = anothercoefficient/selfcoefficient
               if ((nself != 0) and (ratio != previousratio)):
                  return 0
               previousratio = ratio
               found = 1
               alreadyused.append(nanother)
         if (not found):
            return 0
      return ratio

   def checkparity(self):
      """Check if the parity of permutations seems correct"""
      for n in range(len(self.coefficients)):
         if (self.permutations[n] == []):
            denominator = self.coefficients[n]
      for n in range(len(self.coefficients)):
         if (self.permutations[n]):
            parity = self.coefficients[n]/denominator
            permutations = permutationwithparity(len(self.permutations[n])/2)
            for permutation in permutations:
               same = 1
               for m in range(len(self.permutations[n])/2):
                  if (not self.permutations[n][m].isidenticalto( \
                          self.permutations[n][permutation[m+1]-1+len(self.permutations[n])/2])):
                     same = 0
               if (same):
                  if (parity != permutation[0]):
                     return 0
      return 1

   def canonicalize(self,permutables):
      """Reorder the permutable indexes in the ascending order"""
      # "Permutable indexes" are the target indexes appearing in one tensor
      # By canonicalizing permutation indexes, one can break down
      # permutation operator into two smaller ones plus take advantage
      # of restricted target index ranges
 
      another = self.duplicate()
      # sort the left half in the ascending order regardless of permutables
      for nfactor in range(len(another.coefficients)):
         coefficient = another.coefficients[nfactor]
         permutation = another.permutations[nfactor]
         done = 0
         while (not done):
            done = 1
            for nindexa in range(len(permutation)/4):
               for nindexb in range(len(permutation)/4):
                  if (nindexa >= nindexb):
                     continue
                  indexa = permutation[nindexa]
                  indexb = permutation[nindexb]
                  if (indexa.isgreaterthan(indexb)):
                     another.permutations[nfactor][nindexb] = copy.deepcopy(indexa)
                     another.permutations[nfactor][nindexa] = copy.deepcopy(indexb)
                     indexc = another.permutations[nfactor][nindexa+len(permutation)/2]
                     indexd = another.permutations[nfactor][nindexb+len(permutation)/2]
                     another.permutations[nfactor][nindexb+len(permutation)/2] = copy.deepcopy(indexc)
                     another.permutations[nfactor][nindexa+len(permutation)/2] = copy.deepcopy(indexd)
                     done = 0
         done = 0
         while (not done):
            done = 1
            for nindexa in range(len(permutation)/4,len(permutation)/2):
               for nindexb in range(len(permutation)/4,len(permutation)/2):
                  if (nindexa >= nindexb):
                     continue
                  indexa = permutation[nindexa]
                  indexb = permutation[nindexb]
                  if (indexa.isgreaterthan(indexb)):
                     another.permutations[nfactor][nindexb] = copy.deepcopy(indexa)
                     another.permutations[nfactor][nindexa] = copy.deepcopy(indexb)
                     indexc = another.permutations[nfactor][nindexa+len(permutation)/2]
                     indexd = another.permutations[nfactor][nindexb+len(permutation)/2]
                     another.permutations[nfactor][nindexb+len(permutation)/2] = copy.deepcopy(indexc)
                     another.permutations[nfactor][nindexa+len(permutation)/2] = copy.deepcopy(indexd)
                     done = 0
      # sort the right half in the ascending order within the permutables
      for nfactor in range(len(another.coefficients)):
         coefficient = another.coefficients[nfactor]
         permutation = another.permutations[nfactor]
         done = 0
         while (not done):
            done = 1
            for nindexa in range(len(permutation)/2,len(permutation)):
               for nindexb in range(len(permutation)/2,len(permutation)):
                  if (nindexa >= nindexb):
                     continue
                  indexa = permutation[nindexa]
                  indexb = permutation[nindexb]
                  if (permutation[nindexa-len(permutation)/2].isin(permutables) and permutation[nindexb-len(permutation)/2].isin(permutables)):
                     if (indexa.isgreaterthan(indexb)):
                        another.permutations[nfactor][nindexb] = copy.deepcopy(indexa)
                        another.permutations[nfactor][nindexa] = copy.deepcopy(indexb)
                        another.coefficients[nfactor] = (-1.0) * coefficient
                        done = 0
      return another

   def product(self,another):
      """Returns a product of two permutation operators"""
      factorobjectiscreated = 0
      for iself in range(len(self.permutations)):
         selfpermutation = self.permutations[iself]
         selfcoefficient = self.coefficients[iself]
         for ianother in range(len(another.permutations)):
            anotherpermutation = another.permutations[ianother]
            anothercoefficient = another.coefficients[ianother]
            productpermutation = combinepermutations(selfpermutation,anotherpermutation)
            productcoefficient = selfcoefficient * anothercoefficient
            if (factorobjectiscreated):
               product.add(Factor([productcoefficient],[productpermutation]))
            else:
               product = Factor([productcoefficient],[productpermutation])
               factorobjectiscreated = 1
      return product

class Summation:

   def __init__(self,indexes=[]):
      """Creates a summation"""
      self.indexes = indexes

   def __str__(self):
      """Prints the content"""
      return self.show()

   def show(self):
      """Returns a human-friendly string of the content"""
      show = "Sum ("
      for index in self.indexes:
         show = string.join([show, index.show()])
      show = string.join([show,")"])
      return show

   def hastheindex(self,another):
      """Returns true if the summation has the input index"""
      has = 0
      for index in self.indexes:
         if (index.isidenticalto(another)):
            has = 1
      return has

class Tensor:

   def __init__(self,type="unknown",indexes=[],label=0):
      """Creates an integral/amplitude"""
      self.type = type
      self.indexes = indexes
      self.label = label

   def __str__(self):
      """Prints the content"""
      return self.show()

   def show(self):
      """Returns a human-friendly string of the content"""
      show = self.type
      if (self.type == "i"):
         show = string.join([show, repr(self.label)],"")
      show = string.join([show, "("])
      for index in self.indexes:
         show = string.join([show, index.show()])
      show = string.join([show,")"])
      return show
 
   def duplicate(self):
      """Makes a copy of itself"""
      duplicate = Tensor()
      duplicate.type = self.type
      duplicate.indexes = copy.deepcopy(self.indexes)
      duplicate.label = self.label
      return duplicate
 
   def usesindexlabel(self,label):
      """Returns true if the input index label is already in use"""
      for index in self.indexes:
         if (index.label == label):
            return 1
      return 0

   def relabels(self,oldlabel,newlabel):
      """Renames an index label (followed by index sort if the tensor is intermediate)"""
      for nindex in range(len(self.indexes)):
         index = self.indexes[nindex]
         if (index.label == oldlabel):
            self.indexes[nindex].label = newlabel
      if (self.type == "i"):
         parity = self.sortindexes()

   def swapindexes(self,indexone,indextwo):
      """Swaps indexes"""
      for nindex in range(len(self.indexes)):
         index = self.indexes[nindex]
         if (index.isidenticalto(indexone)):
            self.indexes[nindex] = indextwo
         elif (index.isidenticalto(indextwo)):
            self.indexes[nindex] = indexone
      if (self.type == "i"):
         parity = self.sortindexes()

   def sortindexes(self):
      """Sort super and sub indexes of tensors in ascending order"""
      parity = 1
      alwaystrue = 1
      while (alwaystrue):
         done = 1
         for nindex in range(len(self.indexes)/2):
            indextype = self.indexes[nindex].type
            indexlabel = self.indexes[nindex].label
            for nanother in range(len(self.indexes)/2):
               if (nindex < nanother):
                  anothertype = self.indexes[nanother].type
                  anotherlabel = self.indexes[nanother].label
                  if ((indextype == 'particle') and (anothertype == 'hole')):
                     done = 0
                     swapa = nindex
                     swapb = nanother
                  elif ((indextype == anothertype) and (indexlabel >= anotherlabel)):
                     done = 0
                     swapa = nindex
                     swapb = nanother
         if (done):
            alwaystrue = 1
            while (alwaystrue):
               done = 1
               for nindex in range(len(self.indexes)/2,len(self.indexes)):
                  indextype = self.indexes[nindex].type
                  indexlabel = self.indexes[nindex].label
                  for nanother in range(len(self.indexes)/2,len(self.indexes)):
                     if (nindex < nanother):
                        anothertype = self.indexes[nanother].type
                        anotherlabel = self.indexes[nanother].label
                        if ((indextype == 'particle') and (anothertype == 'hole')):
                           done = 0
                           swapa = nindex
                           swapb = nanother
                        elif ((indextype == anothertype) and (indexlabel >= anotherlabel)):
                           done = 0
                           swapa = nindex
                           swapb = nanother
               if (done):
                  return parity
               else:
                  swap = self.indexes[swapa]
                  self.indexes[swapa] = self.indexes[swapb]
                  self.indexes[swapb] = swap
                  parity = parity * (-1)
         else:
            swap = self.indexes[swapa]
            self.indexes[swapa] = self.indexes[swapb]
            self.indexes[swapb] = swap
            parity = parity * (-1)

   def isidenticalto(self,another):
      """Returns true if two tensors are identical"""
      if (self.type != another.type):
         return 0
      if (self.label != another.label):
         return 0
      if (len(self.indexes) != len(another.indexes)):
         return 0
      for nindex in range(len(self.indexes)):
         selfindex = self.indexes[nindex]
         anotherindex = another.indexes[nindex]
         if (not selfindex.isidenticalto(anotherindex)):
            return 0
      return 1

   def hasindexeswith(self,another):
      """Returns a non-redundant set of indexes that are in self and another tensors"""
      result = []
      for index in self.indexes:
         alreadyincluded = 0
         for resultindex in result:
            if (index.isidenticalto(resultindex)):
               alreadyincluded = 1
         if (not alreadyincluded):
            result.append(index)
      for index in another.indexes:
         alreadyincluded = 0
         for resultindex in result:
            if (index.isidenticalto(resultindex)):
               alreadyincluded = 1
         if (not alreadyincluded):
            result.append(index)
      return result

   def hascommonindexeswith(self,another):
      """Returns a set of indexes that are commonly in self and another tensors"""
      result = []
      for index in self.indexes:
         for anotherindex in another.indexes:
            if (index.isidenticalto(anotherindex)):
               result.append(index)
      return result

   def contracts(self,another,label):
      """Return the tensor obtained by a contraction of self and another tensors"""

      indexes = self.indexes[0:len(self.indexes)/2] + another.indexes[0:len(another.indexes)/2] \
              + self.indexes[len(self.indexes)/2:]  + another.indexes[len(another.indexes)/2:]

      # Eliminate any common indexes between super/subindexes
      alwaystrue = 1
      while (alwaystrue):
         common = 0
         halflength = len(indexes)/2
         for isuper in range(0,halflength):
            superindex = indexes[isuper]
            for isub in range(halflength,2*halflength):
               subindex = indexes[isub]
               if (superindex.isidenticalto(subindex)):
                  common = 1
                  super = isuper
                  sub = isub
         if (not common):
            # reorder the super and sub indexes individually
            # (I think that the order of indexes of intermediates is immaterial, so we can decide for our convenience.
            #  However, do not mix up super and sub indexes, since otherwise contraction will be screwed up.)
            intermediate = Tensor("i",indexes,label)
            parity = intermediate.sortindexes()
            return intermediate
         else:
            if (super == sub - halflength):
               # preserve the order of deletion
               del indexes[sub]
               del indexes[super]
            else:
               indexes[super] = indexes[sub-halflength]
               # preserve the order of deletion
               del indexes[sub]
               del indexes[sub-halflength]
 
   def isequivalentto(self,another,tensorcontraction):
      """Returns true if two amplitudes are of the same type and are connected in the same way"""
 
      if (self.type != another.type):
         return 0
      if (len(self.indexes) != len(another.indexes)):
         return 0
      # super hole, super particle, super general, sub hole, sub particle, sub general
      selftargets = [0,0,0,0,0,0]
      for iselfindex in range(len(self.indexes)/2):
         selfindex = self.indexes[iselfindex]
         if (not tensorcontraction.summation.hastheindex(selfindex)):
            if (selfindex.type == 'hole'):
               selftargets[0] = selftargets[0] + 1
            elif (selfindex.type == 'particle'):
               selftargets[1] = selftargets[1] + 1
            elif (selfindex.type == 'general'):
               selftargets[2] = selftargets[2] + 1
      for iselfindex in range(len(self.indexes)/2,len(self.indexes)):
         selfindex = self.indexes[iselfindex]
         if (not tensorcontraction.summation.hastheindex(selfindex)):
            if (selfindex.type == 'hole'):
               selftargets[3] = selftargets[3] + 1
            elif (selfindex.type == 'particle'):
               selftargets[4] = selftargets[4] + 1
            elif (selfindex.type == 'general'):
               selftargets[5] = selftargets[5] + 1
      anothertargets = [0,0,0,0,0,0]
      for ianotherindex in range(len(another.indexes)/2):
         anotherindex = another.indexes[ianotherindex]
         if (not tensorcontraction.summation.hastheindex(anotherindex)):
            if (anotherindex.type == 'hole'):
               anothertargets[0] = anothertargets[0] + 1
            elif (anotherindex.type == 'particle'):
               anothertargets[1] = anothertargets[1] + 1
            elif (anotherindex.type == 'general'):
               anothertargets[2] = anothertargets[2] + 1
      for ianotherindex in range(len(another.indexes)/2,len(another.indexes)):
         anotherindex = another.indexes[ianotherindex]
         if (not tensorcontraction.summation.hastheindex(anotherindex)):
            if (anotherindex.type == 'hole'):
               anothertargets[3] = anothertargets[3] + 1
            elif (anotherindex.type == 'particle'):
               anothertargets[4] = anothertargets[4] + 1
            elif (anotherindex.type == 'general'):
               anothertargets[5] = anothertargets[5] + 1
      if (selftargets != anothertargets):
         return 0
      else:
         return 1

   def pythongen(self):
      """Returns a character expression in Python syntax"""
      pythoncode = self.type
      if (self.type == "i"):
         pythoncode = string.join([pythoncode,repr(self.label)],"")
      else:
         pythoncode = string.join([pythoncode,repr(len(self.indexes)/2)],"")
      pythoncode = string.join([pythoncode,"[","("*len(self.indexes)],"")
      if (self.indexes):
         for nindex in range(len(self.indexes)):
            index = self.indexes[nindex]
            if (nindex == 0):
               pythoncode = string.join([pythoncode,index.show(),")"],"")
            else:
               pythoncode = string.join([pythoncode,"*N+",index.show(),")"],"")
      else:
         pythoncode = string.join([pythoncode,"0"],"")
      pythoncode = string.join([pythoncode,"]"],"")
      return pythoncode

   def fortran90(self,permutation=[],reverse=0,suffix=""):
      """Returns a character expression in Fortran90 syntax"""
      f90code = self.type
      if (self.type == "i"):
         f90code = string.join([f90code,repr(self.label),suffix],"")
      else:
         f90code = string.join([f90code,repr(len(self.indexes)/2),suffix],"")
      f90code = string.join([f90code,"(","("*len(self.indexes)],"")
      if (self.indexes):
         for nindex in range(len(self.indexes)):
            if (permutation == []):
               index = self.indexes[nindex]
            else:
               if (reverse):
                  beforeindex = self.indexes[nindex]
                  index = beforeindex
                  for nbeforeindex in range(len(permutation)/2):
                     if (beforeindex.isidenticalto(permutation[nbeforeindex + len(permutation)/2])):
                        index = permutation[nbeforeindex]
               else:
                  beforeindex = self.indexes[nindex]
                  index = beforeindex
                  for nbeforeindex in range(len(permutation)/2):
                     if (beforeindex.isidenticalto(permutation[nbeforeindex])):
                        index = permutation[nbeforeindex+len(permutation)/2]
            if (nindex == 0):
               f90code = string.join([f90code,index.show(),"-1)"],"")
            elif (nindex == len(self.indexes) - 1):
               f90code = string.join([f90code,"*N+",index.show(),")"],"")
            else:
               f90code = string.join([f90code,"*N+",index.show(),"-1)"],"")
      else:
         f90code = string.join([f90code,"1"],"")
      f90code = string.join([f90code,")"],"")
      return f90code

   def fortran90x(self):
      """Anti-symmetrizer"""

      newcode = Code("Fortran90","")
      
      if (not self.indexes):
         return newcode

      # generate loops over indexes
      for index in self.indexes:
         newcode.insertdoloop(index)
      
      # generate anti-symmetrizer statement
      
      nindexes = len(self.indexes)/2
      npermutations = factorial(nindexes)
      permutations = permutationwithparity(nindexes)
      newline = string.join(["TMP = 0.0d0"])
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      for terma in range(npermutations):
         for termb in range(npermutations):
            newindexes = []
            for nindexa in range(1,nindexes+1):
               newindexes.append(self.indexes[permutations[terma][nindexa]-1])
            for nindexb in range(1,nindexes+1):
               newindexes.append(self.indexes[nindexes+permutations[termb][nindexb]-1])
            newtensor = Tensor(self.type,newindexes,self.label)
            if (permutations[terma][0]*permutations[termb][0] == 1):
               parity = "+"
            else:
               parity = "-"
            newline = string.join(["TMP = TMP",parity,newtensor.fortran90()])
            newcode.statements.insert(newcode.pointer,newline)
            newcode.pointer = newcode.pointer + 1
      newline = string.join([self.fortran90()," = TMP / ",repr(npermutations**2),".0d0"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = len(newcode.statements)

      return newcode

   def fortran77x(self,subroutinename="NONAME"):
      """Anti-symmetrizer"""

      errquit = 0

      newcode = Code("Fortran77","ANTISYM_"+subroutinename)
 
      # header
      newline = "!" + self.show()
      newcode.add("headers",newline)
      newline = "IMPLICIT NONE"
      newcode.add("headers",newline)
 
      # insert include statements
      newline = '#include "global.fh"'
      newcode.add("headers",newline)
      newline = '#include "mafdecls.fh"'
      newcode.add("headers",newline)
      newline = '#include "sym.fh"'
      newcode.add("headers",newline)
      newline = '#include "tce.fh"'
      newcode.add("headers",newline)
 
      # declaration
      newint = "d_a"
      newcode.add("integers",newint)
      newcode.add("arguments",newint)
      newint = "k_a_offset"
      newcode.add("integers",newint)
      newcode.add("arguments",newint)
      
      # parallel declaration
      newint = "NXTVAL"
      newcode.add("integers",newint)
      newcode.add("externals",newint)
      newint = "next"
      newcode.add("integers",newint)
      newint = "nprocs"
      newcode.add("integers",newint)
      newint = "count"
      newcode.add("integers",newint)

      super = self.indexes[0:len(self.indexes)/2]
      sub = self.indexes[len(self.indexes)/2:len(self.indexes)]
      all = super + sub
 
      # parallel related
      newline = "nprocs = GA_NNODES()"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "count = 0"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "next = NXTVAL(nprocs)"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1

      # loop over output tensor indexes
      newcode.inserttileddoloops(sub[0:1])
      newcode.inserttileddoloops(super[0:1])
      for index in super:
         if (not index.isidenticalto(super[0])):
            newint = index.show()+"b"
            newcode.add("integers",newint)
            newline = string.join([newint," = ",super[0].show(),"b"],"")
            newcode.statements.insert(newcode.pointer,newline)
            newcode.pointer = newcode.pointer + 1
      for index in sub:
         if (not index.isidenticalto(sub[0])):
            newint = index.show()+"b"
            newcode.add("integers",newint)
            newline = string.join([newint," = ",sub[0].show(),"b"],"")
            newcode.statements.insert(newcode.pointer,newline)
            newcode.pointer = newcode.pointer + 1
      
      # parallel related
      newline = "IF (next.eq.count) THEN"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.setamark(1)
      newcode.pointer = newcode.pointer + 1
      newline = "next = NXTVAL(nprocs)"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "END IF"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "count = count + 1"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.getamark(1) + 1
 
      # symmetry of output tensor
      newcode.inserttiledifsymmetry(super,sub)

      # allocate for original and antisymmetrized tensors
      newcode.add("integers","dim0")
      newline = ""
      for index in all:
         if (newline == ""):
            newline = string.join(["dim0 = int_mb(k_range+",index.show(),"b-1)"],"")
         else:
            newline = string.join([newline," * int_mb(k_range+",index.show(),"b-1)"],"")
      if (newline == ""):
         newline = "dim0 = 1"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newcode.add("integers","l_b")
      newcode.add("integers","k_b")
      newline = string.join(["IF (.not.MA_PUSH_GET(mt_dbl,dim0,'noname',l_b,k_b)) CALL ERRQUIT('",\
                             subroutinename,"',",repr(errquit),")"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      errquit = errquit + 1
      newcode.add("integers","l_a")
      newcode.add("integers","k_a")
      newline = string.join(["IF (.not.MA_PUSH_GET(mt_dbl,dim0,'noname',l_a,k_a)) CALL ERRQUIT('",\
                             subroutinename,"',",repr(errquit),")"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      errquit = errquit + 1

      # get a diagonal block
      newline = "IF (dim0 .gt. 0) THEN"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "END IF"
      newcode.statements.insert(newcode.pointer,newline)
      arguments = ""
      argumentsend = ""
      for nindex in range(len(all)-1,-1,-1):
         if (all[nindex].type == "hole"):
            boffset = "b - 1"
         else:
            boffset = "b - noab - 1"
         if (arguments == ""):
            arguments = string.join(["d_a,dbl_mb(k_a),dim0,int_mb(k_a_offset + ",all[nindex].show(),boffset],"")
         else:
            if (all[nindex+1].type == "hole"):
               arguments = string.join([arguments," + noab * (",all[nindex].show(),boffset],"")
            else:
               arguments = string.join([arguments," + nvab * (",all[nindex].show(),boffset],"")
            argumentsend = string.join([argumentsend,")"],"")
      arguments = string.join([arguments,argumentsend,")"],"")
      newline = string.join(["CALL GET_BLOCK(",arguments,")"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1

      # do loops over indexes in the diagonal block
      for nindex in range(len(all)):
         index = all[nindex]
         newint = index.show()
         newcode.add("integers",newint)
         newline = string.join(["DO ",newint," = 1,int_mb(k_range+",index.show(),"b-1)"],"")
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1
         newline = "END DO"
         newcode.statements.insert(newcode.pointer,newline)
         if (nindex == 0):
            newcode.setamark(2)

      # permutations
      newline = ""
      newlineend = ""
      newcode.add("integers","idim0")
      for nindex in range(len(all)-1,-1,-1):
         if (newline == ""):
            newline = string.join(["idim0 = ",all[nindex].show()],"")
         else:
            newline = string.join([newline," + int_mb(k_range+",all[nindex+1].show(),"b-1)"\
                                   " * ((",all[nindex].show()," - 1)"],"")
            newlineend = string.join([newlineend,")"],"")
      newline = string.join([newline,newlineend],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1

      oldline = ""
      integerlabel = 0
      # the following does not mean this is for super alone, len(super)
      # is used just to get half the number of indexes
      permutations = permutationwithparity(len(super))
      for permutationa in permutations:
         for permutationb in permutations:
            integerlabel = integerlabel + 1
            newint = "idim"+repr(integerlabel)
            newcode.add("integers",newint)
            newindexes = []
            for nindexa in range(1,len(super)+1):
               newindexes.append(self.indexes[permutationa[nindexa]-1])
            for nindexb in range(1,len(super)+1):
               newindexes.append(self.indexes[len(super)+permutationb[nindexb]-1])
            newline = ""
            newlineend = ""
            for nindex in range(len(all)-1,-1,-1):
               if (newline == ""):
                  newline = string.join([newint," = ",newindexes[nindex].show()],"")
               else:
                  newline = string.join([newline," + int_mb(k_range+",newindexes[nindex+1].show(),"b-1)"\
                                         " * ((",newindexes[nindex].show()," - 1)"],"")
                  newlineend = string.join([newlineend,")"],"")
            newline = string.join([newline,newlineend],"")
            newcode.statements.insert(newcode.pointer,newline)
            newcode.pointer = newcode.pointer + 1
            if (permutationa[0] * permutationb[0] == 1):
               if (oldline):
                  oldline = string.join([oldline," + dbl_mb(k_a + ",newint," - 1)"],"")
               else:
                  oldline = string.join(["dbl_mb(k_b + idim0 - 1) = (dbl_mb(k_a + ",newint," - 1)"],"")
            else:
               if (oldline):
                  oldline = string.join([oldline," - dbl_mb(k_a + ",newint," - 1)"],"")
               else:
                  oldline = string.join(["dbl_mb(k_b + idim0 - 1) = (-dbl_mb(k_a + ",newint," - 1)"],"")
      factor = float(factorial(len(super))*factorial(len(sub)))
      newline = string.join([oldline,") * ",repr(1.0/factor),"d0"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1

      newcode.pointer = newcode.getamark(2) + 1
      arguments = ""
      argumentsend = ""
      for nindex in range(len(all)-1,-1,-1):
         if (all[nindex].type == "hole"):
            boffset = "b - 1"
         else:
            boffset = "b - noab - 1"
         if (arguments == ""):
            arguments = string.join(["d_a,dbl_mb(k_b),dim0,int_mb(k_a_offset + ",all[nindex].show(),boffset],"")
         else:
            if (all[nindex+1].type == "hole"):
               arguments = string.join([arguments," + noab * (",all[nindex].show(),boffset],"")
            else:
               arguments = string.join([arguments," + nvab * (",all[nindex].show(),boffset],"")
            argumentsend = string.join([argumentsend,")"],"")
      arguments = string.join([arguments,argumentsend,")"],"")
      newline = string.join(["CALL PUT_BLOCK(",arguments,")"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = string.join(["IF (.not.MA_POP_STACK(l_a)) CALL ERRQUIT('",subroutinename,"',",repr(errquit),")"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      errquit = errquit + 1
      newline = string.join(["IF (.not.MA_POP_STACK(l_b)) CALL ERRQUIT('",subroutinename,"',",repr(errquit),")"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      errquit = errquit + 1

      newcode.pointer = len(newcode.statements)
      newline = "next = NXTVAL(-nprocs)"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "call GA_SYNC()"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "RETURN"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "END"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      return newcode

   def fortran77y(self,globaltargetindexes,subroutinename="NONAME"):
      """Precompute offsets and size"""

      errquit = 0

      newcode = Code("Fortran77","OFFSET_"+subroutinename)
 
      # header
      newline = "!" + self.show()
      newcode.add("headers",newline)
      newline = "IMPLICIT NONE"
      newcode.add("headers",newline)
 
      # insert include statements
      newline = '#include "global.fh"'
      newcode.add("headers",newline)
      newline = '#include "mafdecls.fh"'
      newcode.add("headers",newline)
      newline = '#include "sym.fh"'
      newcode.add("headers",newline)
      newline = '#include "tce.fh"'
      newcode.add("headers",newline)
 
      # declaration
      newint = "d_a"
      newcode.add("integers",newint)
      newcode.add("arguments",newint)
      newint = "l_a_offset"
      newcode.add("integers",newint)
      newcode.add("arguments",newint)
      newint = "k_a_offset"
      newcode.add("integers",newint)
      newcode.add("arguments",newint)
      newint = "size"
      newcode.add("integers",newint)
      newcode.add("arguments",newint)

      # allocate offsets
      arguments = ""
      for index in self.indexes:
         if (index.type == "hole"):
            factor = "noab"
         else:
            factor = "nvab"
         if (arguments):
            arguments = string.join([arguments,"*",factor],"")
         else:
            arguments = factor
      if (arguments == ""):
         arguments = "1"
      newline = string.join(["IF (.not.MA_PUSH_GET(mt_int,",arguments,",'noname',l_a_offset,k_a_offset)) CALL ERRQUIT('",\
                             subroutinename,"',",repr(errquit),")"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      errquit = errquit + 1

      # classify indexes
      globalsuper = []
      localsuper = []
      globalsub = []
      localsub = []
      super = []
      sub = []
      for nindex in range(len(self.indexes)/2):
         index = self.indexes[nindex]
         super.append(index)
         if (index.isin(globaltargetindexes)):
            globalsuper.append(index)
         else:
            localsuper.append(index)
      for nindex in range(len(self.indexes)/2,len(self.indexes)):
         index = self.indexes[nindex]
         sub.append(index)
         if (index.isin(globaltargetindexes)):
            globalsub.append(index)
         else:
            localsub.append(index)

      # do loops and if's
      newline = "size = 0"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newcode.inserttileddoloops(globalsuper)
      newcode.inserttileddoloops(localsuper)
      newcode.inserttileddoloops(globalsub)
      newcode.inserttileddoloops(localsub)
      newcode.inserttiledifsymmetry(super,sub)

      # offsets and size (offset first!)
      newline = ""
      newlineend = ""
      all = globalsuper + localsuper + globalsub + localsub
      for nindex in range(len(all)-1,-1,-1):
         if (all[nindex].type == "hole"):
            boffset = "b - 1"
         else:
            boffset = "b - noab - 1"
         if (newline == ""):
            newline = string.join(["int_mb(k_a_offset + ",all[nindex].show(),boffset],"")
         else:
            if (all[nindex+1].type == "hole"):
               newline = string.join([newline," + noab * (",all[nindex].show(),boffset],"")
            else:
               newline = string.join([newline," + nvab * (",all[nindex].show(),boffset],"")
            newlineend = string.join([newlineend,")"],"")
      if (newline == ""):
         newline = "int_mb(k_a_offset"
      newline = string.join([newline,newlineend,") = size"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = ""
      for index in all:
         if (newline == ""):
            newline = string.join(["size = size + int_mb(k_range+",index.show(),"b-1)"],"")
         else:
            newline = string.join([newline," * int_mb(k_range+",index.show(),"b-1)"],"")
      if (newline == ""):
         newline = "size = 1"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      
      newcode.pointer = len(newcode.statements)
      newline = "RETURN"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "END"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      return newcode

class TensorContraction:

   def __init__(self,factor=[],summation=[],tensors=[]):
      """Creates a tensor contraction"""
      self.factor = factor
      self.summation = summation
      self.tensors = tensors

   def __str__(self):
      """Prints the content"""
      return self.show()

   def show(self):
      """Returns a human-friendly string of the content"""
      show = self.factor.show()
      if (self.summation):
         if (len(self.summation.indexes) > 0):
            show = string.join([show, "*", self.summation.show()])
      for selftensor in self.tensors:
         show = string.join([show, "*", selftensor.show()])
      return show 

   def duplicate(self):
      """Returns a deepcopy"""
      duplicate = TensorContraction(copy.deepcopy(self.factor),copy.deepcopy(self.summation),copy.deepcopy(self.tensors))
      return duplicate

   def findthebestbreakdown(self,verbose=0):
      """Returns the best breakdown in terms of flop costs and then memory costs"""
      ntensors = len(self.tensors)
      nbreakdowns = factorial(ntensors)
      breakdowns = permutation(ntensors)
      print " ... there are %d ways of breaking down the sequence into elementary tensor contractions" % (nbreakdowns)
      if (ntensors == 1):
         ibest = 0
         minoperationcost = [0,0,0]
         minmemorycost = [0,0,0]
      else:
         minoperationcost = [99999,99999,99999]
         minmemorycost = [99999,99999,99999]
         minaggoperationcost = [99999,99999,99999]
         minaggmemorycost = [99999,99999,99999]
         ibest = 0
         for ibreakdown in range(0,nbreakdowns):
            if (verbose):
               print " ... ", ibreakdown + 1, breakdowns[ibreakdown]
            tensorone = self.tensors[breakdowns[ibreakdown][0]-1]
            # The triplets are the exponents of N, O, V
            maxoperationcost = [0,0,0]
            maxmemorycost = [0,0,0]
            aggoperationcost = [0,0,0]
            aggmemorycost = [0,0,0]
            for ielementary in range(0,ntensors-1):
               tensortwo = self.tensors[breakdowns[ibreakdown][ielementary+1]-1]
               allindexes = tensorone.hasindexeswith(tensortwo)
               commonindexes = tensorone.hascommonindexeswith(tensortwo)
               operationcost = [0,0,0]
               memorycost = [0,0,0]
               for index in allindexes:
                  if (index.isgeneral()):
                     operationcost[0] = operationcost[0] + 1
                     memorycost[0] = memorycost[0] + 1
                  elif (index.ishole()):
                     operationcost[1] = operationcost[1] + 1
                     memorycost[1] = memorycost[1] + 1
                  elif (index.isparticle()):
                     operationcost[2] = operationcost[2] + 1
                     memorycost[2] = memorycost[2] + 1
               for index in commonindexes:
                  if (index.isgeneral()):
                     memorycost[0] = memorycost[0] - 1
                  elif (index.ishole()):
                     memorycost[1] = memorycost[1] - 1
                  elif (index.isparticle()):
                     memorycost[2] = memorycost[2] - 1
               aggoperationcost[0] = aggoperationcost[0] + operationcost[0]
               aggoperationcost[1] = aggoperationcost[1] + operationcost[1]
               aggoperationcost[2] = aggoperationcost[2] + operationcost[2]
               aggmemorycost[0] = aggmemorycost[0] + memorycost[0]
               aggmemorycost[1] = aggmemorycost[1] + memorycost[1]
               aggmemorycost[2] = aggmemorycost[2] + memorycost[2]
               if (verbose):
                  print " ...... ",tensorone.show(), tensortwo.show(), operationcost, memorycost
               tensorone = tensorone.contracts(tensortwo,0)
               if (operationcost[0]+operationcost[1]+operationcost[2] > maxoperationcost[0]+maxoperationcost[1]+maxoperationcost[2]):
                  maxoperationcost = operationcost
               elif (operationcost[0]+operationcost[1]+operationcost[2] == maxoperationcost[0]+maxoperationcost[1]+maxoperationcost[2]):
                  if (operationcost[0] > maxoperationcost[0]):
                     maxoperationcost = operationcost
                  elif (operationcost[0] == maxoperationcost[0]):
                     if (operationcost[2] > maxoperationcost[2]):
                        maxoperationcost = operationcost
               if (memorycost[0]+memorycost[1]+memorycost[2] > maxmemorycost[0]+maxmemorycost[1]+maxmemorycost[2]):
                  maxmemorycost = memorycost
               elif (memorycost[0]+memorycost[1]+memorycost[2] == maxmemorycost[0]+maxmemorycost[1]+maxmemorycost[2]):
                  if (memorycost[0] > maxmemorycost[0]):
                     maxmemorycost = memorycost
                  elif (memorycost[0] == maxmemorycost[0]):
                     if (memorycost[2] > maxmemorycost[2]):
                        maxmemorycost = memorycost
            if (maxoperationcost[0]+maxoperationcost[1]+maxoperationcost[2] < minoperationcost[0]+minoperationcost[1]+minoperationcost[2]):
               minoperationcost = maxoperationcost
               minmemorycost = maxmemorycost
               ibest = ibreakdown
            elif (maxoperationcost[0]+maxoperationcost[1]+maxoperationcost[2] == minoperationcost[0]+minoperationcost[1]+minoperationcost[2]):
               if (maxoperationcost[0] < minoperationcost[0]):
                  minoperationcost = maxoperationcost
                  minmemorycost = maxmemorycost
                  ibest = ibreakdown
               elif (maxoperationcost[0] == minoperationcost[0]):
                  if (maxoperationcost[2] < minoperationcost[2]):
                     minoperationcost = maxoperationcost
                     minmemorycost = maxmemorycost
                     ibest = ibreakdown
                  elif (maxoperationcost[2] == minoperationcost[2]):
                     if (maxmemorycost[0]+maxmemorycost[1]+maxmemorycost[2] < minmemorycost[0]+minmemorycost[1]+minmemorycost[2]):
                        minoperationcost = maxoperationcost
                        minmemorycost = maxmemorycost
                        ibest = ibreakdown
                     elif (maxmemorycost[0]+maxmemorycost[1]+maxmemorycost[2] == minmemorycost[0]+minmemorycost[1]+minmemorycost[2]):
                        if (maxmemorycost[0] < minmemorycost[0]):
                           minoperationcost = maxoperationcost
                           minmemorycost = maxmemorycost
                           ibest = ibreakdown
                        elif (maxmemorycost[0] == minmemorycost[0]):
                           if (maxmemorycost[2] < minmemorycost[2]):
                              minoperationcost = maxoperationcost
                              minmemorycost = maxmemorycost
                              ibest = ibreakdown
                           elif (aggoperationcost[0]+aggoperationcost[1]+aggoperationcost[2] < minaggoperationcost[0]+minaggoperationcost[1]+minaggoperationcost[2]):
                              minaggoperationcost = aggoperationcost
                              minaggmemorycost = aggmemorycost
                              ibest = ibreakdown
                           elif (aggoperationcost[0]+aggoperationcost[1]+aggoperationcost[2] == minaggoperationcost[0]+minaggoperationcost[1]+minaggoperationcost[2]):
                              if (aggoperationcost[0] < minaggoperationcost[0]):
                                 minaggoperationcost = aggoperationcost
                                 minaggmemorycost = aggmemorycost
                                 ibest = ibreakdown
                              elif (aggoperationcost[0] == minaggoperationcost[0]):
                                 if (aggoperationcost[2] < minaggoperationcost[2]):
                                    minaggoperationcost = aggoperationcost
                                    minaggmemorycost = aggmemorycost
                                    ibest = ibreakdown
                                 elif (aggoperationcost[2] == minaggoperationcost[2]):
                                    if (aggmemorycost[0]+aggmemorycost[1]+aggmemorycost[2] < minaggmemorycost[0]+minaggmemorycost[1]+minaggmemorycost[2]):
                                       minaggoperationcost = aggoperationcost
                                       minaggmemorycost = aggmemorycost
                                       ibest = ibreakdown
                                    elif (aggmemorycost[0]+aggmemorycost[1]+aggmemorycost[2] == minaggmemorycost[0]+minaggmemorycost[1]+minaggmemorycost[2]):
                                       if (aggmemorycost[0] < minaggmemorycost[0]):
                                          minaggoperationcost = aggoperationcost
                                          minaggmemorycost = aggmemorycost
                                          ibest = ibreakdown
                                       elif (aggmemorycost[0] == minaggmemorycost[0]):
                                          if (aggmemorycost[2] < minaggmemorycost[2]):
                                             minaggoperationcost = aggoperationcost
                                             minaggmemorycost = aggmemorycost
                                             ibest = ibreakdown

      print " ... the best breakdown is %s with operationcost=N%d O%d V%d, memorycost=N%d O%d V%d " % (breakdowns[ibest], \
      minoperationcost[0], minoperationcost[1], minoperationcost[2], minmemorycost[0], minmemorycost[1], minmemorycost[2])

      return breakdowns[ibest]

   def breakdown(self,label=-1):
      """Breaks down the tensor contraction into elementary tensor contractions according to a given order"""
      another = self.canonicalize(1)
      another = another.symmetrize(0)
      order = another.findthebestbreakdown()
      if (label < 0):
         if (len(order) == 1):
            label = 0
         else:
            label = len(order)-2
      result = OperationTree()
      tensorone = another.tensors[order[0]-1]
      targettensor = another.tensors[0]
      if (len(another.tensors) > 1):
         for i in range(len(another.tensors)-1):
            targettensor = targettensor.contracts(another.tensors[i+1],0)
      targetsuper = copy.deepcopy(targettensor.indexes[0:len(targettensor.indexes)/2])
      targetsub   = copy.deepcopy(targettensor.indexes[len(targettensor.indexes)/2:len(targettensor.indexes)])
      if (len(order) == 1):
         tensorthree = tensorone.duplicate()
         tensorthree.label = label
         tensorthree.type = "i"
         # reorder the super and sub indexes individually of tensorthree
         # (I think that the order of indexes of intermediates is immaterial, so we can decide for our convenience.
         # However, do not mix up super and sub indexes, since otherwise contraction will be screwed up.)
         alwaystrue = 1
         while (alwaystrue):
            done = 1
            for nindex in range(len(tensorthree.indexes)/2):
               indexlabel = tensorthree.indexes[nindex].label
               for nanother in range(len(tensorthree.indexes)/2):
                  if (nindex < nanother):
                     anotherlabel = tensorthree.indexes[nanother].label
                     if (indexlabel >= anotherlabel):
                        done = 0
                        swapa = nindex
                        swapb = nanother
            if (done):
               alwaystrue = 1
               while (alwaystrue):
                  done = 1
                  for nindex in range(len(tensorthree.indexes)/2,len(tensorthree.indexes)):
                     indexlabel = tensorthree.indexes[nindex].label
                     for nanother in range(len(tensorthree.indexes)/2,len(tensorthree.indexes)):
                        if (nindex < nanother):
                           anotherlabel = tensorthree.indexes[nanother].label
                           if (indexlabel >= anotherlabel):
                              done = 0
                              swapa = nindex
                              swapb = nanother
                  if (done):
                     elementary = ElementaryTensorContraction(another.factor,another.summation,[tensorthree,tensorone])
                     result = OperationTree(elementary,[],[result])
                     return result
                  else:
                     swap = tensorthree.indexes[swapa]
                     tensorthree.indexes[swapa] = tensorthree.indexes[swapb]
                     tensorthree.indexes[swapb] = swap
            else:
               swap = tensorthree.indexes[swapa]
               tensorthree.indexes[swapa] = tensorthree.indexes[swapb]
               tensorthree.indexes[swapb] = swap
      else:

         # breakdown of a permutation operator
         suggestedfactors = []
         factorproduct = Factor([1.0],[[]])
         for contraction in range(0,len(order)-1):
            tensortwo = another.tensors[order[contraction+1]-1]
            onesuper   = []
            onesub     = []
            twosuper   = []
            twosub     = []
            for index in tensorone.indexes:
               if (index.isin(targetsuper)):
                  onesuper.append(index)
            for index in tensorone.indexes:
               if (index.isin(targetsub)):
                  onesub.append(index)
            for index in tensortwo.indexes:
               if (index.isin(targetsuper)):
                  twosuper.append(index)
            for index in tensortwo.indexes:
               if (index.isin(targetsub)):
                  twosub.append(index)
            nswapsuper = min(len(onesuper),len(twosuper)) + 1
            nswapsub = min(len(onesub),len(twosub)) + 1
            if (contraction == len(order)-2):
               newfactor = Factor([another.factor.coefficients[0]],[[]])
            else:
               newfactor = Factor([1.0],[[]])
            for iswapsuper in range(nswapsuper):
               swaponesuperlists = picknfromlist(iswapsuper,onesuper)
               swaptwosuperlists = picknfromlist(iswapsuper,twosuper)
               for swaponesuperlist in swaponesuperlists:
                  for swaptwosuperlist in swaptwosuperlists:
                     for iswapsub in range(nswapsub):
                        swaponesublists = picknfromlist(iswapsub,onesub)
                        swaptwosublists = picknfromlist(iswapsub,twosub)
                        for swaponesublist in swaponesublists:
                           for swaptwosublist in swaptwosublists:
                              permutation = []
                              permutation = permutation + copy.deepcopy(targetsuper) + copy.deepcopy(targetsub)
                              parity = 1.0
                              for targetindex in targetsuper:
                                 swapped = 0
                                 for nindexone in range(len(swaponesuperlist)):
                                    indexone = swaponesuperlist[nindexone]
                                    if (targetindex.isidenticalto(indexone)):
                                       permutation.append(copy.deepcopy(swaptwosuperlist[nindexone]))
                                       swapped = 1
                                       parity = parity * (-1.0)
                                 for nindextwo in range(len(swaponesuperlist)):
                                    indextwo = swaptwosuperlist[nindextwo]
                                    if (targetindex.isidenticalto(indextwo)):
                                       permutation.append(copy.deepcopy(swaponesuperlist[nindextwo]))
                                       swapped = 1
                                 if (not swapped):
                                    permutation.append(targetindex)
                              for targetindex in targetsub:
                                 swapped = 0
                                 for nindexone in range(len(swaponesublist)):
                                    indexone = swaponesublist[nindexone]
                                    if (targetindex.isidenticalto(indexone)):
                                       permutation.append(copy.deepcopy(swaptwosublist[nindexone]))
                                       swapped = 1
                                       parity = parity * (-1.0)
                                 for nindextwo in range(len(swaponesublist)):
                                    indextwo = swaptwosublist[nindextwo]
                                    if (targetindex.isidenticalto(indextwo)):
                                       permutation.append(copy.deepcopy(swaponesublist[nindextwo]))
                                       swapped = 1
                                 if (not swapped):
                                    permutation.append(targetindex)
                              identity = 1
                              for nindex in range(len(permutation)/2):
                                 if (not permutation[nindex].isidenticalto(permutation[nindex+len(permutation)/2])):
                                    identity = 0
                              if (not identity):
                                 if (contraction == len(order)-2):
                                    newfactor.add(Factor([parity*another.factor.coefficients[0]],[permutation]))
                                 else:
                                    newfactor.add(Factor([parity],[permutation]))
            newfactor = newfactor.canonicalize(onesuper)
            newfactor = newfactor.canonicalize(onesub)
            newfactor = newfactor.canonicalize(twosuper)
            newfactor = newfactor.canonicalize(twosub)
            suggestedfactors.append(newfactor)
            factorproduct = factorproduct.product(newfactor)
            tensorthree = tensorone.contracts(tensortwo,label)
            tensorone = copy.deepcopy(tensorthree)
         for tensor in self.tensors:
            super = []
            for nindex in range(len(tensor.indexes)/2):
               index = tensor.indexes[nindex]
               common = 0
               if (self.summation):
                  for anotherindex in self.summation.indexes:
                     if (index.isidenticalto(anotherindex)):
                        common = 1
               if (not common):
                  super.append(tensor.indexes[nindex])
            factorproduct = factorproduct.canonicalize(super)
            sub = []
            for nindex in range(len(tensor.indexes)/2,len(tensor.indexes)):
               index = tensor.indexes[nindex]
               common = 0
               if (self.summation):
                  for anotherindex in self.summation.indexes:
                     if (index.isidenticalto(anotherindex)):
                        common = 1
               if (not common):
                  sub.append(tensor.indexes[nindex])
            factorproduct = factorproduct.canonicalize(sub)
         if (factorproduct.isthesameas(another.factor)):
            factorisbrokendown = 1
            print " ... the suggested decomposition of the permutation operator is valid"
         else:
            factorisbrokendown = 0
            print " ************ WARNING! ************"
            print " ... the permutation operator cannot be broken down"

         # breakdown of a multiple tensor contraction
         tensorone = another.tensors[order[0]-1]
         for contraction in range(0,len(order)-1):
            tensortwo = another.tensors[order[contraction+1]-1]
            tensorthree = tensorone.contracts(tensortwo,label)
            label = label - 1
            if (factorisbrokendown):
               factor = suggestedfactors[contraction]
            else:
               if (contraction == len(order)-2):
                  factor = copy.deepcopy(another.factor)
               else:
                  factor = Factor([1.0],[[]])
            summation = Summation(tensorone.hascommonindexeswith(tensortwo))
            elementary = ElementaryTensorContraction(factor,summation,[tensorthree,tensorone,tensortwo])
            result = OperationTree(elementary,[],[result])
            tensorone = copy.deepcopy(tensorthree)
         result.sortindexes()
         return result

   def canonicalize(self,verbose=0):
      """ Canonicalizes the permutation operators"""
 
      if (verbose):
         print " ... canonicalizing permutation operator expressions"
      another = self.duplicate()
      for tensor in self.tensors:
         super = []
         for nindex in range(len(tensor.indexes)/2):
            index = tensor.indexes[nindex]
            common = 0
            if (self.summation):
               for anotherindex in self.summation.indexes:
                  if (index.isidenticalto(anotherindex)):
                     common = 1
            if (not common):
               super.append(tensor.indexes[nindex])
         another.factor = another.factor.canonicalize(super)
         sub = []
         for nindex in range(len(tensor.indexes)/2,len(tensor.indexes)):
            index = tensor.indexes[nindex]
            common = 0
            if (self.summation):
               for anotherindex in self.summation.indexes:
                  if (index.isidenticalto(anotherindex)):
                     common = 1
            if (not common):
               sub.append(tensor.indexes[nindex])
         another.factor = another.factor.canonicalize(sub)

      return another
 
   def symmetrize(self,verbose=0):
      """Introduces a permutation operator that permutes equivalent target indexes of permutable amplitudes"""

      symmetrized = 0

      # target indexes
      targetsuper = []
      targetsub = []
      for tensor in self.tensors:
         for nindex in range(len(tensor.indexes)/2):
            index = tensor.indexes[nindex]
            common = 0
            if (self.summation):
               for anotherindex in self.summation.indexes:
                  if (index.isidenticalto(anotherindex)):
                     common = 1
            if (not common):
               targetsuper.append(tensor.indexes[nindex])
         for nindex in range(len(tensor.indexes)/2,len(tensor.indexes)):
            index = tensor.indexes[nindex]
            common = 0
            if (self.summation):
               for anotherindex in self.summation.indexes:
                  if (index.isidenticalto(anotherindex)):
                     common = 1
            if (not common):
               targetsub.append(tensor.indexes[nindex])

      # identify equivalent tensors
      another = self.duplicate()
      for itensora in range(len(another.tensors)):
         tensora = another.tensors[itensora]
         super = []
         sub = []
         for itensorb in range(len(another.tensors)):
            tensorb = another.tensors[itensorb]
            if (itensorb <= itensora):
               continue
            if (tensora.isequivalentto(tensorb,another)):
               if ((not super) and (not sub)):
                  for nindex in range(len(tensora.indexes)/2):
                     index = tensora.indexes[nindex]
                     if (not another.summation.hastheindex(index)):
                        super.append(index)
                  for nindex in range(len(tensora.indexes)/2,len(tensora.indexes)):
                     index = tensora.indexes[nindex]
                     if (not another.summation.hastheindex(index)):
                        sub.append(index)
               for nindex in range(len(tensorb.indexes)/2):
                  index = tensorb.indexes[nindex]
                  if (not another.summation.hastheindex(index)):
                     super.append(index)
               for nindex in range(len(tensorb.indexes)/2,len(tensorb.indexes)):
                  index = tensorb.indexes[nindex]
                  if (not another.summation.hastheindex(index)):
                     sub.append(index)
         # multiply permutation operator of norm unity
         if (super):
            symmetrized = 1
            factor = createfactor(super,targetsuper+targetsub)
            another.factor = factor.product(another.factor)
         if (sub):
            symmetrized = 1
            factor = createfactor(sub,targetsuper+targetsub)
            another.factor = factor.product(another.factor)

      if (symmetrized):
         print " ... expression has been symmetrized"
      if (verbose):
         if (symmetrized):
            print self.show()
            print another.show()
            print ""

      return another

class ListTensorContractions:
 
   def __init__(self):
      """Creates a list of tensor contractions"""
      self.list = []
 
   def __str__(self):
      """Prints the content"""
      print ""
      for line in self.show():
         print line
      return ""
 
   def show(self):
      """Prints the tensor contractions"""
      show = []
      for tensorcontraction in self.list:
         show.append(tensorcontraction.show())
      return show

   def findthebestbreakdown(self,verbose=0):
      """Iteratively calls findthebestbreakdown() for all tensor contractions"""
      for tensorcontraction in self.list:
         print tensorcontraction.show()
         tensorcontraction.findthebestbreakdown(verbose)

   def breakdown(self):
      """Iteratively calls breakdown() for all tensor contractions"""
      children = []
      for tensorcontraction in self.list:
         if (len(tensorcontraction.tensors) == 1):
            label = 0
         else:
            label = len(tensorcontraction.tensors) - 2
         newchild = tensorcontraction.breakdown(label)
         children.append(newchild)
      result = OperationTree(NoOperation(),[],children)
      return result

   def canonicalize(self):
      """Calls canonicalize() for all tensor contractions"""
      for ntensorcontraction in range(len(self.list)):
         tensorcontraction = self.list[ntensorcontraction]
         self.list[ntensorcontraction] = tensorcontraction.canonicalize(0)
      return self

   def symmetrize(self,verbose=1):
      """Calls symmetrize() for all tensor contractions"""
      for ntensorcontraction in range(len(self.list)):
         tensorcontraction = self.list[ntensorcontraction]
         self.list[ntensorcontraction] = tensorcontraction.symmetrize(verbose)
      return self

   def pythongen(self,filename="NONAME"):
      """Genrates a python code for debugging purposes"""

      pythoncode = []
      newline = "# This is a Python program generated by Tensor Contraction Engine v.1.0"
      pythoncode.append(newline)
      newline = "# (c) All rights reserved by Battelle & Pacific Northwest Nat'l Lab (2002)"
      pythoncode.append(newline)

      tensors = ["i0"]
      for tensorcontraction in self.list:
         for tensor in tensorcontraction.tensors:
            newtensor = tensor.type+repr(len(tensor.indexes)/2)
            if (not (newtensor in tensors)):
               tensors.append(newtensor)
      newline = string.join(["def ",filename,"(N,nall,nocc"],"")
      for tensor in tensors:
         newline = string.join([newline,",",tensor],"")
      newline = string.join([newline,"):"],"")
      pythoncode.append(newline)

      for tensorcontraction in self.list:

         # generate a target tensor
         super = []
         sub = []
         for tensor in tensorcontraction.tensors:
            for nindex in range(len(tensor.indexes)/2):
               index = tensor.indexes[nindex]
               common = 0
               if (tensorcontraction.summation):
                  for another in tensorcontraction.summation.indexes:
                     if (index.isidenticalto(another)):
                        common = 1
               if (not common):
                  super.append(tensor.indexes[nindex]) 
            for nindex in range(len(tensor.indexes)/2,len(tensor.indexes)):
               index = tensor.indexes[nindex]
               common = 0
               if (tensorcontraction.summation):
                  for another in tensorcontraction.summation.indexes:
                     if (index.isidenticalto(another)):
                        common = 1
               if (not common):
                  sub.append(tensor.indexes[nindex]) 
         intermediate = Tensor("i",super+sub,0)
         parity = intermediate.sortindexes()

         # generate loops over target indexes
         indent = 1
         for index in intermediate.indexes:
            spin = string.join(["spin",repr(index.label)],"")
            newline = string.join(["for ",spin," in range(2):"],"")
            newline = string.join([" "*indent,newline],"")
            pythoncode.append(newline)
            indent = indent + 1
            if (index.type == 'hole'):
               newline = string.join(["for ",index.show()," in range(",spin,"*nall[0],",spin,"*nall[0]+nocc[",spin,"]):"],"")
               newline = string.join([" "*indent,newline],"")
               pythoncode.append(newline)
               indent = indent + 1
            elif (index.type == 'particle'):
               newline = string.join(["for ",index.show()," in range(",spin,"*nall[0]+nocc[",spin,"],",spin,"*nall[0]+nall[",spin,"]):"],"")
               newline = string.join([" "*indent,newline],"")
               pythoncode.append(newline)
               indent = indent + 1
            elif (index.type == 'general'):
               newline = string.join(["for ",index.show()," in range(",spin,"*nall[0],",spin,"*nall[0]+nall[",spin,"]):"],"")
               newline = string.join([" "*indent,newline],"")
               pythoncode.append(newline)
               indent = indent + 1

         # generate loops over common indexes
         if (tensorcontraction.summation):
            for index in tensorcontraction.summation.indexes:
               spin = string.join(["spin",repr(index.label)],"")
               newline = string.join(["for ",spin," in range(2):"],"")
               newline = string.join([" "*indent,newline],"")
               pythoncode.append(newline)
               indent = indent + 1
               if (index.type == 'hole'):
                  newline = string.join(["for ",index.show()," in range(",spin,"*nall[0],",spin,"*nall[0]+nocc[",spin,"]):"],"")
                  newline = string.join([" "*indent,newline],"")
                  pythoncode.append(newline)
                  indent = indent + 1
               elif (index.type == 'particle'):
                  newline = string.join(["for ",index.show()," in range(",spin,"*nall[0]+nocc[",spin,"],",spin,"*nall[0]+nall[",spin,"]):"],"")
                  newline = string.join([" "*indent,newline],"")
                  pythoncode.append(newline)
                  indent = indent + 1
               elif (index.type == 'general'):
                  newline = string.join(["for ",index.show()," in range(",spin,"*nall[0],",spin,"*nall[0]+nall[",spin,"]):"],"")
                  newline = string.join([" "*indent,newline],"")
                  pythoncode.append(newline)
                  indent = indent + 1
         newline = string.join([intermediate.pythongen(),"=",intermediate.pythongen(),"+",\
                                "(",repr(tensorcontraction.factor),")"],"")
         for tensor in tensorcontraction.tensors:
            newline = string.join([newline,"*",tensor.pythongen()],"")
         newline = string.join([" "*indent,newline],"")
         pythoncode.append(newline)
         
      # dump the code to a file
      writetofile(pythoncode,string.join([filename,".py.out"],""))

class NoOperation:

   def __init__(self):
      """Creates a dummy operation"""

   def __str__(self):
      """Prints the content"""
      return self.show()

   def show(self):
      """Returns a dummy operation expression"""
      show = "No operation"
      return show

   def isoperation(self):
      """Returns false"""
      return 0

   def usesindexlabel(self,label):
      """Returns false"""
      return 0

   def relabels(self,oldlabel,newlabel):
      """Just returns"""

   def swapindexes(self,indexone,indextwo):
      """Just returns"""

class ElementaryTensorContraction:

   def __init__(self,factor=[],summation=[],tensors=[]):
      """Creates an elementary tensor contraction: tensor A = factor * tensor B * tensor C"""
      self.factor = factor
      self.summation = summation
      self.tensors = tensors
 
   def __str__(self):
      """Prints the content"""
      return self.show()

   def show(self,verbose=1):
      """Returns a human-friendly string of the content"""
      show = string.join([self.tensors[0].show(),"+ ="])
      show = string.join([show,self.factor.show(verbose)])
      if (self.summation):
         if (len(self.summation.indexes) > 0):
            show = string.join([show, "*", self.summation.show()])
      show = string.join([show, "*", self.tensors[1].show()])
      if (len(self.tensors) == 3):
         show = string.join([show, "*", self.tensors[2].show()])
      return show 

   def isoperation(self):
      """Returns true"""
      return 1

   def usesindexlabel(self,label):
      """Returns true if the index label is already in use"""
      for tensor in self.tensors:
         if (tensor.usesindexlabel(label)):
            return 1
      return 0

   def relabels(self,oldlabel,newlabel):
      """Renames an index label"""
      for tensor in self.tensors:
         tensor.relabels(oldlabel,newlabel)
      if (self.summation):
         for nindex in range(len(self.summation.indexes)):
            index = self.summation.indexes[nindex]
            if (index.label == oldlabel):
               self.summation.indexes[nindex].label = newlabel

   def swapindexes(self,indexone,indextwo):
      """Swaps indexes"""
      for tensor in self.tensors:
         tensor.swapindexes(indexone,indextwo)
         if (self.summation):
            for nindex in range(len(self.summation.indexes)):
               index = self.summation.indexes[nindex]
               if (index.isidenticalto(indexone)):
                  self.summation.indexes[nindex] = copy.deepcopy(indextwo)
               elif (index.isidenticalto(indextwo)):
                  self.summation.indexes[nindex] = copy.deepcopy(indexone)

   def sortindexes(self):
      """Sorts the indexes of tensors taking account of parities"""
      for tensor in self.tensors:
         self.factor.multiply(tensor.sortindexes())

   def fortran77(self,globaltargetindexes,subroutinename="NONAME"):
      """Suggests an implementation in Fortran77 for an elementary tensor contraction C = A * B"""

      if (len(self.tensors) == 3):
         three = 1
      else:
         three = 0

      errquit = 0

      newcode = Code("Fortran77",subroutinename)

      # header
      newline = "!" + self.show(0)
      newcode.add("headers",newline)
      newline = "IMPLICIT NONE"
      newcode.add("headers",newline)
      
      # insert include statements
      newline = '#include "global.fh"'
      newcode.add("headers",newline)
      newline = '#include "mafdecls.fh"'
      newcode.add("headers",newline)
      newline = '#include "sym.fh"'
      newcode.add("headers",newline)
      newline = '#include "tce.fh"'
      newcode.add("headers",newline)

      # declaration
      newint = "d_a"
      newcode.add("integers",newint)
      newcode.add("arguments",newint)
      newint = "k_a_offset"
      newcode.add("integers",newint)
      newcode.add("arguments",newint)
      if (three):
         newint = "d_b"
         newcode.add("integers",newint)
         newcode.add("arguments",newint)
         newint = "k_b_offset"
         newcode.add("integers",newint)
         newcode.add("arguments",newint)
      newint = "d_c"
      newcode.add("integers",newint)
      newcode.add("arguments",newint)
      newint = "k_c_offset"
      newcode.add("integers",newint)
      newcode.add("arguments",newint)
      newint = "NXTVAL"
      newcode.add("integers",newint)
      newcode.add("externals",newint)
      newint = "next"
      newcode.add("integers",newint)
      newint = "nprocs"
      newcode.add("integers",newint)
      newint = "count"
      newcode.add("integers",newint)
            
      # Tensor 0
      superglobalzero = []
      subglobalzero = []
      superlocalzero = []
      sublocalzero = []
      for nindex in range(len(self.tensors[0].indexes)/2):
         index = self.tensors[0].indexes[nindex]
         if (index.isin(globaltargetindexes)):
            superglobalzero.append(index)
         else:
            superlocalzero.append(index)
      for nindex in range(len(self.tensors[0].indexes)/2,len(self.tensors[0].indexes)):
         index = self.tensors[0].indexes[nindex]
         if (index.isin(globaltargetindexes)):
            subglobalzero.append(index)
         else:
            sublocalzero.append(index)

      # Tensor 1
      superglobalone = []
      subglobalone = []
      superlocalone = []
      sublocalone = []
      supercommonone = []
      subcommonone = []
      for nindex in range(len(self.tensors[1].indexes)/2):
         index = self.tensors[1].indexes[nindex]
         if (index.isin(globaltargetindexes)):
            superglobalone.append(index)
         elif (self.summation):
            if (index.isin(self.summation.indexes)):
               supercommonone.append(index)
            else:
               superlocalone.append(index)
         else:
            superlocalone.append(index)
      for nindex in range(len(self.tensors[1].indexes)/2,len(self.tensors[1].indexes)):
         index = self.tensors[1].indexes[nindex]
         if (index.isin(globaltargetindexes)):
            subglobalone.append(index)
         elif (self.summation):
            if (index.isin(self.summation.indexes)):
               subcommonone.append(index)
            else:
               sublocalone.append(index)
         else:
            sublocalone.append(index)

      # Tensor 2
      superglobaltwo = []
      subglobaltwo = []
      superlocaltwo = []
      sublocaltwo = []
      supercommontwo = []
      subcommontwo = []
      if (three):
         for nindex in range(len(self.tensors[2].indexes)/2):
            index = self.tensors[2].indexes[nindex]
            if (index.isin(globaltargetindexes)):
               superglobaltwo.append(index)
            elif (self.summation):
               if (index.isin(self.summation.indexes)):
                  supercommontwo.append(index)
               else:
                  superlocaltwo.append(index)
            else:
               superlocaltwo.append(index)
         for nindex in range(len(self.tensors[2].indexes)/2,len(self.tensors[2].indexes)):
            index = self.tensors[2].indexes[nindex]
            if (index.isin(globaltargetindexes)):
               subglobaltwo.append(index)
            elif (self.summation):
               if (index.isin(self.summation.indexes)):
                  subcommontwo.append(index)
               else:
                  sublocaltwo.append(index)
            else:
               sublocaltwo.append(index)
      if (len(supercommonone) > len(subcommontwo)):
         supercommon = supercommonone
      else:
         supercommon = subcommontwo
      if (len(subcommonone) > len(supercommontwo)):
         subcommon = subcommonone
      else:
         subcommon = supercommontwo

      # parallel related
      newline = "nprocs = GA_NNODES()"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "count = 0"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "next = NXTVAL(nprocs)"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1

      # loop over output tensor indexes
      newcode.inserttileddoloops(superglobalone)
      if (three):
         newcode.inserttileddoloops(superglobaltwo)
      newcode.inserttileddoloops(superlocalone)
      if (three):
         newcode.inserttileddoloops(superlocaltwo)
      newcode.inserttileddoloops(subglobalone)
      if (three):
         newcode.inserttileddoloops(subglobaltwo)
      newcode.inserttileddoloops(sublocalone)
      if (three):
         newcode.inserttileddoloops(sublocaltwo)

      # parallel related
      newline = "IF (next.eq.count) THEN"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.setamark(4)
      newcode.pointer = newcode.pointer + 1
      newline = "next = NXTVAL(nprocs)"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "END IF"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "count = count + 1"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.getamark(4) + 1

      # symmetry of output tensor
      super = superglobalzero + superlocalzero
      sub = subglobalzero + sublocalzero
      newcode.inserttiledifsymmetry(super,sub)

      # loop over summation indexes
      newcode.inserttileddoloops(supercommon)
      newcode.inserttileddoloops(subcommon)

      # symmetry of input tensor 1
      if (three):
         super = superglobalone + superlocalone + supercommonone
         sub = subglobalone + sublocalone + subcommonone
         newcode.inserttiledifsymmetry(super,sub)

      # create MA's for tensor 1
      newcode.add("integers","dim_common")
      newline = ""
      for index in supercommonone + subcommonone:
         if (newline == ""):
            newline = string.join(["dim_common = int_mb(k_range+",index.show(),"b-1)"],"")
         else:
            newline = string.join([newline," * int_mb(k_range+",index.show(),"b-1)"],"")
      if (newline == ""):
         newline = "dim_common = 1"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newcode.add("integers","dima_sort")
      newline = ""
      for index in superglobalone + superlocalone + subglobalone + sublocalone:
         if (newline == ""):
            newline = string.join(["dima_sort = int_mb(k_range+",index.show(),"b-1)"],"")
         else:
            newline = string.join([newline," * int_mb(k_range+",index.show(),"b-1)"],"")
      if (newline == ""):
         newline = "dima_sort = 1"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newcode.add("integers","dima")
      newline = "dima = dim_common * dima_sort"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1

      # create MA's for tensor 2
      if (three):
         newcode.add("integers","dimb_sort")
         newline = ""
         for index in superglobaltwo + superlocaltwo + subglobaltwo + sublocaltwo:
            if (newline == ""):
               newline = string.join(["dimb_sort = int_mb(k_range+",index.show(),"b-1)"],"")
            else:
               newline = string.join([newline," * int_mb(k_range+",index.show(),"b-1)"],"")
         if (newline == ""):
            newline = "dimb_sort = 1"
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1
         newcode.add("integers","dimb")
         newline = "dimb = dim_common * dimb_sort"
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1

      if (three):
         newline = "IF ((dima .gt. 0) .and. (dimb .gt. 0)) THEN"
      else:
         newline = "IF (dima .gt. 0) THEN"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "END IF"
      newcode.statements.insert(newcode.pointer,newline)

      # allocate sorted and unsorted tensor 1
      newcode.add("integers","l_a_sort")
      newcode.add("integers","k_a_sort")
      newline = string.join(["IF (.not.MA_PUSH_GET(mt_dbl,dima,'noname',l_a_sort,k_a_sort)) CALL ERRQUIT('",\
                             subroutinename,"',",repr(errquit),")"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      errquit = errquit + 1
      newcode.add("integers","l_a")
      newcode.add("integers","k_a")
      newline = string.join(["IF (.not.MA_PUSH_GET(mt_dbl,dima,'noname',l_a,k_a)) CALL ERRQUIT('",\
                             subroutinename,"',",repr(errquit),")"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      errquit = errquit + 1

      # mapping to a permutation symmetry unique block
      if (self.tensors[1].type == "i"):
         superpermutations = restrictedpermutationwithparity(superlocalone,supercommonone,[])
      else:
         superpermutations = restrictedpermutationwithparity(superglobalone,superlocalone,supercommonone)
      if (self.tensors[1].type == "i"):
         subpermutations = restrictedpermutationwithparity(sublocalone,subcommonone,[])
      else:
         subpermutations = restrictedpermutationwithparity(subglobalone,sublocalone,subcommonone)
      newcode.pointer = newcode.pointer - 1
      newcode.setamark(1)
      newcode.pointer = newcode.pointer + 1
      ifblock = 0
      for superpermutation in superpermutations:
         superline = ""
         if (self.tensors[1].type == "i"):
            permutation = superlocalone + supercommonone
         else:
            permutation = superglobalone + superlocalone + supercommonone
         if (superpermutation[1] == "empty"):
            permutation = permutation + permutation
         else:
            permutation = permutation + superpermutation[1:]
         if (self.tensors[1].type == "i"):
            indexesintheoriginalorder = copy.deepcopy(superglobalone + sortindexes(superlocalone + supercommonone))
         else:
            indexesintheoriginalorder = copy.deepcopy(self.tensors[1].indexes[0:len(self.tensors[1].indexes)/2])
         superpermutedindexes = performpermutation(indexesintheoriginalorder,permutation,0)
         if (superpermutation[1] != "empty"):
            for nindex in range(len(superpermutedindexes)-1):
               indexa = superpermutedindexes[nindex]
               indexb = superpermutedindexes[nindex+1]
               if ((self.tensors[1].type == "i") and (indexa.isin(superglobalone) or indexb.isin(superglobalone))):
                  continue
               if (indexa.isin(superglobalone) and indexb.isin(superglobalone)):
                  continue
               if (indexa.isin(superlocalone) and indexb.isin(superlocalone)):
                  continue
               if (indexa.isin(supercommonone) and indexb.isin(supercommonone)):
                  continue
               if (indexa.isgreaterthan(indexb)):
                  inequality = " .lt. "
               else:
                  inequality = " .le. "
               if (superline):
                  superline = string.join([superline," .and. (",indexa.show(),"b",inequality,indexb.show(),"b)"],"")
               else:
                  superline = string.join([superline,"IF ((",indexa.show(),"b",inequality,indexb.show(),"b)"],"")
         for subpermutation in subpermutations:
            subline = superline
            if (self.tensors[1].type == "i"):
               permutation = sublocalone + subcommonone
            else:
               permutation = subglobalone + sublocalone + subcommonone
            if (subpermutation[1] == "empty"):
               permutation = permutation + permutation
            else:
               permutation = permutation + subpermutation[1:]
            if (self.tensors[1].type == "i"):
               indexesintheoriginalorder = copy.deepcopy(subglobalone + sortindexes(sublocalone + subcommonone))
            else:
               indexesintheoriginalorder = copy.deepcopy(self.tensors[1].indexes[len(self.tensors[1].indexes)/2:len(self.tensors[1].indexes)])
            subpermutedindexes = performpermutation(indexesintheoriginalorder,permutation,0)
            if (subpermutation[1] != "empty"):
               for nindex in range(len(subpermutedindexes)-1):
                  indexa = subpermutedindexes[nindex]
                  indexb = subpermutedindexes[nindex+1]
                  if ((self.tensors[1].type == "i") and (indexa.isin(subglobalone) or indexb.isin(subglobalone))):
                     continue
                  if (indexa.isin(subglobalone) and indexb.isin(subglobalone)):
                     continue
                  if (indexa.isin(sublocalone) and indexb.isin(sublocalone)):
                     continue
                  if (indexa.isin(subcommonone) and indexb.isin(subcommonone)):
                     continue
                  if (indexa.isgreaterthan(indexb)):
                     inequality = " .lt. "
                  else:
                     inequality = " .le. "
                  if (subline):
                     subline = string.join([subline," .and. (",indexa.show(),"b",inequality,indexb.show(),"b)"],"")
                  else:
                     subline = string.join([subline,"IF ((",indexa.show(),"b",inequality,indexb.show(),"b)"],"")
            if (subline):
               subline = string.join([subline,") THEN"],"")
               newcode.pointer = newcode.getamark(1) + 1
               newcode.statements.insert(newcode.pointer,subline)
               newcode.pointer = newcode.pointer + 1
               newline = "END IF"
               newcode.statements.insert(newcode.pointer,newline)
               newcode.setamark(1)
               ifblock = 1

            permutedindexes = superpermutedindexes + subpermutedindexes
      
            # get a block
            arguments = ""
            argumentsend = ""
            for nindex in range(len(permutedindexes)-1,-1,-1):
               if (permutedindexes[nindex].type == "hole"):
                  boffset = "b - 1"
               else:
                  if ((self.tensors[1].type == "f") or (self.tensors[1].type == "v")):
                     boffset = "b - 1"
                  else:
                     boffset = "b - noab - 1"
               if (arguments == ""):
                  arguments = string.join(["d_a,dbl_mb(k_a),dima,int_mb(k_a_offset + ",permutedindexes[nindex].show(),boffset],"")
               else:
                  if ((self.tensors[1].type == "f") or (self.tensors[1].type == "v")):
                     arguments = string.join([arguments," + (noab+nvab) * (",permutedindexes[nindex].show(),boffset],"")
                  else:
                     if (permutedindexes[nindex+1].type == "hole"):
                        arguments = string.join([arguments," + noab * (",permutedindexes[nindex].show(),boffset],"")
                     else:
                        arguments = string.join([arguments," + nvab * (",permutedindexes[nindex].show(),boffset],"")
                  argumentsend = string.join([argumentsend,")"],"")
            arguments = string.join([arguments,argumentsend,")"],"")
            newline = string.join(["CALL GET_BLOCK(",arguments,")"],"")
            newcode.statements.insert(newcode.pointer,newline)
            newcode.pointer = newcode.pointer + 1

            # sort indexes of tensor 1
            for nindex in range(len(permutedindexes)):
               index = permutedindexes[nindex]
               newint = index.show()
               newcode.add("integers",newint)
               newline = string.join(["DO ",newint," = 1,int_mb(k_range+",newint,"b-1)"],"")
               newcode.statements.insert(newcode.pointer,newline)
               newcode.pointer = newcode.pointer + 1
               newline = "END DO"
               newcode.statements.insert(newcode.pointer,newline)
               if ((not ifblock) and (nindex == 0)):
                  newcode.setamark(1)
            newline = ""
            newlineend = ""
            newcode.add("integers","idima")
            for nindex in range(len(permutedindexes)-1,-1,-1):
               if (newline == ""):
                  newline = string.join(["idima = ",permutedindexes[nindex].show()],"")
               else:
                  newline = string.join([newline," + int_mb(k_range+",permutedindexes[nindex+1].show(),"b-1)"\
                                         " * ((",permutedindexes[nindex].show()," - 1)"],"")
                  newlineend = string.join([newlineend,")"],"")
            newline = string.join([newline,newlineend],"")
            newcode.statements.insert(newcode.pointer,newline)
            newcode.pointer = newcode.pointer + 1
            newline = ""
            newlineend = ""
            newcode.add("integers","idima_sort")
            sorted = supercommonone + subcommonone + superglobalone + superlocalone + subglobalone + sublocalone
            for nindex in range(len(sorted)):
               if (newline == ""):
                  newline = string.join(["idima_sort = ",sorted[nindex].show()],"")
               else:
                  newline = string.join([newline," + int_mb(k_range+",sorted[nindex-1].show(),"b-1)"\
                                         " * ((",sorted[nindex].show()," - 1)"],"")
                  newlineend = string.join([newlineend,")"],"")
            newline = string.join([newline,newlineend],"")
            newcode.statements.insert(newcode.pointer,newline)
            newcode.pointer = newcode.pointer + 1
            if (superpermutation[0]*subpermutation[0] == 1):
               newline = "dbl_mb(k_a_sort + idima_sort - 1) = dbl_mb(k_a + idima - 1)"
            else:
               newline = "dbl_mb(k_a_sort + idima_sort - 1) = - dbl_mb(k_a + idima - 1)"
            newcode.statements.insert(newcode.pointer,newline)
            newcode.pointer = newcode.pointer + 1

      newcode.pointer = newcode.getamark(1) + 1
      newline = string.join(["IF (.not.MA_POP_STACK(l_a)) CALL ERRQUIT('",subroutinename,"',",repr(errquit),")"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      errquit = errquit + 1

      # allocate sorted and unsorted tensor 2
      if (three):
         newcode.add("integers","l_b_sort")
         newcode.add("integers","k_b_sort")
         newline = string.join(["IF (.not.MA_PUSH_GET(mt_dbl,dimb,'noname',l_b_sort,k_b_sort)) CALL ERRQUIT('",\
                                subroutinename,"',",repr(errquit),")"],"")
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1
         errquit = errquit + 1
         newcode.add("integers","l_b")
         newcode.add("integers","k_b")
         newline = string.join(["IF (.not.MA_PUSH_GET(mt_dbl,dimb,'noname',l_b,k_b)) CALL ERRQUIT('",\
                                subroutinename,"',",repr(errquit),")"],"")
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1
         errquit = errquit + 1
   
         # mapping to a permutation symmetry unique block
         if (self.tensors[2].type == "i"):
            superpermutations = restrictedpermutationwithparity(superlocaltwo,supercommontwo,[])
         else:
            superpermutations = restrictedpermutationwithparity(superglobaltwo,superlocaltwo,supercommontwo)
         if (self.tensors[2].type == "i"):
            subpermutations = restrictedpermutationwithparity(sublocaltwo,subcommontwo,[])
         else:
            subpermutations = restrictedpermutationwithparity(subglobaltwo,sublocaltwo,subcommontwo)
         newcode.pointer = newcode.pointer - 1
         newcode.setamark(2)
         newcode.pointer = newcode.pointer + 1
         ifblock = 0
         for superpermutation in superpermutations:
            superline = ""
            if (self.tensors[2].type == "i"):
               permutation = superlocaltwo + supercommontwo
            else:
               permutation = superglobaltwo + superlocaltwo + supercommontwo
            if (superpermutation[1] == "empty"):
               permutation = permutation + permutation
            else:
               permutation = permutation + superpermutation[1:]
            if (self.tensors[2].type == "i"):
               indexesintheoriginalorder = copy.deepcopy(superglobaltwo + sortindexes(superlocaltwo + supercommontwo))
            else:
               indexesintheoriginalorder = copy.deepcopy(self.tensors[2].indexes[0:len(self.tensors[2].indexes)/2])
            superpermutedindexes = performpermutation(indexesintheoriginalorder,permutation,0)
            if (superpermutation[1] != "empty"):
               for nindex in range(len(superpermutedindexes)-1):
                  indexa = superpermutedindexes[nindex]
                  indexb = superpermutedindexes[nindex+1]
                  if ((self.tensors[2].type == "i") and (indexa.isin(superglobaltwo) or indexb.isin(superglobaltwo))):
                     continue
                  if (indexa.isin(superglobaltwo) and indexb.isin(superglobaltwo)):
                     continue
                  if (indexa.isin(superlocaltwo) and indexb.isin(superlocaltwo)):
                     continue
                  if (indexa.isin(supercommontwo) and indexb.isin(supercommontwo)):
                     continue
                  if (indexa.isgreaterthan(indexb)):
                     inequality = " .lt. "
                  else:
                     inequality = " .le. "
                  if (superline):
                     superline = string.join([superline," .and. (",indexa.show(),"b",inequality,indexb.show(),"b)"],"")
                  else:
                     superline = string.join([superline,"IF ((",indexa.show(),"b",inequality,indexb.show(),"b)"],"")
            for subpermutation in subpermutations:
               subline = superline
               if (self.tensors[2].type == "i"):
                  permutation = sublocaltwo + subcommontwo
               else:
                  permutation = subglobaltwo + sublocaltwo + subcommontwo
               if (subpermutation[1] == "empty"):
                  permutation = permutation + permutation
               else:
                  permutation = permutation + subpermutation[1:]
               if (self.tensors[2].type == "i"):
                  indexesintheoriginalorder = copy.deepcopy(subglobaltwo + sortindexes(sublocaltwo + subcommontwo))
               else:
                  indexesintheoriginalorder = copy.deepcopy(self.tensors[2].indexes[len(self.tensors[2].indexes)/2:len(self.tensors[2].indexes)])
               subpermutedindexes = performpermutation(indexesintheoriginalorder,permutation,0)
               if (subpermutation[1] != "empty"):
                  for nindex in range(len(subpermutedindexes)-1):
                     indexa = subpermutedindexes[nindex]
                     indexb = subpermutedindexes[nindex+1]
                     if ((self.tensors[2].type == "i") and (indexa.isin(subglobaltwo) or indexb.isin(subglobaltwo))):
                        continue
                     if (indexa.isin(subglobaltwo) and indexb.isin(subglobaltwo)):
                        continue
                     if (indexa.isin(sublocaltwo) and indexb.isin(sublocaltwo)):
                        continue
                     if (indexa.isin(subcommontwo) and indexb.isin(subcommontwo)):
                        continue
                     if (indexa.isgreaterthan(indexb)):
                        inequality = " .lt. "
                     else:
                        inequality = " .le. "
                     if (subline):
                        subline = string.join([subline," .and. (",indexa.show(),"b",inequality,indexb.show(),"b)"],"")
                     else:
                        subline = string.join([subline,"IF ((",indexa.show(),"b",inequality,indexb.show(),"b)"],"")
               if (subline):
                  subline = string.join([subline,") THEN"],"")
                  newcode.pointer = newcode.getamark(2) + 1
                  newcode.statements.insert(newcode.pointer,subline)
                  newcode.pointer = newcode.pointer + 1
                  newline = "END IF"
                  newcode.statements.insert(newcode.pointer,newline)
                  newcode.setamark(2)
                  ifblock = 1
   
               permutedindexes = superpermutedindexes + subpermutedindexes
         
               # get a block
               arguments = ""
               argumentsend = ""
               for nindex in range(len(permutedindexes)-1,-1,-1):
                  if (permutedindexes[nindex].type == "hole"):
                     boffset = "b - 1"
                  else:
                     if ((self.tensors[2].type == "f") or (self.tensors[2].type == "v")):
                        boffset = "b - 1"
                     else:
                        boffset = "b - noab - 1"
                  if (arguments == ""):
                     arguments = string.join(["d_b,dbl_mb(k_b),dimb,int_mb(k_b_offset + ",permutedindexes[nindex].show(),boffset],"")
                  else:
                     if ((self.tensors[2].type == "f") or (self.tensors[2].type == "v")):
                        arguments = string.join([arguments," + (noab+nvab) * (",permutedindexes[nindex].show(),boffset],"")
                     else:
                        if (permutedindexes[nindex+1].type == "hole"):
                           arguments = string.join([arguments," + noab * (",permutedindexes[nindex].show(),boffset],"")
                        else:
                           arguments = string.join([arguments," + nvab * (",permutedindexes[nindex].show(),boffset],"")
                     argumentsend = string.join([argumentsend,")"],"")
               arguments = string.join([arguments,argumentsend,")"],"")
               newline = string.join(["CALL GET_BLOCK(",arguments,")"],"")
               newcode.statements.insert(newcode.pointer,newline)
               newcode.pointer = newcode.pointer + 1
   
               # sort indexes of tensor 2
               for nindex in range(len(permutedindexes)):
                  index = permutedindexes[nindex]
                  newint = index.show()
                  newcode.add("integers",newint)
                  newline = string.join(["DO ",newint," = 1,int_mb(k_range+",newint,"b-1)"],"")
                  newcode.statements.insert(newcode.pointer,newline)
                  newcode.pointer = newcode.pointer + 1
                  newline = "END DO"
                  newcode.statements.insert(newcode.pointer,newline)
                  if ((not ifblock) and (nindex == 0)):
                     newcode.setamark(2)
               newline = ""
               newlineend = ""
               newcode.add("integers","idimb")
               for nindex in range(len(permutedindexes)-1,-1,-1):
                  if (newline == ""):
                     newline = string.join(["idimb = ",permutedindexes[nindex].show()],"")
                  else:
                     newline = string.join([newline," + int_mb(k_range+",permutedindexes[nindex+1].show(),"b-1)"\
                                            " * ((",permutedindexes[nindex].show()," - 1)"],"")
                     newlineend = string.join([newlineend,")"],"")
               newline = string.join([newline,newlineend],"")
               newcode.statements.insert(newcode.pointer,newline)
               newcode.pointer = newcode.pointer + 1
               newline = ""
               newlineend = ""
               newcode.add("integers","idimb_sort")
               # note the sub - super order !
               sorted = subcommontwo + supercommontwo + superglobaltwo + superlocaltwo + subglobaltwo + sublocaltwo
               for nindex in range(len(sorted)):
                  if (newline == ""):
                     newline = string.join(["idimb_sort = ",sorted[nindex].show()],"")
                  else:
                     newline = string.join([newline," + int_mb(k_range+",sorted[nindex-1].show(),"b-1)"\
                                            " * ((",sorted[nindex].show()," - 1)"],"")
                     newlineend = string.join([newlineend,")"],"")
               newline = string.join([newline,newlineend],"")
               newcode.statements.insert(newcode.pointer,newline)
               newcode.pointer = newcode.pointer + 1
               if (superpermutation[0]*subpermutation[0] == 1):
                  newline = "dbl_mb(k_b_sort + idimb_sort - 1) = dbl_mb(k_b + idimb - 1)"
               else:
                  newline = "dbl_mb(k_b_sort + idimb_sort - 1) = - dbl_mb(k_b + idimb - 1)"
               newcode.statements.insert(newcode.pointer,newline)
               newcode.pointer = newcode.pointer + 1

         newcode.pointer = newcode.getamark(2) + 1
         newline = string.join(["IF (.not.MA_POP_STACK(l_b)) CALL ERRQUIT('",subroutinename,"',",repr(errquit),")"],"")
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1
         errquit = errquit + 1

         # factor
         factorialforsuper = 0
         if (len(supercommon) > 1):
            factorialforsuper = 1
            newint = "nsuper"
            newcode.add("integers",newint)
            newline = "nsuper = 1"
            newcode.statements.insert(newcode.pointer,newline)
            newcode.pointer = newcode.pointer + 1
            for nindex in range(len(supercommon)-1):
               newline = string.join(["IF (",supercommon[nindex].show(),"b .ne. ",supercommon[nindex+1].show(),\
                                      "b) nsuper = nsuper + 1"],"")
               newcode.statements.insert(newcode.pointer,newline)
               newcode.pointer = newcode.pointer + 1
         factorialforsub = 0
         if (len(subcommon) > 1):
            factorialforsub = 1
            newint = "nsub"
            newcode.add("integers",newint)
            newline = "nsub = 1"
            newcode.statements.insert(newcode.pointer,newline)
            newcode.pointer = newcode.pointer + 1
            for nindex in range(len(subcommon)-1):
               newline = string.join(["IF (",subcommon[nindex].show(),"b .ne. ",subcommon[nindex+1].show(),\
                                      "b) nsub = nsub + 1"],"")
               newcode.statements.insert(newcode.pointer,newline)
               newcode.pointer = newcode.pointer + 1
         if (factorialforsuper and factorialforsub):
            newdbl = "FACTORIAL"
            newcode.add("doubles",newdbl)
            newcode.add("externals",newdbl)
            factor = "FACTORIAL(nsuper)*FACTORIAL(nsub)"
         elif (factorialforsuper):
            newdbl = "FACTORIAL"
            newcode.add("doubles",newdbl)
            newcode.add("externals",newdbl)
            factor = "FACTORIAL(nsuper)"
         elif (factorialforsub):
            newdbl = "FACTORIAL"
            newcode.add("doubles",newdbl)
            newcode.add("externals",newdbl)
            factor = "FACTORIAL(nsub)"
         else:
            factor = "1.0d0"
   
         # perform contraction and store the result
         newcode.add("integers","l_c_sort")
         newcode.add("integers","k_c_sort")
         if (three):
            newline = string.join(["IF (.not.MA_PUSH_GET(mt_dbl,dima_sort*dimb_sort,'noname',l_c_sort,k_c_sort)) CALL ERRQUIT('",\
                                   subroutinename,"',",repr(errquit),")"],"")
         else:
            newline = string.join(["IF (.not.MA_PUSH_GET(mt_dbl,dima_sort,'noname',l_c_sort,k_c_sort)) CALL ERRQUIT('",\
                                   subroutinename,"',",repr(errquit),")"],"")
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1
         errquit = errquit + 1
         newline = string.join(["CALL DGEMM('T','N',dima_sort,dimb_sort,dim_common,",factor,\
                                ",dbl_mb(k_a_sort),dim_common,dbl_mb(k_b_sort),dim_common,0.0d0,dbl_mb(k_c_sort),dima_sort)"],"")
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1

      # create an MA for unsorted tensor 0
      newcode.add("integers","l_c")
      newcode.add("integers","k_c")
      if (three):
         newline = string.join(["IF (.not.MA_PUSH_GET(mt_dbl,dima_sort*dimb_sort,'noname',l_c,k_c)) CALL ERRQUIT('",\
                                subroutinename,"',",repr(errquit),")"],"")
      else:
         newline = string.join(["IF (.not.MA_PUSH_GET(mt_dbl,dima_sort,'noname',l_c,k_c)) CALL ERRQUIT('",\
                                subroutinename,"',",repr(errquit),")"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      errquit = errquit + 1
         
      # mapping to a permutation symmetry unique block
      newcode.pointer = newcode.pointer - 1
      newcode.setamark(3)
      newcode.pointer = newcode.pointer + 1
      ifblock = 0
      for npermutation in range(len(self.factor.permutations)):
         permutation = self.factor.permutations[npermutation]
         indexesintheoriginalorder = copy.deepcopy(superglobalzero + superlocalzero + subglobalzero + sublocalzero)
         permutedindexes = performpermutation(indexesintheoriginalorder,permutation,1)
         newline = ""
         for nindex in range(len(permutedindexes)-1):
            # no IF across super and sub indexes
            if (nindex == len(permutedindexes)/2-1):
               continue
            indexa = permutedindexes[nindex]
            indexb = permutedindexes[nindex+1]
            if (indexa.isin(superglobalone) and indexb.isin(superglobalone)):
               continue
            if (indexa.isin(superglobaltwo) and indexb.isin(superglobaltwo)):
               continue
            if (indexa.isin(superlocalone) and indexb.isin(superlocalone)):
               continue
            if (indexa.isin(superlocaltwo) and indexb.isin(superlocaltwo)):
               continue
            if (indexa.isin(subglobalone) and indexb.isin(subglobalone)):
               continue
            if (indexa.isin(subglobaltwo) and indexb.isin(subglobaltwo)):
               continue
            if (indexa.isin(sublocalone) and indexb.isin(sublocalone)):
               continue
            if (indexa.isin(sublocaltwo) and indexb.isin(sublocaltwo)):
               continue
            if (indexa.type != indexb.type):
               continue
            inequality = " .le. "
            if (newline):
               newline = string.join([newline," .and. (",indexa.show(),"b",inequality,indexb.show(),"b)"],"")
            else:
               newline = string.join(["IF ((",indexa.show(),"b",inequality,indexb.show(),"b)"],"")
         if (newline):
            newline = string.join([newline,") THEN"],"")
            newcode.pointer = newcode.getamark(3) + 1
            newcode.statements.insert(newcode.pointer,newline)
            newcode.pointer = newcode.pointer + 1
            newline = "END IF"
            newcode.statements.insert(newcode.pointer,newline)
            newcode.setamark(3)
            ifblock = 1

         # sort indexes of tensor 0
         doloop = 0
         for nindex in range(len(permutedindexes)):
            index = permutedindexes[nindex]
            newint = index.show()
            newcode.add("integers",newint)
            newline = string.join(["DO ",newint," = 1,int_mb(k_range+",newint,"b-1)"],"")
            newcode.statements.insert(newcode.pointer,newline)
            newcode.pointer = newcode.pointer + 1
            newline = "END DO"
            newcode.statements.insert(newcode.pointer,newline)
            if (nindex == 0):
               if (ifblock):
                  newcode.setamark(4)
                  doloop = 1
               else:
                  newcode.setamark(3)
                  doloop = 1
         newline = ""
         newlineend = ""
         if (three):
            newcode.add("integers","idimc_sort")
         sorted = superglobalone + superlocalone + subglobalone + sublocalone \
                + superglobaltwo + superlocaltwo + subglobaltwo + sublocaltwo
         for nindex in range(len(sorted)):
            if (newline == ""):
               if (three):
                  newline = string.join(["idimc_sort = ",sorted[nindex].show()],"")
               else:
                  newline = string.join(["idima_sort = ",sorted[nindex].show()],"")
            else:
               newline = string.join([newline," + int_mb(k_range+",sorted[nindex-1].show(),"b-1)"\
                                      " * ((",sorted[nindex].show()," - 1)"],"")
               newlineend = string.join([newlineend,")"],"")
         newline = string.join([newline,newlineend],"")
         if (not newline):
            if (three):
               newline = "idimc_sort = 1"
            else:
               newline = "idima_sort = 1"
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1
         newline = ""
         newlineend = ""
         newcode.add("integers","idimc")
         for nindex in range(len(permutedindexes)-1,-1,-1):
            if (newline == ""):
               newline = string.join(["idimc = ",permutedindexes[nindex].show()],"")
            else:
               newline = string.join([newline," + int_mb(k_range+",permutedindexes[nindex+1].show(),"b-1)"\
                                      " * ((",permutedindexes[nindex].show()," - 1)"],"")
               newlineend = string.join([newlineend,")"],"")
         if (not newline):
            newline = "idimc = 1"
         newline = string.join([newline,newlineend],"")
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1
         if (three):
            if (self.factor.coefficients[npermutation] == 1.0):
               newline = "dbl_mb(k_c + idimc - 1) = dbl_mb(k_c_sort + idimc_sort - 1)"
            elif (self.factor.coefficients[npermutation] == - 1.0):
               newline = "dbl_mb(k_c + idimc - 1) = - dbl_mb(k_c_sort + idimc_sort - 1)"
            else:
               newline = string.join(["dbl_mb(k_c + idimc - 1) = ",repr(self.factor.coefficients[npermutation]),\
                                      "d0 * dbl_mb(k_c_sort + idimc_sort - 1)"],"")
         else:
            if (self.factor.coefficients[npermutation] == 1.0):
               newline = "dbl_mb(k_c + idimc - 1) = dbl_mb(k_a_sort + idima_sort - 1)"
            elif (self.factor.coefficients[npermutation] == - 1.0):
               newline = "dbl_mb(k_c + idimc - 1) = - dbl_mb(k_a_sort + idima_sort - 1)"
            else:
               newline = string.join(["dbl_mb(k_c + idimc - 1) = ",repr(self.factor.coefficients[npermutation]),\
                                      "d0 * dbl_mb(k_a_sort + idima_sort - 1)"],"")
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1

         # accumulate a block
         if (ifblock):
            newcode.pointer = newcode.getamark(4) + 1
         elif (doloop):
            newcode.pointer = newcode.getamark(3) + 1
         arguments = ""
         argumentsend = ""
         for nindex in range(len(permutedindexes)-1,-1,-1):
            if (permutedindexes[nindex].type == "hole"):
               boffset = "b - 1"
            else:
               boffset = "b - noab - 1"
            if (arguments == ""):
               if (three):
                  arguments = string.join(["d_c,dbl_mb(k_c),dima_sort*dimb_sort,int_mb(k_c_offset + ",permutedindexes[nindex].show(),boffset],"")
               else:
                  arguments = string.join(["d_c,dbl_mb(k_c),dima_sort,int_mb(k_c_offset + ",permutedindexes[nindex].show(),boffset],"")
            else:
               if (permutedindexes[nindex+1].type == "hole"):
                  arguments = string.join([arguments," + noab * (",permutedindexes[nindex].show(),boffset],"")
               else:
                  arguments = string.join([arguments," + nvab * (",permutedindexes[nindex].show(),boffset],"")
               argumentsend = string.join([argumentsend,")"],"")
         if (arguments == ""):
            if (three):
               arguments = "d_c,dbl_mb(k_c),dima_sort*dimb_sort,int_mb(k_c_offset"
            else:
               arguments = "d_c,dbl_mb(k_c),dima_sort,int_mb(k_c_offset"
            argumentsend = ""
         arguments = string.join([arguments,argumentsend,")"],"")
         newline = string.join(["CALL ADD_BLOCK(",arguments,")"],"")
         newcode.statements.insert(newcode.pointer,newline)
         if (not ifblock):
            newcode.setamark(3)
         newcode.pointer = newcode.pointer + 1

      newcode.pointer = newcode.getamark(3) + 1
      newline = string.join(["IF (.not.MA_POP_STACK(l_c)) CALL ERRQUIT('",subroutinename,"',",repr(errquit),")"],"")
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      errquit = errquit + 1
      if (three):
         newline = string.join(["IF (.not.MA_POP_STACK(l_c_sort)) CALL ERRQUIT('",subroutinename,"',",repr(errquit),")"],"")
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1
         errquit = errquit + 1
         newline = string.join(["IF (.not.MA_POP_STACK(l_b_sort)) CALL ERRQUIT('",subroutinename,"',",repr(errquit),")"],"")
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1
         errquit = errquit + 1
         newline = string.join(["IF (.not.MA_POP_STACK(l_a_sort)) CALL ERRQUIT('",subroutinename,"',",repr(errquit),")"],"")
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1
         errquit = errquit + 1
      else:
         newline = string.join(["IF (.not.MA_POP_STACK(l_a_sort)) CALL ERRQUIT('",subroutinename,"',",repr(errquit),")"],"")
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1
         errquit = errquit + 1

      # close the subroutine
      newcode.pointer = len(newcode.statements)
      newline = "next = NXTVAL(-nprocs)"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "call GA_SYNC()"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "RETURN"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "END"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1

      return newcode

class OperationTree:
 
   def __init__(self,contraction=NoOperation(),common=[],children=[]):
      """Creates a tree of contraction operations"""
      self.contraction = contraction
      self.common = common
      self.children = children

   def isoperation(self):
      """Returns true if the operation has a valid contraction"""
      return self.contraction.isoperation()
 
   def __str__(self):
      """Prints the content"""
      print ""
      for line in self.show():
         print line
      return ""

   def show(self,ntab=0,verbose=1):
      """Returns the contents as a list of strings"""
      show = []
      if (self.contraction.isoperation()):
         show.append(string.join(["    "*ntab,self.contraction.show(verbose)],""))
      for child in self.children:
         if (child.isoperation()):
            show = show + child.show(ntab+1,verbose)
      return show
 
   def tensorslist(self,list=[]):
      """Returns the non-redundant list of the names of tensors appearing in the tree"""
      if (self.contraction.isoperation()):
         for tensor in self.contraction.tensors:
            if (tensor.type == 'i'):
               tensorname = tensor.type + repr(tensor.label)
            else:
               tensorname = tensor.type + repr(len(tensor.indexes)/2)
            if (tensorname not in list):
               list.append(tensorname)
      if (self.children):
         for child in self.children:
            list = child.tensorslist(list)
      return list

   def usesindexlabel(self,label):
      """Recursively examines whether the index label is used"""
      if (self.contraction.usesindexlabel(label)):
         return 1
      if (self.common):
         if (self.common.usesindexlabel(label)):
            return 1
      for child in self.children:
         if (child.usesindexlabel(label)):
            return 1
      return 0 

   def relabelsone(self,oldlabel,newlabel):
      """Renames an index label in a whole operation tree"""
      self.contraction.relabels(oldlabel,newlabel)
      if (self.common):
         self.common.relabels(oldlabel,newlabel)
      for child in self.children:
         child.relabelsone(oldlabel,newlabel)

   def relabelstwo(self,another,selflabel,anotherlabel,reserved=[]):
      """Renames index labels that are among summation indexes and are arbitrary so that the two input operation trees look more alike"""
      newlabel = 0
      exist = 1
      while (exist):
         newlabel = newlabel + 1
         exist = 0
         if (self.usesindexlabel(newlabel)):
            exist = 1
         if (another.usesindexlabel(newlabel)):
            exist = 1
         if (newlabel in reserved):
            exist = 1
      self.relabelsone(selflabel,newlabel)
      another.relabelsone(anotherlabel,newlabel)

   def swapindexes(self,indexone,indextwo):
      """Swaps two indexes in a whole operation tree"""
      self.contraction.swapindexes(indexone,indextwo)
      if (self.common):
         self.common.swapindexes(indexone,indextwo)
      for child in self.children:
         child.swapindexes(indexone,indextwo)

   def isfactorizablewith(self,another,reserved=[],verbose=0):
      """Returns true if two elementary tensor contractions can be factorized"""

      selfcopy = OperationTree()
      anothercopy = OperationTree()
      selfcopy.contraction = copy.deepcopy(self.contraction)
      selfcopy.common = copy.deepcopy(self.common)
      selfcopy.children = copy.deepcopy(self.children)
      anothercopy.contraction = copy.deepcopy(another.contraction)
      anothercopy.common = copy.deepcopy(another.common)
      anothercopy.children = copy.deepcopy(another.children)

      # check if the two operator trees have valid contraction operations
      if (not (selfcopy.contraction.isoperation() and anothercopy.contraction.isoperation())):
         if (verbose):
            print "not a valid contraction operation"
         return 0

      # check if the output tensors have the identical form
      # (do not check the output tensor types since they are always "i")
      nselfindex = len(selfcopy.contraction.tensors[0].indexes)
      if (nselfindex != len(anothercopy.contraction.tensors[0].indexes)):
         if (verbose):
            print "output tensors imcompatible"
         return 0
      for nindex in range(nselfindex):
         if (not selfcopy.contraction.tensors[0].indexes[nindex].isidenticalto(anothercopy.contraction.tensors[0].indexes[nindex])):
            if (verbose):
               print "output tensors imcompatible"
            return 0

      # check if the factors (permutation operators) are compatible
      ratio = selfcopy.contraction.factor.isthesameas(anothercopy.contraction.factor)
      if (ratio == 0):
         if (verbose):
            print "factors incompatible"
         return 0

      # check if the summation indexes have the same number of holes and particles
      nselfhole = 0
      nselfparticle = 0
      nselfgeneral = 0
      if (not selfcopy.contraction.summation):
         if (verbose):
            print "summations incompatible"
         return 0
      for index in selfcopy.contraction.summation.indexes:
         if (index.type == 'hole'):
            nselfhole = nselfhole + 1
         elif (index.type == 'particle'):
            nselfparticle = nselfparticle + 1
         elif (index.type == 'general'):
            nselfgeneral = nselfgeneral + 1
      nanotherhole = 0
      nanotherparticle = 0
      nanothergeneral = 0
      if (not anothercopy.contraction.summation):
         if (verbose):
            print "summations incompatible"
         return 0
      for index in anothercopy.contraction.summation.indexes:
         if (index.type == 'hole'):
            nanotherhole = nanotherhole + 1
         elif (index.type == 'particle'):
            nanotherparticle = nanotherparticle + 1
         elif (index.type == 'general'):
            nanothergeneral = nanothergeneral + 1
      if ((nselfhole != nanotherhole) or (nselfparticle != nanotherparticle) or (nselfgeneral != nanothergeneral)):
         if (verbose):
            print "summations incompatible"
         return 0

      # find a common tensor
      # (note that the common tensor cannot be an intermediate, and must be identical to the common tensor
      #  used in prior factorizations)
      for nselftensor in range(1,3):
         selftensor = selfcopy.contraction.tensors[nselftensor]
         for nanothertensor in range(1,3):
            anothertensor = anothercopy.contraction.tensors[nanothertensor]
            found = 1
            if (selftensor.type != anothertensor.type):
               found = 0
            elif (selftensor.type == 'i'):
               found = 0
            elif (len(selftensor.indexes) != len(anothertensor.indexes)):
               found = 0
            else:
               for nindex in range(len(selftensor.indexes)):
                  selfindex = selftensor.indexes[nindex]
                  anotherindex = anothertensor.indexes[nindex]
                  if (selfindex.type != anotherindex.type):
                     found = 0
                  elif (selfindex.label != anotherindex.label):
                     if ((not selfcopy.contraction.summation.hastheindex(selfindex)) or \
                         (not anothercopy.contraction.summation.hastheindex(anotherindex))):
                        if (len(anothercopy.contraction.factor.permutations) > 1):
                           before = []
                           for permutation in anothercopy.contraction.factor.permutations:
                              if (len(permutation)/2 > len(before)):
                                 before = copy.deepcopy(permutation[0:len(permutation)/2])
                           beforeandafter = before
                           for nindex in range(len(before)):
                              if (before[nindex].isidenticalto(selfindex)):
                                 beforeandafter.append(anotherindex)
                              elif (before[nindex].isidenticalto(anotherindex)):
                                 beforeandafter.append(selfindex)
                              else:
                                 beforeandafter.append(before[nindex])
                           newfactor = Factor([1.0],[beforeandafter])
                           newfactor = anothercopy.contraction.factor.product(newfactor)
                           ratio = ratio * anothercopy.contraction.factor.isthesameas(newfactor)
                           if (ratio != 0):
                              anothercopy.swapindexes(selfindex,anotherindex)
                           else:
                              found = 0
                        else:
                           found = 0
                     else:
                        selfcopy.relabelstwo(anothercopy,selfindex.label,anotherindex.label,reserved)
               if (selfcopy.common):
                  if (not selfcopy.common.isidenticalto(selftensor)):
                     found = 0

            if (found):
               commonself = selftensor
               if (nselftensor == 1):
                  nuncommonself = 2
               else:
                  nuncommonself = 1
               uncommonself = selfcopy.contraction.tensors[nuncommonself]
               commonanother = anothertensor
               if (nanothertensor == 1):
                  nuncommonanother = 2
               else:
                  nuncommonanother = 1
               uncommonanother = anothercopy.contraction.tensors[nuncommonanother]

               newlabel = selfcopy.contraction.tensors[0].label + 1
               if (uncommonanother.type != "i"):
                  newintermediate = uncommonanother.duplicate()
                  newintermediate.type = "i"
                  newintermediate.label = newlabel
                  parity = newintermediate.sortindexes()
                  newcontraction = ElementaryTensorContraction(Factor([1.0],[[]]),[],[newintermediate,uncommonanother])
                  newchild = OperationTree(newcontraction,[],[])
                  anothercopy.contraction.tensors[nuncommonself] = newintermediate
                  anothercopy.children.insert(0,newchild)
               if (uncommonself.type != "i"):
                  newintermediate = uncommonself.duplicate()
                  newintermediate.type = "i"
                  newintermediate.label = newlabel
                  parity = newintermediate.sortindexes()
                  newcontraction = ElementaryTensorContraction(Factor([1.0],[[]]),[],[newintermediate,uncommonself])
                  newchild = OperationTree(newcontraction,[],[])
                  selfcopy.contraction.tensors[nuncommonself] = newintermediate
                  selfcopy.children.insert(0,newchild)
               selfcopy.common = commonself
               for child in anothercopy.children:
                  if (child.contraction.isoperation()):
                     child.contraction.factor.multiply(ratio)
                  selfcopy.children.append(child)

               # now we overwrite the self operation tree
               # (nothing is done to another after all, since it will be deleted anyway)
               self.contraction = copy.deepcopy(selfcopy.contraction)
               self.common = copy.deepcopy(selfcopy.common)
               self.children = copy.deepcopy(selfcopy.children)
               return 1

      # no common tensor found
      if (verbose):
         print "no common tensor"
      return 0

   def factorize(self,reserved=[],verbose=0):
      """Factors a common operation"""
      deletelist = []
      for nchilda in range(len(self.children)):
         if (nchilda in deletelist):
            continue
         childa = self.children[nchilda]
         if (childa.contraction.isoperation()):
            for nchildb in range(len(self.children)):
               if (nchildb in deletelist):
                  continue
               if (nchilda >= nchildb):
                  continue
               childb = self.children[nchildb]
               if (childb.contraction.isoperation()):
                  childc = copy.deepcopy(childa)
                  if (childa.isfactorizablewith(childb,reserved)):
                     if (verbose):
                        print childc
                        print " ... and"
                        print childb
                        print " ... have been consolidated into"
                        print childa
                        print ""
                     self.children[nchilda] = childa
                     deletelist.append(nchildb)
      if (deletelist):
         print " ... %d terms have been consolidated" %(len(deletelist))
         for nchildb in range(len(self.children)-1,-1,-1):
            if (nchildb in deletelist):
               del self.children[nchildb]
         return 1
      else:
         return 0

   def fullyfactorize(self,verbose=0,iteration=0,generation=1,reserved=[]):
      """Performs factorize() recursively until fully factorized"""
      if ((iteration == 0) and (generation == 1)):
         reserved = []
         for targetindex in self.children[0].contraction.tensors[0].indexes:
            reserved.append(targetindex.label)
         print " ... commencing full factorization"
         print " ... initial contraction cost %d" %(self.operationcost())
      print " ... tensor contraction tier %d" %(generation)
      while (self.factorize(reserved,verbose)):
         iteration = iteration + 1
         print " ... iteration %d cost %d" %(iteration, self.operationcost())
      if (self.children):
         for child in self.children:
            child.fullyfactorize(verbose,0,generation+1,reserved)
      if (generation == 1):
         print " ... exiting full factorization"
         print " ... final contraction cost %d" %(self.operationcost())
      self.sortindexes()
      return self

   def sortindexes(self):
      """Perform sortindex() for the whole operation tree"""
      if (self.contraction.isoperation()):
         self.contraction.sortindexes()
      if (self.children):
         for child in self.children:
            child.sortindexes()
      return self

   def operationcost(self,cost=0):
      """Returns a contraction cost"""
      if (self.contraction.isoperation()):
         if (len(self.contraction.tensors) > 2):
            cost = cost + 1
      for child in self.children:
         cost = child.operationcost(cost)
      return cost

   def fortran77(self,filename="NONAME"):
      """Suggests an implementation in Fortran77 for the whole operation tree"""

      newlistofcodes = ListofCodes()

      # callees (tensor contraction subroutines called from the main)
      callees = ListofCodes()

      # copy of self will be reduced as we write the program
      selfcopy = OperationTree()
      selfcopy.contraction = copy.deepcopy(self.contraction)
      selfcopy.common = copy.deepcopy(self.common)
      selfcopy.children = copy.deepcopy(self.children)

      # target indexes
      if (selfcopy.children[0].contraction.isoperation()):
         globaltargetindexes = copy.deepcopy(selfcopy.children[0].contraction.tensors[0].indexes)
      else:
         return "The tree top must be an addition"

      newcode = Code("Fortran77",filename)

      # header
      for newline in self.show(0,0):
         newline = string.join(["!",newline[4:]],"")
         newcode.add("headers",newline)
      newline = "IMPLICIT NONE"
      newcode.add("headers",newline)
      newline = '#include "global.fh"'
      newcode.add("headers",newline)
      newline = '#include "mafdecls.fh"'
      newcode.add("headers",newline)
      newline = '#include "tce.fh"'
      newcode.add("headers",newline)
      
      # loop over the tree
      newcode.join(selfcopy.fortran77a(filename,globaltargetindexes,callees).expand())

      # antisymmetrizer
      newcode.pointer = len(newcode.statements)
      if (globaltargetindexes):
         newline = string.join(["CALL ANTISYM_",filename,"(d_i0,k_i0_offset)"],"")
         newcode.statements.insert(newcode.pointer,newline)
         newcode.pointer = newcode.pointer + 1
         antisymmetrizer = selfcopy.children[0].contraction.tensors[0].fortran77x(filename)

      # close the subroutine
      newline = "RETURN"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1
      newline = "END"
      newcode.statements.insert(newcode.pointer,newline)
      newcode.pointer = newcode.pointer + 1

      # append the callees
      newlistofcodes.add(newcode)
      newlistofcodes.join(callees)
      if (globaltargetindexes):
         newlistofcodes.add(antisymmetrizer)

      return newlistofcodes

   def fortran77a(self,subroutinename,globaltargetindexes,callees):
      """Returns a part of program that is generated by recursively interpreting the tree"""

      newcode = Code("Fortran77",subroutinename)

      # check if we need to proceed
      if (not self.children):
         return newcode
      else:
         empty = 1
         for child in self.children:
            if (child.contraction.isoperation()):
               empty = 0
         if (empty):
            return newcode

      # get a filename for intermediate storage
      d_c = string.join(["d_i",repr(self.children[0].contraction.tensors[0].label)],"")
      newcode.add("integers",d_c)
      if (not self.contraction.isoperation()):
         newcode.add("arguments",d_c)
      l_c_offset = string.join(["l_i",repr(self.children[0].contraction.tensors[0].label),"_offset"],"")
      k_c_offset = string.join(["k_i",repr(self.children[0].contraction.tensors[0].label),"_offset"],"")
      newcode.add("integers",k_c_offset)
      if (self.contraction.isoperation()):
         newcode.add("integers",l_c_offset)
      else:
         newcode.add("arguments",k_c_offset)

      # loop over children
      if (self.contraction.isoperation()):
         createfile = 1
      else:
         createfile = 0
      counter = 0
      for nchild in range(len(self.children)):
         child = self.children[nchild]
         if (child.contraction.isoperation()):
            counter = counter + 1
            name = string.join([subroutinename,"_",repr(counter)],"")
 
            # Tensor 1
            superglobalzero = []
            subglobalzero = []
            superlocalzero = []
            sublocalzero = []
            for nindex in range(len(child.contraction.tensors[0].indexes)/2):
               index = child.contraction.tensors[0].indexes[nindex]
               if (index.isin(globaltargetindexes)):
                  superglobalzero.append(index)
               else:
                  superlocalzero.append(index)
            for nindex in range(len(child.contraction.tensors[0].indexes)/2, \
                                len(child.contraction.tensors[0].indexes)):
               index = child.contraction.tensors[0].indexes[nindex]
               if (index.isin(globaltargetindexes)):
                  subglobalzero.append(index)
               else:
                  sublocalzero.append(index)

            # generate the contraction callee
            callee = child.contraction.fortran77(globaltargetindexes,name)
            callees.add(callee)

            if (child.contraction.tensors[1].type == "i"):
               d_a = string.join(["d_i",repr(child.contraction.tensors[1].label)],"") 
               newcode.add("integers",d_a)
               k_a_offset = string.join(["k_i",repr(child.contraction.tensors[1].label),"_offset"],"")
               l_a_offset = string.join(["l_i",repr(child.contraction.tensors[1].label),"_offset"],"")
               newcode.add("integers",k_a_offset)
            else:
               d_a = string.join(["d_",child.contraction.tensors[1].type,repr(len(child.contraction.tensors[1].indexes)/2)],"") 
               newcode.add("integers",d_a)
               newcode.add("arguments",d_a)
               k_a_offset = string.join(["k_",child.contraction.tensors[1].type,\
                            repr(len(child.contraction.tensors[1].indexes)/2),"_offset"],"")
               newcode.add("integers",k_a_offset)
               newcode.add("arguments",k_a_offset)
            if (len(child.contraction.tensors) == 3):
               if (child.contraction.tensors[2].type == "i"):
                  d_b = string.join(["d_i",repr(child.contraction.tensors[2].label)],"") 
                  newcode.add("integers",d_b)
                  k_b_offset = string.join(["k_i",repr(child.contraction.tensors[2].label),"_offset"],"")
                  l_b_offset = string.join(["l_i",repr(child.contraction.tensors[2].label),"_offset"],"")
                  newcode.add("integers",k_b_offset)
               else:
                  d_b = string.join(["d_",child.contraction.tensors[2].type,repr(len(child.contraction.tensors[2].indexes)/2)],"") 
                  newcode.add("integers",d_b)
                  newcode.add("arguments",d_b)
                  k_b_offset = string.join(["k_",child.contraction.tensors[2].type,\
                               repr(len(child.contraction.tensors[2].indexes)/2),"_offset"],"")
                  newcode.add("integers",k_b_offset)
                  newcode.add("arguments",k_b_offset)
            else:
               d_b = ""
            
            # dump the code
            if (createfile):
               newint = "size"
               newcode.add("integers",newint)
               newline = string.join(["CALL OFFSET_",name,"(",d_c,",",l_c_offset,",",k_c_offset,",size)"],"")
               newcode.statements.insert(0,newline)
               filename = string.join([name,"_i",repr(child.contraction.tensors[1].label)],"")
               newline = string.join(["CALL CREATEFILE('",filename,"',",d_c,",size)"],"")
               newcode.statements.insert(0,newline)
               callee = child.contraction.tensors[0].fortran77y(globaltargetindexes,name)
               callees.add(callee)
               createfile = 0
            newcode.statements.insert(0,child.fortran77a(name,globaltargetindexes,callees))
            argument = string.join([d_a,",",k_a_offset],"")
            if (d_b):
               argument = string.join([argument,",",d_b,",",k_b_offset],"")
            argument = string.join([argument,",",d_c,",",k_c_offset],"")
            newline = string.join(["CALL ",name,"(",argument,")"],"")
            newcode.statements.insert(0,newline)
            if (child.contraction.tensors[1].type == "i"):
               newline = string.join(["CALL DELETEFILE(",d_a,")"],"")
               newcode.statements.insert(0,newline)
               newline = string.join(["IF (.not.MA_POP_STACK(",l_a_offset,")) CALL ERRQUIT('",subroutinename,"',-1)"],"")
               newcode.statements.insert(0,newline)
            if (d_b):
               if (child.contraction.tensors[2].type == "i"):
                  newline = string.join(["CALL DELETEFILE(",d_b,")"],"")
                  newcode.statements.insert(0,newline)
                  newline = string.join(["IF (.not.MA_POP_STACK(",l_b_offset,")) CALL ERRQUIT('",subroutinename,"',-1)"],"")
                  newcode.statements.insert(0,newline)
 
      newcode.reverse()
      return newcode

   def pythongen(self,filename="NONAME"):
      """Genrates a python code for debugging purposes"""

      pythoncode = []

      tensornames = self.tensorslist([])
      tensorargument = ""
      for tensorname in tensornames:
         tensorargument = string.join([tensorargument,",",tensorname],"")
      newline = string.join(["def ",filename,"(N,nall,nocc",tensorargument,"):"],"")
      pythoncode.append(newline)
      newline = " # This is a Python program generated by Tensor Contraction Engine v.1.0"
      pythoncode.append(newline)
      newline = " # (c) All rights reserved by Battelle & Pacific Northwest Nat'l Lab (2002)"
      pythoncode.append(newline)
 
      # copy of self will be reduced as we write the program
      selfcopy = OperationTree()
      selfcopy.contraction = copy.deepcopy(self.contraction)
      selfcopy.common = copy.deepcopy(self.common)
      selfcopy.children = copy.deepcopy(self.children)
 
      # loop over the tree
      newcode = selfcopy.pythongena(0)
      newcodeexpanded = expand(newcode)
      for newline in newcodeexpanded:
         pythoncode.append(newline)
         
      # dump the code to a file
      writetofile(pythoncode,string.join([filename,".py.out"],""))

   def pythongena(self,pointer=0):
      """Recursive subprogram called by pythongen"""

      pythoncode = []

      # check if we need to proceed
      if (not self.children):
         return pythoncode
      else:
         empty = 1
         for child in self.children:
            if (child.contraction.isoperation()):
               empty = 0
         if (empty):
            return pythoncode

      # loop over children
      zeroscratch = 1
      for child in self.children:
         if (child.contraction.isoperation()):

            # recursive pythongena() call
            pythoncode.insert(pointer,child.pythongena(pointer))
            pointer = len(pythoncode)
            
            # generate loops over target indexes
            indent = 1
            for index in child.contraction.tensors[0].indexes:
               spin = string.join(["spin",repr(index.label)],"")
               newline = string.join(["for ",spin," in range(2):"],"")
               newline = string.join([" "*indent,newline],"")
               pythoncode.insert(pointer,newline)
               pointer = pointer + 1
               indent = indent + 1
               if (index.type == 'hole'):
                  newline = string.join(["for ",index.show()," in range(",spin,"*nall[0],",spin,"*nall[0]+nocc[",spin,"]):"],"")
                  newline = string.join([" "*indent,newline],"")
                  pythoncode.insert(pointer,newline)
                  pointer = pointer + 1
                  indent = indent + 1
               elif (index.type == 'particle'):
                  newline = string.join(["for ",index.show()," in range(",spin,"*nall[0]+nocc[",spin,"],",spin,"*nall[0]+nall[",spin,"]):"],"")
                  newline = string.join([" "*indent,newline],"")
                  pythoncode.insert(pointer,newline)
                  pointer = pointer + 1
                  indent = indent + 1
               elif (index.type == 'general'):
                  newline = string.join(["for ",index.show()," in range(",spin,"*nall[0],",spin,"*nall[0]+nall[",spin,"]):"],"")
                  newline = string.join([" "*indent,newline],"")
                  pythoncode.insert(pointer,newline)
                  pointer = pointer + 1
                  indent = indent + 1
            if (zeroscratch):
               newline = string.join([child.contraction.tensors[0].pythongen(),"=0.0"],"")
               newline = string.join([" "*indent,newline],"")
               pythoncode.insert(pointer,newline)
               pointer = pointer + 1
               zeroscratch = 0

            # generate loops over common indexes
            if (child.contraction.summation):
               for index in child.contraction.summation.indexes:
                  spin = string.join(["spin",repr(index.label)],"")
                  newline = string.join(["for ",spin," in range(2):"],"")
                  newline = string.join([" "*indent,newline],"")
                  pythoncode.insert(pointer,newline)
                  pointer = pointer + 1
                  indent = indent + 1
                  if (index.type == 'hole'):
                     newline = string.join(["for ",index.show()," in range(",spin,"*nall[0],",spin,"*nall[0]+nocc[",spin,"]):"],"")
                     newline = string.join([" "*indent,newline],"")
                     pythoncode.insert(pointer,newline)
                     pointer = pointer + 1
                     indent = indent + 1
                  elif (index.type == 'particle'):
                     newline = string.join(["for ",index.show()," in range(",spin,"*nall[0]+nocc[",spin,"],",spin,"*nall[0]+nall[",spin,"]):"],"")
                     newline = string.join([" "*indent,newline],"")
                     pythoncode.insert(pointer,newline)
                     pointer = pointer + 1
                     indent = indent + 1
                  elif (index.type == 'general'):
                     newline = string.join(["for ",index.show()," in range(",spin,"*nall[0],",spin,"*nall[0]+nall[",spin,"]):"],"")
                     newline = string.join([" "*indent,newline],"")
                     pythoncode.insert(pointer,newline)
                     pointer = pointer + 1
                     indent = indent + 1
            newline = string.join([child.contraction.tensors[0].pythongen(),"=",child.contraction.tensors[0].pythongen(),"+",\
                                   "(",repr(child.contraction.factor),")"],"")
            for ntensor in range(len(child.contraction.tensors)):
               if (ntensor != 0):
                  tensor = child.contraction.tensors[ntensor]
                  newline = string.join([newline,"*",tensor.pythongen()],"")
            newline = string.join([" "*indent,newline],"")
            pythoncode.insert(pointer,newline)
            pointer = pointer + 1

      return pythoncode

   def fortran90(self,filename="NONAME",mode="nopermutation"):
      """Genrates a partial Fortran90 code for debugging purposes"""
      # Mode = "permutation"   : writes a code which takes index permutation into account
      # Mode = "nopermutation" : writes a code without index permutation considered
      # Mode = "analysis"      : stdouts a plan of implementation with index permutation

      f90code = Code("Fortran90",filename)
      newline = "IMPLICIT NONE"
      f90code.add("headers",newline)

      # copy of self will be reduced as we write the program
      selfcopy = OperationTree()
      selfcopy.contraction = copy.deepcopy(self.contraction)
      selfcopy.common = copy.deepcopy(self.common)
      selfcopy.children = copy.deepcopy(self.children)

      # target indexes
      if (selfcopy.children[0].contraction.isoperation()):
         globaltargetindexes = copy.deepcopy(selfcopy.children[0].contraction.tensors[0].indexes)
      else:
         return "The tree top must be an addition"
      if (mode == "analysis"):
         show = "Global target indexes: "
         for index in globaltargetindexes:
            show = string.join([show,index.show()])
         print show
         print ""
 
      # loop over the tree
      f90code.statements.insert(f90code.pointer,selfcopy.fortran90a(globaltargetindexes,mode))
      
      # add an antisymmetrizer (only for the target intermediate)
      if (mode == "nopermutation"):
         f90code.statements.append(selfcopy.children[0].contraction.tensors[0].fortran90x())
      
      # close the subroutine
      newline = "RETURN"
      f90code.statements.append(newline)
      newline = "END SUBROUTINE"
      f90code.statements.append(newline)

      # headers
      f90code.add("arguments","N")
      f90code.add("integers","N")
      f90code.add("arguments","nocc")
      f90code.add("integers","nocc")
      if (mode == "nopermutation"):
         f90code.add("doubles","TMP")
      for n in self.tensorslist([]):
         f90code.add("arguments",n)
         f90code.add("doublearrays",n)
         if (mode == "permutation"):
            f90code.add("arguments",n+"e")
            f90code.add("doublearrays",n+"e")

      # dump the code to a file
      f90code = f90code.expand()
      f90code.sortarguments()
      f90code.writetofile(filename)
      if (mode == "analysis"):
         return "No Fortran code is dumped"
      else:
         return f90code

   def fortran90a(self,globaltargetindexes,mode="nopermutation"):
      """Recursive subprogram called by fortran90"""

      newcode = Code("Fortran90","")

      # check if we need to proceed
      if (not self.children):
         return newcode
      else:
         empty = 1
         for child in self.children:
            if (child.contraction.isoperation()):
               empty = 0
         if (empty):
            return newcode

      # loop over children
      zeroscratch = 1
      for child in self.children:
         if (child.contraction.isoperation()):

            # recursive fortran90a() call
            newcode.statements.insert(newcode.pointer,child.fortran90a(globaltargetindexes,mode))
            newcode.pointer = len(newcode.statements)
            
            # Tensor 1
            superglobalzero = []
            subglobalzero = []
            superlocalzero = []
            sublocalzero = []
            for nindex in range(len(child.contraction.tensors[0].indexes)/2):
               index = child.contraction.tensors[0].indexes[nindex]
               if (index.isin(globaltargetindexes)):
                  superglobalzero.append(index)
               else:
                  superlocalzero.append(index)
            for nindex in range(len(child.contraction.tensors[0].indexes)/2,len(child.contraction.tensors[0].indexes)):
               index = child.contraction.tensors[0].indexes[nindex]
               if (index.isin(globaltargetindexes)):
                  subglobalzero.append(index)
               else:
                  sublocalzero.append(index)

            # Tensor 2
            superglobalone = []
            subglobalone = []
            superlocalone = []
            sublocalone = []
            supercommonone = []
            subcommonone = []
            for nindex in range(len(child.contraction.tensors[1].indexes)/2):
               index = child.contraction.tensors[1].indexes[nindex]
               if (index.isin(globaltargetindexes)):
                  superglobalone.append(index)
               elif (child.contraction.summation):
                  if (index.isin(child.contraction.summation.indexes)):
                     supercommonone.append(index)
                  else:
                     superlocalone.append(index)
               else:
                  superlocalone.append(index)
            for nindex in range(len(child.contraction.tensors[1].indexes)/2,len(child.contraction.tensors[1].indexes)):
               index = child.contraction.tensors[1].indexes[nindex]
               if (index.isin(globaltargetindexes)):
                  subglobalone.append(index)
               elif (child.contraction.summation):
                  if (index.isin(child.contraction.summation.indexes)):
                     subcommonone.append(index)
                  else:
                     sublocalone.append(index)
               else:
                  sublocalone.append(index)

            # Tensor 3
            superglobaltwo = []
            subglobaltwo = []
            superlocaltwo = []
            sublocaltwo = []
            supercommontwo = []
            subcommontwo = []
            if (len(child.contraction.tensors) > 2):
               for nindex in range(len(child.contraction.tensors[2].indexes)/2):
                  index = child.contraction.tensors[2].indexes[nindex]
                  if (index.isin(globaltargetindexes)):
                     superglobaltwo.append(index)
                  elif (child.contraction.summation):
                     if (index.isin(child.contraction.summation.indexes)):
                        supercommontwo.append(index)
                     else:
                        superlocaltwo.append(index)
                  else:
                     superlocaltwo.append(index)
               for nindex in range(len(child.contraction.tensors[2].indexes)/2,len(child.contraction.tensors[2].indexes)):
                  index = child.contraction.tensors[2].indexes[nindex]
                  if (index.isin(globaltargetindexes)):
                     subglobaltwo.append(index)
                  elif (child.contraction.summation):
                     if (index.isin(child.contraction.summation.indexes)):
                        subcommontwo.append(index)
                     else:
                        sublocaltwo.append(index)
                  else:
                     sublocaltwo.append(index)
            if (len(supercommonone) > len(subcommontwo)):
               supercommon = supercommonone
            else:
               supercommon = subcommontwo
            if (len(subcommonone) > len(supercommontwo)):
               subcommon = subcommonone
            else:
               subcommon = supercommontwo

            if (mode == "analysis"):

               # Zero scratch?
               if (zeroscratch):
                  print child.contraction.tensors[0].show(),"will be zeroscratched"
                  zeroscratch = 0

               # Structure of tensor 1
               tensorzerocompressed = 0
               show = "Storage of tensor 1:"
               if (superglobalzero):
                  show = string.join([show,"["])
                  for nindex in range(len(superglobalzero)):
                     index = superglobalzero[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if (subglobalzero):
                  show = string.join([show,"["])
                  for nindex in range(len(subglobalzero)):
                     index = subglobalzero[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if (superlocalzero):
                  show = string.join([show,"["])
                  for nindex in range(len(superlocalzero)):
                     index = superlocalzero[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if (sublocalzero):
                  show = string.join([show,"["])
                  for nindex in range(len(sublocalzero)):
                     index = sublocalzero[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if ((superglobalone) and (superglobaltwo)):
                  tensorzerocompressed = 1
                  show = string.join([show,"Compress ["])
                  for nindex in range(len(superglobalone)):
                     index = superglobalone[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"] ["])
                  for nindex in range(len(superglobaltwo)):
                     index = superglobaltwo[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if ((subglobalone) and (subglobaltwo)):
                  tensorzerocompressed = 1
                  show = string.join([show,"Compress ["])
                  for nindex in range(len(subglobalone)):
                     index = subglobalone[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"] ["])
                  for nindex in range(len(subglobaltwo)):
                     index = subglobaltwo[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               print show

               # Structure of tensor 2
               tensoroneexpanded = 0
               show = "Storage of tensor 2:"
               if (child.contraction.tensors[1].type == 'i'):
                  if (superglobalone):
                     show = string.join([show,"["])
                     for nindex in range(len(superglobalone)):
                        index = superglobalone[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"]"])
                  if (subglobalone):
                     show = string.join([show,"["])
                     for nindex in range(len(subglobalone)):
                        index = subglobalone[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"]"])
               if (child.contraction.tensors[1].type == 'i'):
                  superremainderone = sortindexes(superlocalone + supercommonone)
               else:
                  superremainderone = sortindexes(superglobalone + superlocalone + supercommonone)
               if (superremainderone):
                  show = string.join([show,"["])
                  for nindex in range(len(superremainderone)):
                     index = superremainderone[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if (child.contraction.tensors[1].type == 'i'):
                  subremainderone = sublocalone + subcommonone
               else:
                  subremainderone = subglobalone + sublocalone + subcommonone
               if (subremainderone):
                  show = string.join([show,"["])
                  for nindex in range(len(subremainderone)):
                     index = subremainderone[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if ((child.contraction.tensors[1].type == 'i') and (superlocalone) and (supercommonone)):
                  tensoroneexpanded = 1
                  show = string.join([show,"Expand ["])
                  for nindex in range(len(superlocalone)):
                     index = superlocalone[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"] ["])
                  for nindex in range(len(supercommonone)):
                     index = supercommonone[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if ((child.contraction.tensors[1].type != 'i') and \
                  (((superglobalone) and (superlocalone)) or \
                  ((superlocalone) and (supercommonone)) or \
                  ((supercommonone) and (superglobalone)))):
                  tensoroneexpanded = 1
                  show = string.join([show,"Expand"])
                  if (superglobalone):
                     show = string.join([show,"["])
                     for nindex in range(len(superglobalone)):
                        index = superglobalone[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"]"])
                  if (superlocalone):
                     show = string.join([show,"["])
                     for nindex in range(len(superlocalone)):
                        index = superlocalone[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"]"])
                  if (supercommonone):
                     show = string.join([show,"["])
                     for nindex in range(len(supercommonone)):
                        index = supercommonone[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"]"])
               if ((child.contraction.tensors[1].type == 'i') and (sublocalone) and (subcommonone)):
                  tensoroneexpanded = 1
                  show = string.join([show,"Expand ["])
                  for nindex in range(len(sublocalone)):
                     index = sublocalone[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"] ["])
                  for nindex in range(len(subcommonone)):
                     index = subcommonone[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if ((child.contraction.tensors[1].type != 'i') and \
                  (((subglobalone) and (sublocalone)) or \
                  ((sublocalone) and (subcommonone)) or \
                  ((subcommonone) and (subglobalone)))):
                  tensoroneexpanded = 1
                  show = string.join([show,"Expand"])
                  if (subglobalone):
                     show = string.join([show,"["])
                     for nindex in range(len(subglobalone)):
                        index = subglobalone[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"]"])
                  if (sublocalone):
                     show = string.join([show,"["])
                     for nindex in range(len(sublocalone)):
                        index = sublocalone[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"]"])
                  if (subcommonone):
                     show = string.join([show,"["])
                     for nindex in range(len(subcommonone)):
                        index = subcommonone[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"]"])
               print show

               # Structure of tensor 2
               if (len(child.contraction.tensors) > 2):
                  tensortwoexpanded = 0
                  show = "Storage of tensor 3:"
                  if (child.contraction.tensors[2].type == 'i'):
                     if (superglobaltwo):
                        show = string.join([show,"["])
                        for nindex in range(len(superglobaltwo)):
                           index = superglobaltwo[nindex]
                           if (nindex > 0):
                              show = string.join([show,"<"])
                           show = string.join([show,index.show()])
                        show = string.join([show,"]"])
                     if (subglobaltwo):
                        show = string.join([show,"["])
                        for nindex in range(len(subglobaltwo)):
                           index = subglobaltwo[nindex]
                           if (nindex > 0):
                              show = string.join([show,"<"])
                           show = string.join([show,index.show()])
                        show = string.join([show,"]"])
                  if (child.contraction.tensors[2].type == 'i'):
                     superremaindertwo = sortindexes(superlocaltwo + supercommontwo)
                  else:
                     superremaindertwo = sortindexes(superglobaltwo + superlocaltwo + supercommontwo)
                  if (superremaindertwo):
                     show = string.join([show,"["])
                     for nindex in range(len(superremaindertwo)):
                        index = superremaindertwo[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"]"])
                  if (child.contraction.tensors[2].type == 'i'):
                     subremaindertwo = sublocaltwo + subcommontwo
                  else:
                     subremaindertwo = subglobaltwo + sublocaltwo + subcommontwo
                  if (subremaindertwo):
                     show = string.join([show,"["])
                     for nindex in range(len(subremaindertwo)):
                        index = subremaindertwo[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"]"])
                  if ((child.contraction.tensors[2].type == 'i') and (superlocaltwo) and (supercommontwo)):
                     tensortwoexpanded = 1
                     show = string.join([show,"Expand ["])
                     for nindex in range(len(superlocaltwo)):
                        index = superlocaltwo[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"] ["])
                     for nindex in range(len(supercommontwo)):
                        index = supercommontwo[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"]"])
                  if ((child.contraction.tensors[2].type != 'i') and \
                     (((superglobaltwo) and (superlocaltwo)) or \
                     ((superlocaltwo) and (supercommontwo)) or \
                     ((supercommontwo) and (superglobaltwo)))):
                     tensortwoexpanded = 1
                     show = string.join([show,"Expand"])
                     if (superglobaltwo):
                        show = string.join([show,"["])
                        for nindex in range(len(superglobaltwo)):
                           index = superglobaltwo[nindex]
                           if (nindex > 0):
                              show = string.join([show,"<"])
                           show = string.join([show,index.show()])
                        show = string.join([show,"]"])
                     if (superlocaltwo):
                        show = string.join([show,"["])
                        for nindex in range(len(superlocaltwo)):
                           index = superlocaltwo[nindex]
                           if (nindex > 0):
                              show = string.join([show,"<"])
                           show = string.join([show,index.show()])
                        show = string.join([show,"]"])
                     if (supercommontwo):
                        show = string.join([show,"["])
                        for nindex in range(len(supercommontwo)):
                           index = supercommontwo[nindex]
                           if (nindex > 0):
                              show = string.join([show,"<"])
                           show = string.join([show,index.show()])
                        show = string.join([show,"]"])
                  if ((child.contraction.tensors[2].type == 'i') and (sublocaltwo) and (subcommontwo)):
                     tensortwoexpanded = 1
                     show = string.join([show,"Expand ["])
                     for nindex in range(len(sublocaltwo)):
                        index = sublocaltwo[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"] ["])
                     for nindex in range(len(subcommontwo)):
                        index = subcommontwo[nindex]
                        if (nindex > 0):
                           show = string.join([show,"<"])
                        show = string.join([show,index.show()])
                     show = string.join([show,"]"])
                  if ((child.contraction.tensors[2].type != 'i') and \
                     (((subglobaltwo) and (sublocaltwo)) or \
                     ((sublocaltwo) and (subcommontwo)) or \
                     ((subcommontwo) and (subglobaltwo)))):
                     tensortwoexpanded = 1
                     show = string.join([show,"Expand"])
                     if (subglobaltwo):
                        show = string.join([show,"["])
                        for nindex in range(len(subglobaltwo)):
                           index = subglobaltwo[nindex]
                           if (nindex > 0):
                              show = string.join([show,"<"])
                           show = string.join([show,index.show()])
                        show = string.join([show,"]"])
                     if (sublocaltwo):
                        show = string.join([show,"["])
                        for nindex in range(len(sublocaltwo)):
                           index = sublocaltwo[nindex]
                           if (nindex > 0):
                              show = string.join([show,"<"])
                           show = string.join([show,index.show()])
                        show = string.join([show,"]"])
                     if (subcommontwo):
                        show = string.join([show,"["])
                        for nindex in range(len(subcommontwo)):
                           index = subcommontwo[nindex]
                           if (nindex > 0):
                              show = string.join([show,"<"])
                           show = string.join([show,index.show()])
                        show = string.join([show,"]"])
                  print show

               # Summation indexes
               show = "Summation composite indexes:"
               if (supercommon):
                  show = string.join([show,"["])
                  for nindex in range(len(supercommon)):
                     index = supercommon[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if (subcommon):
                  show = string.join([show,"["])
                  for nindex in range(len(subcommon)):
                     index = subcommon[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if ((not supercommon) and (not subcommon)):
                  show = string.join([show,"none"])
               else:
                  factor = factorial(len(supercommon)) * factorial(len(subcommon))
                  show = string.join([show,"with a factor of",repr(factor)])
               print show

               # Target indexes
               show = "Target composite indexes:"
               if (superglobalone):
                  show = string.join([show,"["])
                  for nindex in range(len(superglobalone)):
                     index = superglobalone[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if (subglobalone):
                  show = string.join([show,"["])
                  for nindex in range(len(subglobalone)):
                     index = subglobalone[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if (superglobaltwo):
                  show = string.join([show,"["])
                  for nindex in range(len(superglobaltwo)):
                     index = superglobaltwo[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if (subglobaltwo):
                  show = string.join([show,"["])
                  for nindex in range(len(subglobaltwo)):
                     index = subglobaltwo[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if (superlocalone):
                  show = string.join([show,"["])
                  for nindex in range(len(superlocalone)):
                     index = superlocalone[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if (sublocalone):
                  show = string.join([show,"["])
                  for nindex in range(len(sublocalone)):
                     index = sublocalone[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if (superlocaltwo):
                  show = string.join([show,"["])
                  for nindex in range(len(superlocaltwo)):
                     index = superlocaltwo[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               if (sublocaltwo):
                  show = string.join([show,"["])
                  for nindex in range(len(sublocaltwo)):
                     index = sublocaltwo[nindex]
                     if (nindex > 0):
                        show = string.join([show,"<"])
                     show = string.join([show,index.show()])
                  show = string.join([show,"]"])
               print show
               print child.contraction
               print ""

            # zero scratch
            if ((zeroscratch) and (mode == "nopermutation")):
               for index in child.contraction.tensors[0].indexes:
                  newcode.insertdoloop(index)
               newdbl = child.contraction.tensors[0].fortran90()
               newline = string.join([newdbl,"=0.0d0"],"")
               newcode.statements.insert(newcode.pointer,newline)
               newcode.pointer = len(newcode.statements)
               zeroscratch = 0

            expanded = [0,0,0]
            # expand index ranges of tensor 1
            if (mode == "permutation"):
               if (child.contraction.tensors[1].type == "i"):
                  if ((superlocalone and supercommonone) or (sublocalone and subcommonone)):
                     expanded[1] = 1
                     super = sortindexes(superlocalone + supercommonone)
                     sub = sortindexes(sublocalone + subcommonone)
                     for index in superglobalone:
                        newcode.insertdoloop(index)
                     if (len(superglobalone) > 1):
                        newcode.insertif(superglobalone,1)
                     for index in super:
                        newcode.insertdoloop(index)
                     if (len(super) > 1):
                        newcode.insertif(super,1)
                     for index in subglobalone:
                        newcode.insertdoloop(index)
                     if (len(subglobalone) > 1):
                        newcode.insertif(subglobalone,1)
                     for index in sub:
                        newcode.insertdoloop(index)
                     if (len(sub) > 1):
                        newcode.insertif(sub,1)
                     if (superlocalone and supercommonone):
                        nsuperpermutations = factorial(len(super))
                        superpermutations = permutationwithparity(len(super))
                     else:
                        nsuperpermutations = 1
                     if (sublocalone and subcommonone):
                        nsubpermutations = factorial(len(sub))
                        subpermutations = permutationwithparity(len(sub))
                     else:
                        nsubpermutations = 1
                     for nsuperpermutation in range(nsuperpermutations):
                        for nsubpermutation in range(nsubpermutations):
                           permutation = super + sub
                           parity = 1
                           rejected = 0
                           if (superlocalone and supercommonone):
                              parity = parity * superpermutations[nsuperpermutation][0]
                              for nindex in range(1,len(super)+1):
                                 permutation.append(super[superpermutations[nsuperpermutation][nindex]-1])
                              if (len(superlocalone) > 1):
                                 for nindexa in range(len(superlocalone)):
                                    for nindexb in range(len(superlocalone)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = superlocalone[nindexa]
                                       indexb = superlocalone[nindexb]
                                       for nindex in range(len(super)):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(super+sub)+nindexc].isgreaterthan(permutation[len(super+sub)+nindexd])):
                                          rejected = 1
                              if (len(supercommonone) > 1):
                                 for nindexa in range(len(supercommonone)):
                                    for nindexb in range(len(supercommonone)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = supercommonone[nindexa]
                                       indexb = supercommonone[nindexb]
                                       for nindex in range(len(super)):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(super+sub)+nindexc].isgreaterthan(permutation[len(super+sub)+nindexd])):
                                          rejected = 1
                           else:
                              permutation = permutation + super
                           if (sublocalone and subcommonone):
                              parity = parity * subpermutations[nsubpermutation][0]
                              for nindex in range(1,len(sub)+1):
                                 permutation.append(sub[subpermutations[nsubpermutation][nindex]-1])
                              if (len(sublocalone) > 1):
                                 for nindexa in range(len(sublocalone)):
                                    for nindexb in range(len(sublocalone)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = sublocalone[nindexa]
                                       indexb = sublocalone[nindexb]
                                       for nindex in range(len(permutation)/2):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(permutation)/2+nindexc].isgreaterthan(permutation[len(permutation)/2+nindexd])):
                                          rejected = 1
                              if (len(subcommonone) > 1):
                                 for nindexa in range(len(subcommonone)):
                                    for nindexb in range(len(subcommonone)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = subcommonone[nindexa]
                                       indexb = subcommonone[nindexb]
                                       for nindex in range(len(permutation)/2):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(permutation)/2+nindexc].isgreaterthan(permutation[len(permutation)/2+nindexd])):
                                          rejected = 1
                           else:
                              permutation = permutation + sub
                           for nindexa in range(len(permutation)/2,len(permutation)/2+len(permutation)/4):
                              for nindexb in range(len(permutation)/2,len(permutation)/2+len(permutation)/4):
                                 if (nindexa >= nindexb):
                                    continue
                                 indexa = permutation[nindexa]
                                 indexb = permutation[nindexb]
                                 if ((indexa.type == "particle") and (indexb.type == "hole")):
                                    rejected = 1
                           for nindexa in range(len(permutation)/2+len(permutation)/4,len(permutation)):
                              for nindexb in range(len(permutation)/2+len(permutation)/4,len(permutation)):
                                 if (nindexa >= nindexb):
                                    continue
                                 indexa = permutation[nindexa]
                                 indexb = permutation[nindexb]
                                 if ((indexa.type == "particle") and (indexb.type == "hole")):
                                    rejected = 1
                           if (not rejected):
                              if (parity == 1):
                                 sign = " + "
                              else:
                                 sign = " - "
                              newdbl = child.contraction.tensors[1].fortran90(permutation,0,"e")
                              newline = string.join([newdbl,"=",sign,child.contraction.tensors[1].fortran90()],"")
                              newcode.statements.insert(newcode.pointer,newline)
                              newcode.pointer = newcode.pointer + 1
                     newcode.pointer = len(newcode.statements)
               else:
                  if ((superglobalone and superlocalone) or (superglobalone and supercommonone) or (superlocalone and supercommonone) \
                   or (subglobalone and sublocalone) or (subglobalone and subcommonone) or (sublocalone and subcommonone)):
                     expanded[1] = 1
                     super = sortindexes(superglobalone + superlocalone + supercommonone)
                     sub = sortindexes(subglobalone + sublocalone + subcommonone)
                     for index in superglobalone:
                        newcode.insertdoloop(index)
                     for index in superlocalone:
                        newcode.insertdoloop(index)
                     for index in supercommonone:
                        newcode.insertdoloop(index)
                     if (len(super) > 1):
                        newcode.insertif(super,1)
                     for index in subglobalone:
                        newcode.insertdoloop(index)
                     for index in sublocalone:
                        newcode.insertdoloop(index)
                     for index in subcommonone:
                        newcode.insertdoloop(index)
                     if (len(sub) > 1):
                        newcode.insertif(sub,1)
                     if ((superglobalone and superlocalone) or (superglobalone and supercommonone) or (superlocalone and supercommonone)):
                        nsuperpermutations = factorial(len(super))
                        superpermutations = permutationwithparity(len(super))
                     else:
                        nsuperpermutations = 1
                     if ((subglobalone and sublocalone) or (subglobalone and subcommonone) or (sublocalone and subcommonone)):
                        nsubpermutations = factorial(len(sub))
                        subpermutations = permutationwithparity(len(sub))
                     else:
                        nsubpermutations = 1
                     for nsuperpermutation in range(nsuperpermutations):
                        for nsubpermutation in range(nsubpermutations):
                           permutation = super + sub
                           parity = 1
                           rejected = 0
                           if ((superglobalone and superlocalone) or \
                               (superglobalone and supercommonone) or \
                               (superlocalone and supercommonone)):
                              parity = parity * superpermutations[nsuperpermutation][0]
                              for nindex in range(1,len(super)+1):
                                 permutation.append(super[superpermutations[nsuperpermutation][nindex]-1])
                              if (len(superglobalone) > 1):
                                 for nindexa in range(len(superglobalone)):
                                    for nindexb in range(len(superglobalone)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = superglobalone[nindexa]
                                       indexb = superglobalone[nindexb]
                                       for nindex in range(len(super)):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(super+sub)+nindexc].isgreaterthan(permutation[len(super+sub)+nindexd])):
                                          rejected = 1
                              if (len(superlocalone) > 1):
                                 for nindexa in range(len(superlocalone)):
                                    for nindexb in range(len(superlocalone)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = superlocalone[nindexa]
                                       indexb = superlocalone[nindexb]
                                       for nindex in range(len(super)):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(super+sub)+nindexc].isgreaterthan(permutation[len(super+sub)+nindexd])):
                                          rejected = 1
                              if (len(supercommonone) > 1):
                                 for nindexa in range(len(supercommonone)):
                                    for nindexb in range(len(supercommonone)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = supercommonone[nindexa]
                                       indexb = supercommonone[nindexb]
                                       for nindex in range(len(super)):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(super+sub)+nindexc].isgreaterthan(permutation[len(super+sub)+nindexd])):
                                          rejected = 1
                           else:
                              permutation = permutation + super
                           if ((subglobalone and sublocalone) or \
                               (subglobalone and subcommonone) or \
                               (sublocalone and subcommonone)):
                              parity = parity * subpermutations[nsubpermutation][0]
                              for nindex in range(1,len(sub)+1):
                                 permutation.append(sub[subpermutations[nsubpermutation][nindex]-1])
                              if (len(subglobalone) > 1):
                                 for nindexa in range(len(subglobalone)):
                                    for nindexb in range(len(subglobalone)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = subglobalone[nindexa]
                                       indexb = subglobalone[nindexb]
                                       for nindex in range(len(permutation)/2):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(permutation)/2+nindexc].isgreaterthan(permutation[len(permutation)/2+nindexd])):
                                          rejected = 1
                              if (len(sublocalone) > 1):
                                 for nindexa in range(len(sublocalone)):
                                    for nindexb in range(len(sublocalone)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = sublocalone[nindexa]
                                       indexb = sublocalone[nindexb]
                                       for nindex in range(len(permutation)/2):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(permutation)/2+nindexc].isgreaterthan(permutation[len(permutation)/2+nindexd])):
                                          rejected = 1
                              if (len(subcommonone) > 1):
                                 for nindexa in range(len(subcommonone)):
                                    for nindexb in range(len(subcommonone)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = subcommonone[nindexa]
                                       indexb = subcommonone[nindexb]
                                       for nindex in range(len(permutation)/2):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(permutation)/2+nindexc].isgreaterthan(permutation[len(permutation)/2+nindexd])):
                                          rejected = 1
                           else:
                              permutation = permutation + sub
                           for nindexa in range(len(permutation)/2,len(permutation)/2+len(permutation)/4):
                              for nindexb in range(len(permutation)/2,len(permutation)/2+len(permutation)/4):
                                 if (nindexa >= nindexb):
                                    continue
                                 indexa = permutation[nindexa]
                                 indexb = permutation[nindexb]
                                 if ((indexa.type == "particle") and (indexb.type == "hole")):
                                    rejected = 1
                           for nindexa in range(len(permutation)/2+len(permutation)/4,len(permutation)):
                              for nindexb in range(len(permutation)/2+len(permutation)/4,len(permutation)):
                                 if (nindexa >= nindexb):
                                    continue
                                 indexa = permutation[nindexa]
                                 indexb = permutation[nindexb]
                                 if ((indexa.type == "particle") and (indexb.type == "hole")):
                                    rejected = 1
                           if (not rejected):
                              if (parity == 1):
                                 sign = " + "
                              else:
                                 sign = " - "
                              newdbl = child.contraction.tensors[1].fortran90(permutation,0,"e")
                              newline = string.join([newdbl,"=",sign,child.contraction.tensors[1].fortran90()],"")
                              newcode.statements.insert(newcode.pointer,newline)
                              newcode.pointer = newcode.pointer + 1
                     newcode.pointer = len(newcode.statements)

            # expand index ranges of tensor 2
            if ((mode == "permutation") and (len(child.contraction.tensors) > 2)):
               if (child.contraction.tensors[2].type == "i"):
                  if ((superlocaltwo and supercommontwo) or (sublocaltwo and subcommontwo)):
                     expanded[2] = 1
                     super = sortindexes(superlocaltwo + supercommontwo)
                     sub = sortindexes(sublocaltwo + subcommontwo)
                     for index in superglobaltwo:
                        newcode.insertdoloop(index)
                     if (len(superglobaltwo) > 1):
                        newcode.insertif(superglobaltwo,1)
                     for index in super:
                        newcode.insertdoloop(index)
                     if (len(super) > 1):
                        newcode.insertif(super,1)
                     for index in subglobaltwo:
                        newcode.insertdoloop(index)
                     if (len(subglobaltwo) > 1):
                        newcode.insertif(subglobaltwo,1)
                     for index in sub:
                        newcode.insertdoloop(index)
                     if (len(sub) > 1):
                        newcode.insertif(sub,1)
                     if (superlocaltwo and supercommontwo):
                        nsuperpermutations = factorial(len(super))
                        superpermutations = permutationwithparity(len(super))
                     else:
                        nsuperpermutations = 1
                     if (sublocaltwo and subcommontwo):
                        nsubpermutations = factorial(len(sub))
                        subpermutations = permutationwithparity(len(sub))
                     else:
                        nsubpermutations = 1
                     for nsuperpermutation in range(nsuperpermutations):
                        for nsubpermutation in range(nsubpermutations):
                           permutation = super + sub
                           parity = 1
                           rejected = 0
                           if (superlocaltwo and supercommontwo):
                              parity = parity * superpermutations[nsuperpermutation][0]
                              for nindex in range(1,len(super)+1):
                                 permutation.append(super[superpermutations[nsuperpermutation][nindex]-1])
                              if (len(superlocaltwo) > 1):
                                 for nindexa in range(len(superlocaltwo)):
                                    for nindexb in range(len(superlocaltwo)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = superlocaltwo[nindexa]
                                       indexb = superlocaltwo[nindexb]
                                       for nindex in range(len(super)):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(super+sub)+nindexc].isgreaterthan(permutation[len(super+sub)+nindexd])):
                                          rejected = 1
                              if (len(supercommontwo) > 1):
                                 for nindexa in range(len(supercommontwo)):
                                    for nindexb in range(len(supercommontwo)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = supercommontwo[nindexa]
                                       indexb = supercommontwo[nindexb]
                                       for nindex in range(len(super)):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(super+sub)+nindexc].isgreaterthan(permutation[len(super+sub)+nindexd])):
                                          rejected = 1
                           else:
                              permutation = permutation + super
                           if (sublocaltwo and subcommontwo):
                              parity = parity * subpermutations[nsubpermutation][0]
                              for nindex in range(1,len(sub)+1):
                                 permutation.append(sub[subpermutations[nsubpermutation][nindex]-1])
                              if (len(sublocaltwo) > 1):
                                 for nindexa in range(len(sublocaltwo)):
                                    for nindexb in range(len(sublocaltwo)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = sublocaltwo[nindexa]
                                       indexb = sublocaltwo[nindexb]
                                       for nindex in range(len(permutation)/2):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(permutation)/2+nindexc].isgreaterthan(permutation[len(permutation)/2+nindexd])):
                                          rejected = 1
                              if (len(subcommontwo) > 1):
                                 for nindexa in range(len(subcommontwo)):
                                    for nindexb in range(len(subcommontwo)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = subcommontwo[nindexa]
                                       indexb = subcommontwo[nindexb]
                                       for nindex in range(len(permutation)/2):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(permutation)/2+nindexc].isgreaterthan(permutation[len(permutation)/2+nindexd])):
                                          rejected = 1
                           else:
                              permutation = permutation + sub
                           for nindexa in range(len(permutation)/2,len(permutation)/2+len(permutation)/4):
                              for nindexb in range(len(permutation)/2,len(permutation)/2+len(permutation)/4):
                                 if (nindexa >= nindexb):
                                    continue
                                 indexa = permutation[nindexa]
                                 indexb = permutation[nindexb]
                                 if ((indexa.type == "particle") and (indexb.type == "hole")):
                                    rejected = 1
                           for nindexa in range(len(permutation)/2+len(permutation)/4,len(permutation)):
                              for nindexb in range(len(permutation)/2+len(permutation)/4,len(permutation)):
                                 if (nindexa >= nindexb):
                                    continue
                                 indexa = permutation[nindexa]
                                 indexb = permutation[nindexb]
                                 if ((indexa.type == "particle") and (indexb.type == "hole")):
                                    rejected = 1
                           if (not rejected):
                              if (parity == 1):
                                 sign = " + "
                              else:
                                 sign = " - "
                              newdbl = child.contraction.tensors[2].fortran90(permutation,0,"e")
                              newline = string.join([newdbl,"=",sign,child.contraction.tensors[2].fortran90()],"")
                              newcode.statements.insert(newcode.pointer,newline)
                              newcode.pointer = newcode.pointer + 1
                     newcode.pointer = len(newcode.statements)
               else:
                  if ((superglobaltwo and superlocaltwo) or (superglobaltwo and supercommontwo) or (superlocaltwo and supercommontwo) \
                   or (subglobaltwo and sublocaltwo) or (subglobaltwo and subcommontwo) or (sublocaltwo and subcommontwo)):
                     expanded[2] = 1
                     super = sortindexes(superglobaltwo + superlocaltwo + supercommontwo)
                     sub = sortindexes(subglobaltwo + sublocaltwo + subcommontwo)
                     for index in superglobaltwo:
                        newcode.insertdoloop(index)
                     for index in superlocaltwo:
                        newcode.insertdoloop(index)
                     for index in supercommontwo:
                        newcode.insertdoloop(index)
                     if (len(super) > 1):
                        newcode.insertif(super,1)
                     for index in subglobaltwo:
                        newcode.insertdoloop(index)
                     for index in sublocaltwo:
                        newcode.insertdoloop(index)
                     for index in subcommontwo:
                        newcode.insertdoloop(index)
                     if (len(sub) > 1):
                        newcode.insertif(sub,1)
                     if ((superglobaltwo and superlocaltwo) or (superglobaltwo and supercommontwo) or (superlocaltwo and supercommontwo)):
                        nsuperpermutations = factorial(len(super))
                        superpermutations = permutationwithparity(len(super))
                     else:
                        nsuperpermutations = 1
                     if ((subglobaltwo and sublocaltwo) or (subglobaltwo and subcommontwo) or (sublocaltwo and subcommontwo)):
                        nsubpermutations = factorial(len(sub))
                        subpermutations = permutationwithparity(len(sub))
                     else:
                        nsubpermutations = 1
                     for nsuperpermutation in range(nsuperpermutations):
                        for nsubpermutation in range(nsubpermutations):
                           permutation = super + sub
                           parity = 1
                           rejected = 0
                           if ((superglobaltwo and superlocaltwo) or \
                               (superglobaltwo and supercommontwo) or \
                               (superlocaltwo and supercommontwo)):
                              parity = parity * superpermutations[nsuperpermutation][0]
                              for nindex in range(1,len(super)+1):
                                 permutation.append(super[superpermutations[nsuperpermutation][nindex]-1])
                              if (len(superglobaltwo) > 1):
                                 for nindexa in range(len(superglobaltwo)):
                                    for nindexb in range(len(superglobaltwo)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = superglobaltwo[nindexa]
                                       indexb = superglobaltwo[nindexb]
                                       for nindex in range(len(super)):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(super+sub)+nindexc].isgreaterthan(permutation[len(super+sub)+nindexd])):
                                          rejected = 1
                              if (len(superlocaltwo) > 1):
                                 for nindexa in range(len(superlocaltwo)):
                                    for nindexb in range(len(superlocaltwo)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = superlocaltwo[nindexa]
                                       indexb = superlocaltwo[nindexb]
                                       for nindex in range(len(super)):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(super+sub)+nindexc].isgreaterthan(permutation[len(super+sub)+nindexd])):
                                          rejected = 1
                              if (len(supercommontwo) > 1):
                                 for nindexa in range(len(supercommontwo)):
                                    for nindexb in range(len(supercommontwo)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = supercommontwo[nindexa]
                                       indexb = supercommontwo[nindexb]
                                       for nindex in range(len(super)):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(super+sub)+nindexc].isgreaterthan(permutation[len(super+sub)+nindexd])):
                                          rejected = 1
                           else:
                              permutation = permutation + super
                           if ((subglobaltwo and sublocaltwo) or \
                               (subglobaltwo and subcommontwo) or \
                               (sublocaltwo and subcommontwo)):
                              parity = parity * subpermutations[nsubpermutation][0]
                              for nindex in range(1,len(sub)+1):
                                 permutation.append(sub[subpermutations[nsubpermutation][nindex]-1])
                              if (len(subglobaltwo) > 1):
                                 for nindexa in range(len(subglobaltwo)):
                                    for nindexb in range(len(subglobaltwo)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = subglobaltwo[nindexa]
                                       indexb = subglobaltwo[nindexb]
                                       for nindex in range(len(permutation)/2):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(permutation)/2+nindexc].isgreaterthan(permutation[len(permutation)/2+nindexd])):
                                          rejected = 1
                              if (len(sublocaltwo) > 1):
                                 for nindexa in range(len(sublocaltwo)):
                                    for nindexb in range(len(sublocaltwo)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = sublocaltwo[nindexa]
                                       indexb = sublocaltwo[nindexb]
                                       for nindex in range(len(permutation)/2):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(permutation)/2+nindexc].isgreaterthan(permutation[len(permutation)/2+nindexd])):
                                          rejected = 1
                              if (len(subcommontwo) > 1):
                                 for nindexa in range(len(subcommontwo)):
                                    for nindexb in range(len(subcommontwo)):
                                       if (nindexa >= nindexb):
                                          continue
                                       indexa = subcommontwo[nindexa]
                                       indexb = subcommontwo[nindexb]
                                       for nindex in range(len(permutation)/2):
                                          if (permutation[nindex].isidenticalto(indexa)):
                                             nindexc = nindex
                                          elif (permutation[nindex].isidenticalto(indexb)):
                                             nindexd = nindex
                                       if (permutation[len(permutation)/2+nindexc].isgreaterthan(permutation[len(permutation)/2+nindexd])):
                                          rejected = 1
                           else:
                              permutation = permutation + sub
                           for nindexa in range(len(permutation)/2,len(permutation)/2+len(permutation)/4):
                              for nindexb in range(len(permutation)/2,len(permutation)/2+len(permutation)/4):
                                 if (nindexa >= nindexb):
                                    continue
                                 indexa = permutation[nindexa]
                                 indexb = permutation[nindexb]
                                 if ((indexa.type == "particle") and (indexb.type == "hole")):
                                    rejected = 1
                           for nindexa in range(len(permutation)/2+len(permutation)/4,len(permutation)):
                              for nindexb in range(len(permutation)/2+len(permutation)/4,len(permutation)):
                                 if (nindexa >= nindexb):
                                    continue
                                 indexa = permutation[nindexa]
                                 indexb = permutation[nindexb]
                                 if ((indexa.type == "particle") and (indexb.type == "hole")):
                                    rejected = 1
                           if (not rejected):
                              if (parity == 1):
                                 sign = " + "
                              else:
                                 sign = " - "
                              newdbl = child.contraction.tensors[2].fortran90(permutation,0,"e")
                              newline = string.join([newdbl,"=",sign,child.contraction.tensors[2].fortran90()],"")
                              newcode.statements.insert(newcode.pointer,newline)
                              newcode.pointer = newcode.pointer + 1
                     newcode.pointer = len(newcode.statements)
                  
            # generate loops over target indexes
            if (mode == "nopermutation"):
               for index in child.contraction.tensors[0].indexes:
                  newcode.insertdoloop(index)
               newline = "TMP=0.0d0"
               newcode.statements.insert(newcode.pointer,newline)
               newcode.pointer = newcode.pointer + 1
               pointersave = newcode.pointer
               for npermutation in range(len(child.contraction.factor.permutations)):
                  permutation = child.contraction.factor.permutations[npermutation]
                  newdbl = child.contraction.tensors[0].fortran90(permutation,1)
                  newline = string.join([newdbl,"=",newdbl,"+",\
                     "(",repr(child.contraction.factor.coefficients[npermutation]),"d0)*TMP"],"")
                  newcode.statements.insert(newcode.pointer,newline)
                  newcode.pointer = newcode.pointer + 1
               newcode.pointer = pointersave
            elif (mode == "permutation"):
               for index in superglobalzero:
                  newcode.insertdoloop(index)
               if (len(superglobalzero) > 1):
                  newcode.insertif(superglobalzero,1)
               for index in superlocalzero:
                  newcode.insertdoloop(index)
               if (len(superlocalzero) > 1):
                  newcode.insertif(superlocalzero,1)
               for index in subglobalzero:
                  newcode.insertdoloop(index)
               if (len(subglobalzero) > 1):
                  newcode.insertif(subglobalzero,1)
               for index in sublocalzero:
                  newcode.insertdoloop(index)
               if (len(sublocalzero) > 1):
                  newcode.insertif(sublocalzero,1)
               if ((zeroscratch) and (len(child.contraction.tensors) > 2)):
                  newdbl = child.contraction.tensors[0].fortran90()
                  newline = string.join([newdbl,"=0.0d0"],"")
                  newcode.statements.insert(newcode.pointer,newline)
                  newcode.pointer = newcode.pointer + 1
                  zeroscratch = 0

            # generate loops over common indexes
            if (mode == "nopermutation"):
               if (child.contraction.summation):
                  for index in child.contraction.summation.indexes:
                     newcode.insertdoloop(index)
               newline = "TMP=TMP+"
               for ntensor in range(len(child.contraction.tensors)):
                  if (ntensor == 1):
                     newdbl = child.contraction.tensors[ntensor].fortran90()
                     newline = string.join([newline,newdbl],"")
                  elif (ntensor > 1):
                     newdbl = child.contraction.tensors[ntensor].fortran90()
                     newline = string.join([newline,"*",newdbl],"")
               newcode.statements.insert(newcode.pointer,newline)
               newcode.pointer = newcode.pointer + 1
               newcode.pointer = len(newcode.statements)
            elif (mode == "permutation"):
               factor = 1
               for index in supercommon:
                  newcode.insertdoloop(index)
               if (len(supercommon) > 1):
                  newcode.insertif(supercommon,1)
                  factor = factor * factorial(len(supercommon))
               for index in subcommon:
                  newcode.insertdoloop(index)
               if (len(subcommon) > 1):
                  newcode.insertif(subcommon,1)
                  factor = factor * factorial(len(subcommon))
               newdbl = child.contraction.tensors[0].fortran90()
               if ((zeroscratch) and (len(child.contraction.tensors) == 2)):
                  newline = string.join([newdbl,"="],"")
                  zeroscratch = 0
               else:
                  newline = string.join([newdbl,"=",newdbl,"+"],"")
               for npermutation in range(len(child.contraction.factor.permutations)):
                  permutation = child.contraction.factor.permutations[npermutation]
                  if (npermutation > 0):
                     newline = string.join([newline,"+"],"")
                  for ntensor in range(len(child.contraction.tensors)):
                     newfactor = float(factor) * child.contraction.factor.coefficients[npermutation]
                     if (expanded[ntensor]):
                        suffix = "e"
                     else:
                        suffix = ""
                     if (ntensor == 1):
                        newdbl = child.contraction.tensors[ntensor].fortran90(permutation,0,suffix)
                        newline = string.join([newline,"(",repr(newfactor),"d0)*",newdbl],"")
                     elif (ntensor > 1):
                        newdbl = child.contraction.tensors[ntensor].fortran90(permutation,0,suffix)
                        newline = string.join([newline,"*",newdbl],"")
               newcode.statements.insert(newcode.pointer,newline)
               newcode.pointer = newcode.pointer + 1
               newcode.pointer = len(newcode.statements)

      return newcode

class Code:
 
   def __init__(self,language,name):
      """Creates an empty code of program"""
      self.language = language
      self.name = name
      self.statements = []
      self.pointer = 0
      self.headers = []
      self.arguments = []
      self.integers = []
      self.integerarrays = []
      self.doubles = []
      self.doublearrays = []
      self.logicals = []
      self.logicalarrays = []
      self.characters = []
      self.externals = []

      # Comment lines
      if (self.language == "Fortran77"):
         self.comment = "C     "
         self.indent  = "      "
         self.nlang = 0
      elif (self.language == "Fortran90"):
         self.comment = "! "
         self.indent  = ""
         self.nlang = 1
      elif (self.language == "Python"):
         self.comment = "# "
         self.indent  = ""
         self.nlang = 2
      else:
         return "Unknown language"

      # Standard headers
      newline = "!$Id: tce.py,v 1.3 2002-10-23 01:38:52 sohirata Exp $"
      self.headers.append(newline)
      newline = "!This is a " + self.language + " program generated by Tensor Contraction Engine v.1.0"
      self.headers.append(newline)
      newline = "!Copyright (c) Battelle & Pacific Northwest National Laboratory (2002)"
      self.headers.append(newline)

   def __str__(self):
      """Prints code"""
      print ""
      for line in self.wrap():
         print line
      return ""

   def isnested(self):
      """Returns true if self.statements contains a nested code object"""
      for member in self.statements:
         if (isinstance(member,Code)):
            return 1
      return 0

   def expand(self):
      """Expands a code object with a nested statement list into a non-nested code"""
      result = Code(self.language,self.name)
      result.pointer = self.pointer
      for n in self.headers:
         result.add("headers",n)
      for n in self.arguments:
         result.add("arguments",n)
      for n in self.integers:
         result.add("integers",n)
      for n in self.integerarrays:
         result.add("integerarrays",n)
      for n in self.doubles:
         result.add("doubles",n)
      for n in self.doublearrays:
         result.add("doublearrays",n)
      for n in self.logicals:
         result.add("logicals",n)
      for n in self.logicalarrays:
         result.add("logicalarrays",n)
      for n in self.characters:
         result.add("characters",n)
      for n in self.externals:
         result.add("externals",n)
      for member in self.statements:
         if (isinstance(member,Code)):
            result.join(member.expand())
         else:
            result.statements.append(member)
      return result

   def setamark(self,number):
      """Inserts a special symbol with an identifier number"""
      self.deleteamark(number)
      statement = self.statements[self.pointer]
      statement = "#marker"+repr(number)+"#"+statement
      self.statements[self.pointer]=statement

   def getamark(self,number):
      """Returns the position of an input marker"""
      for nstatement in range(len(self.statements)):
         statement = self.statements[nstatement]
         if (statement[0:7] == "#marker"):
            if (number == int(string.split(statement[7:],"#")[0])):
               position = string.index(statement[7:],"#")
               self.statements[nstatement] = statement[position+8:]
               return nstatement

      raise ValueError, "Maker not found"

   def deleteamark(self,number):
      """Delete a marker"""
      for nstatement in range(len(self.statements)):
         statement = self.statements[nstatement]
         if (statement[0:7] == "#marker"):
            if (number == int(string.split(statement[7:],"#")[0])):
               position = string.index(statement[7:],"#")
               self.statements[nstatement] = statement[position+8:]

   def deleteallmarks(self):
      """Deletes all existing marks"""
      for nstatement in range(len(self.statements)):
         statement = self.statements[nstatement]
         if (statement[0:7] == "#marker"):
            position = string.index(statement[7:],"#")
            self.statements[nstatement] = statement[position+8:]

   def show(self): 
      """Returns an output of the contents"""

      self.deleteallmarks()

      if (self.isnested()):
         return "This code object is nested; first use expand()"

      show = []

      if (self.language == "Fortran77"):

         # add the headers and declarations
         pointer = 0
         subroutine = string.join([self.indent,"SUBROUTINE ",self.name],"")
         if (self.arguments):
            subroutine = string.join([subroutine,"("],"")
            for n in range(len(self.arguments)):
               argument = self.arguments[n]
               if (n != 0):
                  argument = string.join([",",argument],"")
               subroutine = string.join([subroutine,argument],"")
            subroutine = string.join([subroutine,")"],"")
         show.insert(pointer,subroutine)
         pointer = pointer + 1
         for n in self.headers:
            if (n[0] == "#"):
               show.insert(pointer,n)
            elif (n[0] == "!"):
               show.insert(pointer,string.join([self.comment,n[1:]],""))
            else:
               show.insert(pointer,string.join([self.indent,n],""))
            pointer = pointer + 1
         for n in self.integers:
            show.insert(pointer,string.join([self.indent,"INTEGER ",n],""))
            pointer = pointer + 1
         for n in self.integerarrays:
            show.insert(pointer,string.join([self.indent,"INTEGER ",n,"(*)"],""))
            pointer = pointer + 1
         for n in self.doubles:
            show.insert(pointer,string.join([self.indent,"DOUBLE PRECISION ",n],""))
            pointer = pointer + 1
         for n in self.doublearrays:
            show.insert(pointer,string.join([self.indent,"DOUBLE PRECISION ",n,"(*)"],""))
            pointer = pointer + 1
         for n in self.logicals:
            show.insert(pointer,string.join([self.indent,"LOGICAL ",n],""))
            pointer = pointer + 1
         for n in self.logicalarrays:
            show.insert(pointer,string.join([self.indent,"LOGICAL ",n,"(*)"],""))
            pointer = pointer + 1
         for n in self.characters:
            if (n in self.arguments):
               show.insert(pointer,string.join([self.indent,"CHARACTER*(*) ",n],""))
               pointer = pointer + 1
            else:
               show.insert(pointer,string.join([self.indent,"CHARACTER*20 ",n],""))
               pointer = pointer + 1
         for n in self.externals:
            show.insert(pointer,string.join([self.indent,"EXTERNAL ",n],""))
            pointer = pointer + 1

         # add the statements
         for n in self.statements:
            show.insert(pointer,string.join([self.indent,n],""))
            pointer = pointer + 1

      elif (self.language == "Fortran90"):

         # add the headers and declarations
         pointer = 0
         subroutine = string.join([self.indent,"SUBROUTINE ",self.name],"")
         if (self.arguments):
            subroutine = string.join([subroutine,"("],"")
            for n in range(len(self.arguments)):
               argument = self.arguments[n]
               if (n != 0):
                  argument = string.join([",",argument],"")
               subroutine = string.join([subroutine,argument],"")
            subroutine = string.join([subroutine,")"],"")
         show.insert(pointer,subroutine)
         pointer = pointer + 1
         for n in self.headers:
            if ((n[0] == "#") or (n[0] == "!")):
               show.insert(pointer,n)
            else:
               show.insert(pointer,string.join([self.indent,n],""))
            pointer = pointer + 1
         for n in self.integers:
            show.insert(pointer,string.join([self.indent,"INTEGER :: ",n],""))
            pointer = pointer + 1
         for n in self.integerarrays:
            show.insert(pointer,string.join([self.indent,"INTEGER :: ",n,"(*)"],""))
            pointer = pointer + 1
         for n in self.doubles:
            show.insert(pointer,string.join([self.indent,"DOUBLE PRECISION :: ",n],""))
            pointer = pointer + 1
         for n in self.doublearrays:
            show.insert(pointer,string.join([self.indent,"DOUBLE PRECISION :: ",n,"(*)"],""))
            pointer = pointer + 1
         for n in self.logicals:
            show.insert(pointer,string.join([self.indent,"LOGICAL :: ",n],""))
            pointer = pointer + 1
         for n in self.logicalarrays:
            show.insert(pointer,string.join([self.indent,"LOGICAL :: ",n,"(*)"],""))
            pointer = pointer + 1
         for n in self.characters:
            show.insert(pointer,string.join([self.indent,"CHARACTER :: ",n,"*(*)"],""))
            pointer = pointer + 1
         for n in self.externals:
            show.insert(pointer,string.join([self.indent,"EXTERNAL :: ",n],""))
            pointer = pointer + 1

         # add the statements
         for n in self.statements:
            show.insert(pointer,string.join([self.indent,n],""))
            pointer = pointer + 1

      return show

   def wrap(self):
      """Wraps around long statements; calls show()"""

      show = self.show()
      
      if (self.language == "Fortran77"):
         show72 = []
         for n in show:
            if ((n[0] == "C") or (n[0] == "c")):
               done = 1
            else:
               done = 0
            while (not done):
               if (len(n) > 72):
                  show72.append(n[0:72])
                  n = string.join(["     &",n[72:]],"")
               else:
                  done = 1
            show72.append(n)
         return show72
      elif (self.language == "Fortran90"):
         show132 = []
         for n in show:
            if (n[0] == "!"):
               done = 1
            else:
               done = 0
            while (not done):
               if (len(n) > 132):
                  show132.append(string.join([n[0:131],"&"],""))
                  n = n[131:]
               else:
                  done = 1
            show132.append(n)
         return show132
      else:
         return show

   def join(self,another):
      """Join two code objects together"""
      if (self.language != another.language):
         return "Cannot join two codes"
      for n in another.headers:
         self.add("headers",n)
      for n in another.arguments:
         self.add("arguments",n)
      for n in another.integers:
         self.add("integers",n)
      for n in another.integerarrays:
         self.add("integerarrays",n)
      for n in another.doubles:
         self.add("doubles",n)
      for n in another.doublearrays:
         self.add("doublearrays",n)
      for n in another.logicals:
         self.add("logicals",n)
      for n in another.logicalarrays:
         self.add("logicalarrays",n)
      for n in another.characters:
         self.add("characters",n)
      for n in another.statements:
         self.statements.append(n)
      for n in another.externals:
         self.add("externals",n)
      return self

   def add(self,towhat,what):
      """Add a new integer/double/logical etc to an existing list; checks redundancy"""
      if (towhat == "integers"):
         redundant = 0
         for n in self.integers:
            if (n == what):
               redundant = 1
         if (not redundant):
            self.integers.append(what)
      elif (towhat == "integerarrays"):
         redundant = 0
         for n in self.integerarrays:
            if (n == what):
               redundant = 1
         if (not redundant):
            self.integerarrays.append(what)
      elif (towhat == "doubles"):
         redundant = 0
         for n in self.doubles:
            if (n == what):
               redundant = 1
         if (not redundant):
            self.doubles.append(what)
      elif (towhat == "doublearrays"):
         redundant = 0
         for n in self.doublearrays:
            if (n == what):
               redundant = 1
         if (not redundant):
            self.doublearrays.append(what)
      elif (towhat == "logicals"):
         redundant = 0
         for n in self.logicals:
            if (n == what):
               redundant = 1
         if (not redundant):
            self.logicals.append(what)
      elif (towhat == "logicalarrays"):
         redundant = 0
         for n in self.logicalarrays:
            if (n == what):
               redundant = 1
         if (not redundant):
            self.logicalarrays.append(what)
      elif (towhat == "characters"):
         redundant = 0
         for n in self.characters:
            if (n == what):
               redundant = 1
         if (not redundant):
            self.characters.append(what)
      elif (towhat == "externals"):
         redundant = 0
         for n in self.externals:
            if (n == what):
               redundant = 1
         if (not redundant):
            self.externals.append(what)
      elif (towhat == "arguments"):
         redundant = 0
         for n in self.arguments:
            if (n == what):
               redundant = 1
         if (not redundant):
            self.arguments.append(what)
      elif (towhat == "headers"):
         redundant = 0
         for n in self.headers:
            if (n == what):
               redundant = 1
         if (not redundant):
            self.headers.append(what)
      else:
         raise ValueError, "Unknown variable type"

   def insertdoloop(self,index):
      """Inserts a DO-ENDDO pair into a code"""
      if (index.type == 'hole'):
         newint = index.show()
         self.add("integers",newint)
         newline = string.join([self.indent,"DO ",newint,"=1,nocc"],"")
         self.statements.insert(self.pointer,newline)
         self.pointer = self.pointer + 1
         newline = "END DO"
         self.statements.insert(self.pointer,newline)
      elif (index.type == 'particle'):
         newint = index.show()
         self.add("integers",newint)
         newline = string.join([self.indent,"DO ",newint,"=nocc+1,N"],"")
         self.statements.insert(self.pointer,newline)
         self.pointer = self.pointer + 1
         newline = "END DO"
         self.statements.insert(self.pointer,newline)
      elif (index.type == 'general'):
         newint = index.show()
         self.add("integers",newint)
         newline = string.join([self.indent,"DO ",newint,"=1,N"],"")
         self.statements.insert(self.pointer,newline)
         self.pointer = self.pointer + 1
         newline = "END DO"
         self.statements.insert(self.pointer,newline)

   def insertif(self,list,holeisalwayslessthanparticle=0):
      """Inserts an IF sentence for skipping permutation redundant block"""
      for nindex in range(len(list)-1):
         indexa = list[nindex]
         indexb = list[nindex+1]
         if (holeisalwayslessthanparticle):
            if ((indexa.type == "hole") and (indexb.type == "particle")):
               return
            elif ((indexa.type == "particle") and (indexb.type == "hole")):
               raise ValueError, "A particle, hole sequence in a tensor"
         newline = string.join(["IF (",indexa.show(),">=",indexb.show(),") CYCLE"],"")
         self.statements.insert(self.pointer,newline)
         self.pointer = self.pointer + 1

   def inserttileddoloops(self,list):
      """Inserts a nested restricted DO-ENDDO pair"""
      for nindex in range(len(list)):
         index = list[nindex]
         newint = string.join([index.show(),"b"],"")
         self.add("integers",newint)
         if (nindex == 0):
            if (index.type == 'hole'):
               newline = string.join(["DO ",newint," = 1,noab"],"")
            if (index.type == 'particle'):
               newline = string.join(["DO ",newint," = noab+1,noab+nvab"],"")
            self.statements.insert(self.pointer,newline)
            self.pointer = self.pointer + 1
            newline = "END DO"
            self.statements.insert(self.pointer,newline)
            previousint = newint
            previoustype = index.type
         else:
            if (index.type == 'hole'):
               if (previoustype == 'hole'):
                  newline = string.join(["DO ",newint," = ",previousint,",noab"],"")
               else:
                  raise ValueError, "non-canonical expression found"
            if (index.type == 'particle'):
               if (previoustype == 'hole'):
                  newline = string.join(["DO ",newint," = noab+1,noab+nvab"],"")
               else:
                  newline = string.join(["DO ",newint," = ",previousint,",noab+nvab"],"")
            self.statements.insert(self.pointer,newline)
            self.pointer = self.pointer + 1
            newline = "END DO"
            self.statements.insert(self.pointer,newline)
            previousint = newint
            previoustype = index.type
 
   def inserttiledifsymmetry(self,super,sub):
      """Inserts an IF-ENDIF pair for screening spin/spatial symmetry"""

      if ((not super) and (not sub)):
         return
      if ((super and (not sub)) or ((not super) and sub)):
         raise ValueError, "asymmetric IF encountered"

      # spin symmetry
      newline = "IF ("
      conjugation = ""
      for index in super:
         newint = string.join([index.show(),"b"],"")
         newline = string.join([newline,conjugation,"int_mb(k_spin+",newint,"-1)"],"")
         conjugation = "+"
      conjugation = " .eq. "
      for index in sub:
         newint = string.join([index.show(),"b"],"")
         newline = string.join([newline,conjugation,"int_mb(k_spin+",newint,"-1)"],"")
         conjugation = "+"
      newline = string.join([newline,") THEN"],"")
      self.statements.insert(self.pointer,newline)
      self.pointer = self.pointer + 1
      newline = "END IF"
      self.statements.insert(self.pointer,newline)

      # spatial symmetry
      all = super + sub
      newline = "IF ("
      conjugation = ""
      for nindex in range(len(all)-1):
         index = all[nindex]
         newint = string.join([index.show(),"b"],"")
         newline = string.join([newline,conjugation,"ieor(int_mb(k_sym+",newint,"-1)"],"")
         conjugation = ","
      index = all[len(all)-1]
      newint = string.join([index.show(),"b"],"")
      newline = string.join([newline,",int_mb(k_sym+",newint,"-1)"],"")
      for nindex in range(len(all)-1):
         newline = string.join([newline,")"],"")
      newline = string.join([newline," .eq. 0) THEN"],"")
      self.statements.insert(self.pointer,newline)
      self.pointer = self.pointer + 1
      newline = "END IF"
      self.statements.insert(self.pointer,newline)

   def inserttiledifpermutation(self,list,holeisalwayslessthanparticle=0):
      """Inserts an IF sentence for skipping permutation redundant block"""
      for nindex in range(len(list)-1):
         indexa = list[nindex]
         indexb = list[nindex+1]
         if (holeisalwayslessthanparticle):
            if ((indexa.type == "hole") and (indexb.type == "particle")):
               return
            elif ((indexa.type == "particle") and (indexb.type == "hole")):
               raise ValueError, "A particle, hole sequence in a tensor"
         newline = string.join(["IF (",indexa.show(),"b .le. ",indexb.show(),"b) THEN"],"")
         self.statements.insert(self.pointer,newline)
         self.pointer = self.pointer + 1
         newline = "END IF"
         self.statements.insert(self.pointer,newline)

   def writetofile(self,filename):
      """Writes a list to a given file"""

      if (self.isnested()):
         return "This code object is nested; first use expand()"

      if (self.language == "Fortran77"):
         file = open(filename+".F","w")
      elif (self.language == "Fortran90"):
         file = open(filename+".f90","w")
      for n in self.wrap():
         file.write(n)
         file.write("\n")

   def sortarguments(self):
      """Sorts the list of arguments in an ascending order"""

      done = 0
      while (not done):
         done = 1
         for n in range(len(self.arguments)):
            for m in range(len(self.arguments)):
               if (n >= m):
                  continue
               if (self.arguments[n] > self.arguments[m]):
                  swap = self.arguments[n]
                  self.arguments[n] = self.arguments[m]
                  self.arguments[m] = swap
                  done = 0

   def reverse(self):
      """Reverse the execution seqeuence of the whole code"""

      newstatements = []
      for statement in self.statements:
         newstatements.insert(0,statement)
      self.statements = copy.deepcopy(newstatements)

class ListofCodes:
 
   def __init__(self):
      """Creates an empty code of program"""
      self.list = []

   def add(self,code):
      """Adds a code"""
      self.list.append(code)

   def join(self,another):
      """Joins two lists of codes"""
      for code in another.list:
         self.list.append(code)

   def show(self):
      """Calls wrap() of each Code object"""
      show = []
      for code in self.list:
         show = show + code.wrap()
      return show

   def __str__(self):
      """Prints code"""
      print ""
      for line in self.show():
         print line
      return ""

   def writetofile(self,filename):
      """Writes a list to a given file"""

      for code in self.list:
         if (code.isnested()):
            return "This code object is nested; first use expand()"

      if (self.list[0].language == "Fortran77"):
         file = open(filename+".F","w")
      elif (self.list[0].language == "Fortran90"):
         file = open(filename+".f90","w")
      for code in self.list:
         for n in code.wrap():
            file.write(n)
            file.write("\n")
