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
  # img = np.array(
  #   [
  #     [
  #       [0,0,0],[50,50,50],[125,125,125]
  #     ],
  #     [
  #       [50,50,50],[125,125,125],[180,180,180]
  #     ],
  #     [
  #       [125,125,125],[180,180,180],[240,240,240]
  #     ]
  #   ])

  # Compress the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO FILL THE 'outputBytes' ARRAY.
  #
  # Note that single-channel images will have a 'shape' with only two
  # components: the y dimensions and the x dimension.  So you will
  # have to detect this and set the number of channels accordingly.
  # Furthermore, single-channel images must be indexed as img[y,x]
  # instead of img[y,x,1].  You'll need two pieces of similar code:
  # one piece for the single-channel case and one piece for the
  # multi-channel case.


  startTime = time.time()
  diffImg = np.zeros(img.shape)

  outputBytes = bytearray()

  output_with_dictionary_source = []

  #create initial dictionary
  dict = {}

  def output(output_symbol):
    if(len(output_symbol) > 1):
      index_value = dict[tuple(output_symbol)]
    else:
      index_value = dict[output_symbol[0]]
    # the index value needs to be split into two bytes
    # append the first byte
    output_with_dictionary_source.append({"dictionary_key": output_symbol, "value": index_value})
    # outputBytes.append(index_value/256)
    outputBytes.append(index_value >> 8)
    # append the second byte
    # outputBytes.append(index_value%256)
    outputBytes.append(index_value & 0xff)

  for ind in range(512):
    #not tuples yet
    dict[ind] = ind

  #if it is a color image
  if (len(img.shape) == 3):
    for y in range(img.shape[0]):
      for x in range(img.shape[1]):
        for c in range(img.shape[2]):
          if (x == 0): #there are no left pixels
            diffImg[y, x, c] = img[y, x, c]
          else:
            diffImg[y, x, c] = int(img[y, x, c]) - int(img[y, x - 1, c]) + 255

          if y == 0  and x == 0 and c == 0:
            #setting the initial symbol value
            symbol = [diffImg[0,0,0]]
          else:
            next = [diffImg[y,x,c]]
            symbol_plus_next = symbol + next
            if(tuple(symbol_plus_next) in dict):
              symbol = symbol_plus_next
            else:
              # if symbol has more than a single value use a tuple, otherwise use int for dict indexing
              output(symbol)
              if(len(dict) < 65536):
                dict[tuple(symbol_plus_next)]= len(dict)
              symbol = next
            if (y == img.shape[0] - 1) and (x == img.shape[1] - 1) and (c == img.shape[2] - 1):
              output(symbol)
  else:
    for y in range(img.shape[0]):
      for x in range(img.shape[1]):

        if (x == 0): #there are no left pixels
          diffImg[y, x] = img[y, x]
        else:
          diffImg[y, x] = int(img[y, x]) - int(img[y, x - 1]) + 255
          
        #setting the initial symbol value
        if y == 0 and x == 0:
          symbol = [img[0,0]]
        else:
          next = [diffImg[y,x]]
          symbol_plus_next = symbol + next

          if(tuple(symbol_plus_next) in dict):
            symbol = symbol_plus_next
          else:
            # if symbol has more than a single value use a tuple, otherwise use int for dict indexing
            output(symbol)
            if(len(dict) < 65536):
              dict[tuple(symbol_plus_next)]= len(dict)
            symbol = next
          if (y == img.shape[0] - 1) and (x == img.shape[1] - 1):
            output(symbol)

  # for i in range(20):
  #   print(outputBytes[i])


  endTime = time.time()

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
  #
  # REPLACE THIS WITH YOUR OWN CODE TO CONVERT THE 'inputBytes' ARRAY INTO AN IMAGE IN 'img'.

  startTime = time.time()
  if(channels == 3):
    img = np.empty( [rows,columns,channels], dtype=np.uint8 )
  else:
    img = np.empty( [rows,columns], dtype=np.uint8 )

  # byteIter = iter(inputBytes)

  #create a list with each symbol from LZW (2 bytes each)
  symbols = []
  # for i in range(len(byteIter)):
  for i in range(len(inputBytes)):
      if (i % 2 == 0):
          # temp = byteIter[i]
          temp = inputBytes[i]
      else:
          # symbols.append((temp << 8) | byteIter[i])
          symbols.append((temp << 8) | inputBytes[i])
  # set up the initial dictionary
  dictDecode = {}
  for ind in range(512):
    #not tuples yet
    dictDecode[ind] = ind

  # look up symbols in the dictionary as they appear, also update dictionary
  # symbolLookup should be a list of all symbols originally encoded
  # prevSym = list(dictDecode[symbols[0]]) # deal with the first symbol case, prevSym will be an int here
  #either a tuple or a int
  prevSym = [dictDecode[symbols[0]]] # deal with the first symbol case, prevSym will be an int here
  symbolLookup = prevSym

  #sym, prevsym and symbolLookup are lists

  for index in range(1, len(symbols)):
      if (symbols[index] in dictDecode):
          # sym = list(dictDecode[symbols[index]])
          decodedSymbol = dictDecode[symbols[index]]
          sym = [decodedSymbol] if type(decodedSymbol) == int else list(decodedSymbol)
          symbolLookup += sym
          # dictDecode[symbols[index]] = tuple([prevSym[0]] + sym)
          if(len(dictDecode) < 65536):
            dictDecode[len(dictDecode)] = tuple(prevSym + [sym[0]])
          prevSym = sym
      else:
          #both need to be lists
          # sym = prevSym + prevSym[0]
          sym = prevSym + [prevSym[0]]
          symbolLookup += sym
          if(len(dictDecode) < 65536):
            dictDecode[symbols[index]] = tuple(sym)
          # dictDecode[len(dictDecode)] = tuple(sym)
          prevSym = sym

    # undo the 'difference' encoding
  symbolLookupIter = iter(symbolLookup)

  if (channels == 3):
    for y in range(rows):
      for x in range(columns):
        for c in range(channels):
          if (x == 0):
            prevPixel = symbolLookupIter.next()
            img[y,x,c] = prevPixel
          else:
            pixel = symbolLookupIter.next()
            img[y,x,c] = pixel + prevPixel - 255
            prevPixel = img[y,x,c]
  else:
    for y in range(rows):
      for x in range(columns):
        if (x == 0):
          prevPixel = symbolLookupIter.next()
          img[y,x] = prevPixel
        else:
          pixel = symbolLookupIter.next()
          img[y,x] = pixel + prevPixel - 255
          prevPixel = img[y,x]

  endTime = time.time()

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
