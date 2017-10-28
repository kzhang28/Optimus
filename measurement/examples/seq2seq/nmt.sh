#Use this script to run the translation  python3 
#! /bin/bash

set -ex

apt-get update
apt-get install -y python3-yaml
apt-get install -y python3-dev python3-setuptools python3-numpy python3-pip

#sudo rm /usr/bin/python
#sudo ln -s /usr/bin/python3.4 /usr/bin/python 

wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
rm get-pip.py
#sudo -H pip3 install tensorboard
sudo -H pip3 install typing       

cp -r /mxnet/python /mxnet/python3
cd /mxnet/python3/
sudo python3 setup.py install

cd /mxnet/example/
mkdir nmt       
wget https://raw.githubusercontent.com/awslabs/sockeye/master/requirements.gpu-cu80.txt
pip3 install sockeye --no-deps -r requirements.gpu-cu80.txt

cd /data
if [ ! -f "/data/train.de" ]; then
  wget http://data.statmt.org/wmt17/translation-task/preprocessed/de-en/corpus.tc.de.gz
  gunzip corpus.tc.de.gz
  head -n 1000000 corpus.tc.de>train.de
fi
if [ ! -f "/data/train.en" ]; then
  wget http://data.statmt.org/wmt17/translation-task/preprocessed/de-en/corpus.tc.en.gz
  gunzip corpus.tc.en.gz
  head -n 1000000 corpus.tc.en >train.en
fi
if [ ! -x "/data/dev" ]; then
  mkdir dev
  cd /./data/dev
  wget http://data.statmt.org/wmt17/translation-task/preprocessed/de-en/dev.tgz
  tar -xvzf dev.tgz
fi
cd /data
python3 -m sockeye.train -s train.de -t train.en  -vs dev/newstest2016.tc.de -vt dev/newstest2016.tc.en --num-embed 128 --rnn-num-hidden 512 --attention-type dot --embed-dropout 0.2 --word-min-count 10 -o nmt_model --device-ids 1 --batch-size 64 ####
