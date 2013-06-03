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
    import OpenGL.GLU as GLU 
     
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

def collide(p1, p2):
    if isinstance(p1, lego.piece) and isinstance(p2, lego.piece):
        if p1 is p2:
            return False
        if not ( p1.left   + p1.position[0] >= p2.right                  + p2.position[0] or p1.right                  + p1.position[0] <= p2.left   + p2.position[0] ) and \
           not (             p1.position[1] >= (1 if p2.size else 1.0/3) + p2.position[1] or (1 if p1.size else 1.0/3) + p1.position[1] <= p2.position[1] )             and \
           not ( p1.bottom + p1.position[2] >= p2.top                    + p2.position[2] or p1.top                    + p1.position[2] <= p2.bottom + p2.position[2] )     :
            d = np.array(( p2.position[0], p2.position[2] )) - np.array(( p1.position[0], p1.position[2] ))
            hit = False
            for s in p1.coords:
                hit |= p2.is_hit(s - d)
                if hit:
                    return True
            for s in p2.coords:
                hit |= p1.is_hit(s + d)
                if hit:
                    return True
            return False
        else:
            return False
            
         

def main():
    window_width = 800
    window_height = 600
    
    print "Loading locale ...",
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
    
    print "Loading pygame ..." ,
    pygame.display.init()
    pygame.font.init()
    print "Done"
    
    print "Loading screen ...",
    pygame.display.set_mode ( (window_width,window_height), pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE, 24 )
    print "Done"
    
    print "Loading opengl ...",
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
    
    menu = reference()
    
    static = dict()
    static["options"] = gui.toggle(  10,10, 145, 37, button_color, button_focus_color, button_error_color, 2, menu )
    static["edit"]    = gui.toggle( 165,10, 145, 37, button_color, button_focus_color, button_error_color, 1, menu )
    
    static_layers = gui.layer_manager()
    static_layers.add( small.render(po["options"], True,text_color), 25, 17, (0,3) )
    static_layers.add( small.render("Edit", True,text_color), 180, 17, (0,3) )
    static_layers.load()
    
    
    edit = dict()
    edit["x"]          = gui.textbox(  11,107,  42, 32, button_color, button_focus_color, button_error_color, bold_small, text_color, text_error_color, (0,4) ) 
    edit["y"]          = gui.textbox( 113,105,  42, 32, button_color, button_focus_color, button_error_color, bold_small, text_color, text_error_color, (0,4) ) 
    edit["z"]          = gui.textbox(  62,107,  42, 32, button_color, button_focus_color, button_error_color, bold_small, text_color, text_error_color, (0,4) ) 
    edit["big"]        = gui.toggle (  33,207,  32, 32, button_color, button_focus_color, button_error_color, lego.LEGO_BIG,   piecesize ) 
    edit["small"]      = gui.toggle ( 101,207,  32, 32, button_color, button_focus_color, button_error_color, lego.LEGO_SMALL, piecesize ) 
    edit["sides"]      = gui.textbox(  11,277, 145,100, button_color, button_focus_color, button_error_color, bold_small, text_color, text_error_color ) 
    edit["grid"]       = gui.toggle ( 123,391,  32, 32, button_color, button_focus_color, button_error_color, True, grid ) 
    edit["raise_grid"] = gui.arrow  (  17,437,  32, 32, button_color, button_focus_color, button_error_color ) 
    edit["lower_grid"] = gui.arrow  ( 117,437,  32, 32, button_color, button_focus_color, button_error_color, False ) 
    edit["send"]       = gui.button (  11,487, 145, 37, button_color, button_focus_color, button_error_color )
    edit["del"]        = gui.button (  11,536,  70, 37, button_color, button_focus_color, button_error_color )
    edit["clear"]      = gui.button (  86,536,  70, 37, button_color, button_focus_color, button_error_color )
    
    edit_layers = gui.layer_manager()
    
    edit_layers.add( pygame.image.load(os.path.join('data','ui.png')), 0, 57, (0,0) )
    
    edit_layers.add( title.render(po["position"],True,text_color),  20,  67, (0,title_scale) )
    edit_layers.add( title.render(po["height"],  True,text_color),  20, 139, (0,title_scale) )
    edit_layers.add( title.render(po["big"],     True,text_color),  20, 179, (0,sub_scale)   )
    edit_layers.add( title.render(po["small"],   True,text_color),  85, 179, (0,sub_scale)   )
    edit_layers.add( title.render(po["sides"],   True,text_color),  20, 239, (0,title_scale) )
    edit_layers.add( title.render(po["grid"],    True,text_color),  20, 387, (0,title_scale) )
    edit_layers.add( title.render("OK",          True,text_color),  67, 494, (0,sub_scale) )
    edit_layers.add( small.render(po["del"],     True,text_color),  20, 545, (0,3) )
    edit_layers.add( small.render(po["clear"],   True,text_color),  95, 545, (0,3) )
    edit_layers.load()
    
    options = dict()
    options["mblur"]       = gui.toggle( 67,355, 32, 32, button_color, button_focus_color, button_error_color, True, mblur )
    options["raise_mblur"] = gui.arrow ( 17,388, 32, 32, button_color, button_focus_color, button_error_color ) 
    options["lower_mblur"] = gui.arrow ( 117,388, 32, 32, button_color, button_focus_color, button_error_color, False )
    options["raise_light"] = gui.arrow ( 17,487, 32, 32, button_color, button_focus_color, button_error_color ) 
    options["lower_light"] = gui.arrow ( 117,487, 32, 32, button_color, button_focus_color, button_error_color, False )
    
    options_layers = gui.layer_manager()
    
    options_layers.add( edit_layers.layer_list[0][0], 0, 57, (0,0) )
    
    options_layers.add( title.render(po["motion_blur"],True,text_color),  8,301, (0,title_scale) )
    options_layers.add( title.render(po["light"],      True,text_color),  8,434, (0,title_scale) )
    
    options_layers.add( small.render(' '.join(( po["forward"], ":" )), True,text_color),  10, 65, (0,3) )
    options_layers.add( small.render(' '.join(( po["back"], ":" )),    True,text_color),  10, 98, (0,3) )
    options_layers.add( small.render(' '.join(( po["left"], ":" )),    True,text_color),  10,131, (0,3) )
    options_layers.add( small.render(' '.join(( po["right"], ":" )),   True,text_color),  10,164, (0,3) )
    options_layers.add( small.render(' '.join(( po["up"], ":" )),      True,text_color),  10,197, (0,3) )
    options_layers.add( small.render(' '.join(( po["down"], ":" )),    True,text_color),  10,230, (0,3) )
    options_layers.add( small.render(' '.join(( po["exit"], ":" )),    True,text_color),  10,263, (0,3) )
    
    options_layers.add( small.render('W',    True,text_color),  100, 65, (0,3) )
    options_layers.add( small.render('S',    True,text_color),  100, 98, (0,3) )
    options_layers.add( small.render('A',    True,text_color),  100,131, (0,3) )
    options_layers.add( small.render('D',    True,text_color),  100,164, (0,3) )
    options_layers.add( small.render('Space',True,text_color),  100,197, (0,3) )
    options_layers.add( small.render('Ctrl', True,text_color),  100,230, (0,3) )
    options_layers.add( small.render('Esc',  True,text_color),  100,263, (0,3) )
    
    options_layers.load()
    
    controls = static.copy()
    menus = { 1 : edit, 2: options }
    
    print "Done"
    
    print "\nEntering drawing loop\n"
    pieces = list()
    pieces.append(lego.piece( (4,2,-2,2,-1,1,-2,-1,-1,-2,2,-2), lego.LEGO_BIG,   (1.0, 0.1, 0.2), (-6, 0,    -6) ))
    pieces.append(lego.piece( (1,-1,1,1,1,-1,1,4,-3,-1,-1,-2),  lego.LEGO_SMALL, (0.2, 0.8, 0.3), (-8, 2.0/3, 2) ))
    pieces.append(lego.piece( (2,2,1,1,-1,2,-2,-5),             lego.LEGO_SMALL, (0.2, 0.3, 0.8), ( 5, 1.0/3, 1) ))
    pieces.append(lego.piece( (5,6,-5,-1,-1,-4,1,-1),           lego.LEGO_BIG,   (0.8, 0.3, 0.8), ( 1, 0    ,-2) ))
    pieces.append(lego.piece( (2,7,-2,-5,-2,-1,2,-1),           lego.LEGO_SMALL, (0.9, 0.9, 0.3), ( 0, 1,     0) ))
    
    lightp = np.array((2.0, 4.0, -4.0, 1.0))
    
    light_int = 0.5
    light_amb = 1.0 - (1.0 - light_int) ** 2
    
    GL.glLightfv( GL.GL_LIGHT0, GL.GL_AMBIENT, (light_amb * 0.1, light_amb * 0.1, light_amb * 0.1, 1.0) )  # Setup The Ambient Light
    GL.glLightfv( GL.GL_LIGHT0, GL.GL_DIFFUSE, (light_amb, light_amb, light_amb, 1.0) )                    # Setup The Diffuse Light
    GL.glEnable(GL.GL_LIGHT0)                                                                              # Enable Light One
    
    eps = sys.float_info.epsilon
    
    ticker = pygame.time.Clock()
    
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
    mouse_down = None
    drag_from = None 
    key_hit = None
    
    errors = set()
    chosen_index = None
    
    grid_level = 0
    
    edit_dyn_layers = gui.dynamic_layer_manager()
    edit_dyn_layers.add( "grid-level", title.render(str(grid_level),True,text_color), 75, 437, (0,title_scale) )
    
    options_dyn_layers = gui.dynamic_layer_manager()
    options_dyn_layers.add( "mblur-level", title.render(str(mblur_rate),True,text_color), 61, 388, (0,title_scale) )
    options_dyn_layers.add( "light-level", title.render(str(light_int) ,True,text_color), 61, 487, (0,title_scale) )
    
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
                mouse_down = event.pos
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
                    start_position = pieces[chosen_index].position
                    if menu.get() == 1:
                        edit["x"].value = format( pieces[chosen_index].position[0], 'g' )
                        edit["y"].value = format( pieces[chosen_index].position[1], 'g')
                        edit["z"].value = format( pieces[chosen_index].position[2], 'g')
                        piecesize.set( pieces[chosen_index].size )
                        edit["sides"].value = ''
                        edit["sides"].value = ','.join(str(i) for i in pieces[chosen_index].sides)
                    
                GL.glRenderMode( GL.GL_SELECT )
                lego.draw_mode_2d(event.pos)
                GL.glInitNames()
                for i in range( 0, len(controls) ):
                    GL.glPushName( i )
                    controls.values()[i].draw()
                    GL.glPopName()
                hits = GL.glRenderMode( GL.GL_RENDER )
                focused = controls.values()[ hits.pop()[2][0] ] if hits else None
                
            elif mouse_down and event.type == pygame.MOUSEMOTION:
                if chosen_index is None or drag_from is None:
                    rotx += float(event.rel[0]) / window_width  * mouse_sens
                    roty += float(event.rel[1]) / window_height * mouse_sens
                else:
                    x,y = event.pos
                    y = window_height - y
                    lego.draw_mode_3d()
                    GL.glMultMatrixf( rot )
                    GL.glMultMatrixf( np.eye(4) + np.vstack(( np.zeros((3,4)), position )) )
                    far = np.array(GLU.gluUnProject( x, y, 1, GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX), GL.glGetDoublev(GL.GL_PROJECTION_MATRIX), GL.glGetIntegerv(GL.GL_VIEWPORT) )) 
                    near =  np.array(GLU.gluUnProject( x, y, 0, GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX), GL.glGetDoublev(GL.GL_PROJECTION_MATRIX), GL.glGetIntegerv(GL.GL_VIEWPORT) ))
                    
                    drag = (drag_from - ( (drag_from[1]-near[1]) / (far[1]-near[1]) ) * (far-near) - near) / -lego.LEGO_GRID
                    
                    prev_position = pieces[chosen_index].position
                    pieces[chosen_index].position = start_position + drag.round()
                    
                    for i,p in enumerate(pieces):
                        collision = collide( p, pieces[chosen_index] )
                        if collision:
                            break
                    if collision:
                        pieces[chosen_index].position = prev_position
                    
                    
                    
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = None 
                drag_from = None
                if menu.get() != 1:
                    chosen_index = None
                    
        if not np.array_equal( move, np.zeros(4) ):
            move = move_speed * move / np.linalg.norm(move)
        position += np.dot( rot, move )
        
        # draw 3D stuff
        lego.draw_mode_3d()
        
        GL.glMultMatrixf( rot )
        GL.glMultMatrixf( np.eye(4) + np.vstack(( np.zeros((3,4)), position )) )
        
        if mblur.value:
            if not accumulate:
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
            GL.glClear( GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT )
            ticker.tick( fps )
            if rotating:
                rotrot = (rotrot + rot_speed) % 360
                GL.glRotatef( rotrot, 0.0, 1.0, 0.0 )
        
        GL.glLightfv( GL.GL_LIGHT0, GL.GL_POSITION, lightp )
        
        if edit["grid"].value:
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
        
        if mouse_down and chosen_index is not None and drag_from is None:
            x,y = mouse_down
            y = window_height - y
            z = GL.glReadPixels(x,y,1,1,GL.GL_DEPTH_COMPONENT,GL.GL_FLOAT) 
            drag_from = np.array(GLU.gluUnProject( x, y, z, GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX), GL.glGetDoublev(GL.GL_PROJECTION_MATRIX), GL.glGetIntegerv(GL.GL_VIEWPORT) ))
        
        # draw 2D stuff
        lego.draw_mode_2d()
        
        if menu.get() == 1:
            edit_layers.draw( 1 )
        elif menu.get() == 2:
            options_layers.draw( 1 )
        
        for b in controls.values():
            
            decide = b is focused
            b.draw( decide, b in errors )
            
            if decide:
                
                if b is static["options"] or b is static["edit"]:
                    if b.value is None:
                        controls = dict_union(controls, menus[b.ref])
                        b.value = b.ref
                    elif b.value == b.ref:
                        b.value = None
                        controls = dict_substract(controls, menus[b.ref])
                    else:
                        controls = dict_substract(controls, menus[b.value])
                        b.value = b.ref
                        controls = dict_union(controls, menus[b.ref])
                elif isinstance(b, gui.toggle):
                    b.value = b.ref
                elif key_hit is not None and isinstance(b, gui.textbox):
                    b.append(key_hit)
                
                if b is edit["raise_grid"]:
                    grid_level += 1
                    edit_dyn_layers.add( "grid-level", title.render(str(grid_level),True,text_color), edit_dyn_layers.layer_list["grid-level"][1], edit_dyn_layers.layer_list["grid-level"][2], (0,title_scale) )
                elif b is edit["lower_grid"]:
                    grid_level -= 1
                    edit_dyn_layers.add( "grid-level", title.render(str(grid_level),True,text_color), edit_dyn_layers.layer_list["grid-level"][1], edit_dyn_layers.layer_list["grid-level"][2], (0,title_scale) )
                elif b is edit["send"]:
                    errors = set()
                    try:
                        try:
                            edit_dyn_layers.remove("error")
                        except KeyError:
                            pass
                        sides = tuple( int(i) for i in edit["sides"].value.split(',') )
                        lego.piece.is_closed(sides)
                    except lego.LoopError as e:
                        if e.errno == 1001:
                            edit_dyn_layers.add( "error", error.render(po["few"],True,text_color), 180, 5, )
                        elif e.errno == 1002:
                            edit_dyn_layers.add( "error", error.render(po["not_even"],True,text_color), 180, 5 )
                        elif e.errno == 1020:
                            edit_dyn_layers.add( "error", error.render(po["both"],True,text_color), 180, 5 )
                        elif e.errno == 1000:
                            edit_dyn_layers.add( "error", error.render(po["even"],True,text_color), 180, 5 )
                        elif e.errno == 1010:
                            edit_dyn_layers.add( "error", error.render(po["odd"],True,text_color), 180, 5 )
                        errors.add(edit["sides"])
                    except ValueError:
                        errors.add(edit["sides"])
                    try:
                        x = float( edit["x"].value )
                    except ValueError:
                        errors.add(edit["x"])
                    try:
                        y = round( float( edit["y"].value )*3 ) / 3.0
                    except ValueError:
                        errors.add(edit["y"])
                    try:
                        z = float( edit["y"].value )
                    except ValueError:
                        errors.add(edit["z"])
                    if piecesize.get() is None:
                        errors.add(edit["big"])
                        errors.add(edit["small"])
                        
                    if not errors:
                        pieces.append( lego.piece(sides, piecesize.value, (0.2, 0.1, 0.8), (x,y,z)) )
                        edit["sides"].value = ''
                        edit["x"].value = '' 
                        edit["y"].value = ''
                        edit["z"].value = ''
                        piecesize.value = None
                elif b is edit["clear"] or menu.get() != 1:
                    edit["sides"].value = ''
                    edit["x"].value = '' 
                    edit["y"].value = ''
                    edit["z"].value = ''
                    piecesize.value = None
                    chosen_index = None
                elif b is edit["del"] and chosen_index is not None:
                    pieces.pop( chosen_index )
                    edit["sides"].value = ''
                    edit["x"].value = '' 
                    edit["y"].value = ''
                    edit["z"].value = ''
                    piecesize.value = None
                    chosen_index = None
            
                if b is options["raise_mblur"] and mblur_rate < 0.9 - eps:
                    mblur_rate += 0.1
                    options_dyn_layers.add( "mblur-level", title.render(str(mblur_rate),True,text_color), options_dyn_layers.layer_list["mblur-level"][1], options_dyn_layers.layer_list["mblur-level"][2], (0,title_scale) )
                elif b is options["lower_mblur"] and mblur_rate > 0.1 + eps:
                    mblur_rate -= 0.1
                    options_dyn_layers.add( "mblur-level", title.render(str(mblur_rate),True,text_color), options_dyn_layers.layer_list["mblur-level"][1], options_dyn_layers.layer_list["mblur-level"][2], (0,title_scale) )
                elif b is options["lower_light"] and light_int > 0.0:
                    light_int -= 0.1
                    if light_int < eps:
                        light_int = 0.0
                    light_amb = 1.0 - (1.0 - light_int) ** 2
                    GL.glLightfv( GL.GL_LIGHT0, GL.GL_AMBIENT, (light_amb * 0.2, light_amb * 0.2, light_amb * 0.2, 1.0) )  # Setup The Ambient Light
                    GL.glLightfv( GL.GL_LIGHT0, GL.GL_DIFFUSE, (light_amb, light_amb, light_amb, 1.0) )
                    options_dyn_layers.add( "light-level", title.render(str(light_int) ,True,text_color), options_dyn_layers.layer_list["light-level"][1], options_dyn_layers.layer_list["light-level"][2], (0,title_scale) )
                elif b is options["raise_light"] and light_int < 1.0 - eps:
                    light_int += 0.1
                    light_amb = 1.0 - (1.0 - light_int) ** 2
                    GL.glLightfv( GL.GL_LIGHT0, GL.GL_AMBIENT, (light_amb * 0.2, light_amb * 0.2, light_amb * 0.2, 0.2) )  # Setup The Ambient Light
                    GL.glLightfv( GL.GL_LIGHT0, GL.GL_DIFFUSE, (light_amb, light_amb, light_amb, 1.0) )
                    options_dyn_layers.add( "light-level", title.render(str(light_int) ,True,text_color), options_dyn_layers.layer_list["light-level"][1], options_dyn_layers.layer_list["light-level"][2], (0,title_scale) )
                        
            if decide and not b.keepfocus:
                focused = None
                
        key_hit = None
        
        static_layers.draw()
        
        if menu.get() == 1:
            edit_layers.draw()
            edit_dyn_layers.draw()
        elif menu.get() == 2:
            options_layers.draw()
            options_dyn_layers.draw()
        
        pygame.display.flip()
            
            
    lego.finish()    
    pygame.quit()
    print "Bye!"


if __name__ == '__main__' : main() 