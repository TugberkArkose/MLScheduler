#!/usr/bin/env python
import sys
import numpy as np
import json
import numpy.matlib as matlab

stats_to_keep = [7, 15, 19, 22, 23, 24, 25, 26, 27]


def mag_func(s):
    return np.ndarray.tolist(np.array(np.matrix(s.strip('[]'))))


x1_step1 = [{
    "xoffset":
    mag_func("[0;0;0;0;0;0;0.0691521565902343;0;0]"),
    "gain":
    mag_func(
        "[2;2;2;5.73284623960209;4.77506387667949;5.39128041995259;2.14857886190492;3.46052845373869;3.51959729112496]"
    ),
    "ymin":
    -1
}, {
    "xoffset":
    mag_func("[0;0;0;0;0;0;0.0700397327039092;0;0]"),
    "gain":
    mag_func(
        "[2;2;2.00095793086932;5.7820297402784;4.77510723250418;5.39127621293902;2.15062951647935;3.46047762128126;3.57502318518594]"
    ),
    "ymin":
    -1
}]
b1 = [
    mag_func(
        "[-3.3688891117011054988;-8.2293320391583790752;-1.7334601286131952058;-1.9986327217042907378;-2.5053416288235963449;-8.1569709032064885434]"
    ),
    mag_func(
        "[-7.2631126800595460224;8.6061465985414429269;-4.3428289981997449942;0.55150336971624480675;-2.3831986848534247869;-1.136130394707973057]"
    )
]

IW1_1 = [
    mag_func(
        "[-2.348719775813743027 -0.22018421716286579182 -1.5802631609840778193 -1.0964083883061301883 -0.10537089047915063067 -0.74392906528934610311 1.3830645128128626897 1.2418361423265078525 2.6389354645902578511;-18.503534653654000408 -1.3567171047952162333 0.9353195637161398901 1.7843220361644791527 4.9499390443557942376 0.035633396763988384182 3.0720821989576103661 1.2256923832207147207 8.4971835470628871434;-3.1653454964820197937 -0.24397203355505769906 -0.050656300689952832306 -0.43268941768256152791 -0.34550645485595032902 1.5441107245900400624 1.2381003255939935226 0.86308100857537672912 0.65459415694979783407;-4.1503988951666155316 -0.69938494574904730428 -0.56663954206674249647 0.73916581338310038962 0.71037692604899072002 0.78001478279345903832 1.1514522124851906959 0.53636795180432417229 0.37414444893035841977;-3.1284099936813904996 -0.26424477417882641372 -0.065946878526028610001 -0.56674909651603255778 -0.53975104505686499756 1.214029544014185058 0.60899329555857206753 0.48664204405458943992 0.3504562959543336409;-15.958109415874996984 -1.4108139497226916959 -1.107162493705539541 3.7211058149574802734 8.454120803477470858 -4.0913589188123138385 -0.63216115828409791266 -2.2097843316655958468 12.95443630772610355]"
    ),
    mag_func(
        "[-11.151061612802777745 -2.3754600684280768874 -3.4270900252152554089 2.2372886535732163793 6.2466158022573363695 1.1398207227553740495 2.2912079801602440732 -1.198803123987999486 7.1871140353689613178;10.026890670306940478 0.7079582208038459612 1.1084845179171047835 5.2704996581265222133 0.30254475882770542894 -2.8093578450872396246 -8.5236978717515512471 1.3669854977724549272 -6.0603960666125722412;-7.3054406886265352838 -1.0061101796225433436 -0.69337277021656618103 -1.4970328567824255916 2.1189064734119922306 0.72350139140024982698 5.0554285063535067124 0.20365686556143400288 3.089141114144779543;0.041389560461311702966 -1.9070487947773706594 1.6195790729541386099 2.6916686499005018085 0.81598720968669646858 0.69392087901276178208 -0.71956239370546548617 -1.7515802695923516907 1.5213821656437727103;-6.2800010694820365131 -1.0219787535179749582 6.951886166240443643 -15.655404693513082393 27.769965023358935241 -21.385386034999452676 15.930924097392697547 -16.717348546531678011 -3.0914624654054656538;-3.8335441060579777961 0.55557827475754828495 -1.8867834548247639503 1.6919331036091977971 -0.41422100720762333737 2.3776921263563539632 1.0605699249411038032 3.5050659497700134004 0.69874633431861554733]"
    )
]
b2 = [-0.44054822888600259079, -0.46192405142443110355]
LW2_1 = [
    mag_func(
        "[0.43254536454252051625 0.23379572177786439591 7.5090219908447366493 0.56053540768479948042 -8.0606532740041636487 -0.23229911349299361967]"
    ),
    mag_func(
        "[-0.64516238158876371145 0.79553441369156374652 1.0685437307833010045 0.46925996203884168256 0.19421705061403940484 0.37276823104822237598]"
    )
]

y1_step1 = [{
    "ymin": -1,
    "gain": 0.755287009063444,
    "xoffset": 0.027
}, {
    "ymin": -1,
    "gain": 0.616142945163278,
    "xoffset": 0.008
}]

for i in range(0, 2):
    x1_step1[i]["xoffset"] = np.array(x1_step1[i]["xoffset"]).reshape(
        len(x1_step1[i]["xoffset"]), 1)
    x1_step1[i]["gain"] = np.array(x1_step1[i]["gain"]).reshape(
        len(x1_step1[i]["gain"]), 1)

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


def mapminmax_reverse(y, settings):

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

    #if this fails try to change the os.popen paramater for this scripts location in demo.py, called path
    '''
    arg[0] is the script name
    arg[1] is the core number stats are from
    arg[2] is the stats json format
    '''
    core = int(sys.argv[1])

    x1 = json.loads(sys.argv[2])

    x1 = formatRawData(x1)

    # f = open("/home/tugberk/stat0102.txt", "a")

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

    x1 = np.transpose(x1.reshape(Q, x1.shape[0]))

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
    print y1
