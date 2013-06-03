'''
Created on 2013.04.03.

@author: arsene
'''

import sys,os

import OpenGL.GL as GL
import OpenGL.GLU as GLU

import numpy as np

import pygame
from pygame import error as PygameError

from gui import layer_manager

try:
    __image = pygame.image.load(os.path.join('data','legocap.png'))
except PygameError as e:
    print e.message
    sys.exit(1)

LEGO_CAP_WIDTH = __image.get_width()
LEGO_CAP_HEIGHT = __image.get_height()

LEGO_SMALL_HEIGHT = 0.32
LEGO_BIG_HEIGHT = 0.96
LEGO_BUMP_HEIGHT = 0.17

LEGO_HALF_BUMP_DIST = 0.15
LEGO_BUMP_RADIUS = 0.25
LEGO_GRID = 2*(LEGO_BUMP_RADIUS+LEGO_HALF_BUMP_DIST)

LEGO_BIG = True
LEGO_SMALL = False

SCREEN_WIDTH = None 
SCREEN_HEIGHT = None

class LoopError( ValueError ):
    def __init__( self, message, errno=None ):
        super(ValueError, self).__init__(message)
        self.errno = errno

class piece( object ):
    def __init__( self, sides, size, color,  position = (0.0, 0.0, 0.0) ):
        self.sides = sides
        self.color = color
        self.size = size
        self.position = np.array(position)
        
        height = LEGO_BIG_HEIGHT if self.size else LEGO_SMALL_HEIGHT
        length = self.bottom - self.top
        combine = lambda _points, _vertices, _weights: _points 
            
        self.__tess = GLU.gluNewTess()
        GLU.gluTessCallback(self.__tess, GLU.GLU_TESS_BEGIN, GL.glBegin)
        GLU.gluTessCallback(self.__tess,GLU.GLU_TESS_VERTEX,GL.glVertex3fv)
        GLU.gluTessCallback(self.__tess,GLU.GLU_TESS_COMBINE,combine)
        GLU.gluTessCallback(self.__tess, GLU.GLU_TESS_END, GL.glEnd)
        GLU.gluTessProperty(self.__tess, GLU.GLU_TESS_WINDING_RULE, GLU.GLU_TESS_WINDING_ODD)

        self.__gllist = GL.glGenLists(1)
        
        GL.glNewList(self.__gllist,GL.GL_COMPILE)
        GL.glColor3fv(self.color)
        GL.glBindTexture(GL.GL_TEXTURE_2D,0)
        
        GLU.gluTessNormal(self.__tess, 0.0, 1.0, 0.0)
        GL.glNormal3f(0.0, 1.0, 0.0)
        GLU.gluTessBeginPolygon(self.__tess,None)
        GLU.gluTessBeginContour(self.__tess)
        for i in range(0,len(self.coords)):
            vertex =  (self.coords[i][0]*LEGO_GRID, height, self.coords[i-1][1]*LEGO_GRID)
            GLU.gluTessVertex(self.__tess, vertex, vertex)
            vertex =  (self.coords[i][0]*LEGO_GRID, height, self.coords[i][1]*LEGO_GRID)
            GLU.gluTessVertex(self.__tess, vertex, vertex)
        GLU.gluTessEndContour(self.__tess)
        GLU.gluTessEndPolygon(self.__tess)
        
        for i in range(0,len(self.coords)):
            GL.glBegin(GL.GL_QUADS)
            sign = float(np.sign(self.sides[2*i-1]))
            GL.glNormal3f( sign, 0.0, 0.0 )
            GL.glVertex3f( self.coords[i][0] * LEGO_GRID, height, self.coords[i-1][1] * LEGO_GRID)
            GL.glVertex3f( self.coords[i][0] * LEGO_GRID, height, self.coords[i]  [1]   * LEGO_GRID)
            GL.glVertex3f( self.coords[i][0] * LEGO_GRID, 0.0,    self.coords[i]  [1]   * LEGO_GRID)
            GL.glVertex3f( self.coords[i][0] * LEGO_GRID, 0.0,    self.coords[i-1][1] * LEGO_GRID)
            sign = float(np.sign(self.sides[2*i-2]))
            GL.glNormal3f( 0.0, 0.0, -sign )
            GL.glVertex3f( self.coords[i-1][0] * LEGO_GRID, height, self.coords[i-1][1] * LEGO_GRID )
            GL.glVertex3f( self.coords[i]  [0] * LEGO_GRID, height, self.coords[i-1][1] * LEGO_GRID )
            GL.glVertex3f( self.coords[i]  [0] * LEGO_GRID, 0.0,    self.coords[i-1][1] * LEGO_GRID )
            GL.glVertex3f( self.coords[i-1][0] * LEGO_GRID, 0.0,    self.coords[i-1][1] * LEGO_GRID )
            GL.glEnd()
            
        GL.glTranslatef( self.left*LEGO_GRID + LEGO_GRID/2.0, (LEGO_BUMP_HEIGHT+height)/2.0 , self.bottom*LEGO_GRID - LEGO_GRID/2.0 )
        for i in range( self.left+1, self.right+1 ):
            for j in range( self.bottom+1, self.top+1 ):
                GL.glTranslatef( 0.0, 0.0, LEGO_GRID )
                if self.is_hit( (i,j) ):
                    _caped_cylinder( LEGO_BUMP_RADIUS, height+LEGO_BUMP_HEIGHT, 32 )
            GL.glTranslatef( 0.0, 0.0, length*LEGO_GRID )
            GL.glTranslatef( LEGO_GRID, 0.0, 0.0 )
        GL.glEndList()


    def __del__( self ):
        if hasattr( self,'__tess' ):
        # checking this might be speared, but shit happens ?
            GLU.gluDeleteTess( self.__tess )
    
    @property
    def position( self ):
        return self.__position
    
    @position.setter
    def position( self, position ):
        self.__position = position
        self.__real_position = (position[0] * LEGO_GRID, position[1] * LEGO_BIG_HEIGHT, position[2] * LEGO_GRID )
                
    @property
    def sides( self ):
        return self.__sides
    
    @sides.setter
    def sides( self, sides ):
        self.__is_closed( sides )
        self.__sides = sides
        
    @classmethod
    def is_closed( cls, sides ):
        length = len( sides )
        if length < 4:
            raise LoopError("Too few sides given to describe a rectangular shape", 1001)
        if length % 2 == 1:
            raise LoopError("Odd number of sides can't border a rectangular shape", 1002)
        xmax=0
        xmin=0
        zmax=0
        zmin=0
        horizontal = [0]
        for i,s in enumerate( sides[::2] ):
            x = horizontal[i] + s
            horizontal.append(x)
            if x > xmax:
                xmax = x
            if x < xmin:
                xmin = x
        vertical = [0]
        for j,s in enumerate( sides[1::2] ):
            z = vertical[j] + s
            vertical.append( z )
            if z > zmax:
                zmax = z
            if z < zmin:
                zmin = z
        i+=1
        j+=1
        if vertical[j] and horizontal[i]:
            raise LoopError("Neither even nor odd indexed sides are closed", 1020)
        if vertical[j]:
            raise LoopError("Even indexed sides are not closed", 1000)
        if horizontal[i]:
            raise LoopError("Odd indexed sides are not closed", 1010)
        return  tuple( np.array(i) for i in zip(horizontal[:-1], vertical[:-1]) ), xmax, xmin, zmax, zmin
        
    def __is_closed(self, sides):
        self.coords, self.right, self.left, self.top, self.bottom = self.__class__.is_closed(sides)
    
    def is_hit( self, point ):
        x = point[0]
        y = point[1]
        odd = False
        for i in range(0, len(self.coords) ):
            print (self.coords[i][0] >= x) , ((self.coords[i][1] >= y) , (self.coords[i-1][1] >= y))
            if (self.coords[i][0] >= x) and ((self.coords[i][1] >= y) != (self.coords[i-1][1] >= y)):
                odd = not odd        
        return odd
    
    def draw( self ):
        GL.glPushMatrix()
        
        GL.glTranslatef( *self.__real_position )
        GL.glCallList( self.__gllist )
        
        GL.glPopMatrix()

