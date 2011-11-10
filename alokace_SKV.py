"""
Alokace funkce S a KV do bunek
"""
import numpy.ma
import string
import dis_population_1 as dp
import time
import win32com.client
import tables
import cPickle
import numpy
import math
import os
import udrzhra_functions
import numexpr as ne

def matrix_sort(matrix,caseFieldIndex):
    """
    Funkce pro setrideni pole podle prislusneho indexu (sloupce)
    matrix - pole k setrideni, caseFieldIndex - index sloupce v danem poli
    """
    s = matrix[:]
#    print type(s)
    def por(a,b):      # trideni podle daneho indexu / hodnota iter=hodnota sloupce
        """
        neco
        """
        i = caseFieldIndex
        return cmp(a[i],b[i])
    s.sort(por)
    return s

def alok(sMap,sMap_S, dx):
    """vraci seznam kodu bunek pro (de)alokaci funkci"""
    alok_funkce =[]
    if dx > 0:
        list_prob = sMap.items()
        list_prob_sort = matrix_sort(list_prob,1)
        index = -1 # bude brat od nejvetsiho, posledni prvek v setridenem seznamu
        while dx > 0:
            s_kod = list_prob_sort[index][0]
            alok_funkce.append(s_kod)
            index -= 1
            dx = dx - 1
    elif dx < 0:
        list_prob = sMap_S.items()
        list_prob_sort = matrix_sort(list_prob,1)
        index = 0
        while dx < 0:
            s_kod = list_prob_sort[index][0] # vybiram od nejmensiho, prvni index
            alok_funkce.append(s_kod)
            index = index + 1
            dx = dx + 1
    return alok_funkce

def alok_update_new(gp,s_add,s_rem,kv_add,kv_rem,feacNew, sit_Prob_KV, sit_Prob_S):
    """update funkci ve vrstve"""
    orpCond = '"ORP" = 1'
    rows = gp.UpdateCursor(feacNew,orpCond)  # zapisuje do vrstvy feacNew
    row = rows.Next()
    while row:
        cr = row.Col_Row
        if cr in s_add:
            if row.funkce == 'BI':
                row.funkce = 'BI_S'
            elif row.funkce == 'BH':
                row.funkce = 'BH_S'
        elif cr in s_rem:
            if row.funkce == 'BI_S':
                row.funkce = 'BI'
            elif row.funkce == 'BH_S':
                row.funkce = 'BH'
        if cr in kv_add:
            row.funkce = 'KV'
        elif cr in kv_rem:
            row.funkce = 'KR'
        if sit_Prob_KV.has_key(cr):
            row.P_KV = sit_Prob_KV[cr]
        if sit_Prob_S.has_key(cr):
            row.P_S = sit_Prob_S[cr]
        rows.UpdateRow(row)
        row = rows.Next()
    del rows, row

