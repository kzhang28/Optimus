set -x

echo "install prerequisites..."
sudo apt-get update
sudo apt-get install -y build-essential git
sudo apt-get install -y libopenblas-dev liblapack-dev libopencv-dev

cd ~
git clone --recursive https://github.com/apache/incubator-mxnet.git
mv incubator-mxnet mxnet
cd mxnet

MKLML_ROOT=/home/net/mxnet/mkl
[[ ":$LD_LIBRARY_PATH:" != *":${MKLML_ROOT}/lib:"* ]] && echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${MKLML_ROOT}/lib" >> ~/.bashrc && source ~/.bashrc

nvidia-smi
if [ $? -eq 0 ]; then
    echo "install mxnet GPU version..."
    make -j $(nproc) USE_OPENCV=1 USE_BLAS=openblas USE_CUDA=1 USE_CUDA_PATH=/usr/local/cuda USE_CUDNN=1 USE_DIST_KVSTORE=1 USE_MKL2017=1 USE_MKL2017_EXPERIMENTAL=1 MKLML_ROOT=$MKLML_ROOT
else
    echo "install mxnet CPU version..."
    make -j $(nproc) USE_OPENCV=1 USE_BLAS=openblas USE_DIST_KVSTORE=1 USE_MKL2017=1 USE_MKL2017_EXPERIMENTAL=1 MKLML_ROOT=$MKLML_ROOT
fi

echo "install python binding..."
sudo apt-get install -y python-dev python-setuptools python-numpy python-pip
cd python
python setup.py build
sudo python setup.py install

