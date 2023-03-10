## CNN / Daily Mail
### Download and Preprocess
Follow this [instruction](https://github.com/artmatsak/cnn-dailymail). You still need 
two modifications in this [file](https://github.com/artmatsak/cnn-dailymail/blob/master/make_datafiles.py):
  * Replace this [line](https://github.com/artmatsak/cnn-dailymail/blob/b6d20708a1180f58dd96b5ab923ed099ced6b2ab/make_datafiles.py#L49) as:
    ```python
    # BART prefers non-tokenized style
    return line + " ."  ----> return line + "."  
    ```
  * Add the following code after this [line](https://github.com/artmatsak/cnn-dailymail/blob/b6d20708a1180f58dd96b5ab923ed099ced6b2ab/make_datafiles.py#L108):
    ```python
    # There might be "(CNN)" and useless news location before "(CNN)" at the 
    # beginning of the document
    if "(CNN)" in article[:50]:
        article = article.split("(CNN)")[1]
    ```

  
### Evaluate with Fine-tuned BART
* Results

  Method |    R1     |    R2     | RL 
  ---|:---------:|:---------:|:---:
  `BART paper` |   44.16   |   21.28   | 40.90 
  `our` | **44.26** | **21.31** | **41.06**

* Requied packages:
  * [fairseq](https://github.com/facebookresearch/fairseq#requirements-and-installation) 
  (already verified on version 0.12.2 with pytorch1.11)
    
      Compared to XSum, the following lines don't affect the result. 
  You don't need to add them.
      ```python
      # force the model to predict bos at the beginning and never predict bos later
      if step == 0:
        lprobs[:, self.tgt_dict.bos()] = 1000
      else:
        lprobs[:, self.tgt_dict.bos()] = -math.inf
      ```
  * [files2rouge](https://github.com/pltrdy/files2rouge)

* Download the fine-tuned model [bart.large.cnn](https://github.com/facebookresearch/fairseq/tree/main/examples/bart#pre-trained-models)
* Generate; If you have mulltiple GPUs, you can split the test file into small files
and then generate to speed up the inference.
  ```bash
  mkdir inference
  python /path/to/fairseq/examples/bart/summarize.py \
      --model-dir /path/to/bart.large.xsum \
      --model-file model.pt \
      --src /path/to/test.source \
      --out inference/test.hyp \
      --bsz 64 
  ```
* Tokenize and evaluate
  ```bash
  wget https://repo1.maven.org/maven2/edu/stanford/nlp/stanford-corenlp/3.7.0/stanford-corenlp-3.7.0.jar
  export CLASSPATH=/path/to/stanford-corenlp-3.7.0.jar
  cat inference/test.hyp | java edu.stanford.nlp.process.PTBTokenizer -ioFileList -preserveLines > inference/test.hyp.tokenized
  cat path/to/test.target | java edu.stanford.nlp.process.PTBTokenizer -ioFileList -preserveLines > inference/test.target.tokenized
  files2rouge inference/test.target.tokenized inference/test.hyp.tokenized > inference/score
  ```


### Fine-tune Pre-trained BART

    

### Acknowledgements
* Preprocess data: https://github.com/artmatsak/cnn-dailymail, https://github.com/facebookresearch/fairseq/issues/1391
* BART repositrory: https://github.com/facebookresearch/fairseq/tree/main/examples/bart