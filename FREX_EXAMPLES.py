#LSYS EXAMPLES

EXAMPLES = {

'Hilbert_2D' : {'axiom': 'A',
'rule_1': 'A:-BF+AFA+FB-',
'rule_2': 'B:+AF-BFB-FA+',
'angle': 90.0,
'length': 1.0,
'length_scale': 1.0,
'radius': 1.0,
'radius_scale': 1.0,
'min_angle': 0.0,
'max_angle': 0.0,
'min_len': 0.0,
'max_len': 0.0,
'iteration': 5},

'TEX_Hilbert_2D' : {'image_settings': '(512,512,512,512)',
'blur': 1,
'caps': 1,
'C1': '(255,255,255,255)',
'C2': '(255,255,255,255)',
'C3': '(255,255,255,255)',
'C4': '(255,255,255,255)',
'axiom': 'A',
'rule_1': 'A:-BF+AFA+FB-',
'rule_2': 'B:+AF-BFB-FA+',
'angle': 90.0,
'length': 16,
'length_scale': 1.0,
'radius': 6.0,
'radius_scale': 1.0,
'min_angle': 0.0,
'max_angle': 0.0,
'min_len': 0.0,
'max_len': 0.0,
'iteration': 5},

"Sierpinski_triangle" : {'axiom': 'F-G-G',
'rule_1': 'F:F-G+F+G-F',
'rule_2': 'G:GG',
'angle': 120.0,
'length': 1.0,
'length_scale': 1.0,
'radius': 1.0,
'radius_scale': 1.0,
'min_angle': 0.0,
'max_angle': 0.0,
'min_len': 0.0,
'max_len': 0.0,
'iteration': 5} ,


"Hilbert_3D" : {'axiom': 'A',
'rule_1': 'A:B-F+CFC+F-D&F^D-F+&&CFC+F+B//',
'rule_2': 'B:A&F^CFB^F^D^^-F-D^|F^B|FC^F^A//',
'rule_3': 'C:|D^|F^B-F+C^F^A&&FA&F^C+F+B^F^D//',
'rule_4': 'D:|CFB-F+B|FA&F^A&&FB-F+B|FC//',
'angle': 90.0,
'length': 1.0,
'length_scale': 1.0,
'radius': 1.0,
'radius_scale': 1.0,
'min_angle': 0.0,
'max_angle': 0.0,
'min_len': 0.0,
'max_len': 0.0,
'iteration': 4} ,


"Binary_tree" : {'axiom': 'FA',
'rule_1': 'A:[+FSA][-FSA]',
'angle': 55.0,
'length': 1.0,
'length_scale': 0.6000000238418579,
'radius': 0.30000001192092896,
'radius_scale': 0.5,
'min_angle': 0.0,
'max_angle': 0.0,
'min_len': 0.0,
'max_len': 0.0,
'iteration': 10}

}
