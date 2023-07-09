import matplotlib.image as img
from bitarray import bitarray
import math
from PIL import Image
import time

compressingPathOpen = "data/original/landscape.bmp"
compressingPathSave = "data/compressed/zipado.bin"
decompressingPathOpen = "data/compressed/zipado3EGG.bin"
decompressingPathSave = "data/decompressed/deszipado.bmp"
  
 
#DOES EVERYTHING 0/10/110/1110
def coder(path):
    data = importData(path)
    dicio = count(data[2:])  #exclude first 2 because those are the number of lines and columns
    dicio = sortDict(dicio)
    dicio = creatDict(dicio)
    codify(data,dicio)
    

#imports image data and returns a 1D list being the 1st element the number of lines and the second the number of pixels per line
def importData(path):                                         
    data=img.imread(path)
    dataF = [len(data) , len(data[0])] #save nº of lines and nº of columns thats important for decode
    #if image has RGB instead of simple gray scale, make it a simple grey scale by choosing the 1st one of each pixel
    if len(data.shape) == 3:
        for i in range(len(data)):
            for ii in range(len(data[i])):
                n = data[i][ii][0]
                dataF += [n] 
    #if not, simply make it a 1D array
    else:
        for i in range(len(data)):
            for ii in range(len(data[i])):
                n = data[i][ii]
                dataF += [n]
    return dataF

    
#Count the number of ocurrences in a list received and returns a dictionary being the keys what occurs and the values the number of times
def count(image):
    dicio = {}
    for i in image:
        if i in dicio.keys():
            n = dicio.get(i) + 1
            dicio.pop(i)
            dicio.update({i : n})
        else:
            dicio.update({i : 1})
    return dicio


#Sorts a dictionary received by decreasing order of it's values
def sortDict(dicio):
    dicioN = {}
    for i in range(len(dicio.keys())):
        v = 0
        k = 0
        for x,y in dicio.items():
            if y > v:
                v = y
                k = x
        dicio.pop(k)
        dicioN.update({k : v})
    #print(dicioN)
    return dicioN


#Receives a sorted Dictionary and returns a Dict with same keys but with binary values (1st: 0 // 2nd: 10 // 3rd: 110 .... )
def creatDict(dicio):
    dicioN = {}
    n = 0
    for key in dicio.keys():
        val = bitarray()
        for i in range(n):
            val.append(True)
        val.append(False)
        dicioN.update({key: val})
        n += 1
    #print(dicioN)
    return dicioN


#receives image data and binary dict and saves in binary file the compressed data
def codify(data,dicio):
    file = open(compressingPathSave,"wb")
    b = bitarray('')
    
    #ADD THE FIRST BYTES THAT ARE NOT COLORS BUT INSTEAD CODES IMPORTANT TO DECODE AFTER
    b.extend(intToBitArray(data[0], 16))        #convert nº of lines to binary and add to code to b
    b.extend(intToBitArray(data[1], 16))        #convert nº of pixels/line to binary and add to b
    
    #ADD THE COLORS BY DECREASING ORDER OF PROBABILITY (to be able to creat the dictionary in the decoder)
    b.extend(intToBitArray(len(dicio.keys())-1, 8)) #to save length of dictionary -1 to use 8 bits
    for i in dicio.keys():             
        b.extend(intToBitArray(i, 8))
    
    #ADD THE COLORS
    for i in data[2:]:
        b.extend(dicio.get(i))
    #print(b)
    b.tofile(file)
    file.close()
    

#receives an int string and returns a binary array
def intToBitArray(n , nBits):
    n = format(n, 'b').zfill(nBits)
    n = strToBitArray(n)
    return n


#receives a binary string and returns a binary array
def strToBitArray(string):
    b = bitarray('')
    for i in string:
        if i == '1':
            b.append(True)
        else:
            b.append(False)
    return b


#decodifies 0/10/110.... 
def decoder(path):
    file = open(path , 'rb')
    b = bitarray('')
    b.fromfile(file)
    data = []
    dataF = [[]]
    #Save importante info for decode
    nLines , b = bitArrayToInt(b[:16]) , b[16:]                #save nº of lines and delete those 2 bytes from b
    nPixelsLine , b = bitArrayToInt(b[:16]) , b[16:]           #save nº of pixels per lines and delete those 2 bytes from b
    dictLen , b = bitArrayToInt(b[:8])+1 , b[8:]          

    #creats lists with sorted colors by probability
    colOrder = []
    for i in range(dictLen):
        #print(i)
        color, b = bitArrayToInt(b[:8]) , b[8:]
        colOrder += [color]

    #decode itself
    #put all in a 1D array
    l = len(b)
    n = 0
    #counts nº of 1s and goes to list to put correct color on data
    for i in range(l):
        if b[i] == True:
            n += 1
        else:
            #print("TAMANHO = " , dictLen)
            #print("N = " , n)
            data += [colOrder[n]]
            n = 0
    
    #now convert to a 2D array
    for i in range(nLines):
        dataF += [[]]
        for ii in range(nPixelsLine):
            dataF[i] += [data[nPixelsLine * i + ii]]
    dataF = dataF[:nLines]
    
    #now put it all on a new image
    pic = Image.new('L' , (nPixelsLine , nLines)) #create new file
    pixels = pic.load()   
    for i in range(nLines):
        for ii in range(nPixelsLine):
            pixels[ii,i] = dataF[i][ii]
    pic.save(decompressingPathSave)   
    

