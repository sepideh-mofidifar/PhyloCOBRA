
<h1>PhyloMICOM</h1>

<p>PhyloMICOM is an extension of the <strong>MICOM</strong> package [1], designed to improve the accuracy and efficiency of microbial community simulations by incorporating phylogenetic relationships. This project introduces a modified version of the <code>community.py</code> file from the MICOM package. This modification, pools the metabolic models of phylogenetically related organisms at the order level which allows for more accurate and phylogenetically-informed simulations of microbial communities.</p>

<h3>Installation</h3>

<p>PhyloMICOM is available on PyPi and can be installed via:</p>

<pre><code>pip install PhyloMICOM==0.1.0</code></pre>


<h3>Example usage:</h3>

<p>To use the PhyloMICOM package, you can import the following functions:</p>
<pre><code>
from micom import load_pickle
from micom.workflows import build
from micom.data import test_medium
from micom.qiime_formats import load_qiime_medium
</code></pre>

<h4>Building community models:</h4>

<p>To build a community model with PhyloMICOM, you can use the following code:</p>

<pre><code>
manifest = build(data, out_folder="models", model_db=test_db, cutoff=0.0001, threads=2)
</code></pre>

<h4>Performing a community simulation:</h4>

<p>To perform a community simulation, you can load your Qiime medium and run the model:</p>

<pre><code>
medium = load_qiime_medium('western_diet_gut.qza')
growth_results = grow(manifest, model_folder="models", medium=medium, tradeoff=0.5, threads=2)
</code></pre>


<h3>License</h3>

<p>PhyloMICOM is developed for non-commercial use and is provided as-is. Contributions are welcome and appreciated. For inquiries about collaborations or commercial usage and development, please contact us at <a href="mailto:s.mofidifar@gmail.com">s.mofidifar@gmail.com</a>.</p>

<h3>Reference</h3>

<p>[1] Diener CGibbons SM, Resendis-Antonio O 2020. MICOM: Metagenome-Scale Modeling To Infer Metabolic Interactions in the Gut Microbiota. mSystems 5:10.1128/msystems.00606-19.
https://doi.org/10.1128/msystems.00606-19</p>
</body>
</html>
