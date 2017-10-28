# build an experiment image

FROM xxx/mxnet-cpu

MAINTAINER xxx

# experiment scripts
COPY scripts/init.sh /
RUN chmod +x /init.sh
COPY scripts/init.py /
COPY scripts/start.py /
COPY scripts/speed-monitor.py /
COPY scripts/progress-monitor.py /

# image-classification
COPY scripts/train_mnist.py /mxnet/example/image-classification/
COPY scripts/train_cifar10.py /mxnet/example/image-classification/
COPY scripts/train_imagenet.py /mxnet/example/image-classification/
COPY scripts/fit.py /mxnet/example/image-classification/common/
COPY scripts/data.py /mxnet/example/image-classification/common/

# neural machine translation
COPY scripts/prep_env.sh /
RUN chmod +x /prep_env.sh
RUN /bin/bash /prep_env.sh

# parameter load balancing
COPY scripts/model.py /mxnet/python/mxnet/
COPY scripts/base_module.py /mxnet/python/mxnet/module/

COPY scripts/kvstore_dist.h /mxnet/src/kvstore/
COPY scripts/kvstore_dist_server.h /mxnet/src/kvstore/
COPY scripts/kv_app.h /mxnet/ps-lite/include/ps/

# cnn text classification
COPY scripts/text_cnn.py /mxnet/example/cnn_text_classification/
COPY scripts/data_helpers.py /mxnet/example/cnn_text_classification/

# recomplile with INTEL_MKL
ENV BUILD_OPTS "USE_OPENCV=1 USE_BLAS=openblas USE_DIST_KVSTORE=1 USE_MKL2017=1 USE_MKL2017_EXPERIMENTAL=1 MKLML_ROOT=/mxnet/mkl"
ENV LD_LIBRARY_PATH /mxnet/mkl/lib:$LD_LIBRARY_PATH

RUN cd mxnet && make clean && \
    make -j $(nproc) $BUILD_OPTS && \
    cd python && python setup.py build && python setup.py install

CMD sleep 1000000000