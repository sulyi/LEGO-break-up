'''
Created on 2013.05.03.

@author: arsene
'''
import OpenGL.GL as GL

import pygame
import numpy as np

from reference import reference

class button( object ):
    def __init__( self, x, y, width, height, color, focus_color, error_color, keepfocus = False ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.focus_color = focus_color
        self.error_color = error_color
        self.keepfocus = keepfocus
        
        self.topleft = (x,y)
        self.topright = (x+width,y)
        self.bottomleft = (x,y+height)
        self.bottomright = (x+width,y+height)
        
    def draw( self, focused=False, error=False ):
        if not focused:
            GL.glColor3fv( self.color if not error else self.error_color )
        else:
            GL.glColor3fv( self.focus_color)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glRectiv( self.topleft, self.bottomright )

class arrow( button ):
    def __init__(self, x, y, width, height, color, focus_color, error_color, up = True ):
        super( arrow, self ).__init__( x, y, width, height, color, focus_color, error_color )
        self.up = up
        
    def draw(self, focused=False, error=False ):
        if not error:
            GL.glColor3fv( self.color if not focused else self.focus_color )
        else:
            GL.glColor3fv( self.error_color)
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
    def __init__(self, x, y, width, height, color, focus_color, error_color, font, text_color, text_error_color, text_offset = (0,0), text_scale=(0,0), text_max_length=None, keepfocus = True, value = '' ):
        super(textbox, self).__init__( x, y, width, height, color, focus_color, error_color, keepfocus )
        self.font = font
        self.text_color = text_color
        self.text_error_color = text_error_color
        self.text_scale = text_scale
        self.text_offset = text_offset
        self.text_max_length = text_max_length
        self.lines = 0
        self.__texs = list()
        self.error = False
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
                self.value = ''.join((self.value,value.unicode))
                    
    @property
    def value(self):
        return ''.join( self.__value.split('\n') )
    
    @value.setter
    def value(self, value):
        self.__value = ''
        ll = 1 if value else 0
        linesize = self.font.get_linesize()
        for letter in value:
            if self.font.size(self.__value.split('\n').pop())[0] + linesize/2 + self.text_offset[0] + self.font.size(letter)[0] + self.text_scale[0] < self.width:
                self.__value = ''.join((self.__value,letter))
            elif (ll+1) * (linesize+self.text_scale[1]) + self.text_offset[1] < self.height:
                ll += 1
                self.__value = ''.join((self.__value,'\n',letter))
        lines = self.__value.split('\n')
        newlines = ll - self.lines
        if newlines > 0:
            new_texs = GL.glGenTextures(2*newlines)  # it's prepared to take paste in
            for i in range(0, newlines):
                text = layer_manager.growPOT( self.font.render(lines[i+self.lines], True, self.text_color if not self.error else self.text_error_color ) )
                text_width = text.get_width()
                text_height = text.get_height()
                self.__texs.append(( layer_manager.load_2d_texture( pygame.image.tostring(text,'RGBA', True) , text_width, text_height, new_texs[0]+2*i ), text_width, text_height ))
        elif newlines < 0:
            damned = list()
            for _i in range(0, -newlines):
                damned.append(self.__texs.pop()[0])
            GL.glDeleteTextures(damned)
            self.lines = len(self.__texs)
        elif self.__texs:
            last = self.__texs.pop() 
            line = lines.pop()
            text = layer_manager.growPOT( self.font.render(line, True, self.text_color if not self.error else self.text_error_color ) )
            text_width = text.get_width()
            text_height = text.get_height()
            self.__texs.append(( layer_manager.load_2d_texture( pygame.image.tostring(text,'RGBA', True) , text_width, text_height, last[0] ), text_width, text_height ))
        self.lines = ll
    
    def draw( self, focused = False, error=False ):
        super( textbox, self ).draw( focused, error )
        #TODO: handle cursor
        if self.error != (error and not focused):
            self.error = error and not focused
            tmp = self.value
            self.value = ''
            self.value = tmp
        if self.value:
            linesize = self.font.get_linesize()
            x = self.x + linesize / 4 + self.text_offset[0]
            y = self.y + linesize / 4 + self.text_offset[1]
            for i,tex in enumerate(self.__texs):
                layer_manager.draw_ortho_layer( tex[0], x, y+i*(linesize+self.text_scale[1]), x+tex[1]+self.text_scale[0], y+i*linesize+tex[2]+self.text_scale[1]*self.lines )

class toggle( button ):
    def __init__(self, x, y, width, height, color, focus_color, error_color, value, ref ):
        super( toggle, self ).__init__( x, y, width, height, color, focus_color, error_color, False )
        self.ref = value
        if isinstance( ref, reference ):
            self.__value = ref
        else:
            raise ValueError, "Toggle button should have a reference as value"
    def draw( self, _focused=None, error=False ):
        super( toggle, self ).draw( self.value == self.ref, error )
    @property
    def value( self ):
        return self.__value.get()
    @value.setter
    def value( self, value ):
        self.__value.set( value )
            
class layer_manager( object ):
    
    @classmethod
    def growPOT( cls, surface ):
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
    
    @classmethod
    def draw_ortho_layer( cls, texture, x, y, width, height, color = (1.0, 1.0, 1.0) ):
        GL.glColor3fv(color)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        
        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0.0, 1.0); GL.glVertex2i(x,y)
        # FIXME: height should be height+y and so on ... (change effects def add)
        GL.glTexCoord2f(0.0, 0.0); GL.glVertex2i(x,height)
        GL.glTexCoord2f(1.0, 0.0); GL.glVertex2i(width,height)
        GL.glTexCoord2f(1.0, 1.0); GL.glVertex2i(width,y)    
        GL.glEnd()
        
    @classmethod    
    def load_2d_texture( cls, imageData, width, height, texture=None ):
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
        self.layer_list = list()
        self.position = 0
    
    def add( self, tex, x, y, scale=(0,0) ):
        if isinstance( tex, pygame.Surface ):
            tex = self.__class__.growPOT(tex)
            width = tex.get_width()
            height = tex.get_height()
            self._image_list.append(( tex, width, height, x, y, x+width+scale[0], y+height+scale[1] ))
        elif isinstance( tex, np.int64 ):
            act = GL.glGetInteger(GL.GL_ACTIVE_TEXTURE)
            GL.glBindTexture( GL.GL_TEXTURE_2D, tex )
            width = GL.glGetTexLevelParameteriv( GL.GL_TEXTURE_2D, 0, GL.GL_TEXTURE_WIDTH )
            height = GL.glGetTexLevelParameteriv( GL.GL_TEXTURE_2D, 0, GL.GL_TEXTURE_HEIGHT )
            GL.glBindTexture( GL.GL_TEXTURE_2D, act )
            self.layer_list.append(( tex, x, y, x+width+scale[0], y+height+scale[1] ))
        return len(self._image_list) - 1
    
    def remove( self, key ):
        del self._image_list[key]
        if self.layer_list is not None:
            GL.glDeleteTextures([self.layer_list[key][0]])
            del self.layer_list[key]
    
    def load( self ):
        n = len(self._image_list)
        if n == 1:
            first = GL.glGenTextures(n)
        else:
            first = GL.glGenTextures(n)[0]
        for i,tex in enumerate( self._image_list ):
            self.layer_list.append(( self.__class__.load_2d_texture( pygame.image.tostring(tex[0], 'RGBA', True), tex[1], tex[2], first+i ),
                                  tex[3], tex[4], tex[5], tex[6] ))
        
    def draw( self, n=None ):
        if n is not None:
            n += self.position
        for i in self.layer_list[self.position:n]:
            self.__class__.draw_ortho_layer(*i)
        if n == len(self.layer_list) or n is None:
            self.position = 0
        else:
            self.position = n

class dynamic_layer_manager( layer_manager ):
    def __init__( self ):
        self.layer_list = dict()
    
    def add( self, name, tex, x, y, scale=(0,0) ):
        tex = self.__class__.growPOT(tex)
        width = tex.get_width()
        height = tex.get_height()
        if self.layer_list.has_key(name):
            first = self.layer_list[name][0]
        else:
            first = GL.glGenTextures(1)
        self.layer_list[name] = ( super(dynamic_layer_manager, self.__class__).load_2d_texture( pygame.image.tostring(tex, 'RGBA', True), width, height, first ),
                                  x, y, x+width+scale[0], y+height+scale[1] )
        return len(self.layer_list) - 1
    
    def remove(self, key):
        GL.glDeleteTextures([self.layer_list[key][0]])
        del self.layer_list[key]
    
    def draw( self ):
        for i in self.layer_list.values():
            super(dynamic_layer_manager, self.__class__).draw_ortho_layer(*i)
        