'''
Created on 2013.04.03.

@author: arsene
'''

from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from OpenGL.raw.GL import glTexCoord2i, glVertex2d

LEGO_SMALL_HEIGHT=0.32
LEGO_BIG_HEIGHT=0.96
LEGO_BUMP_HEIGHT=0.17

LEGO_HALF_BUMP_DIST=0.15
LEGO_BUMP_RADIUS=0.25

LEGO_BIG=True
LEGO_SMALL=False

SCREEN_WIDTH = None 
SCREEN_HEIGHT = None

L_DRAW_2D = None
L_DRAW_3D = None

def gl_init(width, height):
    global quadratic,L_DRAW_2D,L_DRAW_3D, SCREEN_WIDTH, SCREEN_HEIGHT
    
    SCREEN_WIDTH = width
    SCREEN_HEIGHT = height
    
    L_DRAW_2D = glGenLists(2)
    L_DRAW_3D = L_DRAW_2D + 1

    glClearColor(0.0, 0.2, 0.5, 1.0)
    glViewport(0,0,width,height)
    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GREATER,0.1)
    quadratic = gluNewQuadric()
    
    gluQuadricDrawStyle(quadratic,GLU_FILL)    
    gluQuadricOrientation(quadratic, GLU_OUTSIDE)
    gluQuadricNormals(quadratic, GLU_SMOOTH)
    
    glNewList(L_DRAW_3D,GL_COMPILE)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING) # TODO: add lighting and enable it
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_CULL_FACE)
    
    glEndList()
    
    glNewList(L_DRAW_2D, GL_COMPILE)
    glOrtho(0.0, width, height, 0.0, -1.0, 10.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)
    glDisable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    glClear(GL_DEPTH_BUFFER_BIT)
    glEndList()
    
    glCallList(L_DRAW_3D)
    
def _caped_cylinder(radius,height,segments):
    global quadratic
    glPushMatrix()
    glRotatef(-90, 1.0, 0.0, 0.0)
    glTranslatef(0.0, 0.0, -height/2.0)
    
#    glColor3f(1.0, 0.0 , 1.0)
#    gluQuadricOrientation(quadratic, GLU_INSIDE)
#    gluDisk(quadratic,0,radius,segments,1)
#    gluQuadricOrientation(quadratic, GLU_OUTSIDE)
    
    glColor3f(1.0, 1.0 , 1.0)
    gluCylinder(quadratic,radius,radius,height,segments,segments)
        
    glColor3f(1.0, 1.0 , 0.0)
    glTranslatef(0.0,0.0,height)
    
    gluDisk(quadratic,0,radius,segments,1)
    glPopMatrix()
    
def _five_face_box(width,height,depth):
    _width=width/2.0
    _height=height/2.0
    _depth=depth/2.0
    
    glColor3f(0.0, 0.8 , 0.8)
    glBegin(GL_QUADS)                # Start Drawing The Cube

    # Front Face
    glVertex3f(-_width, -_height,  _depth)
    glVertex3f( _width, -_height,  _depth)
    glVertex3f( _width,  _height,  _depth)
    glVertex3f(-_width,  _height,  _depth)

    glEnd()

    glColor3f(1.0, 1.0 , 0.5)
    glBegin(GL_QUADS)
    
    # Back Face
    glVertex3f(-_width, -_height, -_depth)
    glVertex3f(-_width,  _height, -_depth)
    glVertex3f( _width,  _height, -_depth)
    glVertex3f( _width, -_height, -_depth)
    
    glEnd()
    
    glColor3f(1.0, 0.5 , 0.5)
    glBegin(GL_QUADS)

    # Top Face
    glVertex3f(-_width,  _height, -_depth)
    glVertex3f(-_width,  _height,  _depth)
    glVertex3f( _width,  _height,  _depth)
    glVertex3f( _width,  _height, -_depth)
    
    glEnd()
    
#    glColor3f(0.0, 0.0 , 0.0)
#    glBegin(GL_QUADS)
#
#    # Bottom Face
#    glVertex3f(-_width, -_height, -_depth)
#    glVertex3f( _width, -_height, -_depth)
#    glVertex3f( _width, -_height,  _depth)
#    glVertex3f(-_width, -_height,  _depth)
#
#    glEnd()
    
    glColor3f(0.5, 0.5 , 1.0)
    glBegin(GL_QUADS)

    # Right face
    glVertex3f( _width, -_height, -_depth)
    glVertex3f( _width,  _height, -_depth)
    glVertex3f( _width,  _height,  _depth)
    glVertex3f( _width, -_height,  _depth)
    
    glEnd()
    
    glColor3f(0.0, 0.8 , 0.2)
    glBegin(GL_QUADS)

    # Left Face
    glVertex3f(-_width, -_height, -_depth)
    glVertex3f(-_width, -_height,  _depth)
    glVertex3f(-_width,  _height,  _depth)
    glVertex3f(-_width,  _height, -_depth)
    
    glEnd()                # Done Drawing The Cube

def draw_lego_brick(width, depth, size):
    glPushMatrix()
    _width=width*2*(LEGO_BUMP_RADIUS+LEGO_HALF_BUMP_DIST)
    _depth=depth*2*(LEGO_BUMP_RADIUS+LEGO_HALF_BUMP_DIST)
    _height=LEGO_BIG_HEIGHT if size else LEGO_SMALL_HEIGHT
    _five_face_box(_width, _height, _depth)
    grid=(LEGO_HALF_BUMP_DIST+LEGO_BUMP_RADIUS)*2
    glTranslatef(LEGO_BUMP_RADIUS+LEGO_HALF_BUMP_DIST-_width/2.0, LEGO_BUMP_HEIGHT/2.0, -LEGO_BUMP_RADIUS-LEGO_HALF_BUMP_DIST-_depth/2.0)
    for _i in range(0, width):
        for _j in range(0, depth):
            glTranslatef(0.0, 0.0, grid)
            _caped_cylinder(LEGO_BUMP_RADIUS, _height+LEGO_BUMP_HEIGHT, 32)
        glTranslatef(0.0, 0.0, -depth*grid)
        glTranslatef(grid, 0.0, 0.0)
    glPopMatrix()

def draw_ortho_layer(filename, x=None, y=None, width=None, height=None):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    if x is None: x = 0 
    if y is None: y = 0
    if width is None: width = SCREEN_WIDTH
    if height is None: height = SCREEN_HEIGHT
    image = pygame.image.load(filename)
    imageData = pygame.image.tostring(image, "RGBA", 1)
    
    texture = glGenTextures(1)
    
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.get_width(), image.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, imageData)
    
    glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0); glVertex2i(x,y)
    glTexCoord2f(0.0, 0.0); glVertex2i(x,height)
    glTexCoord2f(1.0, 0.0); glVertex2i(width,height)
    glTexCoord2f(1.0, 1.0); glVertex2i(width,y)
    glEnd()
    #glDeleteTextures(texture)
    
