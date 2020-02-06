import gurobipy as gp
from gurobipy import GRB
from time import process_time
from functools import cmp_to_key
from param import *
from visualize import visualize

def enlargeItemSize(item_size):
    n_size = len(item_size[0])
    for i in range(3):
        for j in range(n_size):
            item_size[i][j] += margin
    return item_size

def compare(item1, item2):
    [seq1, x1, y1, z1, ori1] = item1
    [seq2, x2, y2, z2, ori2] = item2
    bool2int = lambda b: 1 if b else -1
    if abs(z1 - z2) > 0.1:
        return bool2int(z1 > z2)
    elif abs(y1 - y2) > 0.1:
        return bool2int(y1 > y2)
    else:
        return bool2int(x1 > x2)
    
def extractOrientation(variables):
    values = {'e_am' : [], 'e_an' : [], 'e_al' : [],
              'e_bm' : [], 'e_bn' : [], 'e_bl' : [],
              'e_cm' : [], 'e_cn' : [], 'e_cl' : [],}
    
    for var in variables:
        var_name = var.varName.split('[')[0]
        if var_name in values:
            values[var_name].append(var.x)
    
    orientation = []
    n_item = len(values['e_am'])
    for i in range(n_item):
        ori = []
        # longest, M
        if values['e_am'][i] == 0:
            ori.append('x')
        elif values['e_bm'][i] == 0:
            ori.append('y')
        elif values['e_cm'][i] == 0:
            ori.append('z')

        # middle, N
        if values['e_an'][i] == 0:
            ori.append('x')
        elif values['e_bn'][i] == 0:
            ori.append('y')
        elif values['e_cn'][i] == 0:
            ori.append('z')

        # shortest, L
        if values['e_al'][i] == 0:
            ori.append('x')
        elif values['e_bl'][i] == 0:
            ori.append('y')
        elif values['e_cl'][i] == 0:
            ori.append('z')

        orientation.append(ori)

    return orientation


# INPUT
# container_size = [x, y, z]
# item_size = [[x1, x2, x3, ...], [y1, y2, y3, ...], [z1, z2, z3, ...]]

