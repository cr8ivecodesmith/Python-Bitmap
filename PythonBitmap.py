class Image:
    
    compression = { # Compression type and format
        0:('BI_RGB', 'no compression'), 
        1:('BI_RLE8', '8bit RLE encoding'), 
        2:('BI_RLE4', '4bit RLE encoding')}
        
    bits_per_pixel = { # Type of bits and the number of colours supported
        1:{'type':'monochrome palette', 'NumColors':1},
        4:{'type':'4bit palletised', 'NumColors':16},
        8:{'type':'8bit palletised', 'NumColors':256},
        16:{'type':'16bit RGB', 'NumColors':65536},
        24:{'type':'24bit RGB', 'NumColors':16000000}} 
    
    def __init__(self, content):
        
        self.raw = content # Return the raw byte values
        
    class Utils: # Image utilites
        
        def rasterData(bits):
            if bits == 1: return {'color':'black/white', 'compression':0, 'byte_pixels':8}
            elif bits == 4: return {'color':'16_color', 'compression':0, 'byte_pixels':2}
            elif bits == 8: return {'color':'256_color', 'compression':0, 'byte_pixels':1}
            else: raise Exception('UnrecordedError: This bit number is unknown or has not been recorded')         
        
    # -------------------------------------------------------------------------
    # END OF UTILS
    # -------------------------------------------------------------------------
        
    def __getBytesAwayFromColorTable(self):
        
        bitCount = Image(self.raw).getBitCount()
        if bitCount <= 8: 
            return 54+(4*Image.bits_per_pixel[bitCount]['NumColors'])
        else: 
            return 54
        
    
    def __colorTableAlgorithm(x): # Find the closest multiple of 4
        import math
        return 4*math.ceil(x/4)
        
    # -------------------------------------------------------------------------
    # START OF HEADER
    # -------------------------------------------------------------------------
    # 14 bytes

    def ofType(self):        
        """Return image type, returns False otherwise."""
        bytes_ = self.raw[:2]
        header_field = (b'BM', b'BA', b'CI', b'CP', b'IC', b'PT') # Different types        
        if bytes_ in header_field: return bytes_ # Check if it appears in the list and return the value
        else: return False # Otherwise return False
        
    def getHeader(self): 
        """Returns just the header data of the image."""
        return self.raw[:14]     
    
    def getSignature(self):
        """Return the signature of the image (first two bytes)."""
        return self.raw[:2]
    
    def getFileSize(self):
        """Get the file size of the bitmap image (independant of file)."""
        return int.from_bytes(self.raw[2:6], byteorder='little')
        
    def checkReserved(self):
        """Return the reserved content of the image."""
        return self.raw[6:10]
    
    def getDataOffset(self):
        """Return the File offset to Raster data of the bitmap"""
        return self.raw[10:14]
    
    # -------------------------------------------------------------------------
    # END OF HEADER
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # START OF INFOHEADER
    # -------------------------------------------------------------------------
    # 40 bytes
    
    def getInfoHeader(self):
        """Return the Info Header of the image"""
        return self.raw[14:54]
    
    def getInfoHeaderSize(self):
        """Return the size of the Info Header of image"""
        return int.from_bytes(self.raw[14:18], byteorder='little') 
    
    def getBitmapWidth(self):       
        """Return the width in pixels of the bitmap image"""
        return int.from_bytes(self.raw[18:22], byteorder='little')
    
    def getBitmapHeight(self):
        """Return the height in pixels of the bitmap image"""
        return int.from_bytes(self.raw[22:26], byteorder='little')
    
    def getPlanes(self):
        """Return the plane of the image"""
        return int.from_bytes(self.raw[26:28], byteorder='little') 
    
    def  getBitCount(self):
        """Return the type of bits per pixel"""
        return int.from_bytes(self.raw[28:30], byteorder='little')
    
    def getCompression(self):
        """Return the compression of the image"""
        return int.from_bytes(self.raw[30:34], byteorder='little')
    
    def getImageSize(self):
        """Return the compressed size of the image"""
        return int.from_bytes(self.raw[34:38], byteorder='little')
    
    # ---------------------
    # Compression must be 0
    # ---------------------
    
    def getXpixelsPerM(self):
        """The horizontal resolution in pixels per meter"""
        compression = Image(self.raw)
        if compression.getCompression() == 0: # Return the horizontal resolution
            return int.from_bytes(self.raw[38:42], byteorder='little')            
        else: raise Exception('CompressionSizeError: The image compression size must be 0') # Raise an exception if compression is not 0

    def getYpixelsPerM(self):
        """The vertical resolution in pixels per meter"""
        compression = Image(self.raw)
        if compression.getCompression() == 0: # Return the vertical resolution
            return int.from_bytes(self.raw[42:46], byteorder='little')            
        else: raise Exception('CompressionSizeError: The image compression size must be 0') # Raise an exception if compression is not 0


    def getColorsUsed(self):
        """Number of colours used in the image"""
        compression = Image(self.raw)
        if compression.getCompression() == 0: # Return the number of colors used
            return self.raw[46:50]
            #return int.from_bytes(self.raw[46:50], byteorder='little')            
        else: raise Exception('CompressionSizeError: The image compression size must be 0') # Raise an exception if compression is not 0

    def getColorsImportant(self):
        """Number of important colors, where 0 is all"""
        compression = Image(self.raw)
        if compression.getCompression() == 0: # Return the important colors
            return int.from_bytes(self.raw[50:54], byteorder='little')            
        else: raise Exception('CompressionSizeError: The image compression size must be 0') # Raise an exception if compression is not 0

    def getHeaderAndHeaderInfo(self):
        """Return both the header and the info header of the image"""
        return self.raw[:54]
    
    # -------------------------------------------------------------------------
    # END OF HEADER INFO
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # START OF COLORTABLE
    # -------------------------------------------------------------------------
    # 4 * NumColors bytes

    def getColorTable(self):
        """Get the ColorTable of the image, returns 0 if the value of Image.getBitCount()is higher than 8.  Run Image.bits_per_pixel for the full list of possible values."""
        bitCount = Image(self.raw).getBitCount()
        if bitCount <= 8: 
            return self.raw[54:Image.__getBytesAwayFromColorTable(self)]
        else: 
            return 0
        
    # -------------------------------------------------------------------------
    # END OF COLORTABLE
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # START OF PIXELDATA
    # -------------------------------------------------------------------------
     
    def getRawPixelData(self):
        """Return the raw pixel data of the image"""
        return self.raw[Image(self.raw).__getBytesAwayFromColorTable():]
    
    def getPixels(self):
        """Return a list of bytes.  Every three bytes represents a RGB value.  Each element in the list is the number of lines of the image"""        
        width = Image(self.raw).getBitmapWidth()* 3 # Get the pixel width and RGB values     
        return list(filter(None, self.raw[54:].split(b'\x00'*(Image.__colorTableAlgorithm(width) - width))))
        
