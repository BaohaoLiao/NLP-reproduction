## Extreme Summarization (XSum)
### Download and Split
* Required packages:
  * python >= 3.6
  * json
* Download raw data. 
You are expected to obtain a folder named after `bbc-summary-data` and 237018 
`\<id>.summary` files inside.
    ``` bash
    cd summarization
    mkdir data
    cd data
    wget http://bollin.inf.ed.ac.uk/public/direct/XSUM-EMNLP18-Summary-Data-Original.tar.gz --no-check-certificate
    tar -zxvf XSUM-EMNLP18-Summary-Data-Original.tar.gz
    ```
* Split into train/dev/test sets. 
You are expected to obtain a folder named after `xsum` which contains 
`train.document/summary`, `validation.document/summary`, `test.document/summary`.
The number of sentences is 204045, 11332, 11334 for train, validation and test sets, respectively.
    ```bash
    wget https://github.com/EdinburghNLP/XSum/raw/master/XSum-Dataset/XSum-TRAINING-DEV-TEST-SPLIT-90-5-5.json 
    python ../xsum/xsum_split.py bbc-summary-data XSum-TRAINING-DEV-TEST-SPLIT-90-5-5.json xsum
    ```
  
### Evaluate with Fine-tuned BART
* Results

  Method | R1 | R2 | RL
  ---|----|----|---
  `BART paper` | 45.14 | **22.27** | **37.25** 
  `our` | **45.20** | 21.91 | 36.69 
  `our without tokenizing` | 45.17 | 21.83 | 36.65 
  `our without modifying fairseq` | 44.30 | 20.90 | 35.19

* Requied packages:
  * [fairseq](https://github.com/facebookresearch/fairseq#requirements-and-installation) 
  (already verified on version 0.10.2 and 0.12.2 (recommended))
    
      Add the following lines after this [line](https://github.com/facebookresearch/fairseq/blob/0338cdc3094ca7d29ff4d36d64791f7b4e4b5e6e/fairseq/sequence_generator.py#L378)
      (lose about **1** Rouge score without this modification)
      ```python
      # force the model to predict bos at the beginning and never predict bos later
      if step == 0:
          lprobs[:, self.tgt_dict.bos()] = 1000
      else:
          lprobs[:, self.tgt_dict.bos()] = -math.inf
      ```
  * [files2rouge](https://github.com/pltrdy/files2rouge)

* Download fine-tuned model [bart.large.xsum.tar.gz](https://github.com/facebookresearch/fairseq/tree/main/examples/bart#pre-trained-models)
* Generate
  ```bash
  mkdir inference
  python /path/to/fairseq/examples/bart/summarize.py \
      --model-dir /path/to/bart.large.xsum \
      --model-file model.pt \
      --src /path/to/test.document \
      --out inference/test.hyp \
      --bsz 64 \
      --xsum-kwargs
  ```
* Evaluate
  ```bash
  wget https://repo1.maven.org/maven2/edu/stanford/nlp/stanford-corenlp/3.7.0/stanford-corenlp-3.7.0.jar
  export CLASSPATH=/path/to/stanford-corenlp-3.7.0.jar
  cat inference/test.hyp | java edu.stanford.nlp.process.PTBTokenizer -ioFileList -preserveLines > inference/test.hyp.tokenized
  cat path/to/test.summary | java edu.stanford.nlp.process.PTBTokenizer -ioFileList -preserveLines > inference/test.target.tokenized
  files2rouge inference/test.target.tokenized inference/test.hyp.tokenized > inference/score
  ```


### Fine-tune Pre-trained BART

    

### Acknowledgements
* Original XSum repository: https://github.com/EdinburghNLP/XSum
* Link for data download: https://github.com/EdinburghNLP/XSum/issues/9
* BART repositrory: https://github.com/facebookresearch/fairseq/tree/main/examples/bart
* FairSeq modification: https://github.com/facebookresearch/fairseq/issues/1971