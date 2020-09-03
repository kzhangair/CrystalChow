import opencc

def tra2sim(source, target, config='hk2s.json'):
    converter = opencc.OpenCC(config)
    with open(target, 'w', encoding='utf-8') as fw:
        with open(source, 'r', encoding='utf-8') as fr:
            for line in fr.readlines():
                items = line.strip().split('\t')
                if len(items) < 2:
                    print(items)
                    continue
                tra_line = items[0]
                jyutping_seq = items[1]
                sim_line = converter.convert(tra_line)
                fw.write(sim_line+'\t'+ jyutping_seq  + '\n')

def sentence_segment():
    pass