###def prob_kv_map(gp,layer,cell_all_pop,kr_mask,dCell,cN,rN,map_file_folder,beta=2):
###    ''' vypocet pravdepodobnostni mapy pro KV  '''
###    # nacte kody bunek v ORP (odpovida vzdalenostem v d_Cell
###    file_temp = map_file_folder + 'cellsORP.txt'
###    #soubor = open('p:/cellsORP.txt','r')
###    soubor = open(file_temp,'r')
###    code_orp = cPickle.load(soubor)
###    soubor.close()
###
###    kv_cell_zsj =[]
###    k_index = []
###    cond = '"ORP" = 1'
###    rows = gp.SearchCursor(layer, cond)
###    row = rows.Next()
###    while row:
###        if row.funkce == 'KV':
###            kv_cell_zsj.append(row.Col_Row)
###        row = rows.Next()
###    del row, rows
###
###
###    bydleni = numpy.zeros(len(code_orp),dtype='uint8')
###    nezastavene = bydleni.copy()
###    cell_popul = numpy.zeros(len(code_orp))
###    for i in xrange(len(code_orp)):
###        colRow = string.split(code_orp[i])
###        c = int(colRow[0])
###        r = int(colRow[2])
###        if cell_all_pop[c-1][r-1]>0:
###            bydleni[i]=1
###            cell_popul[i]=cell_all_pop[c-1][r-1]
###        elif code_orp[i] in kv_cell_zsj:
###            k_index.append(i)
###        if kr_mask [c-1][r-1]==1:
###            nezastavene[i]=1
###    print cell_popul[cell_popul>0]
###    print "Vytvoreny numpy pole s maskou bydleni, nezastavene a cell_popul"
###
###    # prochazeni a aktualizace pravdepodobnostni mapy
###    # pocitam pro nezastavene bunky pravdepodobnosti
###    sit_Prob={}
###    print 'len(nezastavene): ',len(nezastavene[nezastavene>0])
###    for i in xrange(len(nezastavene)):  # for i in xrange(200):
###       if nezastavene[i]==1:
###                dis = dCell[i][0]/1000. #*bydleni
###                dis *= beta
###                dis *= (-1)
###                dis = numpy.exp(dis)
###                dis = dis * cell_popul
###                pop = dis*bydleni
###                sit_Prob[code_orp[i]]=numpy.sum(pop)
###                if i in range(1000,180000,1000):
###                    print i
###
###    file_temp = map_file_folder + 'cellsKVmap.txt'
###    #soubor = open('c:/Projekty/udrzhra/data/map_files/cellsKVmap.txt','w')
###    soubor = open(file_temp,'w')
###    cPickle.dump(sit_Prob,soubor)
###    soubor.close()
###    print 'Mapa probability KV map je ulozena v souboru.'
###
###    sit_Prob_KV={}
###    for i in k_index:
###        dis = dCell[i][0]/1000.0 #*bydleni
###        dis *= beta
###        dis *= (-1)
###        dis = numpy.exp(dis)
###        pop = dis*bydleni*cell_popul
###        sit_Prob_KV[code_orp[i]]=numpy.sum(pop)
###        print 'sit_prob_KV: %s : %s'%(code_orp[i],sit_Prob_KV)
###        if i in range(1000,180000,1000):
###                print i
###
####    nacteni pravdepodobnostni mapy ze souboru a nacteni do vrstvy
###    #soubor = open('c:/Projekty/udrzhra/data/map_files/cellsKVmap.txt','r')
###    soubor = open(file_temp,'r')
###    sit_Prob = cPickle.load(soubor)
###    soubor.close()
###
###
###    # prevede slovnik s pravdepodobonostmi na pole sit_P[4][415]
###    sit_P = numpy.zeros(cN*rN).reshape(cN,rN)  # naplneni prazdneho pole s bunkami
###    for i in sit_Prob.keys():
###        b = string.split(i)
###        c = int(b[0])
###        r = int(b[2])
###        sit_P[c-1][r-1]=sit_Prob[i]
###
###    prob_pc = []
###    for c in xrange(cN):
###        for r in xrange(rN):
###            okoli = sit_P[(c-1):(c+2),(r-1):(r+2)]  # cluster okoli = 8
###            okoli_P = numpy.prod(okoli)
###            if numpy.size(okoli)==0:                # okrajove bunky ORP
###                okoli_P = 0
###            cr = str(c+1)+' - '+str(r+1)
###            prob_pc.append([cr, okoli_P])
###
###    sitKV_P = {}
###    for i in prob_pc:
###        sitKV_P[i[0]]=i[1]
###
######    # prevede slovnik s pravdepodobonostmi na pole
######    sitKV_P = numpy.zeros(cN*rN).reshape(cN,rN)
######    for i in prob_pc:
######        b = string.split(i[0])
######        c = int(b[0])
######        r = int(b[2])
######        sitKV_P[c-1][r-1]=i[1]
###
###    return sitKV_P,sit_Prob_KV

def prob_kv_map(gp,layer,dict_zsj_cr,zsj_new,cell_all_pop,kr_mask,dCell,cN,rN,map_file_folder,beta=2):
    """ vypocet pravdepodobnostni mapy pro KV  """
    # nacte kody bunek v ORP
    file_temp = map_file_folder + 'cellsORP.txt'
    soubor = open(file_temp,'r')
    code_orp = cPickle.load(soubor)
    soubor.close()

    # nacte kody bunek, ktere jsou KV
    kv_cell_zsj =[]
    k_index = []
    temp = dict((k,v) for k,v in dict_zsj_cr.iteritems() if v in ['KV'])
    kv_cell_zsj= temp.values()