def packing(container_size, item_size, enlarge=False, visualization=False):

    # ---------------------------------------- MODEL ---------------------------------------- 

    model = gp.Model("packing")

    # ---------------------------------------- PARAMETERS ---------------------------------------- 

    # container dimensions
    A = container_size[0]
    B = container_size[1]
    C = container_size[2]

    # item dimensions
    if enlarge:
        enlargeItemSize(item_size)

    M = item_size[0]
    N = item_size[1]
    L = item_size[2]
    
    assert len(M) == len(N)
    assert len(N) == len(L)
    n_item = len(M)

    U = max(A, B, C) + max(max(M), max(N), max(L))

    # ---------------------------------------- VARIABLES ----------------------------------------

    # position
    x = model.addVars(n_item, lb=0, name='x')
    y = model.addVars(n_item, lb=0, name='y')
    z = model.addVars(n_item, lb=0, name='z')

    # orientation after packing
    a = model.addVars(n_item, lb=0, name='a')
    b = model.addVars(n_item, lb=0, name='b')
    c = model.addVars(n_item, lb=0, name='c')

    # non-overlapping
    o_x = model.addVars(n_item, n_item, vtype=GRB.BINARY, name='o_x')
    o_y = model.addVars(n_item, n_item, vtype=GRB.BINARY, name='o_y')
    o_z = model.addVars(n_item, n_item, vtype=GRB.BINARY, name='o_z')

    # orientation-selection
    e_am = model.addVars(n_item, vtype=GRB.BINARY, name='e_am')
    e_an = model.addVars(n_item, vtype=GRB.BINARY, name='e_an')
    e_al = model.addVars(n_item, vtype=GRB.BINARY, name='e_al')
    e_bm = model.addVars(n_item, vtype=GRB.BINARY, name='e_bm')
    e_bn = model.addVars(n_item, vtype=GRB.BINARY, name='e_bn')
    e_bl = model.addVars(n_item, vtype=GRB.BINARY, name='e_bl')
    e_cm = model.addVars(n_item, vtype=GRB.BINARY, name='e_cm')
    e_cn = model.addVars(n_item, vtype=GRB.BINARY, name='e_cn')
    e_cl = model.addVars(n_item, vtype=GRB.BINARY, name='e_cl')

    #   max height
    max_height = model.addVar(lb=0, name='max_height')

    # ---------------------------------------- OBJECTIVE ----------------------------------------

    model.setObjective(max_height, GRB.MINIMIZE)

    # ---------------------------------------- CONSTRAINT ----------------------------------------

    for i in range(n_item):
        # in container
        model.addConstr(x[i] + a[i] <= A, name='in_container_x_%d'%i)
        model.addConstr(y[i] + b[i] <= B, name='in_container_y_%d'%i)
        model.addConstr(z[i] + c[i] <= C, name='in_container_z_%d'%i)

        # orientation selection
        model.addConstr(a[i] - M[i] <= U * e_am[i], name='orientation_selection_am_0_%d'%i)
        model.addConstr(M[i] - a[i] <= U * e_am[i], name='orientation_selection_am_1_%d'%i)
        model.addConstr(a[i] - N[i] <= U * e_an[i], name='orientation_selection_an_0_%d'%i)
        model.addConstr(N[i] - a[i] <= U * e_an[i], name='orientation_selection_an_1_%d'%i)
        model.addConstr(a[i] - L[i] <=  U * e_al[i], name='orientation_selection_al_0_%d'%i)
        model.addConstr(L[i] - a[i] <= U * e_al[i], name='orientation_selection_al_1_%d'%i)

        model.addConstr(b[i] - M[i] <= U * e_bm[i], name='orientation_selection_bm_0_%d'%i)
        model.addConstr(M[i] - b[i] <= U * e_bm[i], name='orientation_selection_bm_1_%d'%i)
        model.addConstr(b[i] - N[i] <= U * e_bn[i], name='orientation_selection_bn_0_%d'%i)
        model.addConstr(N[i] - b[i] <= U * e_bn[i], name='orientation_selection_bn_1_%d'%i)
        model.addConstr(b[i] - L[i] <= U * e_bl[i], name='orientation_selection_bl_0_%d'%i)
        model.addConstr(L[i] - b[i] <= U * e_bl[i], name='orientation_selection_bl_0_%d'%i)

        model.addConstr(c[i] - M[i] <= U * e_cm[i], name='orientation_selection_cm_0_%d'%i)
        model.addConstr(M[i] - c[i] <= U * e_cm[i], name='orientation_selection_cm_1_%d'%i)
        model.addConstr(c[i] - N[i] <= U * e_cn[i], name='orientation_selection_cn_0_%d'%i)
        model.addConstr(N[i] - c[i] <= U * e_cn[i], name='orientation_selection_cm_1_%d'%i)
        model.addConstr(c[i] - L[i] <= U * e_cl[i], name='orientation_selection_cl_0_%d'%i)
        model.addConstr(L[i] - c[i] <= U * e_cl[i], name='orientation_selection_cl_1_%d'%i)

        model.addConstr(e_am[i] + e_an[i] + e_al[i] == 2, name='orientation_selection_sum_a_%d'%i)
        model.addConstr(e_bm[i] + e_bn[i] + e_bl[i] == 2, name='orientation_selection_sum_b_%d'%i)
        model.addConstr(e_cm[i] + e_cn[i] + e_cl[i] == 2, name='orientation_selection_sum_c_%d'%i)
        model.addConstr(e_am[i] + e_bm[i] + e_cm[i] == 2, name='orientation_selection_sum_m_%d'%i)
        model.addConstr(e_an[i] + e_bn[i] + e_cn[i] == 2, name='orientation_selection_sum_n_%d'%i)
        model.addConstr(e_al[i] + e_bl[i] + e_cl[i] == 2, name='orientation_selection_sum_l_%d'%i)
        
        # non-overlapping
        for j in range(n_item):
            model.addConstr(x[j] - x[i] - a[i] >= -U * o_x[i, j], name='overlapping_x_0_%d_%d'%(i,j))
            model.addConstr(y[j] - y[i] - b[i] >= -U * o_y[i, j], name='overlapping_y_0_%d_%d'%(i,j))
            model.addConstr(z[j] - z[i] - c[i] >= -U * o_z[i, j], name='overlapping_z_0_%d_%d'%(i,j))
            if j > i:
                model.addConstr(o_x[i, j] + o_x[j, i] + o_y[i, j] + o_y[j, i] + o_z[j, i] + o_z[j, i] <= 5, name='overlapping_sum_%d_%d'%(i,j))

        # max height
        model.addConstr(max_height >= z[i] + c[i], name='max_height_%d'%i)

    model.optimize()

    # ---------------------------------------- GRAVITY ----------------------------------------

    fixed = [False] * n_item
    for i in range(n_item):
        
        # find the highest non-fixed item
        max_height_id = None
        max_height_cur = 0
        for j in range(n_item):
            if (fixed[j] == False) and (z[j].x + c[j].x > max_height_cur):
                max_height_cur = z[j].x + c[j].x
                max_height_id = j
        fixed[max_height_id] = True
        
        # add fixed position constraint and remove max_height constraint
        constr_pair = list(zip(range(len(model.getConstrs())), model.getConstrs()))
        found = filter(lambda pair: pair[1].ConstrName == 'max_height_%d'%max_height_id, constr_pair)
        constr_id = list(found)[0][0]

        model.remove(model.getConstrs()[constr_id])
        model.addConstr(x[max_height_id] == x[max_height_id].x, name='fixed_x%d'%max_height_id)
        model.addConstr(y[max_height_id] == y[max_height_id].x, name='fixed_y%d'%max_height_id)
        model.addConstr(z[max_height_id] == z[max_height_id].x, name='fixed_z%d'%max_height_id)
        model.addConstr(a[max_height_id] == a[max_height_id].x, name='fixed_a%d'%max_height_id)
        model.addConstr(b[max_height_id] == b[max_height_id].x, name='fixed_b%d'%max_height_id)
        model.addConstr(c[max_height_id] == c[max_height_id].x, name='fixed_c%d'%max_height_id)

        model.optimize()

    # ---------------------------------------- RESULT ----------------------------------------
    print("\ntime: ", process_time(), "sec")

    ret_x, ret_y, ret_z, orientation = None, None, None, None
    if model.Status == GRB.OPTIMAL:

        # position
        getValue = lambda var: var.x
        x_pos = list(map(getValue, x.values()))
        y_pos = list(map(getValue, y.values()))
        z_pos = list(map(getValue, z.values()))
        a_len = list(map(getValue, a.values()))
        b_len = list(map(getValue, b.values()))
        c_len = list(map(getValue, c.values()))

        ret_x = [x_pos + a_len/2 for x_pos, a_len in zip(x_pos, a_len)]
        ret_y = [y_pos + b_len/2 for y_pos, b_len in zip(y_pos, b_len)]
        ret_z = z_pos

        # orientation
        orientation = extractOrientation(model.getVars())

        # sort by z, then x, then y
        item_info = list(zip(range(n_item), ret_x, ret_y, ret_z, orientation))
        item_info.sort(key=cmp_to_key(compare))

        # visualize
        if visualization:
            seq = list(map(lambda item : item[0], item_info))
            visualize(seq, container_size, x_pos, y_pos, z_pos, a_len, b_len, c_len, shrink_ratio=5)
            for i in range(n_item):
                print(i)
                print('%.1f'%x[i].x, "-", '%.1f'%(x[i].x + a[i].x))
                print('%.1f'%y[i].x, "-", '%.1f'%(y[i].x + b[i].x))
                print('%.1f'%z[i].x, "-", '%.1f'%(z[i].x + c[i].x))

    return item_info


# OUTPUT
# [(serial#, centroid_x, centroid_y, bottom_z, ['z', 'x', 'y']), (serial#, centroid_x, centroid_y, bottom_z, ['z', 'x', 'y']), ...]

if __name__ == "__main__":

    item_info = packing(container_size, item_size, enlarge=False, visualization=True)
    for item in item_info:
        seq, x, y, z, [o1, o2, o3] = item
        print(seq, '%.1f'%x, '%.1f'%y, '%.1f'%z, [o1, o2, o3])
