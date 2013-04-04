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
    
    pygame.init()
    screen = pygame.display.set_mode ((800,600), pygame.OPENGL|pygame.DOUBLEBUF, 24)
    
    # draw dialog screen 
    
    button = pygame.Rect(10,10, 50, 50)
    
    lego.gl_init(800,600)
    
    
    
    
    glTranslatef(0.0,0.0,-6)
    glRotatef(40, 1.0, 0.0, 0.0)
    
    ticker = pygame.time.Clock()
    
    rot_speed = 3
    running = True
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYUP:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                print event.pos
                print button.contains( pygame.Rect(event.pos,(1,1)) ) 
        
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
        
        lego.draw_ortho_layer(os.path.join('data','ui.png'))
        
        #glMatrixMode(GL_PROJECTION)
        #glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
        pygame.display.flip()
        pygame.time.wait(100)
        
    print "Bye!"
            