# -----------------------------------------------------------------------------
# Credits:
# -----------------------------------------------------------------------------


#  From https://stackoverflow.com/questions/49753697/getting-file-size-of-bmp-image/49753926#49753926
#  Thank you DarkArctic https://stackoverflow.com/users/1240522/darkarctic
#  Who suggested the "int.from_bytes(raw, byteorder='little')" method for reading the byte values 

# Thank you SShah https://stackoverflow.com/users/7705353/sshah
# Who helped solve the ColorTable byte size 

# Thank you Andras Deak https://stackoverflow.com/users/5067311/andras-deak
# Who contributed the 4*math.ceil(x/4) algorim (as well as help on the usage and several other functions)
# Full transcript: https://chat.stackoverflow.com/transcript/message/42074275#42074275
# For the impatient: https://chat.stackoverflow.com/transcript/message/42074683#42074683

# Thanks to Stack Overflow https://www.stackoverflow.com
# And to the members of Room 6: Python https://chat.stackoverflow.com/rooms/6/python
# Who have helped me countless times.


# -----------------------------------------------------------------------------
# References:
# -----------------------------------------------------------------------------

# http://www.daubnet.com/en/file-format-bmp
# https://en.wikipedia.org/wiki/Bit_plane
# http://www.ece.ualberta.ca/~elliott/ee552/studentAppNotes/2003_w/misc/bmp_file_format/bmp_file_format.htm