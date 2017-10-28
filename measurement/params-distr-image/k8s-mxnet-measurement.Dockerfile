# build an measurement image

FROM xxx/mxnet-cpu

MAINTAINER xxx

COPY scripts/init.py /
COPY scripts/start.py /
COPY scripts/speed-monitor.py /

COPY scripts/train_mnist.py /mxnet/example/image-classification/
COPY scripts/train_cifar10.py /mxnet/example/image-classification/
COPY scripts/train_imagenet.py /mxnet/example/image-classification/
COPY scripts/fit.py /mxnet/example/image-classification/common/
COPY scripts/data.py /mxnet/example/image-classification/common/

COPY scripts/model.py /mxnet/python/mxnet/
COPY scripts/base_module.py /mxnet/python/mxnet/module/

# recompile tainted mxnet
COPY scripts/kvstore_dist.h /mxnet/src/kvstore/
COPY scripts/kvstore_dist_server.h /mxnet/src/kvstore/
COPY scripts/kv_app.h /mxnet/ps-lite/include/ps/

ENV BUILD_OPTS "USE_OPENCV=1 USE_BLAS=openblas USE_DIST_KVSTORE=1 USE_MKL2017=1 USE_MKL2017_EXPERIMENTAL=1 MKLML_ROOT=/mxnet/mkl"
ENV LD_LIBRARY_PATH /mxnet/mkl/lib:$LD_LIBRARY_PATH

# RUN echo "export LD_LIBRARY_PATH=/mxnet/mkl/lib:$LD_LIBRARY_PATH" >> ~/.bashrc
RUN cd mxnet && make clean && \
    make -j $(nproc) $BUILD_OPTS && \
    cd python && python setup.py build && python setup.py install