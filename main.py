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

class button(pygame.Rect):
    def __init__( self, name, x, y, width, height, color, focus_color ):
        self.name = name
        super(button, self ).__init__( x, y, width, height )
        self.color = color
        self.focus_color = focus_color
        
    def draw( self, focused = False ):
        glColor3fv( self.color if not focused else self.focus_color)
        glBindTexture(GL_TEXTURE_2D, 0)
        glRectiv( self.topleft, self.bottomright )
        
    def is_hit_by(self, point):
        return self.contains(pygame.Rect( point, (0,0) ))

if __name__ == '__main__':

    print "Initializing locale ...",
    gettext.install('default', os.path.join('.','locale'))
    po = {"width":  _("Width"), "depth" :  _("Length"), "height" : _("Height") }
    for k in po:
        po[k] = unicode(po[k],'utf8')
    print "Done"
    
    print "Initializing pygame ..." ,
    pygame.init()
    print "Done"
    
    print "Initializing screen ...",
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
    
    buttons = { button( "widthbutton", 60,115, 100,100, (0.8, 0.8, 0.0), (0.3, 0.8, 0.5) ),
                button( "depthbutton", 60,330, 100,100, (0.8, 0.8, 0.0), (0.3, 0.8, 0.5) )
               }
                  
    print "Loading textures ...",
    
    textures = dict()
    
    image = pygame.image.load(os.path.join('data','ui.png'))
    imageData = pygame.image.tostring(image, "RGBA", True)
    
    width = image.get_width()
    height = image.get_height()
    
    textures["ui"] =  ( lego.load_2d_texture(imageData, width , height),
                        (1.0, 1.0, 1.0), 0, 0, width, height )
    
    font = pygame.font.SysFont("courier", 32, True, True)
    
    text_shadow = font.render( po["width"], True, (192, 64, 128) )
    text = font.render( po["width"], True, (153, 76, 178) )
    text_shadow.blit(text, (1,1))
    
    textures["widthtext"] = ( lego.load_2d_texture( pygame.image.tostring(text_shadow, 'RGBA', True), 
                                                 text_shadow.get_width(), text_shadow.get_height() ),   
                           (1.0, 1.0, 1.0), 20, 20, 190, 90 )
    
    text_shadow = font.render( po["depth"], True, (192, 64, 128) )
    text = font.render( po["depth"], True, (153, 76, 178) )
    text_shadow.blit(text, (1,1))
    
    textures["depthtext"] = ( lego.load_2d_texture( pygame.image.tostring(text_shadow, 'RGBA', True), 
                                                 text_shadow.get_width(), text_shadow.get_height() ),   
                           (1.0, 1.0, 1.0), 20, 235, 190, 305 )
    
    text_shadow = font.render( po["height"], True, (192, 64, 128) )
    text = font.render( po["height"], True, (153, 76, 178) )
    text_shadow.blit(text, (1,1))
    
    textures["heighttext"] = ( lego.load_2d_texture( pygame.image.tostring(text_shadow, 'RGBA', True), 
                                                 text_shadow.get_width(), text_shadow.get_height() ),   
                           (1.0, 1.0, 1.0), 20, 20, 190, 90 )  
    
    print "Done"
    
    print "\nEntering drawing loop\n"
    
    glTranslatef(0.8,0.2,-6)
    glRotatef(40, 1.0, 0.0, 0.0)
    
    
    rot_speed = 1.5
    ticker = pygame.time.Clock()
    running = True
    focused = None
    hit = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYUP:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                hit = event.pos
        
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
        lego.draw_ortho_layer( *textures["depthtext"])
        
        for b in  buttons:
            b.draw( b is focused )
            if hit and b.is_hit_by(hit):
                focused = b
                hit = None
        if hit is not None:
            hit = None
            focused = None
            
        
        glPopMatrix()
    
        pygame.display.flip()
        ticker.tick(40)
    
    lego.finish()    
    pygame.quit()    
    print "Bye!"
            
