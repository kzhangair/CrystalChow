# -*- coding: utf-8 -*-   
import re

import opencc
import jieba


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
    segs_list = []
    with open('simTrainlistPh.txt', 'r', encoding='utf-8') as fr:
        for line in fr.readlines():
            simSent = line.strip().split('\t')[0]
            segs = jieba.lcut(simSent, cut_all=True)
            segs_list = segs_list + segs
    segs_list = list(set(segs_list))
    segs_list.sort()
    with open('simWord.txt', 'w', encoding='utf-8') as fw:
        for seg in segs_list:
            fw.write(seg+'\n')
    return segs_list

def jyut2SampChar(charJyutping):
    #jyutping: jyutping of word, e.g. maa4
    #posiInword: word position in sentence, 'I, M, F'
    #return SAMPA of word
    jyut2SampDict = {'aa':'aM', 'aai':'aMj', 'aau':'aMw', 'aam':'aM m', 'aan':'aM n', 'aang':'aM N', 'aap':'aM p', 'aat':'aM t', 'aak':'aM k' \
        ,'a':'M6', 'ai':'M6j', 'au':'M6w', 'am':'M6 m', 'an':'M6 n', 'ang':'M6 N', 'ap':'M6 p', 'at':'M6 t', 'ak':'M6 k'\
            ,'e':'EM', 'ei':'ej', 'eng':'EM N', 'ek':'EM k'\
                ,'i':'iM', 'iu':'iw', 'im':'iM m', 'in':'iM n', 'ing':'iM N', 'ip':'iM p', 'it':'iM t', 'ik':'iM k'\
                    ,'o':'OM', 'oi':'OMj', 'ou':'ow', 'on':'OM n', 'ong':'OM N', 'ot':'OM t', 'ok':'OM k'\
                        ,'u':'uM', 'ui':'uMj', 'un':'uM n', 'ung':'uM N', 'ut':'uM t', 'uk':'uM k'\
                            ,'eoi':'M9y'\
                                ,'eon':'M9M n', 'eot':'M9M t', 'oe':'M9M', 'oeng':'M9M N', 'oek':'M9M k'\
                                    ,'yu':'yM', 'yun':'yM n', 'yut':'yM t'\
                                        ,'m':'m', 'n':'n', 'ng':'N', 'p':'p', 'b':'b', 't':'t', 'd':'d', 'k':'k', 'g':'g'\
                                            ,'kw':'kw', 'gw':'gw', 'f':'f', 's':'s', 'h':'h', 'z':'dz', 'c':'ts'\
                                                ,'j':'j', 'w':'w', 'l':'l'}
    pattern = r'(?P<initials>b|p|m|f|d|t|n|l|gw|kw|ng|h|g|k|w|z|c|s|j)?(?P<finals>aang|aai|aau|aam|aan|aap|ang|aat|aak|aa|ai|au|am|an|ap|at|ak|a|eoi|eon|eot|eng|ei|eu|em|ep|ek|e|ing|iu|im|in|ip|it|ik|i|oeng|ong|oet|oek|oe|oi|ou|on|ok|ot|o|ung|ui|un|uk|ut|u|yun|yut|yu|m|ng)(?P<tone>[1-6])'
    matchObj = re.match(pattern, charJyutping)
    jyutInitials = matchObj.group('initials')
    jyutFinals = matchObj.group('finals')
    tone = matchObj.group('tone')

    if not jyutInitials: #single finals
        sampaFinals = jyut2SampDict[jyutFinals]
        sampaList = sampaFinals.split(' ')
        sampaList[0] = sampaList[0] + '^I;' + tone
        if len(sampaList) > 1:
            sampaList[1] = sampaList[1] + '^F'
    else: #initials + finals
        sampaInitials = jyut2SampDict[jyutInitials]
        sampaFinals = jyut2SampDict[jyutFinals]
        sampaList = [sampaInitials] + sampaFinals.split(' ')
        sampaList[0] = sampaList[0] + '^I'
        if len(sampaFinals.split(' ')) == 1:
            sampaList[1] = sampaList[1] + '^F;' + tone
        elif len(sampaFinals.split(' ')) == 2:
            sampaList[1] = sampaList[1] + '^M;' + tone
            sampaList[2] = sampaList[2] + '^F'
        else:
            print('Error! sampaList length greater than 2')
            print(sampaList)
    return sampaList

