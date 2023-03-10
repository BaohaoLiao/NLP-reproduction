# NLP-reproduction
This repository aims to offer straightforward guidance to reproduce the results from 
NLP papers. We only focus on the tasks that are not easy to reproduce with the official 
guidance, and try to obtain almost the same scores reported in papers. 

Your ⭐ motivate us to continue!!!

### Summarization
* [XSum](summarization/README.xsum.md)

  Method |     R1     |    R2     | RL
  ---|:----------:|:---------:|:---:
  `BART paper` |   45.14    | **22.27** | **37.25** 
  `evaluate fine-tuned BART (our)` | **45.20**  |   21.91   | 36.69
  `finetune pre-tuned BART (our)` |  | |

  * Download and split [2023.03.09]
  * Evaluate fine-tuned BART on fairseq [2023.03.09]
  * TODO: 
    * Finetune pre-trained BART on fairseq

* [CNN/DM](summarization/README.cnndm.md)

  Method |    R1     |    R2     | RL
  ---|:---------:|:---------:|:---:
  `BART paper` |   44.16   |   21.28   | 40.90 
  `evaluate fine-tuned BART (our)` | **44.26** | **21.31** | **41.06**
  `finetune pre-tuned BART (our)` |           |           |

  * Download and preprocess [2023.03.10]
  * Evaluate fine-tuned BART on fairseq [2023.03.10]
  * TODO:
    * Finetune pre-trained BART on fairseq


### Translation
* WMT16 En-Ro  
  * TODO:
    * Data preprocessing
    * Fintune mBART-CC25 
    * post-processing script