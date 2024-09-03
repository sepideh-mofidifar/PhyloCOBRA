import os
import pandas as pd
if __name__ == '__main__':
    os.chdir(r"D:\DrTefagh\MICOMarticle")
    tax = pd.read_csv("genera.csv")
    metadata = pd.read_csv("metadata.csv").rename(columns={"run_accession": "sample_id"})
    metadata=metadata[['sample_id','subset','status']]
    samples=['ERR260139']
    #'ERR260139','ERR414341','ERR260235'
    tax=tax[tax['samples'].isin(samples)]
    tax=tax.rename(columns={'samples':'sample_id'})
    tax=tax.rename(columns={'reads':'abundance'})
    tax['id']=tax['genus']
    tax=tax[['sample_id','abundance','genus','id','relative']]
    tax = pd.merge(tax, metadata, on="sample_id")
    from micom.workflows import build
    from micom import Community
    os.chdir("D:\DrTefagh\MICOMarticle\materials")
    manifest = build(tax, "agora103_genus.qza", "modelsGenus", solver="osqp", threads=2)
#    os.chdir(r"D:\DrTefagh\micomproject_results")
#    os.chdir(r"D:\DrTefagh\MICOMarticle\materials\models")
#    manifest = pd.read_csv('manifest.csv')
    os.chdir("D:\DrTefagh\MICOMarticle\materials")
    from micom.qiime_formats import load_qiime_medium
    medium = load_qiime_medium("western_diet_gut.qza")
    from micom.workflows import grow
    import pickle
    growth_results = grow(manifest, "modelsGenus", medium, tradeoff=0.1, threads=2)

#    result=growth_results[0]
#    result = result.reset_index()
#    rep_rate = pd.read_csv("replication_rates.csv")
#    sample_rate = rep_rate[rep_rate['id'].isin(samples)]