#!/usr/bin/env python
import sys
import numpy as np
import json
import numpy.matlib as matlab
import time


stats_to_keep = [7, 15, 19, 22, 23, 24, 25, 26, 27]

def mag_func(s):
    return np.ndarray.tolist(np.array(np.matrix(s.strip('[]'))))

x1_step1 = [
        {"xoffset":mag_func("[0;0;0;0;0;0;0.0926953034066373;0;0]"),
        "gain":mag_func("[2;2;2.00088334887373;5.73284623960209;4.77506387667949;5.39128041995259;2.2043311442224;5.12987649760669;3.57449341974048]"),
        "ymin":-1},
            {
                "xoffset": mag_func("[0;0;0;0;0;0;0.169995306048303;0;0]"),
                "gain": mag_func("[2;2;2.00095793086932;5.7820297402784;4.77510723250418;5.39127621293902;2.40962492691203;5.1407751768892;3.57502318518594]"),
                "ymin":-1
            }]
b1 = [mag_func("[-1.6934196067985163303;-10.384236654748983497;1.1225027161499918638;2.5926121688859451453;-1.3460843959985449025;28.459639945104481029]"),

      mag_func("[-2.2673011290095534953;0.88434854419302111328;1.598621060813120387;2.1186676620960889217;3.8025579688745718698;-8.6472553087563994723]")]

IW1_1 = [mag_func("[-1.1647627928183150736 -0.035105536691838669372 -0.23233180849846152283 3.083898604114996278 0.64149818857973539554 -1.872734484882589534 -1.2984170453887760033 0.36061137560018452497 -0.41603336327864276489;-17.08028357210019621 7.2302600533111629488 14.044291921659979749 0.28422181953374947572 5.4824362654611205059 -0.16059845638547853852 2.3003585059515017086 -0.77730562380226542185 13.673336443196072665;4.5970608031758750656 -1.3647822808944434225 0.64748737827748559237 -0.00064623914208017082042 -0.59041349012689470221 -0.69268112064925702054 -0.11462328633569129899 -3.144948620676197848 -0.87350446073799925539;6.037478407208420883 0.51772865485210295411 1.1672460318116002487 -2.6421075244801190962 -1.508746371918002982 -0.51833704158431159748 -1.3286411257824028986 -0.21986233409465241739 -0.30959729720786172136;-4.4562522854575155051 1.2370811525936864506 -0.54235295806374828054 0.013481795166784446907 0.48866532865504430649 0.5577713043338420329 -0.097736322600573299901 3.0617925434249277927 0.68552339765536829397;39.514387707261278138 0.14698641113694962956 0.77540788044934205736 -3.3881373057572381491 -7.2192081512073453808 -0.3014186193931605029 -19.522509516079765035 -14.175091358432256428 -7.3826087050184909799]"),

mag_func("[0.85189206483622603727 0.67053177142408604272 0.21208104413053238679 -4.2266669393812570377 -1.1932478736509342099 1.5796103002358696799 1.2929970703546529442 -0.72346923585608613472 2.5761145084525787219;9.4852620218414429587 4.1776984359724638196 -1.2982294300160670542 -5.2316025050325434265 -2.0989084127513906175 -2.6374004938501438566 0.2982447592704412509 0.032647470689417049106 0.21078396042732941429;3.839351382080038011 0.43593300404807200366 -0.26763922130308609448 -1.8548991364430764683 0.15298050182350542148 -0.98956832933680127784 -0.98128955913454130044 -1.3128555210890484606 1.1253314293776619515;3.796932212715177446 0.35930022943473421959 -0.25531604613092134803 -1.5525085709600081607 0.45523171306783349888 -0.63580854077537307667 -0.72971348460323537388 -1.1622562073075428657 1.3053198633529270456;8.3967216112559341923 0.86601977581717370924 1.139521765937204334 1.7446931637708431584 -2.3293059031252063562 -0.50926455342369736368 -4.1167685774256295161 1.0412901944388792685 -4.2502648996869778486;-16.847722545858136556 -2.4284327396417375589 -2.1466817835716440754 1.3086656268646810197 6.775221792616677341 0.23777909312651349105 0.44215856811771242496 -4.0151455151161012935 12.064519846344182952]")]
b2 = [-0.23987855077308700702, -2.2776531347265942529]
LW2_1 = [mag_func("[-0.27179594663366463125 0.15563332819140363039 5.5494516980701646958 -0.34464085705919206282 5.518677297531580983 -0.36771902803275025029]"),

         mag_func("[-2.1224024589705372534 0.30819026570320817715 -3.2062262267889662937 2.9793502949029924132 -0.74949312090854991464 -0.56114181488791403662]")]

y1_step1 = [{"ymin": -1,
      "gain": 0.755287009063444,
      "xoffset": 0.027
      },
        {
            "ymin":-1,
            "gain":0.616142945163278,
            "xoffset":0.008
        }]

