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

  Method |     R1     |     R2     | RL
  ---|:----------:|:----------:|:---:
  `BART paper` |   45.14    | **22.27**  | **37.25** 
  `our` | **45.20**  |   21.91    | 36.69 
  `our without tokenizing` |   45.17    |   21.83    | 36.65 
  `our without modifying fairseq` |   44.30    |   20.90    | 35.19

* Requied packages:
  * [fairseq](https://github.com/facebookresearch/fairseq#requirements-and-installation) 
  (already verified on version 0.10.2 and 0.12.2 (recommended) with pytorch1.11)
    
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

* Download the fine-tuned model [bart.large.xsum](https://github.com/facebookresearch/fairseq/tree/main/examples/bart#pre-trained-models)
* Generate: If you have mulltiple GPUs, you can split the test file into small files
and then generate to speed up the inference.
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
* Tokenize and evaluate
  ```bash
  wget https://repo1.maven.org/maven2/edu/stanford/nlp/stanford-corenlp/3.7.0/stanford-corenlp-3.7.0.jar
  export CLASSPATH=/path/to/stanford-corenlp-3.7.0.jar
  cat inference/test.hyp | java edu.stanford.nlp.process.PTBTokenizer -ioFileList -preserveLines > inference/test.hyp.tokenized
  cat path/to/test.summary | java edu.stanford.nlp.process.PTBTokenizer -ioFileList -preserveLines > inference/test.target.tokenized
  files2rouge inference/test.target.tokenized inference/test.hyp.tokenized > inference/score
  ```


### Fine-tune Pre-trained BART
* Results

  Method |    R1     |    R2     | RL 
  ---|:---------:|:---------:|:---:
  `BART paper` | **45.14** | **22.27**  | **37.25** 
  `our without modifying fairseq` |   44.91   | 21.91 | 36.73
  `our with modifying fairseq` |   44.76   | 21.49 | 36.26

  * Requied packages: Same as [Evaluate with Fine-tuned BART](#evaluate-with-fine-tuned-bart)

    **Note**: You can or can't obtain better result by modifying fairseq like above-mentioning.
    It's quite random. You could try both and the modification only influences the generation.

* Data processing
  ```bash
  wget -N 'https://dl.fbaipublicfiles.com/fairseq/gpt2_bpe/encoder.json'
  wget -N 'https://dl.fbaipublicfiles.com/fairseq/gpt2_bpe/vocab.bpe'
  wget -N 'https://dl.fbaipublicfiles.com/fairseq/gpt2_bpe/dict.txt'

  TASK=cnn_dm
  # Tokenize
  for SPLIT in train validation test
  do
    for LANG in document summary
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
    --source-lang "document" \
    --target-lang "summary" \
    --trainpref "${TASK}/train.bpe" \
    --validpref "${TASK}/validation.bpe" \
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
      --beam 6 --lenpen 1.0 --max-len-b 60  --min-len 10 --no-repeat-ngram-size 3 \
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
* Original XSum repository: https://github.com/EdinburghNLP/XSum
* Link for data download: https://github.com/EdinburghNLP/XSum/issues/9
* BART repositrory: https://github.com/facebookresearch/fairseq/tree/main/examples/bart
* FairSeq modification: https://github.com/facebookresearch/fairseq/issues/1971