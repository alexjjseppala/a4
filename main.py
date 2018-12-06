# Image compression
#
# You'll need Python 2.7 and must install these packages:
#
#   scipy, numpy
#
# You can run this *only* on PNM images, which the netpbm library is used for.
#
# You can also display a PNM image using the netpbm library as, for example:
#
#   python netpbm.py images/cortex.pnm


import sys, os, math, time, netpbm
import numpy as np


# Text at the beginning of the compressed file, to identify it


headerText = 'my compressed image - v1.0'



# Compress an image


def compress( inputFile, outputFile ):

  # Read the input file into a numpy array of 8-bit values
  #
  # The img.shape is a 3-type with rows,columns,channels, where
  # channels is the number of component in each pixel.  The img.dtype
  # is 'uint8', meaning that each component is an 8-bit unsigned
  # integer.

  img = netpbm.imread( inputFile ).astype('uint8')

  # Compress the image

  startTime = time.time() # start timing

  diffImg = np.zeros(img.shape) # create an empty image to store the difference image
  outputBytes = bytearray() # byte array to write to file as compressed image

  # initialize dictionary
  dict = {}
 # append an index value to outputBytes and add it to the dictionary
  def output(output_symbol):
    if(len(output_symbol) > 1):
      index_value = dict[tuple(output_symbol)]
    else:
      index_value = dict[output_symbol[0]]
    # the index value needs to be split into two bytes
    # append the first byte
    outputBytes.append(index_value >> 8)
    # append the second byte
    outputBytes.append(index_value & 0xff)

# populate initial dictionary with all possible diffImg values
  for ind in range(512):
    dict[ind] = ind

  # if it is a color (3 channel) image
  if (len(img.shape) == 3):
    for y in range(img.shape[0]):
      for x in range(img.shape[1]):
        for c in range(img.shape[2]):
          if (x == 0): # there are no pixels to the left
            diffImg[y, x, c] = img[y, x, c]
          else:
            # create difference image and add 255 to keep index values positive
            diffImg[y, x, c] = int(img[y, x, c]) - int(img[y, x - 1, c]) + 255
          if y == 0  and x == 0 and c == 0:
            #setting the initial symbol value
            symbol = [diffImg[0,0,0]]
          else:
            next = [diffImg[y,x,c]]
            symbol_plus_next = symbol + next
            if(tuple(symbol_plus_next) in dict): # if S + x is already in the dictionary
              symbol = symbol_plus_next
            else: # if S + x is not in the dictionary
              # if symbol has more than a single value use a tuple, otherwise use int for dict indexing
              output(symbol)
              if(len(dict) < 65536): # restrict dictionary size so all indices are 2 bytes
                dict[tuple(symbol_plus_next)]= len(dict)
              symbol = next
            # output final symbol
            if (y == img.shape[0] - 1) and (x == img.shape[1] - 1) and (c == img.shape[2] - 1):
              output(symbol)
  else: # for an intensity only (1 channel) image
    for y in range(img.shape[0]):
      for x in range(img.shape[1]):
        if (x == 0): #there are no pixels to the left
          diffImg[y, x] = img[y, x]
        else:
          diffImg[y, x] = int(img[y, x]) - int(img[y, x - 1]) + 255

        #setting the initial symbol value
        if y == 0 and x == 0:
          symbol = [img[0,0]]
        else:
          next = [diffImg[y,x]]
          symbol_plus_next = symbol + next

          if(tuple(symbol_plus_next) in dict): # if S + x is in the dictionary
            symbol = symbol_plus_next
          else: # if S + x is not in the dictionary
            # if symbol has more than a single value use a tuple, otherwise use int for dict indexing
            output(symbol)
            if(len(dict) < 65536): # keep the dictionary size restricted
              dict[tuple(symbol_plus_next)]= len(dict)
            symbol = next
          if (y == img.shape[0] - 1) and (x == img.shape[1] - 1): # output final symbol
            output(symbol)

  endTime = time.time() # finish timing

  # Output the bytes
  #
  # Include the 'headerText' to identify the type of file.  Include
  # the rows, columns, channels so that the image shape can be
  # reconstructed.

  outputFile.write( '%s\n'       % headerText )
  if len(img.shape) == 3:
    outputFile.write( '%d %d %d\n' % (img.shape[0], img.shape[1], img.shape[2]) )
  else:
    outputFile.write( '%d %d %d\n' % (img.shape[0], img.shape[1], 1) )
  outputFile.write( outputBytes )

  # Print information about the compression
  if len(img.shape) == 3:
    inSize  = img.shape[0] * img.shape[1] * img.shape[2]
  else:
    inSize  = img.shape[0] * img.shape[1]
  outSize = len(outputBytes)

  sys.stderr.write( 'Input size:         %d bytes\n' % inSize )
  sys.stderr.write( 'Output size:        %d bytes\n' % outSize )
  sys.stderr.write( 'Compression factor: %.2f\n' % (inSize/float(outSize)) )
  sys.stderr.write( 'Compression time:   %.2f seconds\n' % (endTime - startTime) )
  # sys.stderr.write( 'Compression time:   %.4f seconds\n' % (endTime - startTime) )