###    cond = '"ORP" = 1'
###    rows = gp.SearchCursor(layer, cond)
###    row = rows.Next()
###    while row:
###        if row.funkce == 'KV':
###            kv_cell_zsj.append(row.Col_Row)
###        row = rows.Next()
###    del row, rows

    # P pomoci vzdalenosti centroidu
    zsj_obyv = {}
    l = zsj_new 
    rows = gp.SearchCursor(l)
    row = rows.Next()
    while row:
        zsj_obyv[row.KOD_ZSJ_P] = row.zsjBytAllPopul
        row = rows.Next()
    del row, rows
    print '... Processing ZSJ characteristics for KV'
    file_temp = map_file_folder + 'cells_centroids.txt'
    soubor = open(file_temp,'r')
    zsj_code = cPickle.load(soubor)
    soubor.close()
    print '... Processing centroids for KV'
    cell_popul = []
    for i in zsj_code:
        cell_popul.append(zsj_obyv[i[1]])
    print '... Read cell population.'
    # konec P pomoci vzdalenosti centroidu

    bydleni = numpy.zeros(len(code_orp),dtype='uint8')
    nezastavene = bydleni.copy()
    for i in xrange(len(code_orp)):
        colRow = string.split(code_orp[i])
        c = int(colRow[0])
        r = int(colRow[2])
        if code_orp[i] in kv_cell_zsj:
            k_index.append(i)
        if kr_mask [c-1][r-1]==1:
            nezastavene[i]=1
    print "... Numpy array done - s maskou bydleni, nezastavene a cell_popul"

    # prochazeni a aktualizace pravdepodobnostni mapy
    # pocitam pro nezastavene bunky pravdepodobnosti
    sit_Prob={}
    for i in xrange(len(nezastavene)):
       if nezastavene[i]==1:
                cell_temp = dCell[i]
                pop = ne.evaluate("exp(cell_temp/1000. * beta * (-1))*cell_popul")
                sit_Prob[code_orp[i]]=numpy.sum(pop)
                if i in range(0,180000,3000):
                    print i, time.time()

    file_temp = map_file_folder + 'cellsKVmap.txt'
    soubor = open(file_temp,'w')
    cPickle.dump(sit_Prob,soubor)
    soubor.close()
    print '... KV probability map saved in the file.'

    sit_Prob_KV={}
    for i in k_index:
        cell_temp = dCell[i]
        pop = ne.evaluate("exp(cell_temp/1000. * beta * (-1))*cell_popul") # * bydleni
        sit_Prob_KV[code_orp[i]]=numpy.sum(pop)
        print 'sit_prob_KV: %s : %s'%(code_orp[i],sit_Prob_KV)
        if i in range(1000,180000,1000):
                print i

    # nacteni pravdepodobnostni mapy ze souboru a nacteni do vrstvy
    soubor = open(file_temp,'r')
    sit_Prob = cPickle.load(soubor)
    soubor.close()

    # prevede slovnik s pravdepodobonostmi na pole sit_P[4][415]
    sit_P = numpy.zeros(cN*rN).reshape(cN,rN)  # naplneni prazdneho pole s bunkami
    for i in sit_Prob.keys():
        b = string.split(i)
        c = int(b[0])
        r = int(b[2])
        sit_P[c-1][r-1]=sit_Prob[i]

    prob_pc = []
    for c in xrange(cN):
        for r in xrange(rN):
            okoli = sit_P[(c-1):(c+2),(r-1):(r+2)]  # cluster okoli = 8
            okoli_P = numpy.prod(okoli)
            if numpy.size(okoli)==0:                # okrajove bunky ORP
                okoli_P = 0
            cr = str(c+1)+' - '+str(r+1)
            prob_pc.append([cr, okoli_P])

    sitKV_P = {}
    for i in prob_pc:
        sitKV_P[i[0]]=i[1]
    return sitKV_P,sit_Prob_KV

def prob_s_map(gp,layer,dict_zsj_cr, zsj,cell_all_pop, dCell, f,map_file_folder,beta=2):
    """vypocet pravdepodobnostni mapy pro S"""
    # nacte kody bunek v ORP (odpovida vzdalenostem v d_Cell)
    file_temp = map_file_folder + 'cellsORP.txt'
    soubor = open(file_temp,'r')
    code_orp = cPickle.load(soubor)
    soubor.close()

    #test jakub
    cond = '"KOD_ZSJ_P" = \''+zsj+'\''
    cond_zsj = []
    s_cell_zsj = []
####    temp = dict((k,v) for k,v in dict_zsj_cr[zsj].iteritems() if v in f)
####    s_cell_zsj = temp.keys()
####    cond_zsj = dict_zsj_cr[zsj].keys()
    rows = gp.SearchCursor(layer, cond)
    row = rows.Next()
    while row:
        cond_zsj.append(row.Col_Row)
        if row.funkce in f:  #if row.funkce == f:
            s_cell_zsj.append(row.Col_Row)
        row = rows.Next()
    del row, rows

    # vytvoreni indexu pro bunku prislusnou v ZSJ
    zsj_index = []
    for i in cond_zsj:
        zsj_index.append(code_orp.index(i))

    # vytvoreni poli s identifikatory bydleni
    bydleni = numpy.zeros(len(code_orp))
    cell_popul = numpy.zeros(len(code_orp))
    s_index = []
    for i in zsj_index:
        colRow = string.split(code_orp[i])
        c = int(colRow[0])
        r = int(colRow[2])
        # vytvori pole cell_popul, kde bude hodnota populace pouze pro bunky z daneho zsj
        if (cell_all_pop[c-1][r-1] > 0): 
            bydleni[i]=1
            cell_popul[i]=cell_all_pop[c-1][r-1]
        elif code_orp[i] in s_cell_zsj:
            s_index.append(i)
    print 'len s_index', len(s_index)
    if len(s_index)>10:
        print 'par s_index', s_index[0:10]
    else:
        print 'par s_index', s_index
    # prochazeni a aktualizace pravdepodobnostni mapy
    # pocitam pro bunky bydleni pravdepodobnosti
    sit_Prob={}
    for i in xrange(len(bydleni)):
        if bydleni[i]==1:
            cell_temp = dCell[i][0]
            pop = ne.evaluate("exp(cell_temp/1000. * beta * (-1))*cell_popul*bydleni")
            sit_Prob[code_orp[i]]=numpy.sum(pop)