#receives a bitarray and return the correspondent Int
def bitArrayToInt(b):
    n=0;
    for i in range(len(b)):
        if(b[len(b)-i-1]==True):
             n=n+math.pow(2,i)
    return int(n)
   
    
#codify by repetition
def codifyRepetition(data):
    file = open(compressingPathSave,"wb")              #creats new file
    b = bitarray('')                            #to save binary code
    repCode = unused(data[2:])                  #checks number to use as Code for repetition (without first 2 members that are nºLines and nºcolumns)   
    #print(repCode)       
    repCode = intToBitArray(repCode, 8)         #transform to binary array
    val = -1                                    #to save keys
    valB = bitarray('')                         #to save binary of val
    n = 0                                       #to save number of occurences of val
    nB = bitarray('')                           #to save binary of n
    data += [-1]                                #adds a -1 to data because in cycle last one is not written (and is -1 to guarantee its not equal to last one)
    nRepMax = countMaxRep(data)                 #finds the max number of consecutive color repeated
    nBitsRep = nBitsNec(nRepMax)                #fins the number of bits necessary for represent the number of repetitions
    
    #print(repCode , nBitsRep)
    #ADD THE FIRST BYTES THAT ARE NOT COLORS BUT INSTEAD CODES IMPORTANT TO DECODE AFTER
    b.extend(intToBitArray(data[0], 16))        #convert nº of lines to binary and add to code to b
    b.extend(intToBitArray(data[1], 16))        #convert nº of pixels/line to binary and add to b
    b.extend(repCode)                           #add repCode to b
    b.extend(intToBitArray(nBitsRep, 8))        #convert nº of bits necessary for nº of repeticions and add to b
    
     #ADD COLORS
    x = 0
    for i in data[2:]:   
        x += 1
        print(x)                       
        if i == val:                            #if color equals last one, add 1 to n
            n += 1
        else:                                   #if not
            if valB != repCode:                 #if valB different of repCode                    
                if n < 4:                           #and if n < 4 just write the color n times on b
                    for ii in range(n):
                        b.extend(valB) 
                else:                               #and if n > 4 
                    nB = intToBitArray(n , nBitsRep)           #pass n to binary Array
                    b.extend(repCode)               #write code for repetitions
                    b.extend(nB)                    #write number of times
                    b.extend(valB)                  #write color    
            else:                               #if equals repCode we have to write the repCode and the number of times (even if 1) and the color (=repCode)
                nB = intToBitArray(n, nBitsRep)           #pass n to binary Array
                b.extend(repCode)               #write code for repetitions
                b.extend(nB)                    #write number of times
                b.extend(valB)                  #write color    
            val = i                             #put new color in val
            valB = intToBitArray(val, 8)        #pass val to binary array
            n = 1                               #reset n to 1
    b.tofile(file)                              #save all                          
    file.close()     
   
    
#return the color unsued or the least used if all used
def unused(data):
    for i in range(256):
            if i not in data:
                return i
    dicio = count(data)
    dicio = sortDict(dicio)
    return list(dicio.keys())[len(list(dicio.keys()))-1]


#counts the max number of repetition of a color
def countMaxRep(data):
    nMax = 0
    nNow = 1
    val = -1
    for i in data:
        if i == val:
            nNow += 1
        else:
            if nNow > nMax:
                nMax = nNow
            nNow = 1
            val = i 
    return nMax


#receives an int and returns n of bits necessary to represent that int
def nBitsNec(n):
    nB = math.floor(math.log(n , 2)) + 1
    return nB
 
   
