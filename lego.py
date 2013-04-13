'''
Created on 2013.04.03.

@author: arsene
'''
import OpenGL.GL as GL
import OpenGL.GLU as GLU

try:
    from lego_constants import *
except ImportError:
    print "Please run lego_configure.py"
    raise

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
    global legocaptex,quadratic, \
           L_DRAW_2D,L_DRAW_3D,  \
           SCREEN_WIDTH, SCREEN_HEIGHT, \
           LEGO_CAP_TEXTURE
    
    legocaptex = load_2d_texture(LEGO_CAP_TEXTURE, 256, 256)
    
    SCREEN_WIDTH = width
    SCREEN_HEIGHT = height
   
    quadratic = GLU.gluNewQuadric()
    
    GLU.gluQuadricTexture(quadratic, GLU.GLU_TRUE)
    GLU.gluQuadricDrawStyle(quadratic,GLU.GLU_FILL)    
    GLU.gluQuadricOrientation(quadratic, GLU.GLU_OUTSIDE)
    GLU.gluQuadricNormals(quadratic, GLU.GLU_SMOOTH)
    
    GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, (0.1, 0.1, 0.1, 1.0))        # Setup The Ambient Light
    GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))        # Setup The Diffuse Light
    GL.glEnable(GL.GL_LIGHT0)                                           # Enable Light One
    
    GL.glClearColor(0.0, 0.2, 0.5, 1.0)
    GL.glViewport(0,0,800,600)
    
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glEnable(GL.GL_ALPHA_TEST)
    GL.glAlphaFunc(GL.GL_GREATER,0.1)
    GL.glDisable(GL.GL_CULL_FACE)
    GL.glEnable(GL.GL_COLOR_MATERIAL)
    
    L_DRAW_2D = GL.glGenLists(2)
    L_DRAW_3D = L_DRAW_2D + 1
    
    # L_DRAW_3D list
    
    GL.glNewList(L_DRAW_3D,GL.GL_COMPILE)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GLU.gluPerspective(45.0, float(800)/float(600), 0.1, 100.0)
#    gluLookAt(0.0, 0.0, -6.0,
#              0.0, 0.0, 0.0,
#              0.0, 0.0, 1.0
#              )
    GL.glMatrixMode(GL.GL_MODELVIEW)
    
    #glEnable(GL_COLOR_MATERIAL)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_LIGHTING)
    
    GL.glEndList()
    
    # L_DRAW_2D list
    
    GL.glNewList(L_DRAW_2D, GL.GL_COMPILE)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GL.glOrtho(0.0, width, height, 0.0, -1.0, 10.0)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()
    GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
    
    #glDisable(GL_COLOR_MATERIAL)
    GL.glDisable(GL.GL_DEPTH_TEST)
    GL.glDisable(GL.GL_LIGHTING)
    
    GL.glEndList()
    
    GL.glCallList(L_DRAW_3D)
    
def finish():
    global quadratic
    GLU.gluDeleteQuadric(quadratic)
    
def _caped_cylinder(radius,height,color,segments):
    global quadratic,legocaptex
    GL.glPushMatrix()
    
    GL.glRotatef(-90, 1.0, 0.0, 0.0)
    GL.glTranslatef(0.0, 0.0, -height/2.0)
    