####            if i in range(1000,180000,1000):
####                print i

#####    file_name = 'd:/grillst/udrzhra/map_files/Smap_orp.txt'
#####    soubor = open(file_name,'r')
#####    sit_Prob = cPickle.load(soubor)
#####    soubor.close()

    sit_Prob_S={}
    for i in s_index:
#        print 'zsj %s scell: %s'%(zsj,i)
        dis = dCell[i][0]/1000.0 #*bydleni
        dis *= beta
        dis *= (-1)
        dis = numpy.exp(dis)
        pop = dis*bydleni*cell_popul
        sit_Prob_S[code_orp[i]]=numpy.sum(pop)
#        print '... sit_prob_S: %s : %s'%(code_orp[i],sit_Prob_S)
        if i in range(1000,180000,1000):
                print i

    file_name = map_file_folder+'cellsSmap_'+zsj+'.txt'
    soubor = open(file_name,'w')
    cPickle.dump(sit_Prob,soubor)
    soubor.close()

    return sit_Prob, sit_Prob_S

def cell_freq(gp,layer,workspace,frequency_fields,f):
    '''fce vrati pole[slovniky {kod ZSJ: pocet bunek dane funkce}]'''
    frequency_table = workspace + "/table_cell_freq"
#    frequency_fields = '"funkce;KOD_ZSJ_P"'
    try:
        gp.Frequency(layer, frequency_table ,frequency_fields)
    except:
        print gp.GetMessages()
    bi_dict = {}
    bh_dict = {}
#    s_dict = {}
    kv_dict = {}
    sbi_dict = {}
    sbh_dict = {}
    k = []
    rows = gp.SearchCursor(frequency_table)
    row = rows.next()
    while row:
        k.append(row.KOD_ZSJ_P)
        if f == 0:
            if row.funkce == 'BI':
                bi_dict[row.KOD_ZSJ_P]=row.FREQUENCY
            elif row.funkce == 'BH':
                bh_dict[row.KOD_ZSJ_P]=row.FREQUENCY
#            elif row.funkce in ['S','BI_S','BH_S']:
#                s_dict[row.KOD_ZSJ_P]=row.FREQUENCY
            elif row.funkce == 'BI_S':
                sbi_dict[row.KOD_ZSJ_P]=row.FREQUENCY
            elif row.funkce == 'BH_S':
                sbh_dict[row.KOD_ZSJ_P]=row.FREQUENCY
            elif row.funkce == 'KV':
                kv_dict[row.KOD_ZSJ_P]=row.FREQUENCY
            row=rows.next()
        else:
            if row.funkce == 'BI':
                bi_dict[row.KOD_ZSJ_P]=row.FREQUENCY
            elif row.funkce == 'BH':
                bh_dict[row.KOD_ZSJ_P]=row.FREQUENCY
#            elif row.funkce in ['S','BI_S','BH_S']:
#                s_dict[row.KOD_ZSJ_P]=row.FREQUENCY
            elif row.funkce == 'BI_S':
                sbi_dict[row.KOD_ZSJ_P]=row.FREQUENCY
            elif row.funkce == 'BH_S':
                sbh_dict[row.KOD_ZSJ_P]=row.FREQUENCY
            elif row.funkce == 'KV':
                kv_dict[row.KOD_ZSJ_P]=row.FREQUENCY
            row=rows.next()
    del row, rows
    s_dict = {}
    for i in k:
        if sbi_dict.has_key(i):
            sbi = sbi_dict[i]
        else:
            sbi = 0
        if sbh_dict.has_key(i):
            sbh = sbh_dict[i]
        else:
            sbh = 0
        s_dict[i]=sbi + sbh
    return bi_dict, bh_dict, s_dict, kv_dict, sbi_dict, sbh_dict

