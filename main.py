#!/usr/bin/env python
# coding:utf-8
'''
Created on 2013.04.03.

@author: arsene
'''
import os,gettext

try:
    import pygame
    import numpy as np
    
    import OpenGL.GL as GL
#   import OpenGL.GLU as GLU  
except ImportError:
    with open('README.md', 'r') as markdown:
        for line in markdown:
            print line,
    exit(1) 
import lego

class button(pygame.Rect):
    def __init__( self, x, y, width, height, color, focus_color, value ):
        super( button, self ).__init__( x, y, width, height )
        self.color = color
        self.focus_color = focus_color
        self.value = value
        
    def draw( self, focused = False ):
        GL.glColor3fv( self.color if not focused else self.focus_color)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glRectiv( self.topleft, self.bottomright )
        
    def is_hit_by( self, point ):
        return self.contains(pygame.Rect( point, (0,0) ))

class layer_manager(object):
    def __init__(self):
        self._image_list = list()
        self.layer_list = None
    
    def add( self, tex, x, y, xscale=0, yscale=0 ):
        width = tex.get_width()
        height = tex.get_height()
        self._image_list.append(( tex, width, height, x, y, x+width+xscale, y+height+yscale ))
        
    def load(self):
        self.layer_list = list()
        first = GL.glGenLists(len(self._image_list))
        for i,tex in enumerate( self._image_list ):
            self.layer_list.append(( lego.load_2d_texture( pygame.image.tostring(tex[0], 'RGBA', True), tex[1], tex[2], first+i ),
                                  tex[3], tex[4], tex[5], tex[6] ))

def growPOT(surface):
    powers_of_two = (1,2,4,8,16,32,64,256,512,1024,2048,4096) # further are out of HD
    if not isinstance(surface, pygame.Surface):
        raise ValueError, "growPOT can only be done on a Surface (from pygame)"
    width = surface.get_width()
    height = surface.get_height()
    for i in powers_of_two:
        if width>=i:
            break
    for j in powers_of_two:
        if height>=j:
            break
    if not ( width == powers_of_two[i] and height == powers_of_two[j] ):
        canvas = pygame.Surface((powers_of_two[i], powers_of_two[j]),pygame.SRCALPHA)
        surface.blit(canvas,(0,0))
    return surface

def draw_ortho_layer(texture, x=0, y=0, width=None, height=None, color = (1.0, 1.0, 1.0)):
    if width is None: width = lego.SCREEN_WIDTH - x
    if height is None: height = lego.SCREEN_HEIGHT - y
    GL.glColor3fv(color)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    
    GL.glBegin(GL.GL_QUADS)
    GL.glTexCoord2f(0.0, 1.0); GL.glVertex2i(x,y)
    GL.glTexCoord2f(0.0, 0.0); GL.glVertex2i(x,height)
    GL.glTexCoord2f(1.0, 0.0); GL.glVertex2i(width,height)
    GL.glTexCoord2f(1.0, 1.0); GL.glVertex2i(width,y)    
    GL.glEnd()