def gl_init( width, height ):
    global __legocaptex,__quadratic
    
    setviewport(width, height)
    
    __legocaptex = layer_manager.load_2d_texture(pygame.image.tostring(__image, "RGBA"), LEGO_CAP_WIDTH, LEGO_CAP_HEIGHT)
    __quadratic = GLU.gluNewQuadric()
    
    GLU.gluQuadricTexture(__quadratic, GLU.GLU_TRUE)
    GLU.gluQuadricDrawStyle(__quadratic,GLU.GLU_FILL)    
    GLU.gluQuadricOrientation(__quadratic, GLU.GLU_OUTSIDE)
    GLU.gluQuadricNormals(__quadratic, GLU.GLU_SMOOTH)
    
    GL.glClearColor( 0.0, 0.2, 0.5, 1.0 )
    
    GL.glEnable(GL.GL_POINT_SMOOTH)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glEnable(GL.GL_ALPHA_TEST)
    GL.glEnable(GL.GL_COLOR_MATERIAL)
    GL.glDisable(GL.GL_CULL_FACE)
    GL.glAlphaFunc(GL.GL_GREATER,0.1)
    
    GL.glClearAccum(0.0, 0.0, 0.0, 1.0)
    GL.glClear(GL.GL_ACCUM_BUFFER_BIT)
    
    #GL.glGenLists(1)
    
    draw_mode_3d()

