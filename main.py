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
    def __init__(self, x, y, width, height, color, focus_color, value ):
        super(button, self ).__init__( x, y, width, height )
        self.color = color
        self.focus_color = focus_color
        self.value = value
        
    def draw( self, focused = False ):
        glColor3fv( self.color if not focused else self.focus_color)
        glBindTexture(GL_TEXTURE_2D, 0)
        glRectiv( self.topleft, self.bottomright )
        
    def is_hit_by(self, point):
        return self.contains(pygame.Rect( point, (0,0) ))

if __name__ == '__main__':
    
    
    initial_brick_width = 2
    initial_brick_length = 3
    initial_brick_height = lego.LEGO_BIG
    
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
    
    # FIXME: actually this is a terrible choice (slow data access)
    
    buttons = {
                "width_btn"  : button( 60,115, 100,100, (0.8, 0.8, 0.0), (0.3, 0.8, 0.5), initial_brick_width ),
                "length_btn" : button( 60,330, 100,100, (0.8, 0.8, 0.0), (0.3, 0.8, 0.5) , initial_brick_length ),
               }
                  
    print "Loading textures ...",
    
    textures = dict()
    
    image = pygame.image.load(os.path.join('data','ui.png'))
    imageData = pygame.image.tostring(image, "RGBA", True)
    
    width = image.get_width()
    height = image.get_height()
    
    # TODO: textured Rect 
    
    textures["ui"] =  ( lego.load_2d_texture(imageData, width , height),
                        (1.0, 1.0, 1.0), 0, 0, width, height )
    
    font = pygame.font.SysFont("courier", 32, True, True)
    
    # TODO: text renderer
    
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
    mouse_hit = None
    key_hit = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == 27 or ( event.mod == 64 and (event.key == 113 or event.key == 100 or event.key == 120) ):
                    running=False
                else:
                    try:
                        key_hit = int (event.unicode)
                    except ValueError:
                        pass
                    
                     
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_hit = event.pos
        
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        # drav 3D stuff
        
        glCallList(lego.L_DRAW_3D)
        
        glRotatef(rot_speed, 0.0, 1.0, 0.0)
        
        glLightfv( GL_LIGHT0, GL_POSITION, (3.0, -1.5, 2.0, -1.0) ) 
        
        # TODO: add height_btn, change height argument
        lego.draw_lego_brick( buttons["width_btn"].value, buttons["length_btn"].value, initial_brick_height , (1.0, 0.1, 0.2) )
        
        # drav 2D stuff
        
        glPushMatrix()
        glCallList(lego.L_DRAW_2D)
        
        lego.draw_ortho_layer( *textures["ui"] )
        lego.draw_ortho_layer( *textures["widthtext"])
        lego.draw_ortho_layer( *textures["depthtext"])
        
        for b in  buttons.values():
            b.draw( b is focused )
            if mouse_hit and b.is_hit_by(mouse_hit):
                focused = b
                mouse_hit = None
            if key_hit is not None and b is focused:
                b.value = key_hit
                
        if mouse_hit is not None:
            mouse_hit = None
            focused = None
        
        key_hit = None
        
        glPopMatrix()
    
        pygame.display.flip()
        ticker.tick(40)
    
    lego.finish()    
    pygame.quit()    
    print "Bye!"
            
