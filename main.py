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
  #       [100,100,100],[100,100,100],[100,100,100]
  #     ],
  #     [
  #       [100,100,100],[100,100,100],[100,100,100]
  #     ],
  #     [
  #       [100,100,100],[100,100,100],[100,100,100]
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

  outputBytesTemp = bytearray()

  # output_with_dictionary_source = []

  #create initial dictionary
  dict = {}
  for ind in range(512):
    #not tuples yet
    dict[ind] = ind

  if (len(img.shape) == 3):
    for y in range(img.shape[0]):
      for x in range(img.shape[1]):
        for c in range(img.shape[2]):
          if (x == 0): #there are no left pixels
            diffImg[y, x, c] = img[y, x, c]
          else:
            diffImg[y, x, c] = img[y, x, c] - img[y, x - 1, c] + 255
  else:
    for y in range(img.shape[0]):
      for x in range(img.shape[1]):
        if (x == 0): #there are no left pixels
          diffImg[y, x] = img[y, x]
        else:
          diffImg[y, x] = img[y, x] - img[y, x - 1] + 255

  #if it is a color image
  if (len(img.shape) == 3):
    for y in range(img.shape[0]):
      for x in range(img.shape[1]):
        for c in range(img.shape[2]):
          if y == 0  and x == 0 and c == 0:
            #setting the initial symbol value
            symbol = [img[0,0,0]]
          else:
            next = [diffImg[y,x,c]]
            symbol_plus_next = symbol + next
            if(tuple(symbol_plus_next) in dict):
              symbol = symbol_plus_next
            else:
              # if symbol has more than a single value use a tuple, otherwise use int for dict indexing
              if(len(symbol) > 1):
                index_value = dict[tuple(symbol)]
              else:
                index_value = dict[symbol[0]]
              # the index value needs to be split into two bytes
              # append the first byte
              # output_with_dictionary_source.append({"dictionary_key": symbol, "value": index_value})
              outputBytesTemp.append(index_value/256)
              # append the second byte
              outputBytesTemp.append(index_value%256)
              # print("not seen before")
              if(len(dict) < 65536):
                dict[tuple(symbol_plus_next)]= len(dict)
              symbol = next
  else:
    for y in range(img.shape[0]):
      for x in range(img.shape[1]):
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
            if(len(symbol) > 1):
              index_value = dict[tuple(symbol)]
            else:
              index_value = dict[symbol[0]]
            # the index value needs to be split into two bytes
            # append the first byte
            # output_with_dictionary_source.append({"dictionary_key": symbol, "value": index_value})
            outputBytesTemp.append(index_value/256)
            # append the second byte
            outputBytesTemp.append(index_value%256)
            if(len(dict) < 65536):
              dict[tuple(symbol_plus_next)]= len(dict)
            symbol = next

  # for i in range(len(outputBytesTemp)):
  #   print(outputBytesTemp[i])
  outputBytes = outputBytesTemp

  endTime = time.time()

  # Output the bytes
  #
  # Include the 'headerText' to identify the type of file.  Include
  # the rows, columns, channels so that the image shape can be
  # reconstructed.

  outputFile.write( '%s\n'       % headerText )
  outputFile.write( '%d %d %d\n' % (img.shape[0], img.shape[1], img.shape[2]) )
  outputFile.write( outputBytes )

  # Print information about the compression
  
  inSize  = img.shape[0] * img.shape[1] * img.shape[2]
  outSize = len(outputBytes)

  sys.stderr.write( 'Input size:         %d bytes\n' % inSize )
  sys.stderr.write( 'Output size:        %d bytes\n' % outSize )
  sys.stderr.write( 'Compression factor: %.2f\n' % (inSize/float(outSize)) )
  sys.stderr.write( 'Compression time:   %.2f seconds\n' % (endTime - startTime) )
  


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

  img = np.empty( [rows,columns,channels], dtype=np.uint8 )

  byteIter = iter(inputBytes)
  for y in range(rows):
    for x in range(columns):
      for c in range(channels):
        img[y,x,c] = byteIter.next()

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
