set -ex

apt-get update

# neural machine translation
echo "prepare environment for neural machine translation example..."

apt-get install -y python3-dev python3-pip

wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
rm get-pip.py
pip3 install typing
pip3 install pyyaml setuptools numpy


cp -r /mxnet/python /mxnet/python3
cd /mxnet/python3/
python3 setup.py install

cd /mxnet/example/
mkdir nmt
cd nmt

#pip3 install sockeye

wget https://raw.githubusercontent.com/awslabs/sockeye/master/requirements.gpu-cu80.txt
pip3 install sockeye --no-deps -r requirements.gpu-cu80.txt
rm requirements.gpu-cu80.txt
