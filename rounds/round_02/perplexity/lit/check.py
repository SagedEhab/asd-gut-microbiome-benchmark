import os,re,json
C=[
("37140125","median external AUC 0.60 ASD n-1",[r"0\.60",r"1,?600"]),
("37140125","ASD poor marker consistency",[r"ASD and PD require more samples"]),
("36838256","cross-cohort around 0.5",[r"around 0\.5",r"0\.984",r"0\.81"]),
("37365313","pooled AUC 0.78",[r"0\.78"]),("37365313","David 0.46",[r"0\.46"]),("37365313","Son 0.69",[r"0\.69"]),("37365313","Elliott 0.38",[r"0\.38"]),
("37365313","6 of 9 >0.87",[r"0\.87"]),("37365313","70%/73%",[r"70%",r"73%"]),("37365313","MSE 589.3 / 57.8",[r"589",r"57\.8"]),("37365313","P<0.002 / household",[r"0\.002",r"household"]),
("38191575","0.816 / 0.748 / 0.740 / 0.84",[r"0\.816",r"0\.748",r"0\.74\b|0\.740",r"0\.84"]),("38191575","26 ASVs",[r"26 ASV"]),("38191575","PRJNA589343/PRJNA578223",[r"PRJNA589343",r"PRJNA578223"]),
("34930815","0.86 / 0.78 / 0.82 / 0.67",[r"0\.86",r"0\.78",r"0\.82",r"0\.67"]),("34930815","773 / 429",[r"773",r"429"]),("34930815","re-established",[r"re-?establish"]),
("38977906","0.91 ; 0.68-0.87; 1,627",[r"0\.91",r"0\.68",r"1,?627"]),
("34312160","82.6 / 76.2",[r"82\.6",r"76\.2"]),
("32912596","0.94 / 0.98",[r"0\.94",r"0\.98"]),
("32312186","0.931",[r"0\.931"]),
("39457661","0.61 / 0.81 / R2 0.068 / 0.006",[r"0\.61",r"0\.81",r"0\.068",r"0\.006"]),("39457661","PRJNA578223",[r"PRJNA578223"]),
("34767757","negligible direct",[r"[Nn]egligible"]),
("33149306","13 of 19 ; ASD",[r"13 of",r"autism|ASD"]),
("36220843","4 of 9 / 2 of 10 / no overlap",[r"4 of 9|four of",r"2 of 10|two of",r"overlap"]),
("29684016","6.34%",[r"6\.34"]),("29684016","70%",[r"70%"]),
("29209090","Son, Kang; Prevotella",[r"Prevotella",r"autism|ASD"]),
("31404299","9 studies 254/167",[r"254",r"167"]),("31404299","Bifido 2.2/4.2 ; SMD -1.05",[r"1\.05",r"2\.27",r"0\.18"]),("31404299","Bacteroides -0.35 (-1.20,0.51)",[r"0\.35",r"1\.20",r"0\.51"]),
("31404299","Akk Z=0.44 P=0.66",[r"0\.44",r"0\.66"]),("31404299","Enterococcus -0.14 (-0.47,0.20)",[r"0\.14",r"0\.47"]),("31404299","E coli -0.33 (-1.18,0.52)",[r"0\.33",r"1\.18"]),
("31404299","Lactobacillus 0.53 (-0.001, 1.10)",[r"0\.53",r"0\.001",r"1\.10"]),("31404299","Faecali 10.2 vs 7.7",[r"10\.2",r"7\.7"]),
("32192218","18 studies 493/404",[r"493",r"404"]),("32192218","Bacteroides 9.04 vs 4.69; I2 95.8",[r"9\.04",r"4\.69",r"95\.8"]),("32192218","Bifido 0.46 vs 0.89; 93.9",[r"0\.46",r"0\.89",r"93\.9"]),
("32192218","Parabact 0.32 vs 0.04",[r"0\.32",r"0\.04"]),("32192218","Faecali 6.84 vs 5.00 P=0.040",[r"6\.84",r"5\.00",r"0\.040"]),("32192218","Akk 0.04 vs 0.55 Z 1.25",[r"0\.55",r"1\.25"]),("32192218","Faecali CI 4.15-5.85 / 8.35",[r"5\.85",r"8\.35"]),
("33948825","Bifido SMD -0.513 (-0.953,-0.073)",[r"0\.513",r"0\.953",r"0\.073"]),
("38897955","28 studies 1256/1042; direction",[r"1,?256",r"1,?042",r"Bifidobacterium",r"Parabacteroides",r"Faecalibacterium"]),
("26427004","PRJNA282013 / 59 / 44",[r"PRJNA282013",r"59",r"44"]),
("28222761","PRJEB15418 / 40 / 11.1",[r"PRJEB15418",r"PRJEB15420",r"11\.1",r"Table S9|S9"]),
("23844187","SRA053656",[r"SRA053656"]),
("30895172","data availability",[r"[Dd]ata [Aa]vailab[^.]{0,300}"]),
("33824194","sex counts",[r"female",r"\b27\b",r"\b22\b"]),
("33824194","accession",[r"SRA|PRJ|accession|Oregon|osu"]),
("32830918","Zou region/n",[r"V3|V4",r"\b48\b|\b46\b|\b45\b"]),
("39286497","GSE113690",[r"GSE113690"]),
]
out=[]
for pm,lab,pats in C:
    src='full' if os.path.exists(pm+'.full.txt') else 'abstract'
    t=open(pm+('.full.txt' if src=='full' else '.abs.txt')).read()
    for p in pats:
        ms=[m for m in re.finditer(p,t)]
        q=' | '.join(t[max(0,m.start()-110):m.end()+60].replace('\n',' ') for m in ms[:2])
        out.append(f"{pm}\t{src}\t{lab}\t{p}\t{len(ms)}\t{q}")
open('grep_results.tsv','w').write("pmid\tsource\tclaim\tpattern\thits\tcontext\n"+"\n".join(out))
for o in out:
    f=o.split('\t'); print(f[0],f[1],f[2][:35],f[3][:20],f[4], f[5][:230])
