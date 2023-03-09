## Extreme Summarization (XSum)
### Download and Split
* Required packages:
  * python >= 3.6
  * json
  * 
* Download raw data. 
You are expected to obtain a folder named after **bbc-summary-data** and 237018 
**\<id>.summary** files inside.
    ``` bash
    cd summarization
    mkdir data
    cd data
    wget http://bollin.inf.ed.ac.uk/public/direct/XSUM-EMNLP18-Summary-Data-Original.tar.gz
    tar -zxvf XSUM-EMNLP18-Summary-Data-Original.tar.gz
    ```
* Split into train/dev/test sets. 
You are expected to obtain a folder named after **xsum** which contains **train.src**, 
**train.tgt**, **dev.src**, **dev.tgt**, **test.src** and **test.tgt**.
    ```bash
    wget https://github.com/EdinburghNLP/XSum/raw/master/XSum-Dataset/XSum-TRAINING-DEV-TEST-SPLIT-90-5-5.json 
    python ../xsum_split.py 
    ```
  
### Evaluate with Publicly Fine-tuned BART

### Fine-tune Pre-trained BART

    

### Acknowledgements
* Original XSum repository: https://github.com/EdinburghNLP/XSum
* Link for data download: https://github.com/EdinburghNLP/XSum/issues/9
* 