#decodify by repetition
def decodeRepetition(path):
    file = open(path , 'rb')
    b = bitarray('')
    b.fromfile(file)
    data = []
    dataF = [[]]
    
    #Save importante info for decode
    nLines , b = bitArrayToInt(b[:16]) , b[16:]                #save nº of lines and delete those 2 bytes from b
    nPixelsLine , b = bitArrayToInt(b[:16]) , b[16:]           #save nº of pixels per lines and delete those 2 bytes from b
    repCode , b = b[:8] , b[8:]                                #save repetition code and delete that byte from b
    nBitsRep , b = bitArrayToInt(b[:8]) , b[8:]                #save nº bits necessary for nº of repetitions and delete that byte from b
    
    #print(nLines , nPixelsLine , repCode , nBitsRep)
    #decode colors
    #first put all colors in 1D array 
    l = len(b)
    for i in range(l):
        if len(b) < 8:
            break
        else:
            if b[:8] == repCode:
                n , color , b = b[8: 8+nBitsRep] , b[8+nBitsRep:16+nBitsRep] , b[16+nBitsRep:] #save nº of repetitions and color and delete from b
                color = bitArrayToInt(color)
                n = bitArrayToInt(n)
                for j in range(n):              #adicionar a cor as vezes indicadas
                    data += [color] 
            else:
                color , b = bitArrayToInt(b[:8]) , b[8:] #color and delete from b
                data += [color]
            
    #print (data)
    #now convert to a 2D array
    for i in range(nLines):
        dataF += [[]]
        for ii in range(nPixelsLine):
            dataF[i] += [data[nPixelsLine * i + ii]]
    dataF = dataF[:nLines]

    #now put it all on a new image
    pic = Image.new('L' , (nPixelsLine , nLines)) #create new file
    pixels = pic.load()   
    for i in range(nLines):
        for ii in range(nPixelsLine):
            pixels[ii,i] = dataF[i][ii]
    pic.save(decompressingPathSave)
    


#codify by 0/10/110 and then by repetition (repCode ALWAYS ->  0000 0000 )
def codify2Levels(data):
    file = open(compressingPathSave,"wb")              #creats new file
    b = bitarray('')                            #to save binary code   
    val = -1                                    #to save keys
    valB = bitarray('')                         #to save binary of val
    n = 0                                       #to save number of occurences of val
    nB = bitarray('')                           #to save binary of n
    nRepMax = countMaxRep(data)                 #finds the max number of consecutive color repeated
    nBitsRep = nBitsNec(nRepMax)                #fins the number of bits necessary for represent the number of repetitions
    
    dicio = count(data[2:])
    dicio = sortDict(dicio)
    dicio = creatDict(dicio)
    data += [-1]                                #adds a -1 to data because in cycle last one is not written (and is -1 to guarantee its not equal to last one)
    
    #ADD THE FIRST BYTES THAT ARE NOT COLORS BUT INSTEAD CODES IMPORTANT TO DECODE AFTER
    b.extend(intToBitArray(data[0], 16))        #convert nº of lines to binary and add to code to b
    b.extend(intToBitArray(data[1], 16))        #convert nº of pixels/line to binary and add to b
    b.extend(intToBitArray(len(list(dicio.keys()))-1, 8)) #conver length of dicio to binary and add to b
    b.extend(intToBitArray(nBitsRep, 8))        #convert nº of bits necessary for nº of repeticions and add to b
    
    #ADD THE COLORS BY DECREASING ORDER OF PROBABILITY (to be able to creat the dictionary in the decoder)
    for i in dicio.keys():
        b.extend(intToBitArray(i, 8))
        
    #ADD COLORS
    for i in data[2:]:                          
        if i == val:                            #if color equals last one, add 1 to n
            n += 1
        else:                                   #if not
            if n >= 8 and val == list(dicio.keys())[0]:   
                nB = intToBitArray(n , nBitsRep)    #pass n to binary Array 
                b.extend(bitarray('00000000'))  #add repetition Code
                b.extend(nB)                    #add number of times of repetition
                b.append(False)                 #add color (this case is 0)
            elif n < 8 and val == list(dicio.keys())[0]:
                for ii in range(n):
                    b.append(False)             #add n times the color known by 0
            elif n >= 4:
                nB = intToBitArray(n , nBitsRep)    #pass n to binary Array 
                b.extend(bitarray('00000000'))  #add repetition Code
                b.extend(nB)                    #add number of times of repetition
                b.extend(valB)                  #add color
            else:
                for ii in range(n):
                    b.extend(valB)              #add n times the color
            val = i                             #put new color in val                
            valB = dicio.get(val)               #pass val to binary array
            n = 1                               #reset n to 1
    b.tofile(file)                              #save all
    file.close()
    
