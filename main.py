'''
Created on 2013.04.03.

@author: arsene
'''
import os

import pygame

from OpenGL.GL import *
from OpenGL.GLU import *   

import lego



if __name__ == '__main__':
          
    print "Initializing pygame ..." ,
    pygame.init()
    print "Done"
    print "Creating screen ...",
    screen = pygame.display.set_mode ((800,600), pygame.OPENGL|pygame.DOUBLEBUF, 24)
    print "Done"
    print "Initializing opengl ...",
    
    image = pygame.image.load(os.path.join('data','legocap.png'))
    imageData = pygame.image.tostring(image, "RGBA", 1)
    
    width = image.get_width()
    height = image.get_height()
    
    # FIXME: parse into lego constants py
    lego.LEGO_CAP_TEXTURE = imageData  
    
    lego.gl_init(800,600)
    print "Done"
    
    
    # draw dialog screen 
    
    button = pygame.Rect(10,10, 50, 50)
    
    print "Loading textures ...",
    
    textures = dict()
    
    image = pygame.image.load(os.path.join('data','ui.png'))
    imageData = pygame.image.tostring(image, "RGBA", 1)
    
    width = image.get_width()
    height = image.get_height()
    
    textures["ui"] =  ( lego.load_2d_texture(imageData, width , height), 0, 0, width, height )
     
    print "Done"
    
    print "\nEntering drawing loop\n"
    
    glTranslatef(0.8,0.2,-6)
    glRotatef(40, 1.0, 0.0, 0.0)
    
    
    rot_speed = 1.5
    ticker = pygame.time.Clock()
    running = True
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYUP:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                print event.pos
                print button.contains( pygame.Rect(event.pos,(0,0)) ) 
        
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        glCallList(lego.L_DRAW_3D)
        
        glRotatef(rot_speed, 0.0, 1.0, 0.0)
        
        glLightfv( GL_LIGHT0, GL_POSITION, (3.0, -1.5, 2.0, -1.0) ) 
        
        lego.draw_lego_brick( 3, 3, lego.LEGO_SMALL, (1.0, 0.1, 0.2) )
        
        #glPushMatrix()
        
        #glCallList(lego.L_DRAW_2D)
        #lego.draw_ortho_layer( *textures["ui"] )
        
        #glPopMatrix()
    
        pygame.display.flip()
        ticker.tick(40)
    
    lego.finish()    
    pygame.quit()    
    print "Bye!"
            
