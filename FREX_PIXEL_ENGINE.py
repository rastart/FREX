import math
from math import sin
import bpy
import bmesh

from mathutils import Vector, Matrix
import random
from random import randrange, uniform, getrandbits, choice
from . FREX_UTILS import Cursor
from . utils_profile import GetCurveProf, BWProfManager
from . FREX_GLOBALS import CODEX, GROW_CMDS
from . FREX_TEXTURIZER import *


def FRACTALEX(
    ROOT, axiom, extra_rules, rule_1, rule_2, rule_3, rule_4,  
    a, L, scale, radius_scale, 
    min_angle, max_angle, min_len, max_len, 
    iterations, area, prof_x, multi, custom_input, invoked,
    imageName, blur, img_settings, caps, C1,C2,C3,C4,
    resize, OPT, RandSeed ):

    print('FREX ENGINE START')
    random.seed(RandSeed)

    renderSequence = True if 'P' in OPT else False
        
    W, H, img_x, img_y = img_settings
    W = int(W*resize) ; H = int(H*resize)
    img_x = int(img_x*resize); img_y = int(img_y*resize)
    L *= resize; area *= resize
    imageName = bpy.context.scene.fractal_extruder_props.F_TEX.name
    renderPath = bpy.path.abspath(bpy.context.scene.fractal_extruder_props.renderPath)

    #fob = bpy.data.images[imageName]
    fob = bpy.context.object

    if iterations > bpy.context.scene.fractal_extruder_props.ITERATIONS:
        iterations = bpy.context.scene.fractal_extruder_props.ITERATIONS
    if iterations <= 0:
        iterations = 1 

    #CUSTOM INPUT -> "g j k w"
    g = custom_input[0]
    j = custom_input[1]
    k = custom_input[2]
    w = custom_input[3]
    fob['FREX_CUSTOM_INPUT'] = [g,j,k,w]

    ############# USER VALUES ############# LSYSTEM RULES
    rules = []

    LSD = {}  #Lyndermayer System Data
    LSD['image_settings'] = '('+str(W)+','+str(H)+','+str(img_x)+','+str(img_y)+')'    
    LSD['blur'] = blur

    C1,C2,C3,C4 = RemapColor(C1[:]), RemapColor(C2[:]), RemapColor(C3[:]), RemapColor(C4[:])
    col = C1

    LSD['C1'] = str(C1[:]).replace(" ", "")
    LSD['C2'] = str(C2[:]).replace(" ", "") 
    LSD['C3'] = str(C3[:]).replace(" ", "") 
    LSD['C4'] = str(C4[:]).replace(" ", "")  
    LSD['caps']= caps
    
    LSD['axiom']= axiom
    LSD['rule_1'] =rule_1
    rules.append(rule_1)
    if rule_2 != "": 
        LSD['rule_2'] =rule_2
        rules.append(rule_2)
    if rule_3 != "": 
        LSD['rule_3'] =rule_3
        rules.append(rule_3)
    if rule_4 != "": 
        LSD['rule_4'] =rule_4
        rules.append(rule_4)

    if len(extra_rules)>0:
        for i,R in enumerate (extra_rules):
            r_i = 'rule_'+str(i+5)
            LSD['rule_'+str(i+5)] = R
            
        rules+=extra_rules
    
    LSD['angle'] = a
    LSD['length']= L
    LSD['length_scale']=scale
    LSD['radius'] = area #math.sqrt( area ) /2
    LSD['radius_scale']=radius_scale
    LSD['min_angle']=min_angle
    LSD['max_angle']=max_angle
    LSD['min_len']=min_len
    LSD['max_len']=max_len
    LSD['iteration']=iterations   

    fob["LSYS_DATA"] = str(LSD)
    print (str(LSD))
    rules_dict={}

    for i in rules:
        i=i.split(':')
        rules_dict[i[0]] = i[1]

    up_axis = Vector((0,0,1))

    ###############################################CURVE CURSOR
    if len(bpy.context.selected_objects)==2:
        for o in bpy.context.selected_objects:
            if o.type == 'CURVE':
                cursor = Cursor(o)
                #bpy.context.scene.fractal_extruder_props.PATH_OBJ == o
    else:
        if bpy.context.scene.fractal_extruder_props.PATH_OBJ:
            cursor = Cursor(bpy.context.scene.fractal_extruder_props.PATH_OBJ)
        else:
            cursor = None
    ##############################LSYS DICT GENERATOR

    TREE = axiom
    iters = iterations

    def growX (axiom,rules):
        overwrite = ''
        for i in axiom: #rewriting rules
            overwrite += rules.get(i,i)
        return overwrite

    use_profile = False

    for rule in rules:
        if 'h' in rule or 'H' in rule:
            use_profile = True 
            if not invoked:       
                bw_prof_data = BWProfManager()
                bw_prof_data.store_to_obj_data(fob, prof_x)
            iter_prof = GetCurveProf(iterations)
            break
    
    if not use_profile and 'FREX_PROFILE_DATA' in fob:
        del fob['FREX_PROFILE_DATA']
  
    def profiler(STRING,iter):
        #h = STRING.count('H')
        #if h > 0:
        val = str( iter_prof[iter]*prof_x )
        STRING = STRING.replace('H','F!'+val+'!')
        if 'h' in STRING:
            STRING = STRING.replace('h',val)
        return STRING

    #RANDOM GENERATION FUNCTION
    def Stochastiker(STRING,iter,max_iters):
    
        if '=' in STRING:
            a = STRING.find( '%' )
            b = STRING.find( '=', a+1 )
            c = STRING.find( '%', b+1 )
            val = int ( STRING[ a+1 : b ] ) 
            start_string = STRING[:a]
            out_string = STRING[c+1:]

            in_string = STRING[b+1:c]

            if '@' in in_string:
                in_string = in_string.split('@')
                
                if val == iter+1:
                    in_string = in_string[0]
                else:
                    in_string = in_string[1]
            
            elif val != iter+1:
                in_string =''

            return ( start_string + in_string + out_string, val )

        else:
            a = STRING.find( '%' )

            if '<' in STRING:
                b = STRING.find( '<', a+1 )
            elif '>' in STRING:
                b = STRING.find( '>', a+1 )
            else: 
                b = STRING.find( '°', a+1 )

            c = STRING.find( '%', b+1 ) 

            if b == None or b > c:
                val = 50
            else:
                val = int ( STRING[ a+1 : b ] )
                
            start_string = STRING[:a]
            in_string = STRING[b+1:c]
            out_string = STRING[c+1:]

            stop_event = False

            if '@' in in_string:
                in_string = in_string.split('@')

            elif '$' in in_string:
                stop_event = True
                in_string = in_string.split('$')

            dice = randrange(1,100)
            IN=''

            if not type(in_string) is list:
                if dice <= val and '°' in STRING:
                    IN = in_string
                elif '<' in STRING:
                    if val <= iter:
                        IN = in_string
                elif '>' in STRING:
                    if val > iter:
                        IN = in_string
            else:
                if dice <= val and '°' in STRING:
                    IN = in_string[0]

                elif '<' in STRING:
                    if stop_event and max_iters-1 == iter:
                        IN = in_string[1]

                    elif val < iter:
                        IN = in_string[0]

                    elif not stop_event:
                        IN = in_string[1]

                elif '>' in STRING:
                    if stop_event and max_iters-1 == iter:
                        IN = in_string[1]

                    elif val > iter:
                        IN = in_string[0]

                    elif not stop_event:
                        IN = in_string[1]
                else:
                    IN = choice(in_string[1:]) 

            return start_string + IN + out_string

    index_deepnes = 0 #GLOBAL OVERRIDE FOR BRANCH DEEPNES

    def search_bounds(string,a,b):
        global index_deepnes
        a = string.rfind('{', 0, a+1 )
        b = string.find('}', b+1 )
        if not(a == -1 or b == -1):
            index_deepnes+=1
            search_bounds(string,a,b)

    #randrange(1,100)
    def grow (axiom,rules,iter):
        global index_deepnes
        overwrite = ''
        for gen,i in enumerate(axiom):
            rule = rules.get(i,i)
            
            if i in rules:
                index_deepnes = 0
                if use_profile: rule = profiler(rule,iter)

                if '{' in rule:
                    search_bounds(axiom,gen,gen)
                    if rule[1].isnumeric():
                        limit = rule[:2]
                    else:
                        limit = rule[0]

                    rule = rule[1:]

                    if index_deepnes > int(limit): 
                        continue

                if '%' in rule:
                    rule = Stochastiker(rule,iter,iterations)
                    if type(rule) is tuple:
                        L = rule[1]
                        rule = rule[0]

                        if gen+L < len(axiom):
                            if axiom[gen+L]==']':
                                continue
                
            overwrite += rule

        return overwrite

    #@@@@@@@@@@@@@@@@@@@@@ RULES EDITING
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    for KEY,v in rules_dict.items():
        if 'R' in v:
            new_rule = ""
            v = v.split(' ')
            for i in v:
                if 'R' in i:
                    nv = i[1:].split('_') #remove 'R' and split number from string
                    if not 'm' in i: 
                        new_rule += nv[1]*int(nv[0])
                    else:
                        for ii in range( int(nv[0]) ):
                            new_rule += nv[1].replace('m', str(ii) )
                else:
                    new_rule += i
            rules_dict[KEY] = new_rule
    
    #GENERATE FRACTAL TREE
    iter = 0
    #print("_____________________________________________________START")
    while iters != 0:
        TREE = grow(TREE,rules_dict,iter) 
        iters -=1; iter += 1
    #print (TREE)
    #|  _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _ |#
    #|_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \|#
    ############################################################### BLENDER CONSTRUCTOR   
    #TO DO -> SHAPE KEY IMPLEMENTATION 
    #bpy.ops.object.shape_key_add(from_mix=False)

    turtlePos =  Matrix() #TURTLE INIT

    storePos = [] 
    storeLength = []
    
    verts_co = set()
    
    storeRadius = []
    r = area

    skin = []
    storeColor = []

    ########################################
    img = PilBimage(imageName,W,H)

    if imageName in bpy.data.images:
        bimg = bpy.data.images[imageName]
        bimg.scale (W,H)
        img.BIMG = bimg
    
    else:
        img.SetBIMGData()
    
    img.StartDraw()

    v_count= 0
    verts_index = {}

    continue_counter = 0
    use_custom_val = False
    use_custom_rand = False
    rotate_by_path = False
    random_invert = False

    if min_len >= L:
        min_len == L

    n=0
    K=1; i=1
    tree_len = len(TREE)
    storeIndex = []
    store_iters = []

    KEYFRAME = 0
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ GENERATE GEOMETRY
    iter = 0
    hold_r = None
    LEN = L
    h = 1

    for gen,cmd in enumerate(TREE):

        if continue_counter > 0:
            #print('CMD',cmd,'CONTINUE')
            continue_counter-=1
            continue    

        if cmd == 'h':
            h = iter_prof[i]*prof_x 

        elif cmd == 'K':
            K+=1
            continue

        #GET (...) CUSTOM VALUE
        if cmd == 'p':
            #continue_counter  = 1
            rotate_by_path = True
            continue

        elif cmd=='o':
            random_invert = True
            continue

        elif cmd == 'V': #V+,0,0,0,0; or V1
            continue_counter = 1
            V_op = TREE[gen+1]
            #if V_op == '1': col = C1 
            #elif V_op == '2': col = C2 
            #elif V_op == '3': col = C3 
            #elif V_op == '4': col = C4
            
            if V_op in "+-=*n":
                custom_val = TREE[ gen+2 : TREE.find( ';', gen+2 ) ]
                if '*' in custom_val:
                    V_mod = float(custom_val[ custom_val.find( '*')+1 : ])
                    custom_val = custom_val [ : custom_val.find( '*') ]
                else:
                    V_mod = 1

                continue_counter = len(custom_val)+2
                if ',' in custom_val:
                    custom_val = RemapColor( tuple( [ float(c) for c in custom_val.split(',') ] ) )
                elif '1' in custom_val: custom_val = C1
                elif '2' in custom_val: custom_val = C2
                elif '3' in custom_val: custom_val = C3
                elif '4' in custom_val: custom_val = C4

                if V_op == '=': col = custom_val
                elif V_op == '+': col = tuple( [ c1 + c2 for c1,c2 in zip(col, custom_val) ] )
                elif V_op == '-': col = tuple( [ c1 - c2 for c1,c2 in zip(col, custom_val) ] )
                elif V_op == '*': col = tuple( [ int(c1 * c2 * 0.01) for c1,c2 in zip(col, custom_val) ] )
                elif V_op == 'n': col = tuple( [ int((c+0.1) / (n*V_mod+1) ) for c in custom_val ] )

                #print (col,n)
            continue

        elif gen < tree_len-1 and TREE[gen+1] == "!":
            custom_val = TREE[ gen+2 : TREE.find( "!", gen+2 ) ]
            continue_counter = len(custom_val)+2
            use_custom_val = True

        elif gen < tree_len-1 and TREE[gen+1] == "?":
            custom_val = TREE[ gen+2 : TREE.find( "?", gen+2 ) ]
            continue_counter = len(custom_val)+2
            use_custom_rand = True

        elif gen < tree_len-1 and TREE[gen+1] == "$":
            iter = TREE[ gen+2 : TREE.find( "$", gen+2 ) ]
            continue_counter = len(iter)+2
            iter = int(iter)

        #SET ANGLE
        if cmd in '&^+-\/':

            if use_custom_val:
                if custom_val[0] == '*':
                    if  custom_val[1:] in ('gjkw'):
                        A = a * eval(custom_val[1:])
                    else:
                        A = a * float( custom_val[1:] )
                elif custom_val[0] == '#':
                    from math import sin
                    A = eval(custom_val[1:])
                else:
                    A = eval( custom_val ) if custom_val in ('gjkw') else float( custom_val )
                use_custom_val = False

            elif (min_angle != 0 or max_angle != 0) and not use_custom_rand :  #RANDOM ANGLE
                A = uniform( a - min_angle, a + max_angle )
            
            elif use_custom_rand:
                if ';' in custom_val:
                    custom_val1,custom_val2 = custom_val.split(';')
                else:
                    custom_val1,custom_val2 = custom_val.split(',')
                custom_val1 = eval(custom_val1) if custom_val1[-1] in ('gjkw') else float( custom_val1 )
                custom_val2 = eval(custom_val2) if custom_val2[-1] in ('gjkw') else float( custom_val2 )
                
                if ';' in custom_val:
                    A = uniform( float(custom_val1), float(custom_val2) )
                elif ',' in custom_val:
                    A = float(custom_val1) if getrandbits(1) else float(custom_val2)

                use_custom_rand = False

            else:
                A = a

            if random_invert: 
                A = A if getrandbits(1) else -A
                random_invert = False

        #SET LENGTH    
        elif cmd in GROW_CMDS:
            n+=1
            
            if use_custom_val:
                if custom_val[0] == '*':
                    if  custom_val[1:] in ('gjkw'):
                        LEN = L * eval(custom_val[1:])
                    else:
                        LEN = L * float( custom_val[1:] )
                elif custom_val[0] == '#':
                    ra = uniform(0,1)
                    LEN = eval(custom_val[1:])
                else:
                    LEN = eval( custom_val ) if custom_val in ('gjkw') else float( custom_val )
                use_custom_val = False
                    
            elif min_len != 0 or max_len != 0: #RANDOM LENGTH
                LEN = uniform( L - min_len, L + max_len )

            elif use_custom_rand:
                custom_val1,custom_val2 = custom_val.split(';')
                custom_val1 = eval(custom_val1) if custom_val1[-1] in ('gjkw') else float( custom_val1 )
                custom_val2 = eval(custom_val2) if custom_val2[-1] in ('gjkw') else float( custom_val2 )
                LEN = uniform( L - float(custom_val1), L + float(custom_val2) )
                use_custom_rand = False

            else:
                LEN = L

        elif cmd in 'SsTtLl':
            scale_radius = True if cmd not in 'Ll' else False
            scale_len = True if cmd not in 'Ttl' else False
             
            if use_custom_val:
                #hold_r = r
                
                if custom_val[0] == '*':
                    if  custom_val[1:] in ('gjkw'):
                        scale_custom_val = eval(custom_val[1:])
                    else:
                        scale_custom_val = float( custom_val[1:] )
                    if scale_radius: 
                        r = r * scale_custom_val if cmd in 'ST' else r * 1/scale_custom_val
                    if scale_len:
                        L = L * scale_custom_val if cmd in 'SL' else L * 1/scale_custom_val
                
                elif custom_val[0] == '#':
                    if scale_radius: r = eval(custom_val[1:])
                    if scale_len: L = eval(custom_val[1:])
                
                else:
                    scale_custom_val = eval(custom_val) if custom_val in ('gjkw') else float( custom_val )
                    if scale_radius: r = scale_custom_val if cmd in 'ST' else r * 1/scale_custom_val
                    if scale_len: L = scale_custom_val if cmd in 'SL' else 1/scale_custom_val

                use_custom_val = False
                

            elif use_custom_rand:
                custom_val1, custom_val2 = custom_val.split(';')
                custom_val1 = eval(custom_val1) if custom_val1[-1] in ('gjkw') else float( custom_val1 )
                custom_val2 = eval(custom_val2) if custom_val2[-1] in ('gjkw') else float( custom_val2 )

                if scale_radius:
                    r = uniform( float(custom_val1), float(custom_val2) )
                if scale_len:
                    L = uniform( float(custom_val1), float(custom_val2) )
                use_custom_rand = False

            elif cmd in 'STL': #PROGRESSIVE SCALE ALONG 'S' INSTRUCTION
                if scale_len: L = L * scale
                if scale_radius: r *= radius_scale #skin
                    
            elif cmd in 'stl': #PROGRESSIVE SCALE ALONG 'S' INSTRUCTION
                if scale_len: L = L * 1/scale
                if scale_radius: r *= 1/radius_scale #skin

        if cmd == 'M': # JUST MOVE WITHOUT DRAW
            FW = (turtlePos @ ( up_axis  * LEN ))
            FW = (FW[0],FW[1],FW[2])
            turtlePos[0][3]=FW[0]
            turtlePos[1][3]=FW[1]
            turtlePos[2][3]=FW[2]

        #________________________________________________________________________
        #|  _  \ ___ \/ _ \| |  | |
        #| | | | |_/ / /_\ \ |  | |
        #| | | |    /|  _  | |/\| |
        #| |/ /| |\ \| | | \  /\  /
        #|___/ \_| \_\_| |_/\/  \/ 
        #_________________________________________________________________________

        elif cmd == 'P':
            SK = 50
             #CURSOR CODE
            v1 = turtlePos.decompose()[0]
            if (v1[0],v1[1],v1[2]) == (0,0,0):
                v1 = cursor.evaluate().freeze()
            v1 = (v1[0],v1[1],v1[2])

            verts_co.add(v1)
            verts_index[v1] = v_count
            v_count+=1

            cursor.sample += 0.1 * LEN
            v2 = cursor.evaluate().freeze()
            v2 = (v2[0],v2[1],v2[2])

            verts_index[v2] = v_count
            v_count+=1
            
            turtlePos[0][3]=v2[0]
            turtlePos[1][3]=v2[1]
            turtlePos[2][3]=v2[2]

            verts_co.add(v2)

            A=(v1[0]+img_x,-v1[2]+img_y); B=(v2[0]+img_x,-v2[2]+img_y)

            img.DrawLine(A,B, fill = col, width=int(r), caps = caps )

        elif cmd in GROW_CMDS: #cmd == 'F' or cmd == 'G': # CREATE EDGE

            v1 = turtlePos.decompose()[0]
            v1 = (v1[0],v1[1],v1[2])

            verts_co.add(v1)
            verts_index[v1] = v_count
            v_count+=1

            v2 = (turtlePos @ ( up_axis  * LEN ))
            v2 = (v2[0],v2[1],v2[2])

            verts_index[v2] = v_count
            v_count+=1
            
            turtlePos[0][3]=v2[0]
            turtlePos[1][3]=v2[1]
            turtlePos[2][3]=v2[2]

            verts_co.add(v2)

            A=(v1[0]+img_x,-v1[2]+img_y); B=(v2[0]+img_x,-v2[2]+img_y)

            img.DrawLine(A,B, fill = col, width=int(r), caps = caps )
         
        if rotate_by_path:
            if cmd in '&^':#
                turtlePos = turtlePos @ Matrix.Rotation(math.radians(A if cmd == '&' else -A ), 4, cursor.get_axis('X') )    
            elif cmd in '+-':#
                turtlePos = turtlePos @ Matrix.Rotation(math.radians(A if cmd == '+' else -A ), 4, cursor.get_axis('Y') )
            elif cmd in '\/':#
                turtlePos = turtlePos @ Matrix.Rotation(math.radians(A if cmd == '\\' else -A ), 4, cursor.get_axis('Z') )
            rotate_by_path = False

        elif cmd in '&^':#
            turtlePos = turtlePos @ Matrix.Rotation(math.radians(A if cmd == '&' else -A ), 4, 'X')
                                                        
        elif cmd in '+-':#
            turtlePos = turtlePos @ Matrix.Rotation(math.radians(A if cmd == '+' else -A), 4, 'Y')
        
        elif cmd in '|':#
            turtlePos = turtlePos @ Matrix.Rotation(math.radians(180.0), 4, 'Y')
        
        elif cmd in '\/':#
            turtlePos = turtlePos @ Matrix.Rotation(math.radians(A if cmd == '\\' else -A), 4, 'Z')
        #________________________________________________________________________________________________BRANCHING LOGIK
        elif cmd == '[': # START TRUNK
            storePos.append(turtlePos.copy())
            storeLength.append(L)
            storeRadius.append(r) #skin
            storeIndex.append(n)
            storeColor.append(col)
            n=0
 
        elif cmd == ']': #CLOSE TRUNK
            turtlePos = storePos.pop()
            L = storeLength.pop() 
            r= storeRadius.pop() #skin
            n = storeIndex.pop()
            col = storeColor.pop()

        if cmd in GROW_CMDS and hold_r != None: 
            r = hold_r
            hold_r = None

        i+=1
        if renderSequence and cmd in GROW_CMDS:
            img.PIL_IMG.save( renderPath + str(KEYFRAME) + ".png" )
            KEYFRAME += 1

    if True:
        if blur > 0:
            img.Blur(blur)

        img.PilImgToGrid()
        img.WriteToBIMG()

        imgEditor = ImageEditor()
        imgEditor.LoadImage(imageName)

        #for area in bpy.context.screen.areas:
            #if area.type == 'IMAGE_EDITOR':
                #area.spaces.active.image = bpy.data.images[img.name]

    if ROOT>0:
        img.PIL_IMG.save( renderPath + str(ROOT) + ".png" )

    print('FREX ENGINE STOP')
    ######################################################################