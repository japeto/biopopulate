
import re
import os
import json, time
import itertools
from pymongo import MongoClient
import json

from sources.europmc_search import get_papers_by_keyword
from sources.europmc_annotation import get_annotations, get_article

from nltk import sent_tokenize

def process_input(raw_text="", entities=None):
    try:
        if not(raw_text) and not('body' in raw_text):
            return [],[]
    except:
        return [], []

    def intersection(lst1, lst2):
        return list(set(lst1) & set(lst2))
    sentence=[]
    entities = [ent for lst in [lst for lst in entities.values()] for ent in lst]
    raw_text = raw_text['body']
    for sent in sent_tokenize(raw_text.lower()):
        sent = sent.replace(".", " ")
        inter = intersection(entities, sent.split(" "))
        cmbs = list(itertools.combinations(inter, 2))
        inter.reverse()
        cmbs = cmbs+list(itertools.combinations(inter, 2))
        for tupl in cmbs:
            tupl= "{}\t{}\t".format(tupl[0],tupl[1])
            sentence.append(f'{tupl}{sent}')
            # print(f'{tupl}{sent}')
    return [], sentence

def evaluate(model, data_iterator, num_steps, metric_labels):
    """Evaluate the model on `num_steps` batches."""
    # set model to evaluation mode
    model.eval()
    output_labels = list()
    target_labels = list()
    # compute metrics over the dataset
    for _ in range(num_steps):
        # fetch the next evaluation batch
        batch_data, batch_labels = next(data_iterator)
        # compute model output
        batch_output = model(batch_data)  # batch_size x num_labels
        batch_output_labels = torch.max(batch_output, dim=1)[1]
        output_labels.extend(batch_output_labels.data.cpu().numpy().tolist())
        target_labels.extend(batch_labels.data.cpu().numpy().tolist())
    return output_labels

def save2file(list: str, outf_name="records")->int:
    with open(outf_name, "a", encoding="utf-8") as outfile:
        json.dump(list, outfile)

def file2obj(inf_name="records")->dict:
    with open(inf_name) as infile:
        data = json.load(infile)
        return data

def get_entites(sentence: str) -> str:
    tags = sentence.count("<diseases>") + sentence.count("<chemicals>") \
           + sentence.count("<gene_ontology>") + \
           sentence.count("<gene_proteins>") + sentence.count("<organisms>")

    if tags > 1:
        diseases=re.findall(r'<diseases[^>]*>([^<]+)</diseases>', sentence)
        organisms=re.findall(r'<organisms[^>]*>([^<]+)</organisms>', sentence)
        chemicals=re.findall(r'<chemicals[^>]*>([^<]+)</chemicals>', sentence)
        gene=re.findall(r'<gene_ontology[^>]*>([^<]+)</gene_ontology>', sentence)
        proteins=re.findall(r'<gene_proteins[^>]*>([^<]+)</gene_proteins>', sentence)

        return " ".join(organisms[0:2]) +"\t"+sentence if organisms \
            else " ".join(chemicals[0:2]) +"\t"+sentence if chemicals \
            else " ".join(diseases[0:2]) +"\t"+sentence if diseases \
            else " ".join(gene[0:2]) + "\t" + sentence if gene \
            else " ".join(proteins[0:2]) + "\t" + sentence if proteins \
            else " "

    return ""

if __name__ == "__main__":
    list = ["diabetes", "dengue", "chikungunya", "aedes aegypti", "coronavirus",
     "Infection","Medulloblastoma","Antibody","Cells","Inhale"]
    for kwd in list:
        keywords = f'({kwd} AND ' \
                   '(FIRST_PDATE:[2000-01-01 TO 2020-03-31])) AND OPEN_ACCESS:Y'

        client = MongoClient()
        db=client.biomedicalrelation
        documents= db.documents

        outf_name = keywords.lower().strip().replace(",","_")+".json"
        results = get_papers_by_keyword(keywords=keywords)
        results
        ids=list(results)[0:200]
        user_id = db.user.find_one(
            {"username": "'bioworkbench'"},
            {"_id": 1})["_id"]

        now=time.strftime('%Y-%m-%d')

        for key in ids:
            pub=results[key]
            pub['annotations']=get_annotations(f"{pub['source']}%3A{pub['id'].replace('PMC','')}", source=None)

            if not('pmcid' in pub): break

            pub['fulltext'] = get_article(pub['pmcid'], annotations=pub['annotations'])
            pub['labels'], pub['sentences'] = process_input(pub['fulltext'], pub['annotations'])
            pub['userid'] = user_id
            pub['stated'] = "unprocessed"
            pub['download_date'] = now
            pub['processed_date'] = None
            pub['marked'] = ""
            if pub['fulltext']:
                for snt in sent_tokenize(pub['fulltext']['tagged']):
                    pub['marked'] = pub['marked'] + get_entites(snt)
            # aplicar modelo
            results[key] = pub

        dump = [results[pub] for pub in results if pub in ids ]
        [documents.insert(doc) for doc in dump]
        db.user.update_one(
            {"_id": user_id},
            {"$inc": {"nsearch": 1}},
            upsert=False)


