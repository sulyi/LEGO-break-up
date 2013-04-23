#!/usr/bin/env python2.7
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
    #import OpenGL.GLU as GLU  
except ImportError:
    with open('README.md', 'r') as markdown:
        for line in markdown:
            print line,
    exit(1) 
import lego

class button(pygame.Rect):
    def __init__(self, x, y, width, height, color, focus_color, value ):
        super(button, self ).__init__( x, y, width, height )
        self.color = color
        self.focus_color = focus_color
        self.value = value
        
    def draw( self, focused = False ):
        GL.glColor3fv( self.color if not focused else self.focus_color)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glRectiv( self.topleft, self.bottomright )
        
    def is_hit_by(self, point):
        return self.contains(pygame.Rect( point, (0,0) ))

def growPOT(surface):
    powers_of_two = (1,2,4,8,16,32,64,256,512,1024,2048,4096) # futher are out of HD
    if not isinstance(surface, pygame.Surface):
        raise ValueError, "growPOT can be done on a Surface (from pygame)"
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
         
if __name__ == '__main__':
    
    initial_brick_width = 2
    initial_brick_length = 3
    initial_brick_height = lego.LEGO_BIG
    
    print "Initializing locale ...",
    gettext.install('default', 'locale')
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
    
    lego.gl_init(800,600)
    print "Done"
    
    
    # draw dialog screen 
    
    width_btn=button( 60,115, 100,100, (0.8, 0.8, 0.0), (0.3, 0.8, 0.5), initial_brick_width )
    length_btn=button( 60,330, 100,100, (0.8, 0.8, 0.0), (0.3, 0.8, 0.5) , initial_brick_length )
    
    buttons = [ width_btn, length_btn ]
                  
    print "Loading textures ...",
    
    textures = dict()
    
    image = growPOT(pygame.image.load(os.path.join('data','ui.png')))
    
    imageData = pygame.image.tostring(image, "RGBA", True)
    
    width = image.get_width()
    height = image.get_height()
    
    # TODO: textured Rect class (note growPOT)
    
    textures["ui"] =  ( lego.load_2d_texture(imageData, width , height),
                        (1.0, 1.0, 1.0), 0, 0, width, height )
    
    font = pygame.font.SysFont("courier", 32, True, True)
    
    # TODO: text renderer class
    
    text_shadow = font.render( po["width"], True, (192, 64, 128) )
    text = font.render( po["width"], True, (153, 76, 178) )
    text_shadow.blit(text, (2,2))
    text = growPOT(text_shadow)
    
    textures["width_text"] = ( lego.load_2d_texture( pygame.image.tostring(text, 'RGBA', True), 
                                                 text.get_width(), text.get_height() ),   
                           (1.0, 1.0, 1.0), 20, 20, 190, 90 )
    
    text_shadow = font.render( po["depth"], True, (192, 64, 128) )
    text = font.render( po["depth"], True, (153, 76, 178) )
    text_shadow.blit(text, (2,2))
    text = growPOT(text_shadow)
    
    textures["depth_text"] = ( lego.load_2d_texture( pygame.image.tostring(text, 'RGBA', True), 
                                                 text.get_width(), text.get_height() ),   
                           (1.0, 1.0, 1.0), 20, 235, 190, 305 )
    
    text_shadow = font.render( po["height"], True, (192, 64, 128) )
    text = font.render( po["height"], True, (153, 76, 178) )
    text_shadow.blit(text, (2,2))
    text = growPOT(text_shadow)
    
    textures["height_text"] = ( lego.load_2d_texture( pygame.image.tostring(text, 'RGBA', True), 
                                                 text.get_width(), text.get_height() ),   
                           (1.0, 1.0, 1.0), 20, 20, 190, 90 )  
    
    print "Done"
    
    print "\nEntering drawing loop\n"
    
    #brick = lego.brick((2,1,-1,1,2,-3,2,-1,-3,-2,-1,1,-3,1,2,2),lego.LEGO_BIG,(1.0, 0.1, 0.2))
    brick = lego.brick((5,3,-2,-1,-2, -1,-1,-1),lego.LEGO_BIG,(1.0, 0.1, 0.2))
    lightp = np.array((3.0, -4.0, -4.0, -1.0))
    
    GL.glTranslatef(2.0,0.2,-15)
    GL.glRotatef(40, 1.0, 0.0, 0.0)
    
    rot_speed = 2
    ticker = pygame.time.Clock()
    running = True
    rotating = True
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
                GL.glRotatef(rot_speed/2, 0.0, 1.0, 0.0)
        else:
            pygame.display.flip()
            GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
            ticker.tick(fps)
            if rotating:
                GL.glRotatef(rot_speed, 0.0, 1.0, 0.0)
        
        # draw 3D stuff
        
        GL.glCallList(lego.L_DRAW_3D)
        GL.glLightfv( GL.GL_LIGHT0, GL.GL_POSITION, lightp)
        
        ps = GL.glGetInteger(GL.GL_POINT_SIZE)
        GL.glPointSize(10)
        GL.glColor3f(1.0, 1.0, 0.5)
        GL.glBegin(GL.GL_POINTS)
        GL.glVertex3fv( np.array((-0.1, -0.1, -0.1)) - lightp[:3] )
        GL.glEnd()
        GL.glPointSize(ps)
        
        # TODO: add height_btn, change height argument
        #lego.draw_lego_brick( width_btn.value, length_btn.value, initial_brick_height , (1.0, 0.1, 0.2) )
        brick.draw()
        
        # draw 2D stuff
        
        GL.glPushMatrix()
        GL.glCallList(lego.L_DRAW_2D)
        
        lego.draw_ortho_layer( *textures["ui"] )
        lego.draw_ortho_layer( *textures["width_text"])
        lego.draw_ortho_layer( *textures["depth_text"])
        
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
