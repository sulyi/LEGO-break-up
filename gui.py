'''
Created on 2013.05.03.

@author: arsene
'''
import OpenGL.GL as GL

import pygame

# TODO: create textbox, toggle button (radio button)
class button( object ):
    def __init__( self, x, y, width, height, color, focus_color, keepfocus = False ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.focus_color = focus_color
        self.keepfocus = keepfocus
        
        self.topleft = (x,y)
        self.topright = (x+width,y)
        self.bottomleft = (x,y+height)
        self.bottomright = (x+width,y+height)
        
    def draw( self, focused = False ):
        GL.glColor3fv( self.color if not focused else self.focus_color)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glRectiv( self.topleft, self.bottomright )

class arrow( button ):
    def __init__(self, x, y, width, height, color, focus_color, up = True ):
        super(arrow, self).__init__( x, y, width, height, color, focus_color )
        self.up = up
        
    def draw(self, focused=False):
        GL.glColor3fv( self.color if not focused else self.focus_color)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glBegin(GL.GL_TRIANGLES)
        if self.up:
            GL.glVertex2iv( self.bottomleft  )
            GL.glVertex2iv( self.bottomright )
            GL.glVertex2i( self.x + self.width / 2, self.y )
        else:
            GL.glVertex2iv( self.topleft  )
            GL.glVertex2iv( self.topright )
            GL.glVertex2i( self.x + self.width / 2, self.y + self.height )
        GL.glEnd()

class layer_manager( object ):
    
    @staticmethod
    def growPOT( surface ):
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
            canvas = pygame.Surface( (powers_of_two[i], powers_of_two[j]), pygame.SRCALPHA )
            surface.blit(canvas,(0,0))
        return surface
    
    @staticmethod
    def draw_ortho_layer( texture, x, y, width, height, color = (1.0, 1.0, 1.0) ):
        GL.glColor3fv(color)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        
        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0.0, 1.0); GL.glVertex2i(x,y)
        GL.glTexCoord2f(0.0, 0.0); GL.glVertex2i(x,height)
        GL.glTexCoord2f(1.0, 0.0); GL.glVertex2i(width,height)
        GL.glTexCoord2f(1.0, 1.0); GL.glVertex2i(width,y)    
        GL.glEnd()
        
    @staticmethod    
    def load_2d_texture(imageData, width, height, texture=None ):
        if texture is None:
            texture = GL.glGenTextures(1)
        
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT,1)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D,GL.GL_TEXTURE_WRAP_S,GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D,GL.GL_TEXTURE_WRAP_T,GL.GL_REPEAT)
        
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, imageData)
        return texture
    
    def __init__(self):
        self._image_list = list()
        self.layer_list = None
        self.position = None
    
    def add( self, tex, x, y, xscale=0, yscale=0 ):
        tex = self.growPOT(tex)
        width = tex.get_width()
        height = tex.get_height()
        self._image_list.append(( tex, width, height, x, y, x+width+xscale, y+height+yscale ))
        return len(self._image_list) - 1
    
    def __delitem__( self, key ):
        del self._image_list[key]
        if self.layer_list is not None:
            del self.layer_list[key]
    
    def load( self ):
        self.layer_list = list()
        first = GL.glGenLists(len(self._image_list))
        for i,tex in enumerate( self._image_list ):
            self.layer_list.append(( self.__class__.load_2d_texture( pygame.image.tostring(tex[0], 'RGBA', True), tex[1], tex[2], first+i ),
                                  tex[3], tex[4], tex[5], tex[6] ))
        self.position = 0
    
    def draw( self, n=None ):
        if n is not None:
            n += self.position
        for i in self.layer_list[self.position:n]:
            self.__class__.draw_ortho_layer(*i)
        if n == len(self.layer_list) or n is None:
            self.position = 0
        else:
            self.position = n
    