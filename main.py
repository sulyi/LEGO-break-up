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
    lego.gl_init(800,600)
    print "Done"
    
    
    # draw dialog screen 
    
    button = pygame.Rect(10,10, 50, 50)
    
    glTranslatef(0.0,0.0,-6)
    glRotatef(40, 1.0, 0.0, 0.0)
    
    print "Loading textures ...",
    
    image = pygame.image.load(os.path.join('data','ui.png'))
    imageData = pygame.image.tostring(image, "RGBA", 1)
    
    print "Done"
    
    print "\nEntering drawing loop\n"
    
    rot_speed = 3
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
        lego.draw_lego_brick(3, 5, lego.LEGO_SMALL)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        glMatrixMode(GL_PROJECTION)
        #glPushMatrix()
        glLoadIdentity()
        glCallList(lego.L_DRAW_2D)
        
        lego.draw_ortho_layer(imageData, image.get_width(), image.get_height())
        
        #glMatrixMode(GL_PROJECTION)
        #glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
        pygame.display.flip()
        ticker.tick(40)
        
    print "Bye!"
            