#    glColor3f(1.0, 0.0 , 1.0)
#    gluQuadricOrientation(quadratic, GLU_INSIDE)
#    gluDisk(quadratic,0,radius,segments,1)
#    gluQuadricOrientation(quadratic, GLU_OUTSIDE)
    
    GL.glColor3fv(color)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    GLU.gluCylinder(quadratic,radius,radius,height,segments,segments)
    
    GL.glTranslatef(0.0,0.0,height)
    
    GL.glBindTexture(GL.GL_TEXTURE_2D, legocaptex)
    GLU.gluDisk(quadratic,0,radius,segments,1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    
    GL.glPopMatrix()

def _five_face_box(width,height,depth, color):
    global legocaptex
    _width=width/2.0
    _height=height/2.0
    _depth=depth/2.0
    
    GL.glBindTexture(GL.GL_TEXTURE_2D,0)
    
    GL.glColor3fv(color)
    GL.glNormal3f(0.0, 0.0, 1.0)
    GL.glBegin(GL.GL_QUADS)                # Start Drawing The Cube

    # Front Face
    GL.glTexCoord2f(0.0, 1.0); GL.glVertex3f(-_width, -_height,  _depth)
    GL.glTexCoord2f(1.0, 1.0); GL.glVertex3f( _width, -_height,  _depth)
    GL.glTexCoord2f(1.0, 0.0); GL.glVertex3f( _width,  _height,  _depth)
    GL.glTexCoord2f(0.0, 0.0); GL.glVertex3f(-_width,  _height,  _depth)
    # TODO: add texcoordinates to other faces
    GL.glEnd()

    GL.glNormal3f(0.0, 0.0, -1.0)
    GL.glBegin(GL.GL_QUADS)
    
    # Back Face
    GL.glVertex3f(-_width, -_height, -_depth)
    GL.glVertex3f(-_width,  _height, -_depth)
    GL.glVertex3f( _width,  _height, -_depth)
    GL.glVertex3f( _width, -_height, -_depth)
    
    GL.glEnd()
    
    GL.glNormal3f(0.0, 1.0, 0.0)
    GL.glBegin(GL.GL_QUADS)

    # Top Face
    GL.glVertex3f(-_width,  _height, -_depth)
    GL.glVertex3f(-_width,  _height,  _depth)
    GL.glVertex3f( _width,  _height,  _depth)
    GL.glVertex3f( _width,  _height, -_depth)
    
    GL.glEnd()
    
#    GL.glColor3f(0.0, 0.0 , 0.0)
#    GL.glNormal3f(0.0, -1.0, 0.0)
#    GL.glBegin(GL.GL_QUADS)
#
#    # Bottom Face
#    GL.glVertex3f(-_width, -_height, -_depth)
#    GL.glVertex3f( _width, -_height, -_depth)
#    GL.glVertex3f( _width, -_height,  _depth)
#    GL.glVertex3f(-_width, -_height,  _depth)
#
#    GL.glEnd()
    
    GL.glNormal3f(1.0, 0.0, 0.0)
    GL.glBegin(GL.GL_QUADS)

    # Right face
    GL.glVertex3f( _width, -_height, -_depth)
    GL.glVertex3f( _width,  _height, -_depth)
    GL.glVertex3f( _width,  _height,  _depth)
    GL.glVertex3f( _width, -_height,  _depth)
    
    GL.glEnd()
    
    GL.glNormal3f(-1.0, 0.0, 0.0)
    GL.glBegin(GL.GL_QUADS)

    # Left Face
    GL.glVertex3f(-_width, -_height, -_depth)
    GL.glVertex3f(-_width, -_height,  _depth)
    GL.glVertex3f(-_width,  _height,  _depth)
    GL.glVertex3f(-_width,  _height, -_depth)
    
    GL.glEnd()                # Done Drawing The Cube
    
def draw_lego_brick(width, length, height, color):

    _width=width*2*(LEGO_BUMP_RADIUS+LEGO_HALF_BUMP_DIST)
    _depth=length*2*(LEGO_BUMP_RADIUS+LEGO_HALF_BUMP_DIST)
    _height=LEGO_BIG_HEIGHT if height else LEGO_SMALL_HEIGHT
    _five_face_box(_width, _height, _depth, color)
    GL.glPushMatrix()
    grid=2*(LEGO_BUMP_RADIUS+LEGO_HALF_BUMP_DIST)
    GL.glTranslatef(LEGO_BUMP_RADIUS+LEGO_HALF_BUMP_DIST-_width/2.0, LEGO_BUMP_HEIGHT/2.0, -LEGO_BUMP_RADIUS-LEGO_HALF_BUMP_DIST-_depth/2.0)
    for _i in range(0, width):
        for _j in range(0, length):
            GL.glTranslatef(0.0, 0.0, grid)
            _caped_cylinder(LEGO_BUMP_RADIUS, _height+LEGO_BUMP_HEIGHT, color, 32)
        GL.glTranslatef(0.0, 0.0, -length*grid)
        GL.glTranslatef(grid, 0.0, 0.0)
    GL.glPopMatrix()

def load_2d_texture(imageData, width, height):
    
    texture = GL.glGenTextures(1)
    
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    
    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT,1)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D,GL.GL_TEXTURE_WRAP_S,GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D,GL.GL_TEXTURE_WRAP_T,GL.GL_REPEAT)
    # FIXME: power of 2
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, imageData)
    return texture
    
def draw_ortho_layer(texture, color = (1.0, 1.0, 1.0), x=0, y=0, width=None, height=None):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    if width is None: width = SCREEN_WIDTH - x
    if height is None: height = SCREEN_HEIGHT - y
    GL.glColor3fv(color)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    GL.glBegin(GL.GL_QUADS)
    GL.glTexCoord2f(0.0, 1.0); GL.glVertex2i(x,y)
    GL.glTexCoord2f(0.0, 0.0); GL.glVertex2i(x,height)
    GL.glTexCoord2f(1.0, 0.0); GL.glVertex2i(width,height)
    GL.glTexCoord2f(1.0, 1.0); GL.glVertex2i(width,y)    
    GL.glEnd()
    