def cell_pop(gp,cN,rN,layer,water_file,bi,bh):
    '''funkce vraci matice s poctem obyvatel v bunce'''
    rows = gp.SearchCursor(layer)
    row = rows.next()
    cell_bi_pop = numpy.zeros(cN*rN).reshape(cN,rN)
    cell_bh_pop = numpy.zeros(cN*rN).reshape(cN,rN)
    cell_all_pop = numpy.zeros(cN*rN).reshape(cN,rN)    # matice, kde veskere obyvtelstvo
    kr_mask = numpy.zeros(cN*rN).reshape(cN,rN)

    # omezi moznost alokace do vody
    soubor = open(water_file,'r')
    water = cPickle.load(soubor)
    soubor.close()

#    for c in xrange(cN):
#        for r in xrange(rN):
#            cell_bi_pop[c,r]=-1
    while row:
        b = string.split(row.Col_Row)
        c = int(b[0])
        r = int(b[2])
        kod = row.KOD_ZSJ_P
        funkce = row.funkce
        if (funkce == 'BI') and (bi.has_key(kod)):
            cell_bi_pop[c-1,r-1] = bi[kod]
            cell_all_pop[c-1,r-1] = bi[kod]
        elif (funkce == 'BH') and (bh.has_key(kod)):
            cell_bh_pop[c-1,r-1] = bh[kod]
            cell_all_pop[c-1,r-1] = bh[kod]
        elif (funkce == 'KR') and (row.Col_Row not in water):
            kr_mask[c-1,r-1] = 1
        row=rows.next()
    del row, rows
    return cell_bi_pop,cell_bh_pop, cell_all_pop, kr_mask

def cell_pop_density(dict_zsj,bi_cell,bh_cell):
    '''funkce vraci slovniky s kodem zsj a prumernym poctem obyvatel na bunku'''
    avg_hab_bi = {} # slovnik {kod ZSJ:prumer pop za BI}
    avg_hab_bh = {} # slovnik {kod ZSJ:prumer pop za BH}
    for i in range(len(dict_zsj)):
        kod = dict_zsj[i][0]
        if (bi_cell.has_key(kod)) and (bi_cell[kod]<>0):
            avg_hab_bi[kod] = dict_zsj[i][1]/float(bi_cell[kod])
        else:
            avg_hab_bi[kod] = 0
        if (bh_cell.has_key(kod)) and (bh_cell[kod]<>0):
            avg_hab_bh[kod] = dict_zsj[i][2]/float(bh_cell[kod])
        else:
            avg_hab_bh[kod] = 0
    return avg_hab_bi, avg_hab_bh

def write_value_zsj(gp,layer,field, dict_value):
    '''propise hodnoty do tabulky ZSJ'''
    # existence, zda existuje sloupec ve vrstve
    listField = []
    fieldList = gp.ListFields(layer)
    fieldListOne = fieldList.Next()
    while fieldListOne:
        listField.append(fieldListOne.name)
        fieldListOne = fieldList.Next()
    del fieldList, fieldListOne
    if field not in listField:
        gp.addfield(layer, field, "short")

    # update hodnot
    rows = gp.UpdateCursor(layer)
    row = rows.Next()
    while row:
        kod = row.KOD_ZSJ_P
        if dict_value.has_key(kod):
            row.SetValue(field,dict_value[kod])
        else:
            row.SetValue(field,0)
        rows.UpdateRow(row)
        row = rows.Next()
    del rows, row
    return "... Propsano"

####def write_fields(f,table_zsj,ukazatel):
####    if f == 0:
####        for ukazatel in [bi_cell, bh_cell, s_cell, kv_cell]:
####            if ukazatel == bi_cell: field_ukazatel = 'bi_cell'
####            elif ukazatel == bh_cell: field_ukazatel = 'bh_cell'
####            elif ukazatel == s_cell: field_ukazatel = 's_cell'
####            elif ukazatel == s_need: field_ukazatel = 's_need'
####            elif ukazatel == kv_cell: field_ukazatel = 'kv_cell'
####            write_value_zsj(table_zsj, field_ukazatel,ukazatel)
####    else:
####        for ukazatel in [bi_cell, bh_cell, s_cell, kv_cell,s_need]:
####            if ukazatel == bi_cell: field_ukazatel = 'bi_cell_1'
####            elif ukazatel == bh_cell: field_ukazatel = 'bh_cell_1'
####            elif ukazatel == s_cell: field_ukazatel = 's_cell_1'
####            elif ukazatel == s_need: field_ukazatel = 's_need_1'
####            elif ukazatel == kv_cell: field_ukazatel = 'kv_cell_1'
####            write_value_zsj(table_zsj, field_ukazatel,ukazatel)
####    return

