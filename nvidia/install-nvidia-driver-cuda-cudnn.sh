set -ex

echo "copy nvidia folder from net-r5..."
scp -oBindAddress=10.29.1.* -r net@10.29.1.15:~/nvidia ./

echo "install nvidia driver..."
cd nvidia
chmod +x NVIDIA-Linux-x86_64-375.66.run
sudo ./NVIDIA-Linux-x86_64-375.66.run -a

echo "install cuda..."
sudo dpkg -i cuda-repo-ubuntu1404_8.0.61-1_amd64.deb && sudo apt-get update && sudo apt-get install cuda

echo "install cudnn..."
tar -xvf cudnn-8.0-linux-x64-v6.0.tgz
cd cuda
sudo cp -P include/cudnn.h /usr/include
sudo cp -P lib64/libcudnn* /usr/lib/x86_64-linux-gnu/
sudo chmod a+r /usr/lib/x86_64-linux-gnu/libcudnn*