#decodify 2 levels
def decode2Levels(path):
    file = open(path , 'rb')
    b = bitarray('')
    b.fromfile(file)
    data = []
    dataF = [[]]
    
    #Save importante info for decode
    nLines , b = bitArrayToInt(b[:16]) , b[16:]                #save nº of lines and delete those 2 bytes from b
    nPixelsLine , b = bitArrayToInt(b[:16]) , b[16:]           #save nº of pixels per lines and delete those 2 bytes from b
    dictLen , b = bitArrayToInt(b[:8])+1 , b[8:]                                #save length od dictionary and delete that byte from b
    nBitsRep , b = bitArrayToInt(b[:8]) , b[8:]                #save nº bits necessary for nº of repetitions and delete that byte from b
    
    colOrder = []
    #creats lists with sorted colors by probability
    for i in range(dictLen):
        color, b = bitArrayToInt(b[:8]) , b[8:]
        colOrder += [color]
        #print("COLORS ADDED: " , y)
    
    #decode colors
    #first put all colors in 1D array 
    l = len(b)
    for i in range(l):
        if len(b) == 0:
            break
        else:
            if b[:8] == bitarray('00000000'):            #if equals to repetition Code
                n , b = bitArrayToInt(b[8: 8+nBitsRep]) ,  b[8+nBitsRep:] #save nº of repetitions and delete from b
                n1 = 0                                  #resets count of ones to 0
                for ii in range(l):                     #counts number of ones
                    if b[ii] == True:
                        n1 += 1
                    else:
                        break
                #print(n1)    
                color = colOrder[n1]                    #find color
                for iii in range(n):                    #write on data the color the number of times necessary
                    data += [color]
            else:
                n1 = 0                                   #resets counts of ones
                for ii in range(l):                     #counts number of ones
                    if b[ii] == True:
                        n1 += 1
                    else:
                        break
                #print(n1)
                color = colOrder[n1]                 #find color
                data += [color]                     #add to data
            b = b[n1+1:]                    #eliminates color code from b

            
    #print (data)
    #now convert to a 2D array
    for i in range(nLines):
        dataF += [[]]
        for ii in range(nPixelsLine):
            dataF[i] += [data[nPixelsLine * i + ii]]
    dataF = dataF[:nLines]

    #now put it all on a new image
    pic = Image.new('L' , (nPixelsLine , nLines)) #create new file
    pixels = pic.load()   
    for i in range(nLines):
        for ii in range(nPixelsLine):
            pixels[ii,i] = dataF[i][ii]
    pic.save(decompressingPathSave)


#codifies and then descodifies by the 1st method (0/10/110/1110....)
def type1(path):
    t = time.time()
    coder(path)
    print(time.time() - t , "segundos a codificar")
    t = time.time()
    decoder(decompressingPathOpen)
    print(time.time() - t , "segundos a descodificar")


#codifies and then descodifies by the 2st method (Repetition)
def type2(path):
    t = time.time()
    data = importData(path)
    codifyRepetition(data)
    print(time.time() - t , "segundos a codificar")
    t = time.time()
    decodeRepetition(decompressingPathOpen)
    print(time.time() - t , "segundos a descodificar")
      
    
#codifies and then descodifies by the 1st method (2 Layers)
def type3(path):
    t = time.time()
    data = importData(path)
    codify2Levels(data)   
    print(time.time() - t , "segundos a codificar")
    t = time.time()
    decode2Levels(decompressingPathOpen)
    print(time.time() - t , "segundos a descodificar")
    

#creat and save 4 images for testing
def creatImages():
    halfHalf()
    degrade()
    lines()
    chess()


#Creats a half black hlaf white(vertically) image and saves it        
def halfHalf():
    pic = Image.new('L' , (100 , 100)) #create new file
    pixels = pic.load()   
    for i in range(100):
        for ii in range(100):
            if ii < 50:
                pixels[ii,i] = 0
            else:
                pixels[ii,i] = 255
    pic.save("data/myImages/halfHalf.bmp")
    

#Creats a degrade(diagnoly) image and saves it       
def degrade():
    pic = Image.new('L' , (100 , 100)) #create new file
    pixels = pic.load()   
    for i in range(100):
        for ii in range(100):
            pixels[ii,i] = i + ii
    pic.save("data/myImages/degrade.bmp")
    
    
#Creats an image in wich each line as a different color and saves it
def lines():
    pic = Image.new('L' , (100 , 100)) #create new file
    pixels = pic.load()   
    for i in range(100):
        for ii in range(100):
            pixels[ii,i] = 2 * i
    pic.save("data/myImages/lines.bmp")


#Creats a chess image and saves it
def chess():
    pic = Image.new('L' , (100 , 100)) #create new file
    pixels = pic.load()   
    for i in range(100):
        for ii in range(100):
            if (i+ii)%2 == 0:
                pixels[ii,i] = 0
            else:
                pixels[ii,i] = 255
    pic.save("data/myImages/chess.bmp")
    

#type2(compressingPathOpen)
   
type3(compressingPathOpen)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    