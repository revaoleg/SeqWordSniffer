import os, sys, math, shelve, string, time, random

class IO:
    def __init__(self):
        self.oParser = None
    
    def __len__(self):
        if self.oParser:
            return len(self.oParser.getSequence())
        else:
            return 0
    
    # fasta - FASTA formated collection of sequences    
    def _filename_compatibility(self,fname):
        if not fname:
            return
        for symbol in (" ",">","<","*","?",":","|"):
            fname = fname.replace(symbol,"_")
        return fname
    
    def random_id(self,length=1):
        id = ""
        for i in range(length):
            id += str(random.randint(0,9))
        return id

    def save(self,strText,fname=None):
        if not fname:
            fname = asksaveasfilename([("All files", "*.*")])
        fname = self._filename_compatibility(fname)
        if not fname:
            return
        ofp = open(fname, "w")
        ofp.write(strText)
        ofp.flush()
        ofp.close()
        return fname
    
    def open(self,fname=None):
        if fname and not os.path.exists(fname):
            return None,fname
        if not fname:
            fname = askfilename([("All files", "*.*")])
        if not fname:
            return None,fname
        ofp = open(fname)
        data = ofp.read()
        ofp.close()
        return data,fname
    
    def new_folder(self,folder_name):
        try:
            os.mkdir(folder_name)
            return folder_name
        except:
            return None
    
    # copy text files
    def copy(self,inpath,outpath):
        if not os.path.exists(inpath):
            return
        try:
            f = open(inpath)
            data = f.read()
            f.close()
            f = open(outpath,"w")
            f.write(data)
            f.close()
        except:
            return
        return outpath
    
    # return dictionary of sequences and the path
    def openFasta(self,path=None,filetypes=[]):
        if not filetypes:
            filetypes=[("FASTA files", "*.fasta"),
                       ("FASTA files", "*.fas"),
                       ("FASTA files", "*.fsa"),
                       ("FASTA files", "*.fst")]        
        self.oParser = Parser(path,filetypes)
        return self.oParser.getSequence(),self.oParser.getPath()
    
    # fasta - FASTA formated collection of sequences    
    def saveFasta(self,fasta,fname=None):
        if not fname:
            fname = asksaveasfilename([("All files", "*.*"),
                                       ("FASTA files", "*.fasta"),
                                       ("FASTA files", "*.fas"),
                                       ("FASTA files", "*.fsa"),
                                       ("FASTA files", "*.fna"),
                                       ("FASTA files", "*.fst"),])
        fname = self._filename_compatibility(fname)
        if not fname:
            return
        # check filename extension
        if fname.find(".") == -1 or fname.split('.')[-1] not in ('fasta','fas','fsa','fna','fst'):
            fname += ".fst"
        return self.save(fasta,fname)
    
    def openGBK(self,path=None,datatype="SEQLIST",filetypes=[]): # datatype - seqlist/dataset/sequence/genemap/all
        if not filetypes:
            filetypes=[("GBK files", "*.gbk"),
                       ("GBK files", "*.gb")]        
        self.oParser = Parser(path,filetypes)
        if datatype.upper == "SEQLIST":
            dataset = self.oParser.getDataSet()
            seqname = "%s [%s]" % (dataset['Sequence name'],dataset['Accession'])
            return {seqname:self.oParser.getSequence()},self.oParser.getPath()
        elif datatype.upper == "DATASET":
            return self.oParser.getDataSet()
        elif datatype.upper == "SEQUENCE":
            return self.oParser.getSequence()
        elif datatype.upper == "GENEMAP":
            return self.oParser.getDataSet()['Gene map']
        elif datatype.upper() == "ALL":
            return self.oParser.getAll()
        else:
            return
        
    def saveGBK(self,fname,seq="",start=0,stop=None,locus_name="",comments=""):
        if not self.oParser:
            return
        fname = self._filename_compatibility(fname)
        if not fname:
            return
        heading,body,sequence,shift = self.oParser.getGBK_Components(start,stop,seq,locus_name,comments)
        self.save("\n".join([heading,body,self.oParser.format_dna_seq(sequence)]),fname)

    def openDBFile(self,fname=None, dbkey='$db$', splkey='$suppl$'):
        if not fname or not os.path.exists(fname):
            return
        try:
            f = shelve.open(fname)
            self.oParser = {dbkey:f[dbkey],splkey:{}}
            if f.has_key(splkey):
                self.oParser[splkey].update(f[splkey])
            f.close()
            return fname,self.oParser[dbkey],self.oParser[splkey]
        except:
            return None

    def save_genes2fasta(self,gbkpath,outpath,flg_protein=True,lb=0,rb=None,filetypes=None):
        if not filetypes:
            filetypes=[("GBK files", "*.gbk"),
                       ("GBK files", "*.gb")]        
        self.oParser = Parser(gbkpath,filetypes)
        output = self.oParser.genes2fasta(flg_protein,lb,rb)
        if not output:
            return
        self.save(output,outpath)
        return outpath
    
    def svg(self,X=5,Y=25,width=800,height=30,flg_finish=True):
        if not self.oParser:
            return ""
        svg = ["<text X=\"%d\" Y=\"%d\">%s</text>" % (X,Y+height/2,self.oParser.getName())]
        svg.append("<text X=\"%d\" Y=\"%d\">%s</text>" % (width-50,Y+height/2,str(len(self))+" bp."))
        svg.append("<line x1=\"%d\" y1=\"%d\" x2=\"%d\" y1=\"%d\" fill=\"none\" stroke=\"%s\" stroke-width=\"%f\" /" %
            (X+50,Y+height/2,width-10,Y+height/2,"red",3.0))
        c = float(width-100)/len(self)
        for gene in self.oParser["Gene map"]:
            try:
                lb,rb = map(lambda s: int(s)-self.oParser['Left border']+1,gene.split("-"))
            except:
                lb,rb = map(lambda s: int(s)-self.oParser['Left border']+1,gene.split(".."))
            if (self.oParser['Gene map'][gene]['remark'].find("hypothetical") > -1 or
                self.oParser['Gene map'][gene]['name'].find("hypothetical") > -1 or
                self.oParser['Gene map'][gene]['remark'].find("unknown") > -1 or
                self.oParser['Gene map'][gene]['name'].find("unknown") > -1):
                color = "grey"
            else:
                color = "green"
            bar_height = (height-7)/2
            shift = 0
            if self.oParser['Gene map'][gene]['direction'] == "rev":
                shift = height-bar_height
            svg.append("<rect x=\"%f\" y=\"%f\" width=\"%f\" height=\"%f\" style=\"fill:%s;stroke:%s\" /" %
                (c*lb,Y+shift,c*(rb-lb),bar_height,color,"grey"))
        if flg_finish:
            svg.insert(0,"<svg xmlns=\"http://www.w3.org/2000/svg\" viewbox=\"0 0 %d %d\">" % (width,height))
            svg.append("</svg>")
        return "\n".join(svg)
        
