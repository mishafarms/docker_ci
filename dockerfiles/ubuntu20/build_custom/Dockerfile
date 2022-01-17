# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
FROM nvidia/cuda:11.4.1-cudnn8-devel-ubuntu20.04 AS setup_openvino

LABEL description="This is the dev image for Intel(R) Distribution of OpenVINO(TM) toolkit on Ubuntu 20.04 LTS"
LABEL vendor="Intel Corporation"

# hadolint ignore=DL3008
RUN apt-get update; \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
        apt-utils \
        git \
        git-lfs \
        ca-certificates \
        sudo \
        tzdata; \
    rm -rf /var/lib/apt/lists/*

ARG OPENVINO_FORK="openvinotoolkit"
ARG OPENVINO_BRANCH="master"
ARG OMZ_BRANCH

# hadolint ignore=DL3003
RUN git-lfs install; \
    git clone https://github.com/${OPENVINO_FORK}/openvino.git \
    --recurse-submodules --shallow-submodules --depth 1 -b ${OPENVINO_BRANCH} /opt/intel/repo/openvino; \
    if [ -n "$OMZ_BRANCH" ]; then  \
      cd /opt/intel/repo/openvino/thirdparty/open_model_zoo && \
      git remote set-branches origin '*' && \
      git fetch --depth 1 origin "$OMZ_BRANCH" && \
      git checkout "$OMZ_BRANCH"; \
    fi

WORKDIR /opt/intel/repo/openvino
RUN chmod +x install_build_dependencies.sh; \
    ./install_build_dependencies.sh

ARG OCL_VERSION="19.41.14441"

RUN chmod +x scripts/install_dependencies/install_NEO_OCL_driver.sh; \
    ./scripts/install_dependencies/install_NEO_OCL_driver.sh -y --no_numa -d ${OCL_VERSION}

# hadolint ignore=DL3013
RUN chmod +x scripts/install_dependencies/install_openvino_dependencies.sh; \
    ./scripts/install_dependencies/install_openvino_dependencies.sh -y -c=python; \
    python3 -m pip install --no-cache-dir --upgrade pip; \
    python3 -m pip install --no-cache-dir -r inference-engine/ie_bridges/python/src/requirements-dev.txt

WORKDIR /opt/intel/repo
CMD ["/bin/bash"]
# -------------------------------------------------------------------------------------------------
FROM setup_openvino AS build_openvino

LABEL description="This is the dev image for Intel(R) Distribution of OpenVINO(TM) toolkit on Ubuntu 20.04 LTS"
LABEL vendor="Intel Corporation"

COPY openvino_cmake.txt /opt/intel/repo

RUN python3 -m pip install --no-cache-dir -r /opt/intel/repo/openvino/src/bindings/python/wheel/requirements-dev.txt

WORKDIR /opt/intel/repo/openvino/build
# hadolint ignore=SC2046
RUN cmake $(cat /opt/intel/repo/openvino_cmake.txt) /opt/intel/repo/openvino; \
    make "-j$(nproc)"; \
    make install

WORKDIR /tmp
RUN curl -L https://github.com/libusb/libusb/archive/v1.0.22.zip --output v1.0.22.zip; \
    unzip v1.0.22.zip; \
    rm -rf v1.0.22.zip

WORKDIR /tmp/libusb-1.0.22
RUN ./bootstrap.sh; \
    ./configure --disable-udev --enable-shared; \
    make "-j$(nproc)"

WORKDIR /opt/intel/repo
CMD ["/bin/bash"]
# -------------------------------------------------------------------------------------------------
FROM nvidia/cuda:11.4.1-cudnn8-devel-ubuntu20.04 AS copy_openvino

LABEL description="This is the dev image for Intel(R) Distribution of OpenVINO(TM) toolkit on Ubuntu 20.04 LTS"
LABEL vendor="Intel Corporation"

ENV INTEL_OPENVINO_DIR="/opt/intel/openvino"

COPY --from=build_openvino /opt/intel/repo /opt/intel/repo
RUN rm -rf /opt/intel/repo/openvino/build/install
COPY --from=build_openvino /opt/intel/repo/openvino/build/install ${INTEL_OPENVINO_DIR}
COPY --from=build_openvino /opt/intel/repo/openvino/thirdparty/open_model_zoo/demos ${INTEL_OPENVINO_DIR}/demos
COPY --from=build_openvino /tmp/libusb-1.0.22 /opt/libusb-1.0.22

WORKDIR ${INTEL_OPENVINO_DIR}
CMD ["/bin/bash"]
# -------------------------------------------------------------------------------------------------
FROM copy_openvino AS openvino

LABEL description="This is the dev image for Intel(R) Distribution of OpenVINO(TM) toolkit on Ubuntu 20.04 LTS"
LABEL vendor="Intel Corporation"

# hadolint ignore=DL3008
RUN apt-get update; \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
        apt-utils \
        wget \
        udev \
        sudo \
        gdb \
        tzdata; \
    rm -rf /var/lib/apt/lists/*

WORKDIR ${INTEL_OPENVINO_DIR}
RUN chmod +x install_dependencies/install_openvino_dependencies.sh; \
    ./install_dependencies/install_openvino_dependencies.sh -y -c=python -c=dev

ARG OCL_VERSION="19.41.14441"

RUN chmod +x install_dependencies/install_NEO_OCL_driver.sh; \
    ./install_dependencies/install_NEO_OCL_driver.sh -y --no_numa -d ${OCL_VERSION}

WORKDIR /opt/libusb-1.0.22
RUN ./libtool --mode=install install -c libusb/libusb-1.0.la /usr/local/lib/; \
    mkdir -p /usr/local/include/libusb-1.0; \
    install -c -m 644 libusb/libusb.h /usr/local/include/libusb-1.0; \
    mkdir -p /usr/local/lib/pkgconfig; \
    install -c -m 644 libusb-1.0.pc /usr/local/lib/pkgconfig

WORKDIR ${INTEL_OPENVINO_DIR}
RUN chmod +x install_dependencies/install_NCS_udev_rules.sh; \
    ./install_dependencies/install_NCS_udev_rules.sh

# hadolint ignore=DL3013
RUN python3 -m pip install --no-cache-dir --upgrade pip; \
    python3 -m pip install --no-cache-dir -r python/python3.8/requirements.txt; \
    python3 -m pip install --no-cache-dir openvino --find-links=tools/ ; \
    python3 -m pip install --no-cache-dir 'openvino_dev[caffe,kaldi,mxnet,onnx,pytorch,tensorflow2]' --find-links=tools/

RUN printf "\nsource \${INTEL_OPENVINO_DIR}/setupvars.sh\n" >> /root/.bashrc

CMD ["/bin/bash"]
# -------------------------------------------------------------------------------------------------
FROM openvino AS opencv

LABEL description="This is the dev image for Intel(R) Distribution of OpenVINO(TM) toolkit on Ubuntu 20.04 LTS"
LABEL vendor="Intel Corporation"

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# hadolint ignore=DL3008
RUN apt-get update; \
    apt-get install -y --no-install-recommends \
        git \
        libva-dev \
        libgtk-3-dev \
        libavcodec-dev \
        libavformat-dev \
        libavutil-dev \
        libswscale-dev \
        libavresample-dev \
        libgstreamer1.0-dev \
        libgstreamer-plugins-base1.0-dev \
        libgstreamer-plugins-good1.0-dev \
        libgstreamer-plugins-bad1.0-dev \
	libjpeg-dev \
	libpng-dev \
	libtiff-dev \
	libxvidcore-dev \
	x264 \
	libx264-dev \
	libfaac-dev \
	libmp3lame-dev \
	libtheora-dev \
	libfaac-dev \
	libmp3lame-dev \
	libvorbis-dev \
	libopencore-amrnb-dev \
	libopencore-amrwb-dev \
	libdc1394-22 \
	libdc1394-22-dev \
	libxine2-dev \
	libv4l-dev \
	v4l-utils \
	python3-dev \
	python3-pip \
	python3-testresources \
	libtbb-dev \
	libatlas-base-dev \
	gfortran \
	libprotobuf-dev \
	protobuf-compiler \
	libgoogle-glog-dev \
	libgflags-dev \
	libgphoto2-dev \
	libeigen3-dev \
	libhdf5-dev doxygen; \
    rm -rf /var/lib/apt/lists/*
#pushd /usr/include/linux
#sudo ln -s -f ../libv4l1-videodev.h videodev.h
#popd

WORKDIR /usr/include/linux
RUN ln -s -f ../libv4l1-videodev.h videodev.h

# get the latest cmake
RUN apt remove -y --purge --auto-remove cmake ; \
	apt update && \
	apt install -y software-properties-common lsb-release && \
	apt clean all; \
	wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | sudo tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null; \
	apt-add-repository "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main"; \
	apt update; \
	apt install -y cmake

ARG OPENCV_BRANCH="4.5.3"

ARG BUILD_OPENCV_CONTRIB="yes"
ARG OPENCV_CONTRIB_BRANCH="4.5.3"

WORKDIR /opt/intel/repo
RUN git clone https://github.com/opencv/opencv.git --depth 1 -b ${OPENCV_BRANCH} && \
    if [ "$BUILD_OPENCV_CONTRIB" = "yes" ]; then \
    git clone https://github.com/opencv/opencv_contrib.git --depth 1 -b ${OPENCV_CONTRIB_BRANCH}; fi

COPY opencv_cmake.txt /opt/intel/repo

WORKDIR /opt/intel/repo/opencv/build
# hadolint ignore=SC2046
RUN . "${INTEL_OPENVINO_DIR}/setupvars.sh"; \
    if [ "$BUILD_OPENCV_CONTRIB" = "yes" ]; then \
      apt-get update && \
      apt-get install -y --no-install-recommends libtesseract-dev && \
      cmake $(cat /opt/intel/repo/opencv_cmake.txt) -D OPENCV_EXTRA_MODULES_PATH=/opt/intel/repo/opencv_contrib/modules /opt/intel/repo/opencv && \
      rm -rf /var/lib/apt/lists/* ; \
    else \
      cmake $(cat /opt/intel/repo/opencv_cmake.txt) /opt/intel/repo/opencv; \
    fi; \
    make "-j$(nproc)"; \
    make install

WORKDIR /opt/intel/repo/opencv/build/install
RUN mkdir "${INTEL_OPENVINO_DIR}/extras"; \
    cp -r . "${INTEL_OPENVINO_DIR}/extras/opencv"; \
    cp -r "${INTEL_OPENVINO_DIR}/extras/opencv/python/python3" "${INTEL_OPENVINO_DIR}/python"; \
    rm -r "${INTEL_OPENVINO_DIR}/extras/opencv/python"; \
    echo "export OpenCV_DIR=${INTEL_OPENVINO_DIR}/extras/opencv/cmake" | tee -a "${INTEL_OPENVINO_DIR}/extras/opencv/setupvars.sh"; \
    echo "export LD_LIBRARY_PATH=${INTEL_OPENVINO_DIR}/extras/opencv/lib:\$LD_LIBRARY_PATH" | tee -a "${INTEL_OPENVINO_DIR}/extras/opencv/setupvars.sh"; \
    python3 -m pip uninstall -y opencv-python; \
    rm -rf /opt/intel/repo/opencv/build/install

RUN apt update ; apt install -y python3-tk
RUN pip install tk
RUN pip install fiftyone

#RUN mkdir /opt/tensorflow
WORKDIR /opt/tensorflow/ 
RUN git clone https://github.com/tensorflow/models.git

WORKDIR /opt/tensorflow/models/research
RUN protoc object_detection/protos/*.proto --python_out=.

RUN pip install tensorflow_hub
RUN pip install jupyterlab
 
RUN mkdir -p /usr/local/nvidia/lib64
RUN ln -s /usr/local/cuda-11.4/targets/x86_64-linux/lib/libcusolver.so.11 /usr/local/nvidia/lib64/libcusolver.so.10

RUN apt update
RUN apt install -y python3-venv


WORKDIR ${INTEL_OPENVINO_DIR}
CMD ["/bin/bash"]