def calc(gp,layer_new,zsj_new,orp_new,s_norm,workspace,cN,rN,h5file_S,h5file_KV,water_file,map_file_folder):
    '''calc() - vlastni vypocet pravdepodobnostni mapy S, KV a jejich alokace'''
    
    # prahovy pocet obyvatel pro vznik bunky S / tabulka s_norm
    eco_const = udrzhra_functions.read_value_table(gp, s_norm)
    dCellsh5 = tables.openFile(h5file_S,mode='r')
    dCell = dCellsh5.root.precalculation.cellDist
    dCellsh5_KV = tables.openFile(h5file_KV,mode='r')
    dCell_KV = dCellsh5_KV.root.precalculation.cellDist.cols.distance

    # statistiky za ZSJ do pameti
    selField_zsj=('KOD_ZSJ_P','zsjBytRdPopul','zsjBytBdPopul')
    table_zsj = zsj_new
    print '... Select ZSJ layer: ', table_zsj
    dict_zsj = dp.mem_array_zsj(gp,table_zsj,selField_zsj)
    zsj = []   # slovnik s kody ZSJ
    for i in dict_zsj:
        zsj.append(i[0])

    # vrstva site s bunkami do pameti
    layer = layer_new
    print '... Select cell layer: ',layer
    
    # nacteni hodnot za ORP
    table_orp = orp_new
    selField_stav = ('orpBytAllPopul')
    dict_stav = dp.dict_schema(gp,table_orp,selField_stav)
    print '... Select ORP values: ',dict_stav

    # zjisteni poctu bunek s funkcemi bydleni v jednotlivych ZSJ
    frequency_fields = '"funkce;KOD_ZSJ_P"'
    bi_cell, bh_cell, s_cell, kv_cell,sbi_cell, sbh_cell = cell_freq(gp,layer,workspace,frequency_fields,0)
    for ukazatel in [bi_cell, bh_cell, s_cell, kv_cell, sbi_cell, sbh_cell]:
            if ukazatel == bi_cell: field_ukazatel = 'bi_cell'
            elif ukazatel == bh_cell: field_ukazatel = 'bh_cell'
            elif ukazatel == s_cell: field_ukazatel = 's_cell'
            elif ukazatel == kv_cell: field_ukazatel = 'kv_cell'
            elif ukazatel == s_cell: field_ukazatel = 'sbi_cell'
            elif ukazatel == s_cell: field_ukazatel = 'sbh_cell'
            write_value_zsj(gp,table_zsj, field_ukazatel,ukazatel)
###    frequency_fields = '"funkce;KOD_ZSJ_P"'
###    bi_cell, bh_cell, s_cell, kv_cell,sbi_cell, sbh_cell = cell_freq(gp,layer,workspace,frequency_fields,1)
    print "... Number of cell's functions in ZSJ calculated."
    # zjisteni prumerneho poctu obyvatel na bunku BI, BH dle ZSJ
    avg_hab_bi, avg_hab_bh = cell_pop_density(dict_zsj,bi_cell,bh_cell)
    print "... Population density in cells within ZSJ calculated."
    # vytvoreni matice, kde v kazde bunce bude pocet obyvatel
    cell_bi_pop,cell_bh_pop,cell_all_pop, kr_mask = cell_pop(gp,cN,rN,layer,water_file,avg_hab_bi,avg_hab_bh)
    print "... Matrices with population within cells calculated."

    map_files_base = map_file_folder
#    docasne uklada v souboru
###    soubor = open(map_files_base + 'cell_all_pop.txt','w')
###    cPickle.dump(cell_all_pop,soubor)
###    soubor.close()
###    soubor = open(map_files_base + 'kr_mask.txt','w')
###    cPickle.dump(kr_mask,soubor)
###    soubor.close()
###    soubor = open(map_files_base + 's_cell.txt','w')
###    cPickle.dump(s_cell,soubor)
###    soubor.close()
###    soubor = open(map_files_base + 'kv_cell.txt','w')
###    cPickle.dump(kv_cell,soubor)
###    soubor.close()
#     docasne ulozeno

    # docasne nacte ze souboru
#####    soubor = open(map_files_base + 'cell_all_pop.txt','r')
#####    cell_all_pop = cPickle.load(soubor)
#####    soubor.close()
#####    soubor = open(map_files_base + 'kr_mask.txt','r')
#####    kr_mask = cPickle.load(soubor)
#####    soubor.close()
#####    soubor = open(map_files_base + 's_cell.txt','r')
#####    s_cell = cPickle.load(soubor)
#####    soubor.close()
#####    soubor = open(map_files_base + 'kv_cell.txt','r')
#####    kv_cell = cPickle.load(soubor)
#####    soubor.close()
#####    # docasne nacteno ze souboru
#####    print "Ze souboru nacteno."