for i in range(0,2):
    x1_step1[i]["xoffset"] = np.array(x1_step1[i]["xoffset"]).reshape(len(x1_step1[i]["xoffset"]), 1)
    x1_step1[i]["gain"] = np.array(x1_step1[i]["gain"]).reshape(len(x1_step1[i]["gain"]), 1)

    x1_step1[i]["ymin"] = np.array(x1_step1[i]["ymin"])
    b1[i] = np.array(b1[i])
    IW1_1[i] = np.array(IW1_1[i])
    LW2_1[i] = np.array(LW2_1[i])
    LW2_1[i] = LW2_1[i][0].reshape(len(LW2_1[i][0]), 1)

def mapminmax_apply(x, settings):

    y = np.subtract(x, settings['xoffset'])
    y = np.multiply(y, settings['gain'])
    y = y + settings['ymin']
    return y

def tansig_apply(n):

    n = np.array(n)
    n = (1 + np.exp(-2 * n))
    n = np.divide(2, n)
    n = n - 1
    return n

def mapminmax_reverse(y,settings):

    x = np.subtract(y, settings['ymin'])
    x = np.divide(x, settings['gain'])
    x = x + settings['xoffset']
    return x

def formatRawData(x):

    result = []

    dtlbs = x[6]
    if dtlbs == 0:
        dtlbs = 1

    result.append(x[7] / dtlbs)
    result.append(1 - (x[7] / dtlbs))

    itlb = x[8]
    if itlb == 0:
        itlb = 0
    result.append(x[9] / itlb)
    result.append(1 - (x[9] / itlb))

    stlb = x[10]
    if stlb == 0:
        stlb = 1
    result.append(x[11] / stlb)
    result.append(1 - (x[11] / stlb))

    dl1 = x[12] + x[14]
    if dl1 == 0:
        dl1 = 1
    result.append(x[12] / dl1)
    result.append(x[13] / dl1)
    result.append(1 - (x[13] / dl1))
    result.append(x[14] / dl1)

    il1 = x[15] + x[17]
    if il1 == 0:
        il1 = 1
    result.append(x[15] / il1)
    result.append(x[16] / il1)
    result.append(1 - (x[16] / il1))
    result.append(x[17] / il1)

    l2 = x[18] + x[20]
    if l2 == 0:
        l2 = 1
    result.append(x[18] / l2)
    result.append(x[19] / l2)
    result.append(1 - (x[19] / l2))
    result.append(x[20] / l2)

    l3 = x[21] + x[23]
    if l3 == 0:
        l3 = 1
    result.append(x[21] / l3)
    result.append(x[22] / l3)
    result.append(1 - (x[22] / l3))
    result.append(x[23] / l3)

    inst_mix = x[30]
    if inst_mix == 0:
        inst_mix = 1
    result.append(x[24] / inst_mix)
    result.append(x[25] / inst_mix)
    result.append(x[26] / inst_mix)
    result.append(x[27] / inst_mix)
    result.append(x[28] / inst_mix)
    result.append(x[29] / inst_mix)

    return result

def removeconstantrows_apply(stats):

    result = []
    for stat in stats_to_keep:
        result.append(stats[int(stat)])
    return result

if __name__ == '__main__':
    start = time.time()
    #if this fails try to change the os.popen paramater for this scripts location in demo.py, called path
    '''
    arg[0] is the script name
    arg[1] is the core number stats are from
    arg[2] is the stats json format
    '''
    core = int(sys.argv[1])

    x1 = json.loads(sys.argv[2])


    x1 = formatRawData(x1)

    # f = open("/home/tugberk/stats0401.txt", "a")

    x1 = removeconstantrows_apply(x1)

    # if core == 0:
    #     f.write("Big to small  ")
    #     for stat in x1:
    #         f.write(str(stat) + " ")
    # else:
    #     f.write("small to big  ")
    #     for stat in x1:
    #         f.write(str(stat) + " ")


    x1 = np.array(x1)

    if type(x1[0]) is not list:
        Q = 1
    else:
        Q = x1.shape[1]

    x1 = np.transpose(x1.reshape(Q,x1.shape[0]))

    xp1 = mapminmax_apply(x1, x1_step1[core])

    xp1 = np.array(xp1)




    p1 = np.matlib.repmat(b1[core], 1, Q)
    a1 = tansig_apply(p1 + np.dot(IW1_1[core], xp1))


    LW2_1 = np.transpose(LW2_1[core])
    a2 = np.matlib.repmat(b2[core], 1, Q) + np.dot(LW2_1[0], a1)


    y1 = mapminmax_reverse(a2, y1_step1[core])

    y1 = np.transpose(y1)

    y1 = y1.tolist()

    y1 = json.dumps(y1, separators=(',', ':'))

    if '.' in y1 or ',' in y1:
        y1 = y1[2:-3]
    else:
        y1 = 0
    # f.write(" prediction = " + str(y1) +"\n")
    end = time.time()
    with open("/scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/paper1exec.txt", "a") as myfile:
        myfile.write("predict time : " + str(end - start)) 
    print y1
