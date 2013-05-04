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
        
class textbox( button ):
    def __init__(self, x, y, width, height, color, focus_color, font, text_color, text_offset = (0,0), text_scale=(0,0), text_max_length=None, keepfocus = True, value = '' ):
        super(textbox, self).__init__( x, y, width, height, color, focus_color, keepfocus )
        self.font = font
        self.text_color = text_color
        self.text_scale = text_scale
        self.text_offset = text_offset
        self.text_max_length = text_max_length
        self.lines = 0
        self.__texs = list()
        self.value = value
        
    def append(self, value):
        if len(self.value) > self.text_max_length:
            if value.key == pygame.K_BACKSPACE:
                if self.value:
                    if len(self.value) == 1 or self.value[-2] != '\n':
                        self.value = self.value[:-1]
                    else:
                        self.value = self.value[:-2]
            else:
                letter = value.unicode
                linesize = self.font.get_linesize()
                if self.font.size(self.value.split('\n').pop())[0]+linesize/2+self.text_offset[0]+self.font.size(letter)[0]+self.text_scale[0] < self.width:
                    self.value = ''.join((self.value,letter))
                elif (self.lines+1)*(linesize+self.text_scale[1])+self.text_offset[1] < self.height:
                    self.value = ''.join((self.value,'\n',letter))
                    
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        lines = value.split('\n')
        ll = len(lines)
        newlines = ll - self.lines
        if newlines > 0:
            first = GL.glGenTextures(newlines) # it's prepared to take paste in
            for i in range(self.lines, self.lines + newlines):
                text = layer_manager.growPOT( self.font.render(lines[i], True, self.text_color) )
                text_width = text.get_width()
                text_height = text.get_height()
                self.__texs.append(( layer_manager.load_2d_texture( pygame.image.tostring(text,'RGBA', True) , text_width, text_height, first+i ), text_width, text_height ))
        elif newlines < 0:
            damned = list()
            for _i in range(0, -newlines):
                damned.append(self.__texs.pop()[0])
            GL.glDeleteTextures(damned)
            self.lines = len(self.__texs)
        else:
            last = self.__texs.pop()
            line = lines.pop()
            text = layer_manager.growPOT( self.font.render(line, True, self.text_color) )
            text_width = text.get_width()
            text_height = text.get_height()
            self.__texs.append(( layer_manager.load_2d_texture( pygame.image.tostring(text,'RGBA', True) , text_width, text_height, last[0] ), text_width, text_height ))
        self.__value = value
        self.lines = ll
    
    def draw( self, focused = False ):
        super(textbox, self).draw(focused)
        #TODO: handle cursor
        if self.value:
            linesize = self.font.get_linesize()
            x = self.x + linesize / 4 + self.text_offset[0]
            y = self.y + linesize / 4 + self.text_offset[1]
            for i,tex in enumerate(self.__texs):
                layer_manager.draw_ortho_layer( tex[0], x, y+i*(linesize+self.text_scale[1]), x+tex[1]+self.text_scale[0], y+i*linesize+tex[2]+self.text_scale[1]*self.lines )
            
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
    
    def add( self, tex, x, y, scale=(0,0) ):
        tex = self.__class__.growPOT(tex)
        width = tex.get_width()
        height = tex.get_height()
        self._image_list.append(( tex, width, height, x, y, x+width+scale[0], y+height+scale[1] ))
        return len(self._image_list) - 1
    
    def __delitem__( self, key ):
        del self._image_list[key]
        if self.layer_list is not None:
            del self.layer_list[key]
    
    def load( self ):
        self.layer_list = list()
        first = GL.glGenTextures(len(self._image_list))[0]
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
    