def jyut2SampWord(wordJyutping):
    #input: jyutping is the list, jyutping of word, e.g. ['cing1', 'maa5', 'daai6', 'kiu4'], ['cing1']
    #output: sampa list ['h^II', 'ow^MF;2']
    sampList = []
    for charJyutping in wordJyutping:
        sampList = sampList + jyut2SampChar(charJyutping)
    for i in range(len(sampList)):
        if i == 0:
            insertLabel = 'I'
        elif i == len(sampList) - 1:
            insertLabel = 'F'
        else:
            insertLabel = 'M'
        index = sampList[i].find('^') + 1
        sampList[i] = sampList[i][:index] + insertLabel + sampList[i][index:]
    return sampList
                            
def lexicon_ALLfromJyutping():
    lexiconDict = {}
    with open('trainText', 'w', encoding='utf-8') as fw:
        with open('simTrainlistPh.txt', 'r', encoding='utf-8') as fr:
            for line in fr.readlines():
                splitEles = line.strip().split('\t')
                if len(splitEles) == 2:
                    simText, jyutpingTrans = line.strip().split('\t')
                    #remove English char, number, and special symbols 
                    simText = re.sub('[\W\da-zA-Z_]', '', simText)
                    assert len(simText) == len(jyutpingTrans.split('-')), 'simText not equal len with Trans {} {}'.format(simText, jyutpingTrans)
                    
                    segWords = jieba.lcut(simText, cut_all=True)
                    fw.write(' '.join(segWords)+'\n')

                    for word in segWords:
                        begin = simText.find(word)
                        wordJyutping = jyutpingTrans.split('-')[begin:begin+len(word)]
                        if word not in lexiconDict:
                            try:
                                lexiconDict[word] = (['-'.join(wordJyutping)], [jyut2SampWord(wordJyutping)], {' '.join(jyut2SampWord(wordJyutping)):1})
                            except AttributeError:
                                print(word, wordJyutping, jyutpingTrans)
                                continue
                        else:
                            if '-'.join(wordJyutping) not in lexiconDict[word][0]:
                                lexiconDict[word][0].append('-'.join(wordJyutping))
                                lexiconDict[word][1].append(jyut2SampWord(wordJyutping))
                                lexiconDict[word][2][' '.join(jyut2SampWord(wordJyutping))] = 1
                            else:
                                lexiconDict[word][2][' '.join(jyut2SampWord(wordJyutping))] += 1
                else:
                    fw.write(line.strip()+'\n')
    lexiconTuple = sorted(lexiconDict.items(), key=lambda item:item[0], reverse=False)
    finalDict = {}
    with open('lexicon_ALLfromJyutping.txt', 'w', encoding='utf-8') as fw:
        fw.write('!SIL\tSIL\n')
        fw.write('<SPOKEN_NOISE>\tSPN\n')
        fw.write('<UNK>\tSPN\n')
        for word, _tuple in lexiconTuple:
            maxLex = ''
            maxLexCount = 0
            for _lex, _lexCount in _tuple[2].items():
                if maxLexCount < _lexCount:
                    maxLexCount = _lexCount
                    maxLex = _lex
            finalDict[word] = maxLex
            fw.write(word + '\t' + maxLex + '\n')
    return finalDict

def lexicon_OOVfromJyutping_IVfromLexDict():
    lexDict = {}
    with open('ALL_SIM_LiuSAMPA_xSource_20180620.lex', 'r', encoding='utf-8') as fr:
        for line in fr.readlines():
            splitEles = line.strip().split('\t')
            word = splitEles[0]
            prons = splitEles[1:]
            lexDict[word] = prons

    jyutDict = lexicon_ALLfromJyutping()

    finalDict = {}
    with open('simTrainlistPh.txt', 'r', encoding='utf-8') as fr:
        for line in fr.readlines():
            splitEles = line.strip().split('\t')
            if len(splitEles) == 2:
                simText, jyutpingTrans = line.strip().split('\t')
                simText = re.sub('[\W\da-zA-Z_]', '', simText)
                for word in jieba.lcut(simText, cut_all=True):
                    if word not in finalDict:
                        if word in lexDict:
                            finalDict[word] = '\t'.join(lexDict[word])
                        else:
                            finalDict[word] = jyutDict[word]

    lexiconTuple = sorted(finalDict.items(), key=lambda item:item[0], reverse=False)
    with open('lexicon_OOVfromJyutping_IVfromLexDict.txt', 'w', encoding='utf-8') as fw:
        fw.write('!SIL\tSIL\n')
        fw.write('<SPOKEN_NOISE>\tSPN\n')
        fw.write('<UNK>\tSPN\n')
        for word, lexicon in lexiconTuple:
            fw.write(word + '\t' + lexicon + '\n')
    return finalDict
  