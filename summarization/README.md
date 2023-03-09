## Extreme Summarization (XSum)
### Download and Split
* Required packages:
  * python >= 3.6
  * json
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
You are expected to obtain a folder named after **xsum** which contains 
**train.document/summary**, **validation.document/summary**, **test.document/summary**.
The number of sentences is 204045, 11332, 11334 for train, validation and test sets, respectively.
    ```bash
    wget https://github.com/EdinburghNLP/XSum/raw/master/XSum-Dataset/XSum-TRAINING-DEV-TEST-SPLIT-90-5-5.json 
    python ../xsum/xsum_split.py bbc-summary-data XSum-TRAINING-DEV-TEST-SPLIT-90-5-5.json xsum
    ```
  
### Evaluate with Fine-tuned BART

### Fine-tune Pre-trained BART

    

### Acknowledgements
* Original XSum repository: https://github.com/EdinburghNLP/XSum
* Link for data download: https://github.com/EdinburghNLP/XSum/issues/9
* 