##################################
class Parser:
    def __init__(self, path=None, ftypes=[]):
        # ATTRIBUTES
        self.strSeq = ''
        self.path = path
        self.DSet = {'Sequence name':'',
                      'Sequence description':'',
                      'Accession':'',
                      'Total sequence length':0,
                      'Locus length':0,
                      'Left border':1,
                      'Frame':0,
                      'Gene map':None,
                      'Path':"",
                      }        
        if not self.path:
            if ftypes:
                self.path = askopenfilename(filetypes=ftypes)
            else:            
                self.path = askopenfilename(filetypes=[("All files", "*.*"),
                                                       ("FASTA files", "*.fas"),
                                                       ("FASTA files", "*.fsa"),
                                                       ("FASTA files", "*.fst"),
                                                       ("FASTA files", "*.fna"),
                                                       ("GeneBank files", "*.gbk"),
                                                       ("GeneBank files", "*.gb"),
                                                       ("GBFF files", "*.gbff")])
        if self.path and os.path.exists(self.path):
            ext = self.path.split(".")[-1]
            if ext in ('gbk','gb'):
                self.openGBK()
            elif ext in ('fas','fst','fsa','fasta'):
                self.openFASTA()
            elif ext in ('gbff'):
                self.openGBFF()
            else:
                pass
        # {'lborder-rborder':[lborder,rborder,dir,gene name,description,remark]}
        self.blast_output = {'Query':'','Sbjct':'','hsps':{}}
        self.codons = {"T":{"T":{"T":"F","C":"F","A":"L","G":"L"},
                       "C":{"T":"S","C":"S","A":"S","G":"S"},
                       "A":{"T":"Y","C":"Y","A":"*","G":"*"},
                       "G":{"T":"C","C":"C","A":"*","G":"W"},
                        },
                   "C":{"T":{"T":"L","C":"L","A":"L","G":"L"},
                       "C":{"T":"P","C":"P","A":"P","G":"P"},
                       "A":{"T":"H","C":"H","A":"Q","G":"Q"},
                       "G":{"T":"R","C":"R","A":"R","G":"R"},
                        },
                   "A":{"T":{"T":"I","C":"I","A":"I","G":"M"},
                       "C":{"T":"T","C":"T","A":"T","G":"T"},
                       "A":{"T":"N","C":"N","A":"K","G":"K"},
                       "G":{"T":"S","C":"S","A":"R","G":"R"},
                        },
                   "G":{"T":{"T":"V","C":"V","A":"V","G":"V"},
                       "C":{"T":"A","C":"A","A":"A","G":"A"},
                       "A":{"T":"D","C":"D","A":"E","G":"E"},
                       "G":{"T":"G","C":"G","A":"G","G":"G"},
                        },
                }

    # METHODS
    
    def __getitem__(self,key):
        if key in self.DSet:
            return self.DSet[key]
        else:
            return ""

    def openFASTA(self):
        seqlist = {}
        objFile = open(self.path)
        line = objFile.read()
        objFile.close()
        for symbol in ("\r","\\"):
            line = line.replace(symbol,"")
        entries = line.split(">")
        if len(entries) < 2:
            return seqlist
        for entry in entries[1:]:
            data = entry.split("\n")
            seqlist[data[0]] = ("".join(map(lambda s: s.replace(" ",""),data[1:]))).upper()
        self.strSeq = seqlist
        f = open("tmp.out","w")
        f.write(seqlist[seqlist.keys()[0]])
        f.close()

    # possible modes: 'Get gene map', 'Get sequence', 'Get gene map with sequence'
    def openGBK(self, mode='Get gene map with sequence'):
        file = open(self.path,'r')
        line = file.readline()
        if line[:5] != 'LOCUS':
            self.openText()
        rb = line.find(" bp")
        line = line[:rb]
        lb = line.rfind(" ")
        self.DSet['Locus length'] = self.DSet['Total sequence length'] = int(line[lb:])
        
        gene = []
        ind = None
        CDS = None
        
        while line:
            line = file.readline()
            if "     source          " in line:
                line = line.replace("complement(","")
                try:
                    self.DSet['Left border'] = int(line[line.find(" ")+1:line.rfind("..")])
                except:
                    try:
                        self.DSet['Left border'] = int(line[line.find("join(")+5:line.find("..")])
                    except:
                        self.DSet['Left border'] = 0
            if line.find("DEFINITION  ")==0:
                self.DSet['Sequence name'] = line[12:-1]
                continue
            if line.find("ACCESSION   ")==0:
                self.DSet['Accession'] = line[12:-1]
                continue
            if line[5:8] == 'CDS' and mode != 'Get sequence':
                ind = None
                CDS = 1
                if len(gene) == 6:
                    self.addGene(gene)
                    gene = []
                values = line[21:].split('.')
                if len(values) < 3:
                    continue
                if values[2][0] == ">" or values[2][0] == "<":
                    values[2] = values[2][1:]
                if values[0].find('complement') >= 0:
                    if values[0].find('join') >= 0:
                        try:
                            gene.append(int(values[0][16:]))
                        except:
                            try:
                                gene.append(int(values[0][17:]))
                            except:
                                print('Error 1 value fot int(): ' + values[0][17:])
                                continue
                                5/0
                                return None
                        try:
                            gene.append(int(values[len(values)-1][:-3]))
                            gene.append('rev')
                        except:
                            continue
                            5/0
                    else:   
                        try:
                            gene.append(int(values[0][11:]))
                        except:
                            try:
                                gene.append(int(values[0][12:]))
                            except:
                                print('Error 2 value fot int(): ' + values[0][12:])
                                continue
                                5/0
                                return None
                        gene.append(int(values[2][:values[2].rfind(")")]))
                        gene.append('rev')
                elif values[0].find('join') >= 0:
                    strand = "dir"
                    try:
                        gene.append(int(values[0][5:]))
                    except:
                        try:
                            gene.append(int(values[0][values[0].find("(")+1:]))
                        except:
                            try:
                                gene.append(int(values[0][values[0].find("complement(")+11:]))
                                strand = "rev"
                            except:
                                print('Error 3 value fot int(): ' + values[0])
                                continue
                                5/0
                                return None
                    try:
                        gene.append(int(values[-1][:values[-1].find(")")]))
                    except:
                        line = file.readline()
                        while line.find(")") == -1:
                            line = file.readline()
                        gene.append(int(line[line.rfind("..")+2:line.find(")")]))
                    gene.append(strand)
                else:
                    try:
                        gene.append(int(values[0]))
                    except:
                        try:
                            gene.append(int(values[0][1:]))
                        except:
                            print('Error 4 value for int(): ' + values[0][1:])
                            continue
                            5/0
                            return None
                    gene.append(int(values[2]))
                    gene.append('dir')
                for i in range(3):
                    gene.append('')
            elif line[21:22] == r"/" and mode != 'Get sequence' and CDS == 1:
                if line[21:27] == '/gene=' and len(gene) == 6:
                    ind = 3
                    gene[ind] = line[28:-1]
                    if gene[ind] != '' and  gene[ind][-1] == "\"":
                        gene[ind] = gene[ind][:-1]
                        ind = None
                elif line[21:30] == '/product=' and len(gene) == 6:
                    ind = 5
                    gene[ind] = line[31:-1]
                    if gene[ind] != '' and  gene[ind][-1] == "\"":
                        gene[ind] = gene[ind][:-1]
                        ind = None
                elif line[21:27] == '/note=' and len(gene) == 6:
                    ind = 4
                    gene[ind] = line[28:-1]
                    if gene[ind] != '' and gene[ind][-1] == "\"":
                        gene[ind] = gene[ind][:-1]
                        ind = None
                elif line[21:34] == '/translation=':
                    CDS = None
                else:
                    pass
            elif line[:6] == 'ORIGIN' and (mode == 'Get sequence' or mode == 'Get gene map with sequence'):
                ind = None
                if len(gene) == 6:
                    self.addGene(gene)
                self.setSequence(file)
                break
            elif (line == '' or line == '\n') and mode != 'Get sequence' and CDS == 1:
                if len(gene) == 6:
                    self.addGene(gene)
                break
            else:
                if ind and mode != 'Get sequence' and CDS == 1:
                    gene[ind] = gene[ind] + " " + line[21:-1]
                    if gene[ind][-1] == "\"":
                        gene[ind] = gene[ind][:-1]
                        ind = None
                    
        file.close()
        if self.DSet['Total sequence length'] != len(self.strSeq) and len(self.strSeq) != 0:
            self.DSet['Locus length'] = self.DSet['Total sequence length'] = len(self.strSeq)
        return
    
    def openGBFF(self):
        pass

    def addGene(self, gene):
        if self.DSet['Total sequence length'] == 0:
            maxnumlen = 8
        else:
            maxnumlen = len(str(self.DSet['Total sequence length']))
        key = (maxnumlen - len(str(gene[0])))*" " + str(gene[0]) + ".." + str(gene[1])
        if self.DSet['Gene map'] == None:
            self.DSet['Gene map'] = {}
        self.DSet['Gene map'][key] = {}
        subkeys = ('start','stop','direction','name','description','remark')
        for i in range(len(subkeys)):
            self.DSet['Gene map'][key][subkeys[i]] = gene[i]
        return
    
    def e2val(self,e):
        try:
            return float(e)
        except:
            values = e.split("e-")
            if len(values) != 2:
                return None
            if not values[0]:
                values[0] = 1.0
            try:
                return float(values[0]) * (10**(-int(values[1])))
            except:
                return None

    def setSequence(self, file):
        seq = file.read()
        for num in range(10):
            seq = seq.replace(str(num),'')
        for symbol in (' ','/','\\','\n'):
            seq = seq.replace(symbol,'')
        self.strSeq = seq.upper()
        return

    def clear(self):
        self.DSet = {'Sequence name':'',
                        'Accession':'',
                        'Sequence description':'',
                        'Total sequence length':0,
                        'Locus length':0,
                        'Left border':1,
                        'Frame':0,
                        'Gene map':{},
                        }

    # INTERFACE

    # trigger
    def do(self, mode, value=None):
        if mode == 'Set mode':
            self.openGBK(value)
        elif mode == "Import gene map from text file":
            self.openText(value)
        elif mode == "Get line":
            self.showTextViewer(value)
        elif mode == "Set debugger":
            return self.trigger("Set debugger",mode)
        elif mode == "Watch debugger":
            return self.trigger("Watch debugger",mode)
        else:
            print('Error mode: ' + mode)

    def getAll(self):
        if self.path:
            return [self.DSet, self.strSeq, self.path]
        else:
            return None

    def getDataSet(self):
        return self.DSet

    def getGeneMap(self):
        if self.path:
            return self.DSet['Gene map']
        else:
            return None
        
    def getSequence(self):
        return self.strSeq
    
    def getPath(self):
        return self.path
    
    def getName(self):
        if self.DSet["Accession"]:
            return self.DSet["Accession"]
        elif self.DSet["Sequence name"]:
            return self.DSet["Sequence name"]
        elif self.DSet["Sequence description"]:
            return self.DSet["Sequence description"]
        else:
            return os.path.basename(self.path)

    def getGBK_Components(self,lb,rb,seq="",locus_name="",comments="",shift=0,space=21,width=80,flg_circular=True):
        pre_heading = pre_features = pre_sequence = post_heading = post_features = post_sequence = ''
        if len(locus_name) > 22:
            locus_name = locus_name[:23]
        curr_time = self.getTime()
        if len(curr_time) == 10:
            curr_time = "0"+curr_time
        seqlength = str(1+rb-lb)
        heading = ["LOCUS       %s" % filter(lambda s: str(s),[locus_name,"%s [%d..%d]" % (self.DSet['Accession'],lb,rb)][0])]
        heading[-1] += " "*(40-len(heading[-1])-len(seqlength)) + seqlength + " bp    DNA     linear   BCT " + curr_time
        heading.append("DEFINITION  %s" % self.DSet['Sequence name'])
        heading.append("ACCESSION   %s" % self.DSet['Accession'])
        heading.append("SOURCE      %s" % self.DSet['Sequence name'])
        heading.append("COMMENT     locus start: %d; locus end: %d" % (lb,rb))
        if comments:
            heading.append("COMMENT     %s" % comments)
        features = ["FEATURES             Location/Qualifiers"]
        features.append("     source          1.."+seqlength)
        features.append("                     /organism=\""+self.DSet['Sequence name']+"\"")
        if len(features[-1]) > width:
            features[-1] = self.format_string(features[-1],width,space)
        heading.append("\n".join(features))

        if not seq:
            if lb==0:
                lb = 1
            elif lb < 1 and not flg_circular:
                lb = 1
            elif lb < 1 and flg_circulra:
                pre_heading,pre_features,pre_sequence,shift = self.getGBK_Components(len(self.strSeq)+lb,len(self.strSeq),
                        locus_name,shift,space,width)
                lb = 1
                
            if rb > len(self.strSeq) and not flg_circular:
                rb = len(self.strSeq)
            elif rb > len(self.strSeq) and flg_circular:
                post_heading,post_features,post_sequence,rshift = self.getGBK_Components(1,rb-len(self.strSeq)+1,
                        locus_name,1+rb-lb,space,width)
                rb = len(self.strSeq)
            seq = pre_sequence+self.getSequence()[lb-1:rb]+post_sequence

        features = []
        genes = list(self.DSet['Gene map'].keys())
        if len(genes) > 1:
            genes.sort()
        for gene in genes:
            try:
                start,stop = map(lambda s: int(s), gene.split("-"))
            except:
                start,stop = map(lambda s: int(s), gene.split(".."))
            if (start < lb and stop <= lb):
                continue
            elif (start >= rb and stop > rb):
                break
            gene_start = start-lb+shift+1
            if gene_start == 0:
                gene_start = 1
            gene_stop = stop-lb+shift+1
            if self.DSet['Gene map'][gene]['direction']=='dir':
                gene_position = "%d..%d" % (gene_start,gene_stop)
            else:
                gene_position = "complement(%d..%d)" % (gene_start,gene_stop)
            features.append("     gene            %s" % gene_position)
            features.append("                     /gene=\"%s\"" % self.DSet['Gene map'][gene]['name'])
            features.append("                     /locus_tag=\"%s\"" % self.DSet['Gene map'][gene]['name'])
            if len(features[-1]) > width:
                features[-1] = self.format_string(features[-1],width,space)
            features.append("                     /db_xref=\"%d..%d\"" % (start,stop))
            if len(features[-1]) > width:
                features[-1] = self.format_string(features[-1],width,space)
            aa_seq = self.translate(self.getSequence()[start-1:stop],self.DSet['Gene map'][gene]['direction'])
            if aa_seq.find("*") > -1:
                continue
            features.append("     CDS             %s" % gene_position) 
            features.append("                     /gene=\"%s\"" % self.DSet['Gene map'][gene]['name'])
            if len(features[-1]) > width:
                features[-1] = self.format_string(features[-1],width,space)
            features.append("                     /product=\"%s\"" % self.DSet['Gene map'][gene]['remark'])
            if len(features[-1]) > width:
                features[-1] = self.format_string(features[-1],width,space)
            features.append("                     /translation=\"%s\"" % self.format_aa_seq(aa_seq))
        return ("\n".join(heading),
                pre_features+"\n".join(features)+"\n"+post_features,
                seq,1+rb-lb)
    
    def genes2fasta(self,flg_protein=True,lb=0,rb=None):
        if not self.strSeq:
            return
        genes = self.DSet['Gene map'].keys()
        if len(genes) > 1:
            genes.sort(self.sort_genes)
        output = []
        for gene in genes:
            if not gene:
                continue
            try:
                start,stop = map(lambda s: int(s), gene.split(".."))
            except:
                print(gene)
                5/0
            if (start < lb or stop <= lb):
                continue
            elif (rb and (start >= rb or stop > rb)):
                break
            title = "%s, %s (%s) [%d..%d]" % (self.DSet['Gene map'][gene]['name'],
                                            self.DSet['Gene map'][gene]['remark'],
                                            self.DSet['Gene map'][gene]['direction'],
                                            start,stop)
            while title[0] in (" ",","):
                title = title[1:]
            seq = self.substring(start,stop,self.DSet['Gene map'][gene]['direction'])
            if flg_protein:
                seq = self.translate(seq,self.DSet['Gene map'][gene]['direction'])
            output.append(">%s\n%s" % (title,seq))
        return "\n".join(output)
    
    def substring(self,start,stop,strand):
        if strand == "dir":
            if start < 0 and stop >= 0:
                return self.strSeq[start-1:]+self.strSeq[:stop]
            else:
                return self.strSeq[start-1:stop]
        elif strand == "rev":
            if start < 0 and stop >= 0:
                return self.strSeq[start:]+self.strSeq[:stop+1]
            else:
                return self.strSeq[start:stop+1]
        else:
            return
    
    def translate(self,seq,strand='dir'):
        seq = seq.upper()
        start = 0
        aa_seq = ""
        if len(seq) < 3:
            return aa_seq
        if strand == "rev":
            seq = self.reverse_complement(seq)
        codon = seq[start:start+3]
        while start < len(seq)-3:
            if not codon:
                break
            try:
                aa_seq += self.codons[codon[0]][codon[1]][codon[2]]
            except:
                aa_seq += "X"
            start += 3
            if start >= len(seq)-3:
                break
            codon = seq[start:start+3]
        if aa_seq[-1] == "*":
            aa_seq = aa_seq[:-1]
        return aa_seq
    
    def reverse_complement(self,seq):
        seq = seq.upper()
        for s,l in [['A','$'],['T','A'],['$','T'],['C','$'],['G','C'],['$','G']]:
            seq = seq.replace(s,l)
        l = list(seq)
        l.reverse()
        return "".join(l)
    
    def format_aa_seq(self,seq,indend=14,space=21,length=58):
        seq = seq.upper()
        if len(seq) <= length-indend:
            return seq
        i = length-indend
        fseq = [seq[:i]]
        while i < len(seq)-length:
            fseq.append(" "*space + seq[i:i+length])
            i += length
        fseq.append(" "*space + seq[i:])
        return "\n".join(fseq)
    
    def format_dna_seq(self,seq,indend=9,window=60,step=10):
        seq = seq.lower()
        fseq = ["ORIGIN      "]
        i = 1
        while i < len(seq)-window:
            substring = seq[i-1:i+59]
            for j in range(window-step,-1,-step):
                substring = substring[:j]+" "+substring[j:]
            fseq.append(" "*(indend-len(str(i)))+str(i)+substring)
            i += window
        substring = seq[i-1:]
        length = len(substring)
        for j in range(length-length%step,-1,-step):
            substring = substring[:j]+" "+substring[j:]
        fseq.append(" "*(indend-len(str(i)))+str(i)+substring)
        fseq.append("//")
        return "\n".join(fseq)
    
    def format_string(self,seq,width,space):
        j = space
        i = seq.find(" ",j+1)
        border = width
        pos = []
        while i < len(seq):
            if i < 0:
                pos.append(j)
                break
            if i >= border:
                pos.append(j)
                border += width
            j = i
            i = seq.find(" ",j+1)
            
        if pos:
            pos.reverse()
            for p in pos:
                seq = seq[:p] + "\n"+" "*space+seq[p+1:]
        return seq
    
    def getTime(self):
        months = ('JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC')
        year,month,day = time.gmtime()[:3]
        return "%d-%s-%d" % (day,months[month-1],year)
    
    def sort_genes(self,a,b):
        a1,a2 = map(lambda s: int(s), a.split(".."))
        b1,b2 = map(lambda s: int(s), b.split(".."))
        if a1 != b1:
            return a1-b1
        else:
            return a2-b2

##############################################
if __name__ == "__main__":
    oParser = Parser("NC_000117.gbk")
    h,fe,s,shift = oParser.getGBK_Components(100000,105000,"locus")
    f = open("tmp.txt","w")
    f.write("\n".join([h,fe,oParser.format_dna_seq(s)]))
    f.close()
    
