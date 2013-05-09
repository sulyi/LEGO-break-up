#!/usr/bin/env python
# coding:utf-8
'''
Created on 2013.04.03.

@author: arsene
'''
import sys,os,gettext

try:
    import pygame
    import numpy as np
    
    import OpenGL.GL as GL
#    import OpenGL.GLU as GLU  
except ImportError:
    with open( 'README.md', 'r' ) as markdown:
        for line in markdown:
            print line,
    sys.exit(1)
    
import lego
import gui
from reference import reference, opposite

def main():
    window_width = 800
    window_height = 600
    
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
    pygame.display.set_mode ((window_width,window_height), pygame.OPENGL|pygame.DOUBLEBUF, 24)
    print "Done"
    
    print "Initializing opengl ...",
    lego.gl_init(800,600)
    print "Done"
    
    # draw dialog screen 
    
    print "Loading layers ...",
    
    button_color = (0.8, 0.8, 0.0)
    button_focus_color = (0.3, 0.8, 0.5)
    button_error_color = (0.8, 0.4, 0.4)
    
    title = pygame.font.SysFont("courier", 24, True, True)
    small = pygame.font.SysFont("courier", 14, True, True)
    title_scale = 15
    sub_scale = -5
    text_color = ( 192, 64, 128 )
    text_error_color = (204, 204, 0)
    
    piecesize = reference()
    grid = opposite(True)
    
    controls = dict()
    controls["x"]     = gui.textbox(  11, 50,  42, 32, button_color, button_focus_color, button_error_color, small, text_color, text_error_color, (0,4) ) 
    controls["y"]     = gui.textbox(  62, 50,  42, 32, button_color, button_focus_color, button_error_color, small, text_color, text_error_color, (0,4) ) 
    controls["z"]     = gui.textbox( 113, 50,  42, 32, button_color, button_focus_color, button_error_color, small, text_color, text_error_color, (0,4) ) 
    controls["big"]   = gui.toggle (  33,150,  32, 32, button_color, button_focus_color, button_error_color, lego.LEGO_BIG,   piecesize ) 
    controls["small"] = gui.toggle ( 101,150,  32, 32, button_color, button_focus_color, button_error_color, lego.LEGO_SMALL, piecesize ) 
    controls["sides"] = gui.textbox(  11,220, 145,100, button_color, button_focus_color, button_error_color, small, text_color, text_error_color ) 
    controls["grid"]  = gui.toggle ( 123,334,  32, 32, button_color, button_focus_color, button_error_color, True, grid ) 
    controls["raise"] = gui.arrow  (  17,380,  32, 32, button_color, button_focus_color, button_error_color ) 
    controls["lower"] = gui.arrow  ( 117,380,  32, 32, button_color, button_focus_color, button_error_color, False ) 
    controls["send"]  = gui.button (  11,430, 145, 50, button_color, button_focus_color, button_error_color ) 
    
    static_layers = gui.layer_manager()
    static_layers.add( pygame.image.load(os.path.join('data','ui.png')), 0, 0, (0,0) )
    
    static_layers.add( title.render(po["position"],True,text_color),  20,  10, (0,title_scale) )
    static_layers.add( title.render(po["height"],  True,text_color),  20,  82, (0,title_scale) )
    static_layers.add( title.render(po["big"],     True,text_color),  20, 122, (0,sub_scale)   )
    static_layers.add( title.render(po["small"],   True,text_color),  85, 122, (0,sub_scale)   )
    static_layers.add( title.render(po["sides"],   True,text_color),  20, 182, (0,title_scale) )
    static_layers.add( title.render(po["grid"],    True,text_color),  20, 330, (0,title_scale) )
    static_layers.add( title.render("OK",          True,text_color),  67, 435, (0,title_scale) )
    static_layers.load()
    
    print "Done"
    
    print "\nEntering drawing loop\n"
    pieces = list()
    pieces.append(lego.piece( (4,2,-2,2,-1,1,-2,-1,-1,-2,2,-2), lego.LEGO_BIG,   (1.0, 0.1, 0.2), (-6,-6,0) ))
    pieces.append(lego.piece( (1,-1,1,1,1,-1,1,4,-3,-1,-1,-2),  lego.LEGO_BIG,   (0.2, 0.8, 0.3), (-8, 2,0) ))
    pieces.append(lego.piece( (2,2,1,1,-1,2,-2,-5),             lego.LEGO_BIG,   (0.2, 0.3, 0.8), ( 5, 1,0) ))
    pieces.append(lego.piece( (3,4,-3,-1,-1,-2,1,-1),           lego.LEGO_BIG,   (0.8, 0.3, 0.8), ( 1,-2,0) ))
    pieces.append(lego.piece( (2,7,-2,-5,-2,-1,2,-1),           lego.LEGO_SMALL, (0.9, 0.9, 0.3), ( 0, 0,1) ))
    
    lightp = np.array((2.0, 4.0, -4.0, 1.0))
    
    ticker = pygame.time.Clock()
    
    running = True
    fps = 30
    
    motionblur = False
    accumulate = False
    m_blur_f = 0.5
    
    rotating = False
    rotrot = 0.0
    rot_speed = 1.5
    rotx = 0
    roty = -40.0
    mouse_sens = -120
    
    position = np.array(( 2.0, -15, 15, 0.0))
    move = np.array(( 0.0, 0.0, 0.0, 0.0))
    move_speed = 0.5
    
    slow = False
    
    focused = None
    mouse_down = False
    key_hit = None
    
    errors = set()
    chosen = None
    
    grid_level = 0
    
    dyn_layers = gui.dynamic_layer_manager()
    dyn_layers.add( "grid-level", title.render(str(grid_level),True,text_color), 75, 377, (0,title_scale) )
    
    while running:
        cx = np.cos( rotx / 180.0 * np.pi )
        sx = np.sin( rotx / 180.0 * np.pi)
        cy = np.cos( roty / 180.0 * np.pi)
        sy = np.sin( roty / 180.0 * np.pi)

        xrot = np.array(( (cx,  0.0, -sx,  0.0), 
                          (0.0, 1.0,  0.0, 0.0),
                          (sx,  0.0,  cx,  0.0),
                          (0.0, 0.0,  0.0, 1.0)  ))
        
        yrot = np.array(( (1.0,  0.0, 0.0, 0.0), 
                          (0.0,  cy,  sy,  0.0),
                          (0.0, -sy,  cy,  0.0),
                          (0.0,  0.0, 0.0, 1.0)  ))
        
        rot = np.dot( xrot, yrot )
        
        # handle events
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running=False
                if not slow and event.key == 304:
                    mouse_sens = -60
                    slow = True
                    move_speed = 0.1
                    
                # FIXME: after moving down (ctrl) and another direction same time it stucks moving
                if event.mod % 256 == 64 or event.key == 306:
                    move[1] =  1.0
                elif event.key == 32:
                    move[1] = -1.0
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    move[0] =  1.0
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    move[0] = -1.0
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    move[2] =  1.0
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    move[2] = -1.0
                else:
                    key_hit = event
                    
            elif event.type == pygame.KEYUP:
                if event.mod % 256 == 64 or event.key == 306 or event.key == 32:
                    move[1] = 0.0
                elif ( event.key == pygame.K_a or event.key == pygame.K_LEFT or 
                     event.key == pygame.K_d or event.key == pygame.K_RIGHT   ):
                    move[0] = 0.0
                elif ( event.key == pygame.K_s or event.key == pygame.K_DOWN or
                       event.key == pygame.K_w or event.key == pygame.K_UP    ): 
                    move[2] = 0.0
                if slow and event.key == 304:
                    slow = False
                    mouse_sens = -120
                    move_speed = 0.5
                    
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
                GL.glSelectBuffer( 64 )
                
                GL.glRenderMode( GL.GL_SELECT )
                lego.draw_mode_3d(event.pos)
                GL.glInitNames()
                GL.glMultMatrixf( rot )
                GL.glMultMatrixf( np.eye(4) + np.vstack(( np.zeros((3,4)), position )) )
                for i,p in enumerate( pieces ):
                    GL.glPushName( i )
                    p.draw()
                    GL.glPopName()
                hits = GL.glRenderMode( GL.GL_RENDER )
                distance = None
                if hits:
                    for j in hits:
                        if distance > j[1] or distance is None:
                            distance = j[1]
                            chosen = pieces[ j[2][0] ]
                    controls["x"].value = str( chosen.position[0] )
                    controls["y"].value = str( chosen.position[1] )
                    controls["z"].value = str( chosen.position[2] )
                    piecesize.set( chosen.size )
                    controls["sides"].value = ''
                    controls["sides"].value = ','.join(str(i) for i in chosen.sides)
                else:
                    chosen = None
                
                GL.glRenderMode( GL.GL_SELECT )
                lego.draw_mode_2d(event.pos)
                GL.glInitNames()
                i = 0
                l = list()
                for k,b in controls.items():
                    GL.glPushName( i )
                    b.draw()
                    GL.glPopName()
                    l.append(k)
                    i += 1
                hits = GL.glRenderMode( GL.GL_RENDER )
                focused = controls[l[hits.pop()[2][0]]] if hits else None
                
            elif mouse_down and event.type == pygame.MOUSEMOTION:
                rotx += float(event.rel[0]) / window_width  * mouse_sens
                roty += float(event.rel[1]) / window_height * mouse_sens
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
                
        if not np.array_equal( move, np.array(( 0.0, 0.0, 0.0, 0.0 )) ):
            move = move_speed * move / np.sqrt( (move ** 2).sum() )
        position += np.dot( rot, move )
        
        # draw 3D stuff
        lego.draw_mode_3d()
        
        GL.glMultMatrixf( rot )
        GL.glMultMatrixf( np.eye(4) + np.vstack(( np.zeros((3,4)), position )) )
        
        if motionblur:
            if not accumulate:
                pygame.display.flip()
                GL.glClear( GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT )
            else:
                GL.glAccum( GL.GL_ACCUM,m_blur_f )
                GL.glAccum( GL.GL_RETURN, 1.0 )
                GL.glAccum( GL.GL_MULT, 1.0 - m_blur_f ) 
            accumulate = not accumulate
            ticker.tick( 2*fps )
            if rotating:
                rotrot = (rotrot + rot_speed/2) % 360
                GL.glRotatef( rotrot, 0.0, 1.0, 0.0 )
        else:
            pygame.display.flip()
            GL.glClear( GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT )
            ticker.tick( fps )
            if rotating:
                rotrot = (rotrot + rot_speed) % 360
                GL.glRotatef( rotrot, 0.0, 1.0, 0.0 )
        
        GL.glLightfv( GL.GL_LIGHT0, GL.GL_POSITION, lightp )
        
        if controls["grid"].value:
            lego.draw_grid(grid_level)
        
        ps = GL.glGetInteger( GL.GL_POINT_SIZE )
        GL.glPointSize( 10 )
        GL.glColor3f( 1.0, 1.0, 0.5 )
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glNormal3fv(lightp[:3])
        GL.glBegin( GL.GL_POINTS )
        GL.glVertex3fv( lightp[:3] - np.array((0.1, 0.1, 0.1)) )
        GL.glEnd()
        GL.glPointSize( ps )
            
        for piece in pieces:
            piece.draw()
        
        # draw 2D stuff
        lego.draw_mode_2d()
        
        static_layers.draw( 1 )
        
        for b in controls.values():
            
            decide = b is focused
            b.draw( decide, b in errors )
            if b is focused:
                if key_hit is not None and isinstance(b, gui.textbox):
                    b.append(key_hit)
                if isinstance(b, gui.toggle):
                    b.value = b.ref
                if b is controls["raise"]:
                    grid_level += 1
                    dyn_layers.add( "grid-level", title.render(str(grid_level),True,text_color), 75, 377, (0,title_scale) )
                if b is controls["lower"]:
                    grid_level -= 1
                    dyn_layers.add( "grid-level", title.render(str(grid_level),True,text_color), 75, 377, (0,title_scale) )
                if b is controls["send"]:
                    all_ok = True
                    errors = set()
                    try:
                        sides = tuple( int(i) for i in controls["sides"].value.split(',') )
                        lego.piece.is_closed(sides)
                    except lego.LoopError:
                        #TODO: write message on screen (error code)
                        errors.add(controls["sides"])
                        all_ok = False
                    except ValueError:
                        errors.add(controls["sides"])
                        all_ok = False
                    try:
                        x = int( float( controls["x"].value ) )
                    except ValueError:
                        errors.add(controls["x"])
                        all_ok = False
                    try:
                        y = int( float( controls["y"].value )*3 ) / 3.0
                    except ValueError:
                        errors.add(controls["y"])
                        all_ok = False
                    try:
                        z = int( float( controls["z"].value ) )
                    except ValueError:
                        errors.add(controls["z"])
                        all_ok = False
                    if piecesize.get() is None:
                        errors.add(controls["big"])
                        errors.add(controls["small"])
                        all_ok = False    
                        
                    if all_ok:
                        pieces.append( lego.piece(sides, piecesize.value, (0.2, 0.1, 0.8), (x,y,z)) )
                        controls["sides"].value = ''
                        controls["x"].value = '' 
                        controls["y"].value = ''
                        controls["z"].value = ''
                        piecesize.value = None
            if decide and not b.keepfocus:
                focused = None
                
        key_hit = None
        
        static_layers.draw()
        dyn_layers.draw()
        
    lego.finish()    
    pygame.quit()
    print "Bye!"


if __name__ == '__main__' : main() 