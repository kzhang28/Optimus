#Use this script to run the speech_recognition  python2 
#! /bin/bash
sudo rm /usr/bin/python
sudo ln -s /usr/bin/python2.7 /usr/bin/python # change to python2 

wget https://bootstrap.pypa.io/get-pip.py
sudo python2 get-pip.py                        #pip 9

sudo -H pip2 install tensorboard 
sudo -H pip2 install soundfile
sudo -H pip2 install  wget

sudo apt-get -y install sox 
sudo apt-get -y install cmake 


cd ~/
warp_path='~/warp-ctc' 

if [ ! -x "$warp_path" ]; then
  git clone https://github.com/baidu-research/warp-ctc
  cd warp-ctc
  mkdir build
  cd build
  cmake ..
  make 
  sudo make install
fi

sed -i '/WARPCTC_PATH/s/^#//' /./mxnet/make/config.mk  
sed -i '/warpctc.mk/s/^#//' /./mxnet/make/config.mk  

sed -i '25c train_json = /./data/Libri_train.json' /./mxnet/example/speech_recognition/default.cfg
sed -i '26c test_json = /./data/Libri_test.json' /./mxnet/example/speech_recognition/default.cfg
sed -i '27c val_json = /./data/Libri_val.json' /./mxnet/example/speech_recognition/default.cfg


sed -i '27c train_json = /./data/Libri_train.json' /./mxnet/example/speech_recognition/deepspeech.cfg
sed -i '28c test_json = /./data/Libri_test.json' /./mxnet/example/speech_recognition/deepspeech.cfg
sed -i '29c val_json = /./data/Libri_val.json' /./mxnet/example/speech_recognition/deepspeech.cfg

cd /./mxnet
make clean
make -j $(nproc) USE_OPENCV=1 USE_BLAS=openblas USE_CUDA=1 USE_CUDA_PATH=/usr/local/cuda USE_CUDNN=1   

cd /./mxnet/python
python2 setup.py install

cd /./mxnet/example/speech_recognition                  
mkdir checkpoints
mkdir log

if [ ! -f "/./data/Libri_train.json" ]; then
  cd /.
  python2 librispeech.py
fi

if [  -f "/usr/lib/libwarpctc.so" ]; then
  rm /usr/lib/libwarpctc.so
fi
ln -s ~/warp-ctc/build/libwarpctc.so /usr/lib
cd /./mxnet/example/speech_recognition
python2 main.py --configfile default.cfg --archfile arch_deepspeech
