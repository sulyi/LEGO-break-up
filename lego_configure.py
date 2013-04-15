'''
Created on 2013.04.13.

@author: arsene
'''

import os,base64
import pygame.image

def _load_image():
    global imageData, width, height
    
    image = pygame.image.load(os.path.join('data','legocap.png'))
    imageData = pygame.image.tostring(image, "RGBA", True)
        
    width = image.get_width()
    height = image.get_height()

def _write_config():
    global imageData, width, height
    
    with open('lego_constants.py', 'w+') as lego_constants:
        lego_constants.write("import base64\n\n")
        lego_constants.write( "".join(('LEGO_CAP_HEIGHT = ', str(height),'\n')) )
        lego_constants.write( "".join(('LEGO_CAP_WIDTH = ', str(width),'\n')) )
        lego_constants.write( "".join(('LEGO_CAP_TEXTURE = base64.b64decode("', base64.b64encode(imageData),'")')) )
        
    print "lego constants are configured"

def configure():
    print "Running configuration"
    _load_image()
    _write_config()
    
if __name__ == '__main__':
    
    try:
        import lego
        _load_image()
        if lego.LEGO_CAP_TEXTURE != imageData or lego.LEGO_CAP_HEIGHT != height or lego.LEGO_CAP_WIDTH != width:
            _write_config()
        else:
            print "No need to be configured"
    except ImportError:
        configure()
    
             
    
        