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


def FRACTALEX(
    ROOT, axiom, extra_rules, rule_1, rule_2, rule_3, rule_4,  
    a, L, scale, radius_scale, 
    min_angle, max_angle, min_len, max_len, 
    iterations, area, prof_x, multi, custom_input, invoked, RandSeed):

    print('FREX ENGINE START')
    random.seed(RandSeed)
    #_______
    #GLOBALS
    index_deepnes = 0 #GLOBAL OVERRIDE FOR BRANCH DEEPNES

    GEO = bpy.context.scene.fractal_extruder_props.GEO
    particle = False#bpy.context.scene.fractal_extruder_props.particle DEPRECATED
    vgroup_size = bpy.context.scene.fractal_extruder_props.vgroup_size

    SKIN = False if GEO == 'wire' else True

    if iterations > bpy.context.scene.fractal_extruder_props.ITERATIONS:
        iterations = bpy.context.scene.fractal_extruder_props.ITERATIONS
    if iterations <= 0:
        iterations = 1

    if bpy.context.mode == 'EDIT_MESH':
        context = 'mesh'
        obj = bpy.context.object
        fob = bpy.context.scene.fractal_extruder_props.F_OBJ
    else:
        context = 'obj'
        fob = bpy.context.object
    
    #_________________________    
    #CUSTOM INPUT -> "g j k w"

    g = custom_input[0]
    j = custom_input[1]
    k = custom_input[2]
    w = custom_input[3]

    fob['FREX_CUSTOM_INPUT'] = [g,j,k,w]

    #____________________
    # OVERWRITE LSYSTEM RULES ON THE FREX OBJECT

    rules = []
    LSD = {}  #Lyndermayer System Data

    LSD['axiom']=axiom

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
    if context == 'mesh': area = math.sqrt( ROOT[2]) /2
    LSD['radius'] = area #math.sqrt( area ) /2
    LSD['radius_scale']=radius_scale
    LSD['min_angle']=min_angle
    LSD['max_angle']=max_angle
    LSD['min_len']=min_len
    LSD['max_len']=max_len
    LSD['iteration']=iterations   

    fob["LSYS_DATA"] = str(LSD)

    #_________________
    #INIT CURVE CURSOR

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

    #____________________
    #INIT PROFILE WIDGET

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

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #GENERATION FUNCTIONS

    def profiler(STRING,iter):
        #h = STRING.count('H')
        #if h > 0:
        val = str( iter_prof[iter]*prof_x )
        STRING = STRING.replace('H','F!'+val+'!')
        if 'h' in STRING:
            STRING = STRING.replace('h',val)
        return STRING


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


    def search_bounds(string,a,b):
        global index_deepnes
        a = string.rfind('{', 0, a+1 )
        b = string.find('}', b+1 )
        if not(a == -1 or b == -1):
            index_deepnes+=1
            search_bounds(string,a,b)


    def grow (axiom,rules,iter):
        global index_deepnes
        overwrite = ''
        for n,i in enumerate(axiom):
            rule = rules.get(i,i)
            
            if i in rules:
                index_deepnes = 0
                if use_profile: rule = profiler(rule,iter)

                if '{' in rule:
                    search_bounds(axiom,n,n)
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

                        if n+L < len(axiom):
                            if axiom[n+L]==']':
                                continue
                
            overwrite += rule

        return overwrite
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    #____________
    #LOAD RULES

    rules_dict={}

    for i in rules:
        i=i.split(':')
        rules_dict[i[0]] = i[1]

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
    
    #____________            
    #GENERATE FRACTAL TREE
    iter = 0
    TREE = axiom

    iters = iterations
    while iters != 0:
        TREE = grow(TREE,rules_dict,iter) 
        iters -=1; iter += 1

    #print (TREE)
    #|  _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _ |#
    #|_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \|#
    ############################################################### BLENDER CONSTRUCTOR   

    bm = bmesh.new()

    if vgroup_size: 
        frex_tag = bm.verts.layers.int.new('FREX_tag')
        frex_ID = bm.verts.layers.int.new('FREX_id')
        frex_DIR = bm.verts.layers.float_vector.new('FREX_DIR')
        frex_edge_order = bm.verts.layers.int.new('FREX_edge_order')

    if multi:
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(False)
        fob.select_set(True)
        bpy.context.view_layer.objects.active=fob
        bpy.ops.object.mode_set(mode='EDIT')    
        bm = bmesh.from_edit_mesh(fob.data)

    turtlePos =  Matrix() #TURTLE INIT
    up_axis = Vector((0,0,1))

    storePos = [] 
    storeLength = []
    storeRadius = []
    storeIndex = []
    store_iters = []

    if context in ('obj','mesh'):
        direction = ROOT[0]
        wpos = ROOT[1]

    r = area
    skin = []

    EDGES = []
    VERTS = []
    baseVerts = []
    baseVert = None
    v_count= 0
    verts_co = set()
    verts_index = {}

    continue_counter = 0
    use_custom_val = False
    use_custom_rand = False
    rotate_by_path = False
    random_invert = False

    if min_len >= L:
        min_len == L

    n=0
    K=1; i=1; h=1
    tree_len = len(TREE)

    iter = 0
    hold_r = None
    LEN = L
    use_invert_scale = False
    
    BRANCH_CLOSED = False
    BRANCH_STARTED = True
    JUST_MOVE = False
    V2 = None

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ GENERATE GEOMETRY  
    for gen,cmd in enumerate(TREE):

        if continue_counter > 0:
            continue_counter-=1
            continue
        
        if cmd == 'h':
            h = iter_prof[i]*prof_x 

        elif cmd == 'K':
            K+=1
            #i = K
            continue

        elif cmd == "ç": 
            use_invert_scale = True
            continue

        #GET (...) CUSTOM VALUE
        elif cmd == 'p':
            #continue_counter  = 1
            rotate_by_path = True
            continue

        elif cmd=='o':
            random_invert = True
            continue

        if gen < tree_len-1 and TREE[gen+1] == "!":
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

        if cmd == 'M':  # JUST MOVE WITHOUT DRAW
            FW = (turtlePos @ ( up_axis  * LEN ))
            FW = (FW[0],FW[1],FW[2])
            turtlePos[0][3]=FW[0]
            turtlePos[1][3]=FW[1]
            turtlePos[2][3]=FW[2]
            JUST_MOVE = True
        #________________________________________________________________________
        #|  _  \ ___ \/ _ \| |  | |
        #| | | | |_/ / /_\ \ |  | |
        #| | | |    /|  _  | |/\| |
        #| |/ /| |\ \| | | \  /\  /
        #|___/ \_| \_\_| |_/\/  \/ 
        #_________________________________________________________________________

        #____ _  _ ____ _  _ ____    _  _ ____ ___  ____ 
        #|    |  | |__/ |  | |___    |\/| |  | |  \ |___ 
        #|___ |__| |  \  \/  |___    |  | |__| |__/ |___    
        elif cmd == 'P':
             #CURSOR CODE
            v1 = turtlePos.decompose()[0]
            if (v1[0],v1[1],v1[2]) == (0,0,0):
                v1 = cursor.evaluate().freeze()
            v1 = (v1[0],v1[1],v1[2])

            ADD_NEW_VERT = False

            if not SKIN and BRANCH_STARTED: 
                ADD_NEW_VERT = True
                BRANCH_STARTED = False

            if SKIN and not v1 in verts_co: 
                ADD_NEW_VERT = True

            if JUST_MOVE:
                ADD_NEW_VERT = True
                JUST_MOVE = False
                
            if ADD_NEW_VERT:

                verts_co.add(v1)
                skin.append(r)
                verts_index[v1] = v_count
                v_count+=1
                V1 = bm.verts.new(v1)
                VERTS.append( V1 )

                if vgroup_size: 
                    store_iters.append(i)
                    if cmd.islower(): V1[frex_tag] = CODEX[cmd]

            else:
                V1 = V2

            cursor.sample += 0.1 * LEN
            v2 = cursor.evaluate().freeze()
            v2 = (v2[0],v2[1],v2[2])

            verts_index[v2] = v_count
            v_count+=1
            
            turtlePos[0][3]=v2[0]
            turtlePos[1][3]=v2[1]
            turtlePos[2][3]=v2[2]

            verts_co.add(v2)
            skin.append(r)

            V2 = bm.verts.new(v2) 
            VERTS.append( V2 )
            EDGES.append( bm.edges.new((V1,V2)) )

            if vgroup_size: 
                store_iters.append(i)
                if cmd.islower(): V2[frex_tag] = CODEX[cmd]
               

        #___  ____ ____ _ _ _    ____ _ _ _ 
        #|  \ |__/ |__| | | |    |___ | | | 
        #|__/ |  \ |  | |_|_|    |    |_|_| 
        elif cmd in GROW_CMDS: #cmd == 'F' or cmd == 'G': # CREATE EDGE

            v1 = turtlePos.decompose()[0]
            v1 = (v1[0],v1[1],v1[2])
                 
            ADD_NEW_VERT = False

            if not SKIN and BRANCH_STARTED: 
                ADD_NEW_VERT = True
                BRANCH_STARTED = False

            if SKIN and not v1 in verts_co: 
                ADD_NEW_VERT = True

            if JUST_MOVE:
                ADD_NEW_VERT = True
                JUST_MOVE = False
               
            if ADD_NEW_VERT:
            
                verts_co.add(v1)
                skin.append(r)
                verts_index[v1] = v_count
                v_count+=1
                V1 = bm.verts.new(v1)
                VERTS.append( V1 )

                if vgroup_size: 
                    store_iters.append(i)
                    if cmd.islower(): V1[frex_tag] = CODEX[cmd]

            else:   
                V1 = V2

            v2 = (turtlePos @ ( up_axis  * LEN ))
            v2 = (v2[0],v2[1],v2[2])

            verts_index[v2] = v_count
            v_count+=1
            
            turtlePos[0][3]=v2[0]
            turtlePos[1][3]=v2[1]
            turtlePos[2][3]=v2[2]

            verts_co.add(v2)
            skin.append(r)
            
            V2 = bm.verts.new(v2)
            VERTS.append( V2 )
            EDGES.append( bm.edges.new((V1,V2)) )

            if vgroup_size: 
                store_iters.append(i)
                if cmd.islower(): V2[frex_tag] = CODEX[cmd]
                if ADD_NEW_VERT:
                    V1[frex_DIR] = V2.co - V1.co
                V2[frex_DIR] = (turtlePos @ ( up_axis  * LEN )) - V2.co
                V2[frex_edge_order] = 1
                           

        elif cmd.isdigit():
            try:
                V2[frex_ID] = int(cmd)
            except:
                pass

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
            n=0
            if V2 != None: 
                baseVerts.append(V2)
            BRANCH_STARTED = True

        elif cmd == ']': #CLOSE TRUNK
            turtlePos = storePos.pop()
            L = storeLength.pop() 
            r = storeRadius.pop() #skin
            n = storeIndex.pop()
            if len(baseVerts)>0: 
                    V2 = baseVerts.pop()
            else:
                V2 = VERTS[0]

        i+=1
    
    mesh = fob.data

    if context == "mesh":
        #bmesh.ops.remove_doubles(bm, verts = VERTS, dist=0.0001)
        if multi:
            bmesh.update_edit_mesh(mesh, True)
            for v in VERTS:
                rot = up_axis.rotation_difference(direction)
                v.co.rotate(rot)
                v.co += wpos

        else:
            bm.to_mesh(mesh)
            bm.free()

            bpy.ops.object.editmode_toggle()#exit from obj
            
            WORLD = obj.matrix_world
            WPOS, WROT, WSCA = WORLD.decompose()

            obj.select_set(False)
            fob.select_set(True)
            bpy.context.view_layer.objects.active = fob 

            bpy.context.object.rotation_mode = 'QUATERNION'
            bpy.context.object.rotation_quaternion = WROT @ direction.to_track_quat('Z','Y')
            bpy.context.object.rotation_mode = 'XYZ'
            bpy.context.object.location = WORLD @ wpos
            bpy.context.object.scale = WSCA

        if SKIN:
            if fob.modifiers: fob.modifiers.clear() #SKIN MODIFIER
            bpy.ops.object.modifier_add(type='SKIN')
            skin_verts=fob.data.skin_vertices[0].data
            for i,v in enumerate (skin_verts):
                v.radius = skin[i],skin[i]

        if not SKIN:
            for m in fob.modifiers:
                if m.type == 'SKIN': fob.modifiers.remove(m)

        if multi:
            bpy.ops.object.mode_set(mode='OBJECT')
            fob.select_set(False)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT') 

        else:
            obj.select_set(True)
            fob.select_set(False)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.editmode_toggle()

    elif context == "obj":
        #bmesh.ops.remove_doubles(bm, verts = VERTS, dist=0.0001)
        bm.to_mesh(mesh)
        bm.free()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()       
        if SKIN:
            #bpy.ops.object.mode_set(mode = 'OBJECT')
            #if fob.modifiers:fob.modifiers.clear() #SKIN MODIFIER
            for m in fob.modifiers:
                if m.type == 'SKIN': fob.modifiers.remove(m)
            bpy.ops.object.modifier_add(type='SKIN')
            bpy.ops.object.modifier_move_to_index(modifier="Skin", index=0)
            skin_verts=fob.data.skin_vertices[0].data
            for i,v in enumerate (skin_verts):
                v.radius = skin[i],skin[i]
        
        if vgroup_size:
            if "FREX_radius" in fob.vertex_groups:
                FREX_radius = fob.vertex_groups.get("FREX_radius")
                fob.vertex_groups.remove(FREX_radius)

            if "FREX_iters" in fob.vertex_groups:
                FREX_iters = fob.vertex_groups.get("FREX_iters")
                fob.vertex_groups.remove(FREX_iters)

            FREX_radius = fob.vertex_groups.new( name = "FREX_radius" )
            FREX_iters = fob.vertex_groups.new( name = "FREX_iters" )

            import numpy as np

            gverts = np.array(skin)
            norm = np.linalg.norm(gverts)
            normal_array = gverts / norm

            gverts = np.array(store_iters)
            norm = max(gverts)
            store_iters = gverts / norm

            for i,v in enumerate (fob.data.vertices):
                FREX_radius.add( [v.index], normal_array[i], 'REPLACE' )
                FREX_iters.add( [v.index], store_iters[i], 'REPLACE' )

        if not SKIN:
            for m in fob.modifiers:
                if m.type == 'SKIN': fob.modifiers.remove(m)
                
    if particle:
        fobP_name = fob.name + "P"

        if not fobP_name in bpy.data.objects:
            mesh = bpy.data.meshes.new("mesh")
            fobP = bpy.data.objects.new("fractal_obj_points", mesh)
            fobP.name = fob.name + "P"
            bpy.context.collection.objects.link(fobP)  
        else:
            fobP = bpy.data.objects[fobP_name]         
        fobP.parent = fob
        bmP.to_mesh(fobP.data)
        bmP.free()
    
    print('FREX ENGINE STOP')
    ######################################################################

def GrowMesh(bm,cen,dir):
    pass

def AlignVerts(bm,verts,pos,dir):
    align_rot = dir.to_track_quat('Z', 'X').to_matrix()
    bmesh.ops.rotate(bm,verts=verts, cent=(0.0, 0.0, 0.0), matrix=align_rot )
    bmesh.ops.translate(bm, verts=verts, vec=pos)

def AddParticleFob():
    mesh = bpy.data.meshes.new("mesh")
    pfob = bpy.data.objects.new(bpy.context.object.name+"Particle", mesh)
    bpy.context.collection.objects.link(pfob)  
    return pfob