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

def dict_substract( a, b ):
    if isinstance(a, dict) and isinstance(b, dict):
        c = dict(a)
        for k in b:
            if k in a:
                del c[k]
        return c
    else:
        raise ValueError, "Two dictionary is expected"
    
def dict_union( a, b ):
    if isinstance(a, dict) and isinstance(b, dict):
        c = dict(a, **b)
        return c
    else:
        raise ValueError, "Two dictionary is expected"

def main():
    window_width = 800
    window_height = 600
    
    print "Initializing locale ...",
    gettext.install('default', 'locale')
    po = { "position" :  _("Position"), "height" : _("Height"), "big" :  _("Big"), "small" : _("Small"), 
           "sides" : _("Sides"), "grid" : _("Grid"), "exit" : _("Exit"),
           "del" : _("Delete"), "clear" : _("Clear"), "options" : _("Options"),
           "up" : _("Up"), "down" : _("Down"), "left" : _("Left"), "right" : _("Right"), "forward" : _("Forward"), "back" : _("Back"),
           "motion_blur" : _("Motion Blur"), "light" : _("Light"),
           "few"      : _("Too few sides given to describe a rectangular shape"),
           "not_even" : _("Odd number of sides can't border a rectangular shape"),
           "both"     : _("Neither even nor odd indexed sides are closed"),
           "even"     : _("Even indexed sides are not closed"),
           "odd"      : _("Odd indexed sides are not closed")
           }
    for k in po:
        po[k] = unicode(po[k],'utf8')
    print "Done"
    
    print "Initializing pygame ..." ,
    pygame.display.init()
    pygame.font.init()
    print "Done"
    
    print "Initializing screen ...",
    pygame.display.set_mode ( (window_width,window_height), pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE, 24 )
    print "Done"
    
    print "Initializing opengl ...",
    lego.gl_init( window_width, window_height )
    print "Done"
    
    # draw dialog screen 
    
    print "Loading layers ...",
    
    button_color = (0.8, 0.8, 0.0)
    button_focus_color = (0.3, 0.8, 0.5)
    button_error_color = (0.8, 0.4, 0.4)
    
    title      = pygame.font.SysFont("courier", 24, True,  True)
    error      = pygame.font.SysFont("courier", 18, True,  True)
    small      = pygame.font.SysFont("courier", 14, False, True)
    bold_small = pygame.font.SysFont("courier", 14, True,  True)
    title_scale = 15
    sub_scale = -5
    text_color = ( 192, 64, 128 )
    text_error_color = (204, 204, 0)
    
    piecesize = reference()
    grid = opposite(True)
    mblur = opposite(False)
     
    controls = dict()
    controls["x"]          = gui.textbox(  11, 50,  42, 32, button_color, button_focus_color, button_error_color, bold_small, text_color, text_error_color, (0,4) ) 
    controls["y"]          = gui.textbox(  62, 50,  42, 32, button_color, button_focus_color, button_error_color, bold_small, text_color, text_error_color, (0,4) ) 
    controls["z"]          = gui.textbox( 113, 50,  42, 32, button_color, button_focus_color, button_error_color, bold_small, text_color, text_error_color, (0,4) ) 
    controls["big"]        = gui.toggle (  33,150,  32, 32, button_color, button_focus_color, button_error_color, lego.LEGO_BIG,   piecesize ) 
    controls["small"]      = gui.toggle ( 101,150,  32, 32, button_color, button_focus_color, button_error_color, lego.LEGO_SMALL, piecesize ) 
    controls["sides"]      = gui.textbox(  11,220, 145,100, button_color, button_focus_color, button_error_color, bold_small, text_color, text_error_color ) 
    controls["grid"]       = gui.toggle ( 123,334,  32, 32, button_color, button_focus_color, button_error_color, True, grid ) 
    controls["raise_grid"] = gui.arrow  (  17,380,  32, 32, button_color, button_focus_color, button_error_color ) 
    controls["lower_grid"] = gui.arrow  ( 117,380,  32, 32, button_color, button_focus_color, button_error_color, False ) 
    controls["send"]       = gui.button (  11,430, 145, 37, button_color, button_focus_color, button_error_color )
    controls["del"]        = gui.button (  11,479,  70, 37, button_color, button_focus_color, button_error_color )
    controls["clear"]      = gui.button (  86,479,  70, 37, button_color, button_focus_color, button_error_color )
    controls["options"]    = gui.button (  11,545, 145, 37, button_color, button_focus_color, button_error_color )
    
    options = dict()
    options["mblur"]       = gui.toggle( 237,298, 32, 32, button_color, button_focus_color, button_error_color, True, mblur )
    options["raise_mblur"] = gui.arrow ( 187,331, 32, 32, button_color, button_focus_color, button_error_color ) 
    options["lower_mblur"] = gui.arrow ( 287,331, 32, 32, button_color, button_focus_color, button_error_color, False )
    options["raise_light"] = gui.arrow ( 187,430, 32, 32, button_color, button_focus_color, button_error_color ) 
    options["lower_light"] = gui.arrow ( 287,430, 32, 32, button_color, button_focus_color, button_error_color, False )
    
    static_layers = gui.layer_manager()
    
    static_layers.add( pygame.image.load(os.path.join('data','ui.png')), 0, 0, (0,0) )
    
    static_layers.add( title.render(po["position"],True,text_color),  20,  10, (0,title_scale) )
    static_layers.add( title.render(po["height"],  True,text_color),  20,  82, (0,title_scale) )
    static_layers.add( title.render(po["big"],     True,text_color),  20, 122, (0,sub_scale)   )
    static_layers.add( title.render(po["small"],   True,text_color),  85, 122, (0,sub_scale)   )
    static_layers.add( title.render(po["sides"],   True,text_color),  20, 182, (0,title_scale) )
    static_layers.add( title.render(po["grid"],    True,text_color),  20, 330, (0,title_scale) )
    static_layers.add( title.render("OK",          True,text_color),  67, 437, (0,sub_scale) )
    static_layers.add( small.render(po["del"],     True,text_color),  20, 488, (0,3) )
    static_layers.add( small.render(po["clear"],   True,text_color),  95, 488, (0,3) )
    static_layers.add( small.render(po["options"], True,text_color),  50, 553, (0,3) )
    static_layers.load()
    
    options_layers = gui.layer_manager()
    
    options_layers.add( static_layers.layer_list[0][0], 170, 0, (0,0) )
    
    options_layers.add( title.render(po["motion_blur"],True,text_color),  178,244, (0,title_scale) )
    options_layers.add( title.render(po["light"],      True,text_color),  178,377, (0,title_scale) )
    
    options_layers.add( small.render(' '.join(( po["forward"], ":" )), True,text_color),  180,  8, (0,3) )
    options_layers.add( small.render(' '.join(( po["back"], ":" )),    True,text_color),  180, 41, (0,3) )
    options_layers.add( small.render(' '.join(( po["left"], ":" )),    True,text_color),  180, 74, (0,3) )
    options_layers.add( small.render(' '.join(( po["right"], ":" )),   True,text_color),  180,107, (0,3) )
    options_layers.add( small.render(' '.join(( po["up"], ":" )),      True,text_color),  180,140, (0,3) )
    options_layers.add( small.render(' '.join(( po["down"], ":" )),    True,text_color),  180,173, (0,3) )
    options_layers.add( small.render(' '.join(( po["exit"], ":" )),    True,text_color),  180,206, (0,3) )
    
    options_layers.add( small.render('W',    True,text_color),  270,  8, (0,3) )
    options_layers.add( small.render('S',    True,text_color),  270, 41, (0,3) )
    options_layers.add( small.render('A',    True,text_color),  270, 74, (0,3) )
    options_layers.add( small.render('D',    True,text_color),  270,107, (0,3) )
    options_layers.add( small.render('Space',True,text_color),  270,140, (0,3) )
    options_layers.add( small.render('Ctrl', True,text_color),  270,173, (0,3) )
    options_layers.add( small.render('Esc',  True,text_color),  270,206, (0,3) )
    
    options_layers.load()
    
    print "Done"
    
    print "\nEntering drawing loop\n"
    pieces = list()
    pieces.append(lego.piece( (4,2,-2,2,-1,1,-2,-1,-1,-2,2,-2), lego.LEGO_BIG,   (1.0, 0.1, 0.2), (-6,-6,0) ))
    pieces.append(lego.piece( (1,-1,1,1,1,-1,1,4,-3,-1,-1,-2),  lego.LEGO_BIG,   (0.2, 0.8, 0.3), (-8, 2,0) ))
    pieces.append(lego.piece( (2,2,1,1,-1,2,-2,-5),             lego.LEGO_BIG,   (0.2, 0.3, 0.8), ( 5, 1,0) ))
    pieces.append(lego.piece( (3,4,-3,-1,-1,-2,1,-1),           lego.LEGO_BIG,   (0.8, 0.3, 0.8), ( 1,-2,0) ))
    pieces.append(lego.piece( (2,7,-2,-5,-2,-1,2,-1),           lego.LEGO_SMALL, (0.9, 0.9, 0.3), ( 0, 0,1) ))
    
    lightp = np.array((2.0, 4.0, -4.0, 1.0))
    
    light_int = 0.5
    light_amb = 1.0 - (1.0 - light_int) ** 2
    
    GL.glLightfv( GL.GL_LIGHT0, GL.GL_AMBIENT, (light_amb * 0.1, light_amb * 0.1, light_amb * 0.1, 1.0) )  # Setup The Ambient Light
    GL.glLightfv( GL.GL_LIGHT0, GL.GL_DIFFUSE, (light_amb, light_amb, light_amb, 1.0) )                    # Setup The Diffuse Light
    GL.glEnable(GL.GL_LIGHT0)                                                                              # Enable Light One
    
    eps = sys.float_info.epsilon
    
    ticker = pygame.time.Clock()
    
    options_on = False
    #controls = dict_union(controls, options)
    
    running = True
    fps = 30
    
    accumulate = False
    mblur_rate = 0.5
    
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
    chosen_index = None
    
    grid_level = 0
    
    dyn_layers = gui.dynamic_layer_manager()
    dyn_layers.add( "grid-level", title.render(str(grid_level),True,text_color), 75, 377, (0,title_scale) )
    
    options_dyn_layers = gui.dynamic_layer_manager()
    options_dyn_layers.add( "mblur-level", title.render(str(mblur_rate),True,text_color), 231, 331, (0,title_scale) )
    options_dyn_layers.add( "light-level", title.render(str(light_int) ,True,text_color), 231, 430, (0,title_scale) )
    
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
            elif event.type == pygame.VIDEORESIZE:
                window_width, window_height = event.size
                pygame.display.set_mode ( (window_width,window_height), pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE, 24 )
                lego.setviewport(event.w, event.h)
                clear_color = GL.glGetFloatv(GL.GL_COLOR_CLEAR_VALUE)
                GL.glClearColor( 0.0, 0.0, 0.0, 0.0 )
                GL.glClear( GL.GL_COLOR_BUFFER_BIT )
                GL.glClearColor( *clear_color )
                ticker.tick(fps/6)
                
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
                            chosen_index = j[2][0]
                    controls["x"].value = str( pieces[chosen_index].position[0] )
                    controls["y"].value = str( pieces[chosen_index].position[1] )
                    controls["z"].value = str( pieces[chosen_index].position[2] )
                    piecesize.set( pieces[chosen_index].size )
                    controls["sides"].value = ''
                    controls["sides"].value = ','.join(str(i) for i in pieces[chosen_index].sides)
                
                GL.glRenderMode( GL.GL_SELECT )
                lego.draw_mode_2d(event.pos)
                GL.glInitNames()
                for i in range( 0, len(controls) ):
                    GL.glPushName( i )
                    controls.values()[i].draw()
                    GL.glPopName()
                hits = GL.glRenderMode( GL.GL_RENDER )
                focused = controls[ controls.keys()[ hits.pop()[2][0] ] ] if hits else None
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
        
        if mblur.value:
            if not accumulate:
                pygame.display.flip()
                GL.glClear( GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT )
            else:
                GL.glAccum( GL.GL_ACCUM, 1.0 - mblur_rate )
                GL.glAccum( GL.GL_RETURN, 1.0 )
                GL.glAccum( GL.GL_MULT, mblur_rate ) 
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
        
        if options_on:
            options_layers.draw( 1 )
        
        for b in controls.values():
            
            decide = b is focused
            b.draw( decide, b in errors )
            if b is focused:
                if key_hit is not None and isinstance(b, gui.textbox):
                    b.append(key_hit)
                elif isinstance(b, gui.toggle):
                    b.value = b.ref
                elif b is controls["raise_grid"]:
                    grid_level += 1
                    dyn_layers.add( "grid-level", title.render(str(grid_level),True,text_color), 75, 377, (0,title_scale) )
                elif b is controls["lower_grid"]:
                    grid_level -= 1
                    dyn_layers.add( "grid-level", title.render(str(grid_level),True,text_color), 75, 377, (0,title_scale) )
                elif b is controls["send"]:
                    errors = set()
                    try:
                        try:
                            dyn_layers.remove("error")
                        except KeyError:
                            pass
                        sides = tuple( int(i) for i in controls["sides"].value.split(',') )
                        lego.piece.is_closed(sides)
                    except lego.LoopError as e:
                        if e.errno == 1001:
                            dyn_layers.add( "error", error.render(po["few"],True,text_color), 180, 5, )
                        elif e.errno == 1002:
                            dyn_layers.add( "error", error.render(po["not_even"],True,text_color), 180, 5 )
                        elif e.errno == 1020:
                            dyn_layers.add( "error", error.render(po["both"],True,text_color), 180, 5 )
                        elif e.errno == 1000:
                            dyn_layers.add( "error", error.render(po["even"],True,text_color), 180, 5 )
                        elif e.errno == 1010:
                            dyn_layers.add( "error", error.render(po["odd"],True,text_color), 180, 5 )
                        errors.add(controls["sides"])
                    except ValueError:
                        errors.add(controls["sides"])
                    try:
                        x = int( float( controls["x"].value ) )
                    except ValueError:
                        errors.add(controls["x"])
                    try:
                        y = int( float( controls["y"].value ) )
                    except ValueError:
                        errors.add(controls["y"])
                    try:
                        z = round( float( controls["z"].value )*3 ) / 3.0
                    except ValueError:
                        errors.add(controls["z"])
                    if piecesize.get() is None:
                        errors.add(controls["big"])
                        errors.add(controls["small"])
                        
                    if not errors:
                        pieces.append( lego.piece(sides, piecesize.value, (0.2, 0.1, 0.8), (x,y,z)) )
                        controls["sides"].value = ''
                        controls["x"].value = '' 
                        controls["y"].value = ''
                        controls["z"].value = ''
                        piecesize.value = None
                elif b is controls["clear"]:
                    controls["sides"].value = ''
                    controls["x"].value = '' 
                    controls["y"].value = ''
                    controls["z"].value = ''
                    piecesize.value = None
                    chosen_index = None
                elif b is controls["del"] and chosen_index is not None:
                    pieces.pop( chosen_index )
                    controls["sides"].value = ''
                    controls["x"].value = '' 
                    controls["y"].value = ''
                    controls["z"].value = ''
                    piecesize.value = None
                    chosen_index = None
                elif b is controls["options"]:
                    if options_on:
                        controls = dict_substract(controls, options)
                    else:
                        controls = dict_union(controls, options)
                    options_on = not options_on
                elif b is controls["raise_mblur"] and mblur_rate < 0.9 - eps:
                    mblur_rate += 0.1
                    options_dyn_layers.add( "mblur-level", title.render(str(mblur_rate),True,text_color), 231, 331, (0,title_scale) )
                elif b is controls["lower_mblur"] and mblur_rate > 0.1 + eps:
                    mblur_rate -= 0.1
                    options_dyn_layers.add( "mblur-level", title.render(str(mblur_rate),True,text_color), 231, 331, (0,title_scale) )
                elif b is controls["lower_light"] and light_int > 0.0:
                    light_int -= 0.1
                    if light_int < eps:
                        light_int = 0.0
                    light_amb = 1.0 - (1.0 - light_int) ** 2
                    GL.glLightfv( GL.GL_LIGHT0, GL.GL_AMBIENT, (light_amb * 0.2, light_amb * 0.2, light_amb * 0.2, 1.0) )  # Setup The Ambient Light
                    GL.glLightfv( GL.GL_LIGHT0, GL.GL_DIFFUSE, (light_amb, light_amb, light_amb, 1.0) )
                    options_dyn_layers.add( "light-level", title.render(str(light_int) ,True,text_color), 231, 430, (0,title_scale) )
                elif b is controls["raise_light"] and light_int < 1.0 - eps:
                    light_int += 0.1
                    light_amb = 1.0 - (1.0 - light_int) ** 2
                    GL.glLightfv( GL.GL_LIGHT0, GL.GL_AMBIENT, (light_amb * 0.2, light_amb * 0.2, light_amb * 0.2, 0.2) )  # Setup The Ambient Light
                    GL.glLightfv( GL.GL_LIGHT0, GL.GL_DIFFUSE, (light_amb, light_amb, light_amb, 1.0) )
                    options_dyn_layers.add( "light-level", title.render(str(light_int) ,True,text_color), 231, 430, (0,title_scale) )
            if decide and not b.keepfocus:
                focused = None
                
        key_hit = None
        
        if options_on:
            options_layers.draw()
            options_dyn_layers.draw()
        
        static_layers.draw()
        dyn_layers.draw()
        
    lego.finish()    
    pygame.quit()
    print "Bye!"


if __name__ == '__main__' : main() 