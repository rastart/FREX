"""

in axiom s 
in rules s 
in angle s d=30.0 n=2
in length s d=1.0 n=2   
in scale s d=0.8 n=2
in radius s d=1.0 n=2  
in radius_scale s d=1.0 n=2   
in min_angle s d=0 n=2
in max_angle s d=0 n=2  
in min_len s d=0 n=2  
in max_len s d=0 n=2   
in iters s d=3 n=2
in max_iters s d=5 n=2
in iter_profile s
in curve_obj o
in g_j_k_w s

out verts    v
out edges    s
out edge_radius s
out edge_order s
out points_co  v
out point_radius s
out points_tag s
out points_id s
out points_dir  v

"""

import math
import bpy

from mathutils import Vector, Matrix
from random import randrange, uniform, choice, getrandbits


class Cursor(): #FOLLOW CURVE MODE
    
    def __init__(self,curve):
        
        self.points = curve.data.splines[0].points
        self.sample = 0.0

        if not "SV_LSYS_CURSOR_CTRL" in bpy.data.objects:
            self.cursor = bpy.data.objects.new("SV_LSYS_CURSOR_CTRL",None)
            bpy.context.collection.objects.link(self.cursor)
        else:
            self.cursor = bpy.data.objects["SV_LSYS_CURSOR_CTRL"]
            
        self.cursor.location = (0,0,0) #points[0].co[0:3]
        self.cursor.empty_display_type = 'ARROWS'
        for constraint in self.cursor.constraints:
            self.cursor.constraints.remove(constraint)

        self.f_mod = self.cursor.constraints.new(type='FOLLOW_PATH')
        self.f_mod.target = curve
        self.f_mod.use_fixed_location = True
        self.f_mod.use_curve_follow = True
        self.f_mod.use_curve_radius = True
        self.f_mod.forward_axis = 'FORWARD_Z'
        self.f_mod.up_axis = 'UP_X'
        self.f_mod.offset_factor = 0
        

    def evaluate(self):
        self.f_mod.offset_factor = self.sample
        bpy.context.view_layer.update()
        return self.cursor.matrix_world.translation.copy()

    def get_axis(self,axis):
        bpy.context.view_layer.update()
        m = self.cursor.matrix_world
        if axis == 'X':
            axis = Vector((m[0][0],m[1][0],m[2][0]))
        elif axis == 'Y':
            axis = Vector((m[0][1],m[1][1],m[2][1]))
        elif axis == 'Z':
            axis = Vector((m[0][2],m[1][2],m[2][2]))
            
        return axis

    def remove(self):
        
        bpy.data.objects.remove( self.cursor , do_unlink=True) 


