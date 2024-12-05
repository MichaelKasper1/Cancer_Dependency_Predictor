<template>
  <div class="about">
    <div class="columns">
      <!-- Left Column: Background -->
      <div class="column">
        <h2>Background</h2>
        <p>This website is free and open to all users and there is no login requirement. It is designed to predict, prioritize, analyze, and interpret cancer genetic dependencies through the two tools:</p>
        <h3>Gene Dependency Predictor</h3>
        <p>Easy access to cancer gene dependency predictions on a group of cancer cell lines or tumors. This tab uses models trained with cancer gene expression data and post-chronos gene effect scores from <a href="https://depmap.org/portal/data_page/?tab=allData" target="_blank">DepMap</a>. There are two main types of machine learning algorithms:</p>
        <h5>DeepDEP</h5>
        <p>In the publication of DeepDEP, we systematically evaluated the prediction performance using hold-out cancer cell lines and multiple measures, including mean squared error in gene dependency scores and per-cancer cell line correlation coefficients between actual and predicted data. DeepDEP has achieved marked improvements over a diverse array of conventional methods, such as linear regression, support vector machines, and alternative deep learning models trained either with cell lines alone, without transferring features learned from tumors, or using principal components to replace encoder outputs. Furthermore, we validated the predictions with real-world clinical data from corresponding patients. For more details on the model design, validation, and applications, please refer to the publication of DeepDEP (Chiu et al., Science Advances 2021). The Python implementation of DeepDEP is available in our <a href="https://codeocean.com/capsule/7914207/tree/v1" target="_blank">Code Ocean repository</a>.</p>
        <h5>Elastic Net Models</h5>
        <p>filler text for now</p>
        <h3>TCGA Dependency Explorer</h3>
        <p>Provides an exploration tool for identifying significantly intensified gene dependencies in tumors with specific alterations. The predictions of gene dependencies in TCGA tumors is performed with DeedDEP models (HOW MANY OMICS ADD THIS). In the elastic net models used for TCGA gene dependency prediction, model transposition following transcriptional alignment of DepMap to TCGA. With their paper, the authors also provide an Rshiny tool for exploration of results similar to this app, but with less features. Their application's source code, code for aligning transcriptional profiles of DepMap to TCGA, and code to train elastic net models can be found on <a href="https://github.com/xushiabbvie/TDtool" target="_blank">Github</a>. </p>
      
        <!-- Add more background content here -->
      </div>

      <!-- Right Column: Contact Our Team and Acknowledgements -->
      <div class="column">
        <div class="contact">
          <h2>Contact Our Team</h2>
          <p>Email: YUC250@pitt.edu</p>
          <p>Website: <a href="https://www.chiu-lab.org/" target="_blank">Chiu Lab Website</a></p>
        </div>
        <div class="acknowledgements">
          <h2>Acknowledgements</h2>
          <div class="sponsors">
            <div class="sponsor" v-for="(sponsor, index) in sponsors" :key="index">
              <img :src="sponsor.logo" :alt="sponsor.name" class="sponsor-logo">
              <p v-html="sponsor.name"></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'About',
  data() {
    return {
      sponsors: [
        { name: 'UPMC Hillman Cancer Center Developmental Pilot Program (P30CA047904)', logo: '/sponsors/cancercenterlogo.png' },
        { name: 'Leukemia Research Foundation New Investigator Research Grant Program', logo: '/sponsors/LRF-Logo-website-230px-wide.gif' },
        { name: 'NIH/NCI - K99/R00 Pathway to Independence Award (R00CA248944)<br>Deep learning of drug sensitivity and genetic dependency of pediatric cancer cells', logo: '/sponsors/NCI.jpeg' },
        { name: 'NIH/OD - Common Fund R03 (R03OD036494)<br>In silico screening for immune surveillance adaptation in cancer using Common Fund data resources<br>NIH/OD – Administrative Supplement (3R00CA248944-04S1)<br>Enhancing AI-readiness of multi-omics data for cancer pharmacogenomics', logo: '/sponsors/NIH-logo.jpg' },
        { name: 'Pittsburgh Liver Research Center (PLRC) Pilot and Feasibility Grant (P30DK120531)', logo: '/sponsors/PLRC_Site_Icon.png' },
      ],
    };
  },
});
</script>

<style scoped>
.about {
  text-align: center;
}

.columns {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap; /* Allow columns to wrap on smaller screens */
}

.column {
  flex: 1;
  margin: 20px;
  text-align: left; /* Align text to the left for better readability */
}

.contact, .acknowledgements {
  margin-top: 20px;
}

.sponsors {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.sponsor {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.sponsor-logo {
  max-width: 100px;
  height: auto;
  margin-right: 10px; /* Space between logo and text */
}
</style>