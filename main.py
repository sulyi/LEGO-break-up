#!/usr/bin/env python2.7
# coding:utf-8
'''
Created on 2013.04.03.

@author: arsene
'''
import os
import gettext
import pygame

from OpenGL.GL import *
from OpenGL.GLU import *   

import lego
from wicd.translations import language
from distutils.command.config import LANG_EXT



if __name__ == '__main__':
    
    print "Initializing translator ...",
    gettext.install('default', os.path.join('.','locale'))
    po = {"width":  _("width"), "depth" :  _("length"), "height" : _("height") }
    for k in po:
        po[k] = unicode(po[k],'utf8')
    print "Done"
    
    print "Initializing pygame ..." ,
    pygame.init()
    print "Done"
    
    print "Creating screen ...",
    screen = pygame.display.set_mode ((800,600), pygame.OPENGL|pygame.DOUBLEBUF, 24)
    print "Done"
    
    print "Initializing opengl ...",
    image = pygame.image.load(os.path.join('data','legocap.png'))
    imageData = pygame.image.tostring(image, "RGBA", True)
    
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
    imageData = pygame.image.tostring(image, "RGBA", True)
    
    width = image.get_width()
    height = image.get_height()
    
    textures["ui"] =  ( lego.load_2d_texture(imageData, width , height), (1.0, 1.0, 1.0), 0, 0, width, height )
    
    font = pygame.font.SysFont("courier", 32)
    
    text = font.render( po["width"], True, (255, 255, 255) )
    textures["widthtext"] = ( lego.load_2d_texture( pygame.image.tostring(text, 'RGBA', True), 
                                                 text.get_width(), text.get_height() ),   
                           (0.6, 0.3, 0.7), 20, 20, 190, 90 )
    
    text = font.render( po["depth"], True, (255, 255, 255) )
    
    textures["depthtext"] = ( lego.load_2d_texture( pygame.image.tostring(text, 'RGBA', True), 
                                                 text.get_width(), text.get_height() ),   
                           (0.6, 0.3, 0.7), 20, 235, 190, 305 )
    
    text = font.render( po["height"], True, (255, 255, 255) )
    
    textures["heighttext"] = ( lego.load_2d_texture( pygame.image.tostring(text, 'RGBA', True), 
                                                 text.get_width(), text.get_height() ),   
                           (0.6, 0.3, 0.7), 20, 20, 190, 90 )  
    
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
        
        glRectf
        
        glPushMatrix()
        
        glCallList(lego.L_DRAW_2D)
        
        lego.draw_ortho_layer( *textures["ui"] )
        
        lego.draw_ortho_layer( *textures["widthtext"])
        glColor3f(0.8, 0.8, 0.0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glRecti(60,115,160,215)
        
        lego.draw_ortho_layer( *textures["depthtext"])
        glColor3f(0.8, 0.8, 0.0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glRecti(60,330,160,430)
        
        glPopMatrix()
    
        pygame.display.flip()
        ticker.tick(40)
    
    lego.finish()    
    pygame.quit()    
    print "Bye!"
            