def FRACTALEX(
    axiom, rules,  
    a, L, scale, radius, radius_scale, 
    min_angle, max_angle, min_len, max_len, 
    iters, max_iters, custom_input ):

    ############################################# GLOBALS
    GROW_CMDS = 'abcdeFGPM'
    CODEX= {
        'a':1,
        'b':2,
        'c':3,
        'd':4,
        'e':5,    
        }

    ############################################# SETTINGS
    if custom_input != None:
        custom_input = custom_input[0]

    g,j,k,w = 0,0,0,0

    if custom_input != None:
        if len(custom_input)>0:
            g = custom_input[0]

        if len(custom_input)>1:
            j = custom_input[1]

        if len(custom_input)>2:
            k = custom_input[2]

        if len(custom_input)>3:
           w = custom_input[3]
    
    iters = int(iters)

    try:
        if iters > max_iters:
            iters = max_iters
        elif iters <= 0:
            iters = 1
    except:
        iters = 1

    if not axiom: 
        axiom = 'FA'
    else:
        axiom = axiom[0][0]
        
    if not rules: 
        rules = ['A:[&FSA]////[&FSA]////[&FSA]']
    else:
        rules = rules[0]#[0]


    ############################################### CURVE CURSOR
    
    if curve_obj != None:
            cursor = Cursor(curve_obj[0])
    else:
         cursor = None

    ####################################GROW PROFILER
    use_profile = False

    for rule in rules:
        if 'H' in rule:
            use_profile = True
            break

    def profiler(STRING,iter):
        val = str( iter_profile[0][iter])#*prof_x )
        STRING = STRING.replace('H','F!'+val+'!')
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

    
    def grow (axiom,rules,iter):
        global index_deepnes
        overwrite = ''
        for n,i in enumerate(axiom):
            rule = rules.get(i,i)
            
            if i in rules:
                index_deepnes = 0
                if iter_profile != None:
                    rule = profiler(rule,iter)

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
                    rule = Stochastiker(rule,iter,iters)
                    if type(rule) is tuple:
                        L = rule[1]
                        rule = rule[0]

                        if n+L < len(axiom):
                            if axiom[n+L]==']':
                                continue
                
            overwrite += rule

        return overwrite 


    #@@@@@@@@@@@@@@@@@@@@@ RULES EDITING
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    
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

    
    #GENERATE FRACTAL TREE

    iter = 0
    TREE = axiom

    while iters != 0:
        TREE = grow(TREE,rules_dict,iter) 
        iters -=1; iter += 1
    
    #|  _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _   _ |#
    #|_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \|#
    ############################################################### SV CONSTRUCTOR

    bm = set()
    point_tag = [] #bm.verts.layers.int.new('FREX_tag')
    point_ID = [] #bm.verts.layers.int.new('FREX_id')
    point_dir = [] #bm.verts.layers.float_vector.new('FREX_DIR')
    edge_order = [] #bm.verts.layers.int.new('FREX_edge_order')
    point_radius = []
    edge_radius = []

    turtlePos =  Matrix() #TURTLE INIT
    up_axis = Vector((0,0,1))

    storePos = [] 
    storeLength = []
    storeRadius = []
    storeIndex = []
    store_iters = []

    r = radius

    EDGES = []
    VERTS = []
    baseVerts = []
    baseVert = None
    baseIndex = []
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
    storeVcount = []
    V1_index = None
    V2_index = None
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ GENERATE GEOMETRY   
    for gen,cmd in enumerate(TREE):

        if continue_counter > 0:
            continue_counter-=1
            continue

        elif cmd == 'K':
            K+=1
            continue

        elif cmd == "ç": 
            use_invert_scale = True
            continue

        #GET (...) CUSTOM VALUE
        elif cmd == 'p':
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
                if scale_radius: r *= radius_scale #point_radius
                    
            elif cmd in 'stl': #PROGRESSIVE SCALE ALONG 'S' INSTRUCTION
                if scale_len: L = L * 1/scale
                if scale_radius: r *= 1/radius_scale #point_radius


        #________________________________________________________________________
        #|  _  \ ___ \/ _ \| |  | |
        #| | | | |_/ / /_\ \ |  | |
        #| | | |    /|  _  | |/\| |
        #| |/ /| |\ \| | | \  /\  /
        #|___/ \_| \_\_| |_/\/  \/ 
        #_________________________________________________________________________

        if cmd == 'P':
             #CURSOR CODE

            edge_radius.append(r)

            V1 = turtlePos.decompose()[0]
            if (V1[0],V1[1],V1[2]) == (0,0,0):
                V1 = cursor.evaluate().freeze()
            V1 = (V1[0],V1[1],V1[2])
            
            ADD_NEW_VERT = False

            if BRANCH_STARTED: 
                ADD_NEW_VERT = True
                BRANCH_STARTED = False

            if JUST_MOVE:
                ADD_NEW_VERT = True
                JUST_MOVE = False   

            if ADD_NEW_VERT:

                verts_co.add(V1)
                point_radius.append(r)

                VERTS.append( V1 )
                V1_index = v_count
                v_count+=1 
                edge_order.append(0)
                
                store_iters.append(i)

            else:   
                V1 = V2
                V1_index = V2_index

            cursor.sample += 0.1 * LEN
            V2 = cursor.evaluate().freeze()
            V2 = (V2[0],V2[1],V2[2])

            turtlePos[0][3]=V2[0]
            turtlePos[1][3]=V2[1]
            turtlePos[2][3]=V2[2]
            
            verts_co.add(V2)
            point_radius.append(r)

            VERTS.append( V2 )
            V2_index = v_count
            v_count+=1
            store_iters.append(i)
            
            if ADD_NEW_VERT: point_dir = list( Vector(V2) - Vector(V1) )
            point_dir = list( (turtlePos @ ( up_axis  * LEN )) - Vector(V2))
            edge_order.append(1)
            
            EDGES.append( (V1_index , V2_index) )            
         
        elif cmd in GROW_CMDS:
            
            edge_radius.append(r)
            
            V1 = turtlePos.decompose()[0]
            V1 = (V1[0],V1[1],V1[2])
            
            ADD_NEW_VERT = False

            if BRANCH_STARTED: 
                ADD_NEW_VERT = True
                BRANCH_STARTED = False

            if JUST_MOVE:
                ADD_NEW_VERT = True
                JUST_MOVE = False

            if ADD_NEW_VERT:

                verts_co.add(V1)
                point_radius.append(r)

                VERTS.append(V1)
                V1_index = v_count
                v_count+=1 
                edge_order.append(0)

                store_iters.append(i)
                if cmd.islower(): point_tag.append( CODEX[cmd] )

            else:   
                V1 = V2
                V1_index = V2_index

            V2 = (turtlePos @ ( up_axis  * LEN ))
            V2 = (V2[0],V2[1],V2[2])
            
            turtlePos[0][3]=V2[0]
            turtlePos[1][3]=V2[1]
            turtlePos[2][3]=V2[2]

            verts_co.add(V2)
            point_radius.append(r)

            VERTS.append( V2 )
            V2_index = v_count
            v_count+=1
            
            store_iters.append(i)
            if cmd.islower(): point_tag.append( CODEX[cmd] )
            if ADD_NEW_VERT: point_dir = list( Vector(V2) - Vector(V1) )
            point_dir = list( (turtlePos @ ( up_axis  * LEN )) - Vector(V2))
            edge_order.append(1)
            
            EDGES.append( (V1_index , V2_index) )
            
        elif cmd.isdigit():
            try:
                point_ID.append(int(cmd))
            except:
                pass
        
        elif not cmd.isdigit():
            point_ID.append(0)

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
        
        elif cmd == '[': # START TRUNK
            storePos.append(turtlePos.copy())
            storeLength.append(L)
            storeRadius.append(r) #point_radius
            storeIndex.append(n)
            storeVcount.append(v_count)
            n=0
            if V2 != None: 
                baseVerts.append(V2)
                baseIndex.append(V2_index)
            BRANCH_STARTED = True

        elif cmd == ']': #CLOSE TRUNK
            turtlePos = storePos.pop()
            L = storeLength.pop() 
            r = storeRadius.pop() #point_radius
            n = storeIndex.pop()
            root_index = storeVcount.pop()
            if len(baseVerts)>0: 
                    V2 = baseVerts.pop()
                    V2_index = baseIndex.pop()
            else:
                V2 = VERTS[0]
                V2_index = 0
        i += 1


    OUTPUTS = {}     
    OUTPUTS['verts'] = VERTS
    OUTPUTS['edges'] = EDGES
    OUTPUTS['point_radius'] = point_radius
    OUTPUTS['points_co'] = edge_order
    OUTPUTS['points_dir'] = point_dir
    OUTPUTS['points_tag'] = point_tag
    OUTPUTS['points_id'] = point_ID
    OUTPUTS['edge_radius'] = edge_radius

    return OUTPUTS


OUTPUTS = FRACTALEX(
    axiom, rules,  
    angle, length, scale, radius, radius_scale, 
    min_angle, max_angle, min_len, max_len, 
    iters,max_iters, g_j_k_w )
    
verts =  [ OUTPUTS['verts'] ]
edges =  [ OUTPUTS['edges'] ]
point_radius =  [ OUTPUTS['point_radius'] ]
points_co =  [ OUTPUTS['points_co'] ]
points_dir =  [ OUTPUTS['points_dir'] ]
points_layer =  [ OUTPUTS['points_tag'] ]
points_id =  [ OUTPUTS['points_id'] ] 
edge_radius = [ OUTPUTS['edge_radius'] ]