#    sMap,sMap_S = prob_s_map(layer,'145165',cell_all_pop,dCell,'S',2) # testovaci S Map

    # nacteni fce bunek, jejich cr a ZSJ kod
    dict_zsj_cr = {}
    cond = '"ORP" = 1'
    rows = gp.SearchCursor(layer, cond)
    row = rows.Next()
    while row:
        kod = row.KOD_ZSJ_P
        cr = row.Col_Row
        if kod not in dict_zsj_cr:
            dict_zsj_cr[kod] = {}
        dict_zsj_cr[kod][cr] = row.funkce
        row = rows.Next()
    del row, rows

    # ziskani indexu kodu ZSJ
    kod_zsj = []
    for i in xrange(len(dict_zsj)): kod_zsj.append(dict_zsj[i][0])

    print '... Processing of S, KV numbers for areas ...'
    # slovnik {zsj_kod:pocet S bunek}
    s_count = s_cell
    kv_count = 0
    for i in kv_cell.values():      # secte pocet bunek KV za cele ORP
        kv_count = kv_count + i
    ###print '... s_count: %s\nkv_count: %s' %(s_count,kv_count)

    print '... Processing of probability map for KV ...'
    kvMap, kvMap_KV = prob_kv_map(gp,layer,dict_zsj_cr,zsj_new,cell_all_pop,kr_mask,dCell_KV,cN,rN,map_file_folder,2)
    print "... P map for KV done."

    print '... Processing S cell allocation ...'
    s_need = {}
    s_add = []
    s_rem = []

    for i in range(len(dict_zsj)):  
        kod = dict_zsj[i][0]        # zjisteni kodu zsj, pro ktery pocitam
        print 'Processing S for ZSJ: %s in time %s'%(kod, time.time())
        if s_count.has_key(kod):
            s_t = s_count[kod]
        else:
            s_t = 0
        s_t1  = dict_zsj[i][1]/eco_const['orpSobyvPrah']
        d_s = s_t1 - s_t
        d_s = math.floor(d_s) # odriznuti des. casti , drive zaokrouhleni   int(round(d_s))
        s_need[kod]=d_s
        if d_s == 0:
            pass
        else:
            sMap,sMap_S = prob_s_map(gp,layer,dict_zsj_cr,kod,cell_all_pop,dCell,['S','BI_S','BH_S'],map_file_folder,2)           # 2 ... Beta koeficient
            a = alok(sMap,sMap_S,d_s) # alokace bunek s funkci S
            if d_s > 0:
                s_add = s_add + a
            else:
                s_rem = s_rem + a

    soubor = open(map_files_base + 's_add.txt','w')
    cPickle.dump(s_add,soubor)
    soubor.close()
    soubor = open(map_files_base + 's_rem.txt','w')
    cPickle.dump(s_rem,soubor)
    soubor.close()

    frequency_fields = '"funkce;KOD_ZSJ_P"'
    bi_cell, bh_cell, s_cell, kv_cell,sbi_cell, sbh_cell = cell_freq(gp,layer,workspace,frequency_fields,1)  # aktualni prepocet poctu bunek s novymi funkcemi
    for ukazatel in [bi_cell, bh_cell, s_cell, kv_cell, s_need,sbi_cell, sbh_cell]:
        if ukazatel == bi_cell: field_ukazatel = 'bi_cell_1'
        elif ukazatel == bh_cell: field_ukazatel = 'bh_cell_1'
        elif ukazatel == s_cell: field_ukazatel = 's_cell_1'
        elif ukazatel == s_need: field_ukazatel = 's_need'
        elif ukazatel == s_cell: field_ukazatel = 'sbi_cell_1'
        elif ukazatel == s_cell: field_ukazatel = 'sbh_cell_1'
        elif ukazatel == kv_cell: field_ukazatel = 'kv_cell_1'
        write_value_zsj(gp,table_zsj, field_ukazatel,ukazatel)
        
    feacNew = layer # + 'skv'