# Uncompress an image

def uncompress( inputFile, outputFile ):

  # Check that it's a known file

  if inputFile.readline() != headerText + '\n':
    sys.stderr.write( "Input is not in the '%s' format.\n" % headerText )
    sys.exit(1)

  # Read the rows, columns, and channels.

  rows, columns, channels = [ int(x) for x in inputFile.readline().split() ]

  # Read the raw bytes.

  inputBytes = bytearray(inputFile.read())

  # Build the image

  startTime = time.time() # start the timer

  # get rows, columns, channels info from compressed image
  if(channels == 3):
    img = np.empty( [rows,columns,channels], dtype=np.uint8 )
    diffImgDecode = np.empty( [rows,columns,channels], dtype=np.uint8 )
  else:
    img = np.empty( [rows,columns], dtype=np.uint8 )
    diffImgDecode = np.empty( [rows,columns], dtype=np.uint8 )

  # create a list with each symbol from LZW (2 bytes each)
  symbols = []
  # reconstruct symbols from the byte array
  for i in range(len(inputBytes)):
      if (i % 2 == 0):
          temp = inputBytes[i]
      else:
          symbols.append((temp << 8) | inputBytes[i])

  # set up the initial dictionary for decoding with the same initial dictionary
  # as for encoding
  dictDecode = {}
  for ind in range(512):
    #not tuples yet
    dictDecode[ind] = ind

  # look up symbols in the dictionary as they appear, also update dictionary
  # symbolLookup should be a list of all symbols originally encoded
  prevSym = [dictDecode[symbols[0]]] # deal with the first symbol case
  symbolLookup = prevSym[:]

  for index in range(1, len(symbols)):
      if (symbols[index] in dictDecode): # if symbol is in dictonary
          decodedSymbol = dictDecode[symbols[index]]
          sym = [decodedSymbol] if type(decodedSymbol) == int else list(decodedSymbol)
          symbolLookup += sym
          if(len(dictDecode) < 65536): # dictionary restricted like encoding case
            dictDecode[len(dictDecode)] = tuple(prevSym + [sym[0]])
          prevSym = sym
      else: # if symbol is not in dictionary
          sym = prevSym + [prevSym[0]]
          symbolLookup += sym
          if(len(dictDecode) < 65536): # dictionary restricted like encoding case
            dictDecode[len(dictDecode)] = tuple(sym)
          prevSym = sym

    # undo the 'difference' encoding
  symbolLookupIter = iter(symbolLookup)

  if (channels == 3): # if colour (3 channel) image
    for y in range(rows):
      for x in range(columns):
        for c in range(channels):
          if (x == 0): # no pixels to the left
            diffImgDecode[y,x,c] = symbolLookupIter.next()
            img[y,x,c] = diffImgDecode[y,x,c]
          else: # undo difference encoding
            diffImgDecode[y,x,c] = symbolLookupIter.next()
            img[y,x,c] = int(diffImgDecode[y,x,c])  + int(img[y,x-1,c])  - 255
  else: # if intensity only image (1 channel)
    for y in range(rows):
      for x in range(columns):
        if (x == 0):
            diffImgDecode[y,x] = symbolLookupIter.next()
            img[y,x] = diffImgDecode[y,x]
        else:
            diffImgDecode[y,x] = symbolLookupIter.next()
            img[y,x] = int(diffImgDecode[y,x])  + int(img[y,x-1])  - 255

  endTime = time.time() # stop timer

  # Output the image

  netpbm.imsave( outputFile, img )

  sys.stderr.write( 'Uncompression time: %.2f seconds\n' % (endTime - startTime) )




# The command line is
#
#   main.py {flag} {input image filename} {output image filename}
#
# where {flag} is one of 'c' or 'u' for compress or uncompress and
# either filename can be '-' for standard input or standard output.


if len(sys.argv) < 4:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)

# Get input file

if sys.argv[2] == '-':
  inputFile = sys.stdin
else:
  try:
    inputFile = open( sys.argv[2], 'rb' )
  except:
    sys.stderr.write( "Could not open input file '%s'.\n" % sys.argv[2] )
    sys.exit(1)

# Get output file

if sys.argv[3] == '-':
  outputFile = sys.stdout
else:
  try:
    outputFile = open( sys.argv[3], 'wb' )
  except:
    sys.stderr.write( "Could not open output file '%s'.\n" % sys.argv[3] )
    sys.exit(1)

# Run the algorithm

if sys.argv[1] == 'c':
  compress( inputFile, outputFile )
elif sys.argv[1] == 'u':
  uncompress( inputFile, outputFile )
else:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)
