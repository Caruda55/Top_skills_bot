"""**************************************************СОСТАВЛЕНИЕ СПИСКОВ**************************************************"""

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from natasha import (
    Segmenter,
    MorphVocab,

    NewsMorphTagger,
    NewsEmbedding,
    NewsSyntaxParser,
    NewsNERTagger,

    PER,
    LOC,
    NamesExtractor,
    DatesExtractor,
    MoneyExtractor,
    AddrExtractor,

    Doc
    )

def normalize(arg):

    segmenter = Segmenter()
    morph_vocab = MorphVocab()

    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)
    syntax_parser = NewsSyntaxParser(emb)
    ner_tagger = NewsNERTagger(emb)

    names_extractor = NamesExtractor(morph_vocab)
    dates_extractor = DatesExtractor(morph_vocab)
    money_extractor = MoneyExtractor(morph_vocab)
    addr_extractor = AddrExtractor(morph_vocab)

    doc = Doc(arg)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)
    doc.tag_ner(ner_tagger)

    #for span in doc.spans:
      #  span.normalize(morph_vocab)

    #print({i.text: i.normal for i in doc.spans if i.text != i.normal}) #Приведение существительных к нормальной форме

    for token in doc.tokens:
        token.lemmatize(morph_vocab)

    line = [i.lemma for i in doc.tokens]
    #ln = ' '.join(line).replace('.', '')
    
    return line

# Составление окончательных списков с результатами                                                           
def sort(arg):

    vectorizer = TfidfVectorizer()
    vectorizer.fit(arg)

    tf_idf_words = vectorizer.get_feature_names_out()
    tf_idf_table = vectorizer.transform(arg).toarray()

    x = pd.DataFrame(tf_idf_table, columns=tf_idf_words)

    weights = tf_idf_table.sum(axis=0)

    indexes_order = weights.argsort()[::-1]

    middle = tf_idf_words[indexes_order][0:40]

    final_list: str = ''
    count = 0

    for _ in middle:
        count += 1
        final_list = f'{final_list} \n{count}. {_}'

    return final_list









