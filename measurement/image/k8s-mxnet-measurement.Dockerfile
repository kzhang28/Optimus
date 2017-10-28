# build an measurement image

FROM yhpeng/mxnet-cpu

MAINTAINER yhpeng

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

ENV BUILD_OPTS "USE_OPENCV=1 USE_BLAS=openblas USE_DIST_KVSTORE=1"
RUN cd mxnet && make clean && \
    make -j $(nproc) $BUILD_OPTS && \
    cd python && python setup.py build && python setup.py install