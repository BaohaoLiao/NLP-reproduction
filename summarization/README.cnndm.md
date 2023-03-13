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
* Generate: If you have mulltiple GPUs, you can split the test file into small files
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
* Results

  Method |    R1     |    R2     | RL 
  ---|:---------:|:---------:|:---:
  `BART paper` |   44.16   |   21.28   | 40.90 
  `our without modifying fairseq` |   44.38   |   21.49   | 41.23 
  `our with modifying fairseq` | **44.76** | **21.76** | **41.49** 

* Requied packages: Same as [Evaluate with Fine-tuned BART](#evaluate-with-fine-tuned-bart)

  **Note**: You can obtain better result by modifying fairseq like above-mentioning. And it only
  influences the generation.

* Data processing
  ```bash
  wget -N 'https://dl.fbaipublicfiles.com/fairseq/gpt2_bpe/encoder.json'
  wget -N 'https://dl.fbaipublicfiles.com/fairseq/gpt2_bpe/vocab.bpe'
  wget -N 'https://dl.fbaipublicfiles.com/fairseq/gpt2_bpe/dict.txt'

  TASK=cnn_dm
  # Tokenize
  for SPLIT in train val test
  do
    for LANG in source target
    do
      python -m examples.roberta.multiprocessing_bpe_encoder \
        --encoder-json encoder.json \
        --vocab-bpe vocab.bpe \
        --inputs "$TASK/$SPLIT.$LANG" \
        --outputs "$TASK/$SPLIT.bpe.$LANG" \
        --workers 60 \
        --keep-empty;
    done
  done
  
  # Binarize to the format required by fairseq
  fairseq-preprocess \
    --source-lang "source" \
    --target-lang "target" \
    --trainpref "${TASK}/train.bpe" \
    --validpref "${TASK}/val.bpe" \
    --testpref "${TASK}/test.bpe" \
    --destdir "${TASK}-bin/" \
    --workers 60 \
    --srcdict dict.txt \
    --tgtdict dict.txt;
  
  ```
* Training: Follow step 4 in this [instruction](https://github.com/facebookresearch/fairseq/blob/main/examples/bart/README.summarization.md)
* Generation: You can generate by using the same script as [Evaluate with Fine-tuned BART](#evaluate-with-fine-tuned-bart), 
  or you can generate with the binarized file (faster) as:
  ```bash
  DATA=/path/to/${TASK}-bin
  CKPT=/path/to/checkpoint_best.pt
  fairseq-generate $DATA \
      --path $CKPT \
      --gen-subset test \
      --task translation \
      --batch-size 64 \
      --beam 4 --lenpen 2.0 --max-len-b 140  --min-len 55 --no-repeat-ngram-size 3 \
      --truncate-source \
      --bpe gpt2 --remove-bpe 2>&1 | tee gen_out
  
  grep ^T gen_out | LC_ALL=C sort -V | cut -f2- > ref.txt
  grep ^D gen_out | LC_ALL=C sort -V | cut -f3- > hyp.txt

  export CLASSPATH=/path/to/stanford-corenlp-3.7.0.jar

  cat hyp.txt | java edu.stanford.nlp.process.PTBTokenizer -ioFileList -preserveLines > hyp.tokenized.txt
  cat ref.txt | java edu.stanford.nlp.process.PTBTokenizer -ioFileList -preserveLines > ref.tokenized.txt
  files2rouge ref.tokenized.txt hyp.tokenized.txt > score
  ```

    

### Acknowledgements
* Preprocess data: https://github.com/artmatsak/cnn-dailymail, https://github.com/facebookresearch/fairseq/issues/1391
* BART repositrory: https://github.com/facebookresearch/fairseq/tree/main/examples/bart