def setviewport( width, height ):
    global SCREEN_WIDTH, SCREEN_HEIGHT 
    SCREEN_WIDTH = width
    SCREEN_HEIGHT = height
    GL.glViewport( 0, 0, width, height )

def draw_mode_2d( pick=(0,0) ):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    if GL.glGetInteger(GL.GL_RENDER_MODE) == GL.GL_SELECT:
        GLU.gluPickMatrix( pick[0], SCREEN_HEIGHT-pick[1], 10, 10, np.array((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) )
    GL.glOrtho(0.0, SCREEN_WIDTH, SCREEN_HEIGHT, 0.0, -1.0, 10.0)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()
    GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
    
#    GL.glDisable(GL_COLOR_MATERIAL)
    GL.glDisable(GL.GL_DEPTH_TEST)
    GL.glDisable(GL.GL_LIGHTING)

def draw_mode_3d( pick=(0,0) ):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    if GL.glGetInteger(GL.GL_RENDER_MODE) == GL.GL_SELECT:
        GLU.gluPickMatrix( pick[0], SCREEN_HEIGHT-pick[1], 1.0, 1.0, np.array((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) )
    GLU.gluPerspective(45.0, float(SCREEN_WIDTH)/float(SCREEN_HEIGHT), 0.1, 100.0)
    
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()
    GL.glScale( 1.0, 1.0, -1.0 )
    
#    GL.glEnable(GL_COLOR_MATERIAL)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_LIGHTING)
    
def finish():
    global __quadratic
    try:
        GLU.gluDeleteQuadric(__quadratic)
    except NameError as e:
        print e.message

def draw_grid( level ):
    GL.glDisable(GL.GL_LIGHTING)
    ls = GL.glGetFloat(GL.GL_LINE_WIDTH)
    GL.glLineWidth(3.0)
    GL.glColor3f(0.2, 0.5, 0.5)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    
    GL.glBegin(GL.GL_LINES)
    
    half_interval = 10
    
    for i in range(-half_interval, half_interval+1):
        GL.glVertex3f( i * LEGO_GRID, level * LEGO_BIG_HEIGHT,  half_interval * LEGO_GRID )
        GL.glVertex3f( i * LEGO_GRID, level * LEGO_BIG_HEIGHT, -half_interval * LEGO_GRID )
        GL.glVertex3f(  half_interval * LEGO_GRID, level * LEGO_BIG_HEIGHT, i * LEGO_GRID )
        GL.glVertex3f( -half_interval * LEGO_GRID, level * LEGO_BIG_HEIGHT, i * LEGO_GRID )
        
    GL.glEnd()
    GL.glLineWidth(ls)
    GL.glEnable(GL.GL_LIGHTING)
    
def _caped_cylinder( radius, height, segments ):
    global __quadratic, __legocaptex
    GL.glPushMatrix()
    
    GL.glRotatef(-90, 1.0, 0.0, 0.0)
    GL.glTranslatef(0.0, 0.0, -height/2.0)
    
    #GLU.gluQuadricOrientation(__quadratic, GLU.GLU_INSIDE)
    #gluDisk(__quadratic,0,radius,segments,1)
    #GLU.gluQuadricOrientation(__quadratic, GLU.GLU_OUTSIDE)
    
    GLU.gluCylinder( __quadratic, radius, radius, height, segments, 1 )
    
    GL.glTranslatef( 0.0, 0.0, height )
    GL.glBindTexture( GL.GL_TEXTURE_2D, __legocaptex )
    GLU.gluDisk( __quadratic, 0, radius, segments,1 )
    GL.glBindTexture( GL.GL_TEXTURE_2D, 0 )
    
    GL.glPopMatrix()

def _five_face_box( width, height, depth, color ):
    half_width = width/2.0
    half_height = height/2.0
    half_depth = depth/2.0
    
    GL.glBindTexture( GL.GL_TEXTURE_2D, 0 )
    
    GL.glColor3fv( color )
    GL.glNormal3f( 0.0, 0.0, 1.0 )
    GL.glBegin( GL.GL_QUADS )

    # Front Face
    GL.glTexCoord2f(0.0, 1.0); GL.glVertex3f( -half_width, -half_height,  half_depth )
    GL.glTexCoord2f(1.0, 1.0); GL.glVertex3f(  half_width, -half_height,  half_depth )
    GL.glTexCoord2f(1.0, 0.0); GL.glVertex3f(  half_width,  half_height,  half_depth )
    GL.glTexCoord2f(0.0, 0.0); GL.glVertex3f( -half_width,  half_height,  half_depth )
    
    GL.glEnd()
    
# TODO: add texcoordinates to other faces (for bump map)
    GL.glNormal3f( 0.0, 0.0, -1.0 )
    GL.glBegin( GL.GL_QUADS )
    
    # Back Face
    GL.glVertex3f(  half_width, -half_height, -half_depth )
    GL.glVertex3f( -half_width, -half_height, -half_depth )
    GL.glVertex3f( -half_width,  half_height, -half_depth )
    GL.glVertex3f(  half_width,  half_height, -half_depth )
    
    GL.glEnd()
    
    GL.glNormal3f( 1.0, 0.0, 0.0 )
    GL.glBegin( GL.GL_QUADS )

    # Right face
    GL.glVertex3f( half_width, -half_height,  half_depth )
    GL.glVertex3f( half_width, -half_height, -half_depth )
    GL.glVertex3f( half_width,  half_height, -half_depth )
    GL.glVertex3f( half_width,  half_height,  half_depth )
    
    GL.glEnd()
    
    GL.glNormal3f( -1.0, 0.0, 0.0 )
    GL.glBegin( GL.GL_QUADS )

    # Left Face
    GL.glVertex3f( -half_width, -half_height, -half_depth )
    GL.glVertex3f( -half_width, -half_height,  half_depth )
    GL.glVertex3f( -half_width,  half_height,  half_depth )
    GL.glVertex3f( -half_width,  half_height, -half_depth )
    
    GL.glEnd()
    
    GL.glNormal3f(0.0, 1.0, 0.0)
    GL.glBegin(GL.GL_QUADS)

    # Top Face
    GL.glVertex3f( -half_width,  half_height, -half_depth )
    GL.glVertex3f( -half_width,  half_height,  half_depth )
    GL.glVertex3f(  half_width,  half_height,  half_depth )
    GL.glVertex3f(  half_width,  half_height, -half_depth )
    
    GL.glEnd()
    
    #GL.glNormal3f(0.0, -1.0, 0.0)
    #GL.glBegin(GL.GL_QUADS)
    #
    ## Bottom Face
    #GL.glVertex3f( -half_width, -half_height, -half_depth )
    #GL.glVertex3f(  half_width, -half_height, -half_depth )
    #GL.glVertex3f(  half_width, -half_height,  half_depth )
    #GL.glVertex3f( -half_width, -half_height,  half_depth )
    #
    #GL.glEnd()

def draw_lego_brick( width, length, height, color ):
    grid = LEGO_GRID
    grid_width = width*grid
    grid_depth = length*grid
    grid_height = LEGO_BIG_HEIGHT if height else LEGO_SMALL_HEIGHT
    _five_face_box( grid_width, grid_height, grid_depth, color )
    GL.glPushMatrix()
    
    GL.glTranslatef( (grid-grid_width)/2.0, LEGO_BUMP_HEIGHT/2.0, (-grid-grid_depth)/2.0 )
    for _i in range( 0, width ):
        for _j in range( 0, length ):
            GL.glTranslatef( 0.0, 0.0, grid )
            _caped_cylinder( LEGO_BUMP_RADIUS, grid_height+LEGO_BUMP_HEIGHT, color, 32 )
        GL.glTranslatef( 0.0, 0.0, -length*grid )
        GL.glTranslatef( grid, 0.0, 0.0 )
    GL.glPopMatrix()
