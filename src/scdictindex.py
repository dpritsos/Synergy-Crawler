


from scgenrelerner_svmbased import *



def label_properly(webpg_vect_l, vect_l_chnk):
    #Thread or MultiProcess Bellow Part or it will NEVER-END####################################################################
    new_webpg_vect_l = list()
    print("in")
    for pg_vect in webpg_vect_l:
        #pg_vect = webpg_vect_l[i]
        #i = webpg_vect_l.index(pg_vect) # get the index here because it seems that 'in' operator prevent this... Not know why yet
        enc_pg_vect = pg_vect.keys()
        for i in range(len(enc_pg_vect)):
            enc_pg_vect[i] = enc_pg_vect[i].encode("utf-8")
        libsvm_pg_vect = dict() 
        for set_term in Gset_terms:
            if set_term.encode("utf-8") in enc_pg_vect: #Is the 'in' operator cases copy of the pg_vect?
                libsvm_pg_vect[ Gset_terms.index(set_term) ] = pg_vect[set_term]
        new_webpg_vect_l.append( libsvm_pg_vect )
    print("out")
    vect_l_chnk.put( new_webpg_vect_l )
    print("put DONE!")
    
Gset_terms = list()
vect_l_chnk = Queue()



    def make_libsvm_sparse_vect(self, webpg_vect_l):
        set_vect = dict()
        #Creat the Global Term Vector of Frequencies
        for pg_vect in webpg_vect_l:
            pg_trm_l = pg_vect.keys()
            for pg_trm in pg_trm_l:
                if pg_trm in set_vect: 
                    set_vect[pg_trm] += pg_vect[pg_trm]
                else:
                    set_vect[pg_trm] = pg_vect[pg_trm]
        set_terms = set_vect.keys()
        Gset_terms.extend(set_terms)
        print("make_libsvm_sparse_vect: First Part Done")
        print(len(set_vect))
        #set_terms.sort()
        new_webpg_vect_l = list()
        chunck_wp_l =list()
        webpg_vect_l_size = len(webpg_vect_l)
        chnk_size = webpg_vect_l_size/12
        chnk_remain = webpg_vect_l_size%12
        pre_i = 0
        for i in range(chnk_size, webpg_vect_l_size, chnk_size):
            chunck_wp_l.append( webpg_vect_l[ pre_i : i ] )
            pre_i = i
        if chnk_remain != 0 :
            chunck_wp_l[11].extend( webpg_vect_l[ len(chunck_wp_l) : (len(chunck_wp_l) + chnk_remain) ] ) 
        print("Chuncking Done!")
        labeling_ps = list()
        for i in xrange(len(chunck_wp_l)):  
            labeling_ps.append( Process(target=label_properly, args=(chunck_wp_l[i],vect_l_chnk)) )
        for lbl_p in labeling_ps:
            lbl_p.start()
        print("Starting Done!")
        for i in xrange(len(chunck_wp_l)):
            new_webpg_vect_l.extend(vect_l_chnk.get())
        print("concatenation Done!")
        for lbl_pp in labeling_ps:
            lbl_pp.join()
            print("Process End")
        print("Processing Done!")
        #Thread or MultiProcess Bellow Part or it will NEVER-END####################################################################
        #new_webpg_vect_l = list()
        #for pg_vect in webpg_vect_l:
            #pg_vect = webpg_vect_l[i]
            #i = webpg_vect_l.index(pg_vect) # get the index here because it seems that 'in' operator prevent this... Not know why yet
        #    libsvm_pg_vect = dict() 
        #    for set_term in set_terms: 
        #        if set_term in pg_vect: #Is the 'in' operator cases copy of the pg_vect? 
        #            libsvm_pg_vect[ set_terms.index(set_term) ] = pg_vect[set_term]
        #        new_webpg_vect_l.append( libsvm_pg_vect )
        
        print("make_libsvm_sparse_vect: Second Part Done")
        return (new_webpg_vect_l, set_vect, set_terms)