def main():
    initial_brick_width = 2
    initial_brick_length = 3
    initial_brick_height = lego.LEGO_BIG
    
    print "Initializing locale ...",
    gettext.install('default', 'locale')
    po = { "position":  _("Position"), "height" : _("Height"), "big" :  _("Big"), "small" : _("Small"), 
           "sides" : _("Sides"), "grid" : _("Grid") }
    for k in po:
        po[k] = unicode(po[k],'utf8')
    print "Done"
    
    print "Initializing pygame ..." ,
    pygame.display.init()
    pygame.font.init()
    print "Done"
    
    print "Initializing screen ...",
    pygame.display.set_mode ((800,600), pygame.OPENGL|pygame.DOUBLEBUF, 24)
    
    print "Done"
    
    print "Initializing opengl ...",
    
    lego.gl_init(800,600)
    print "Done"
    
    # draw dialog screen 
    
    width_btn=button( 60,115, 100,100, (0.8, 0.8, 0.0), (0.3, 0.8, 0.5), initial_brick_width )
    length_btn=button( 60,330, 100,100, (0.8, 0.8, 0.0), (0.3, 0.8, 0.5) , initial_brick_length )
    
    buttons = [ width_btn, length_btn ]
                  
    print "Loading textures ...",
    
    textures = layer_manager()
    
    image = growPOT( pygame.image.load(os.path.join('data','ui.png')))
    textures.add( image, 0, 0, 0, 0 )
    
    title = pygame.font.SysFont("courier", 24, True, True)
    title_scale = 15
    sub_scale = -5
    text_color = ( 192, 64, 128 )
    
    text = title.render( po["position"], True, text_color )
    text = growPOT(text)
    textures.add( text, 20, 10, 0, title_scale )
    
    text = title.render( po["height"], True, text_color )
    text = growPOT(text)
    textures.add( text, 20, 225, 0, title_scale)

    text = title.render( po["big"], True, text_color )
    text = growPOT(text)
    textures.add( text, 20, 265, 0, sub_scale )
    
    textures.load()
    
    print "Done"
    
    print "\nEntering drawing loop\n"
    
    test_1 = lego.piece( (4,2,-2,2,-1,1,-2,-1,-1,-2,2,-2), lego.LEGO_BIG, (1.0, 0.1, 0.2), (-6,-6,0) )
    test_2 = lego.piece( (1,-1,1,1,1,-1,1,4,-3,-1,-1,-2), lego.LEGO_BIG, (0.2, 0.8, 0.3), (-8,2,0))
    test_3 = lego.piece( (2,2,1,1,-1,2,-2,-5), lego.LEGO_BIG, (0.2, 0.3, 0.8), (5,1,0) )
    test_4 = lego.piece( (3,4,-3,-1,-1,-2,1,-1), lego.LEGO_BIG, (0.8, 0.3, 0.8), (1,-2,0) )
    test_5 = lego.piece( (2,7,-2,-5,-2,-1,2,-1), lego.LEGO_SMALL, (0.8, 0.8, 0.3), (0,0,1) )
    
    lightp = np.array((2.0, 4.0, -4.0, 1.0))
    
    rot_speed = 1.5
    rot = 0
    ticker = pygame.time.Clock()
    running = True
    rotating = False
    focused = None
    mouse_hit = None
    key_hit = None
    motionblur = False
    accumulate = False
    fps = 30
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == 27 or ( event.mod % 256 == 64 and (event.key == 113 or event.key == 100 or event.key == 120) ):
                    running=False
                if event.mod % 256 == 0:
                    if event.key == 32:
                        rotating = not rotating
                    else:
                        try:
                            key_hit = int (event.unicode)
                        except ValueError:
                            pass 
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_hit = event.pos
        
        if motionblur:
            if not accumulate:
                pygame.display.flip()
                GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
            else:
                m_blur_f = 0.4
                GL.glAccum(GL.GL_ACCUM,m_blur_f)
                GL.glAccum(GL.GL_RETURN, 1.0)
                GL.glAccum(GL.GL_MULT,1.0 - m_blur_f)
            accumulate = not accumulate
            ticker.tick(2*fps)
            if rotating:
                rot = (rot + rot_speed/2) % 360
        else:
            pygame.display.flip()
            GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
            ticker.tick(fps)
            if rotating:
                rot = (rot + rot_speed) % 360
        
        # draw 3D stuff
        
        GL.glCallList(lego.L_DRAW_3D)
        
        GL.glTranslatef(2.0,0.2,15)
        GL.glRotatef(  -40, 1.0, 0.0, 0.0 )
        GL.glRotatef( rot, 0.0, 1.0, 0.0 )
        
        GL.glLightfv( GL.GL_LIGHT0, GL.GL_POSITION, -1 * lightp)
        
        lego.draw_grid()
        
        ps = GL.glGetInteger(GL.GL_POINT_SIZE)
        GL.glPointSize(10)
        GL.glColor3f(1.0, 1.0, 0.5)
        GL.glBegin(GL.GL_POINTS)
        GL.glVertex3fv( lightp[:3] - np.array((0.1, 0.1, 0.1)) )
        GL.glEnd()
        GL.glPointSize(ps)
            

        test_1.draw()
        test_2.draw()
        test_3.draw()
        test_4.draw()
        test_5.draw()
        
        # draw 2D stuff
        
        GL.glPushMatrix()
        GL.glCallList(lego.L_DRAW_2D)
        
        for i in textures.layer_list:
            draw_ortho_layer(*i)
        
        for b in  buttons:
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
        
        
        GL.glPopMatrix()
        
    lego.finish()    
    pygame.quit()
    print "Bye!"


if __name__ == '__main__' : main() 