from planners.fo_planner import Operator
# from planners.VectorizedPlanner import BaseOperator

'''							USAGE INSTRUCTIONS
FO Operator Structure: Operator(<header>, [<conditions>...], [<effects>...])

	<header> : ('<name>', '?<var_1>', ... , '?<var_n>')
			example : ('Add', '?x', '?y')
	<conditions> : [(('<attribute>', '?<var_1>'),'?<value_1>'), ... ,
					 (<func>, '?<value_1>', ...), ...
				   ]
			example : [ (('value', '?x'), '?xv'),
	                  (('value', '?y'), '?yv'),
	                  (lambda x, y: x <= y, '?x', '?y')
	                  ]
	<effects> : [(<out_attribute>,
				 	('<name>', ('<in_attribute1>', '?<var_1>'), ...),
				  	(<func>, '?<value_1>', ...)
			     ), ...]
			example :[(('value', ('Add', ('value', '?x'), ('value', '?y'))),
	                     (int_float_add, '?xv', '?yv'))])
	Full Example:
	def int_float_add(x, y):
	    z = float(x) + float(y)
	    if z.is_integer():
	        z = int(z)
	    return str(z)

	add_rule = Operator(('Add', '?x', '?y'),
			            [(('value', '?x'), '?xv'),
			             (('value', '?y'), '?yv'),
			             (lambda x, y: x <= y, '?x', '?y')
			             ],
			            [(('value', ('Add', ('value', '?x'), ('value', '?y'))),
			              (int_float_add, '?xv', '?yv'))])

	Note: You should explicitly register your operators so you can
			 refer to them in your training.json, otherwise the name will
			 be the same as the local variable
			example: Operator.register("Add")

vvvvvvvvvvvvvvvvvvvv WRITE YOUR OPERATORS BELOW vvvvvvvvvvvvvvvvvvvvvvv '''

def diamond(base, exp):
    return str(int(float(base)**float(exp)))[::-1].lstrip("0")

diamond_rule = Operator(('Diamond', '?x', '?y'),
		            [(('value', '?x'), '?xv'),
		             (('value', '?y'), '?yv')],
		            [(('value', ('Diamond', ('value', '?x'), ('value', '?y'))),
		              (diamond, '?xv', '?yv'))])
Operator.register("diamond_rule", diamond_rule)

def sun(a,b,c,d):
  l = int(float(a)) // int(float(b))
  r = int(float(c)) // int(float(d))
  if r == 0:
    return str(-1)
  return str(l // r)

sun_rule = Operator(('Sun', '?x', '?y', '?z', '?w'),
		            [(('value', '?x'), '?xv'),
		             (('value', '?y'), '?yv'),
                     (('value', '?z'), '?zv'),
                     (('value', '?w'), '?wv')],
		            [(('value', ('Sun', ('value', '?x'), ('value', '?y'), ('value', '?z'), ('value', '?w'))),
		              (sun, '?xv', '?yv', '?zv', '?wv'))])
Operator.register("sun_rule", sun_rule)

def command(a,b,c):
  l = int(float(a))
  r = int(float(b)) * int(float(c))
  if r == 0:
      return str(-1)
  return str(l // r)

command_rule = Operator(('Command', '?x', '?y', '?z'),
		            [(('value', '?x'), '?xv'),
		             (('value', '?y'), '?yv'),
                     (('value', '?z'), '?zv')],
		            [(('value', ('Command', ('value', '?x'), ('value', '?y'), ('value', '?z'))),
		              (command, '?xv', '?yv', '?zv'))])
Operator.register("command_rule", command_rule)


















# ^^^^^^^^^^^^^^ DEFINE ALL YOUR OPERATORS ABOVE THIS LINE ^^^^^^^^^^^^^^^^
for name,op in locals().copy().items():
  if(isinstance(op, Operator)):
    Operator.register(name,op)