#    gp.CopyFeatures(layer, feacNew)
    #alok_update_new(gp,s_add,s_rem,'S',feacNew)

    # umisteni KV bunek
    cellArea = 5625. # 75x75 [m]
    kv_add = []
    kv_rem = []
    kv_t1  = dict_stav['orpBytAllPopul']*(eco_const['p_orpAreaRetail']/cellArea)
    print kv_t1
    kv_t = kv_count
    d_kv = kv_t1 - kv_t
    d_kv = math.floor(d_kv)
    if d_kv == 0:
        pass
    else:
        a = alok(kvMap,kvMap_KV,d_kv)
        if d_kv > 0:
            kv_add = kv_add + a
        else:
            kv_rem = kv_rem + a
    
    dCellsh5.close()
    dCellsh5_KV.close()

    # spoji prislusne mapy S do jedne
    lsmap = {}
    count = 0
    suma = 0
    for i in os.listdir(map_file_folder):   #for i in os.listdir('d:/udrzhra/map_files/'):
        if i[0:9]=='cellsSmap':
            soubor_name = map_file_folder + i # soubor_name = 'd:/udrzhra/map_files/'+i
            soubor = open(soubor_name,'r')
            prob = cPickle.load(soubor)
            soubor.close()
            for key in prob:
                lsmap[key] = prob[key]
            ###print i, count, len(prob), len(lsmap)
            suma = suma + len(prob)
            count = count + 1
    #print suma, len(lsmap)
    file_name_S = map_file_folder + 'Smap_orp.txt'
    soubor = open(file_name_S,'w')
    cPickle.dump(lsmap,soubor)
    soubor.close()
    print '... S probability map for ORP saved.'

    # propise atraktivitu KV funkci do vrstvy
    # vytvori novy sloupec
    listField = []
    fieldList = gp.ListFields(feacNew)
    fieldListOne = fieldList.Next()
    while fieldListOne:
        listField.append(fieldListOne.name)
        fieldListOne = fieldList.Next()
    del fieldList, fieldListOne
    newField = ["P_KV","P_S"]
    for field in  newField:
        if field not in listField:
            gp.addfield(feacNew, field, "double")

    file_name = map_file_folder + 'cellsKVmap.txt'
    soubor = open(file_name,'r')
    sit_Prob_KV = cPickle.load(soubor)
    soubor.close()
    soubor = open(file_name_S,'r')
    sit_Prob_S = cPickle.load(soubor)
    soubor.close()

    alok_update_new(gp,s_add,s_rem,kv_add,kv_rem,feacNew, sit_Prob_KV, sit_Prob_S)

    

    
###    orpCond = '"ORP" = 1'
###    rows = gp.UpdateCursor(feacNew,orpCond)
###    row = rows.Next()
###    count = 0
###    while row:
###        if count in range(0,180000,1000):
###            print count
###        cr = row.Col_Row
###        if sit_Prob.has_key(cr):
###            row.P_KV = sit_Prob[cr]
###        rows.UpdateRow(row)
###        count = count + 1
###        row = rows.Next()
###    del rows, row

    # propise atraktivitu S funkci do vrstvy
    # soubor_name = 'd:/udrzhra/map_files/Smap_orp.txt'
   
###    orpCond = '"ORP" = 1'
####    feac = workspace + '/tabor_obyvatelstvo/tabor_sit75_41skv'
###    rows = gp.UpdateCursor(feacNew,orpCond)
###    row = rows.Next()
###    count = 0
###    while row:
###        if count in range(0,180000,10000):
###            print count
###        cr = row.Col_Row
###        if sit_Prob.has_key(cr):
###            row.P_S = sit_Prob[cr]
###        rows.UpdateRow(row)
###        count = count + 1
###        row = rows.Next()
###    del rows, row


if __name__ == "__main__":
    print 'Zaciname ...', time.ctime(time.time())
    print '...'
    cas0 = time.time()
    
    gp = win32com.client.Dispatch("esriGeoprocessing.GpDispatch.1")
    root = 'P:/Projekty/udrzhra/data/'                # zmenit podle umisteni grillst/   udrzhra_tabor75.gdb
    h5file_S = 'P:/Projekty/udrzhra/data/dCells_centroids.h5'                            # soubor s tabulou vzdalenosti h:/dCells.h5
    h5file_KV = 'P:/Projekty/udrzhra/data/dCells_cen.h5'
    workspace = root + 'simulace_81.gdb/'    # workspace
    gp.OverwriteOutput = 1
    gp.workspace = workspace
    cN = 574
    rN = 574
    map_file_folder = 'P:/Projekty/udrzhra/data/map_files/'

    # nastaveni datovych zdroju
    zsj_new = workspace + 'output/zsjStat_81'
    layer_new = workspace+ 'output/tabor_sit75_1'
    orp_new = workspace + 'output/orpStat_81'
    s_norm = workspace + 's_normative'

    # vlastni kalkulace
    calc(gp,layer_new,zsj_new,orp_new,s_norm,workspace,cN,rN,h5file_S,h5file_KV,map_file_folder)

    cas = time.time()- cas0
    print '...'
    print 'Skript dokoncen ', time.ctime(time.time()), 'Cas vypoctu: ',cas,'s'