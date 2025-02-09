# -*- coding: utf-8 -*-
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
import pytest


@pytest.mark.usefixtures('_is_image_os', '_is_distribution')
@pytest.mark.parametrize('_is_image_os', [('ubuntu18', 'ubuntu20')], indirect=True)
@pytest.mark.parametrize('_is_distribution', [('data_dev', 'proprietary')], indirect=True)
class TestDLStreamerLinux:
    def test_draw_face_attributes_cpp_cpu(self, tester, image, install_openvino_dependencies, bash):
        kwargs = {'mem_limit': '3g'}
        tester.test_docker_image(
            image,
            [install_openvino_dependencies,
             bash('cd /opt/intel/openvino/extras/dl_streamer/samples && '
                  './download_models.sh && cd cpp/draw_face_attributes && mkdir build && '
                  'cd build && cmake ../ && make && '
                  'curl -O https://storage.openvinotoolkit.org/data/test_data/videos/face-demographics-walking.mp4 && '
                  './draw_face_attributes -i face-demographics-walking.mp4 -n')],
            self.test_draw_face_attributes_cpp_cpu.__name__, **kwargs,
        )

    @pytest.mark.gpu
    def test_draw_face_attributes_cpp_gpu(self, tester, image, install_openvino_dependencies, bash):
        kwargs = {'devices': ['/dev/dri:/dev/dri'], 'mem_limit': '3g'}
        tester.test_docker_image(
            image,
            [install_openvino_dependencies,
             bash('cd /opt/intel/openvino/extras/dl_streamer/samples && '
                  './download_models.sh && cd cpp/draw_face_attributes && mkdir build && '
                  'cd build && cmake ../ && make && '
                  'curl -O https://storage.openvinotoolkit.org/data/test_data/videos/face-demographics-walking.mp4 && '
                  './draw_face_attributes -i face-demographics-walking.mp4 -n -d GPU')],
            self.test_draw_face_attributes_cpp_gpu.__name__, **kwargs,
        )

    @pytest.mark.vpu
    @pytest.mark.xfail_log(pattern='Can not init Myriad device: NC_ERROR', reason='Sporadic error on MYRIAD device')
    def test_draw_face_attributes_cpp_vpu(self, tester, image, install_openvino_dependencies, bash):
        kwargs = {'device_cgroup_rules': ['c 189:* rmw'],
                  'volumes': ['/dev/bus/usb:/dev/bus/usb'], 'mem_limit': '3g'}  # nosec # noqa: S108
        tester.test_docker_image(
            image,
            [install_openvino_dependencies,
             bash('cd /opt/intel/openvino/extras/dl_streamer/samples && '
                  './download_models.sh && cd cpp/draw_face_attributes && mkdir build && '
                  'cd build && cmake ../ && make && '
                  'curl -O https://storage.openvinotoolkit.org/data/test_data/videos/face-demographics-walking.mp4 && '
                  './draw_face_attributes -i face-demographics-walking.mp4 -n -d MYRIAD -p FP16')],
            self.test_draw_face_attributes_cpp_vpu.__name__, **kwargs,
        )

    @pytest.mark.hddl
    def test_draw_face_attributes_cpp_hddl(self, tester, image, install_openvino_dependencies, bash):
        kwargs = {'devices': ['/dev/ion:/dev/ion'],
                  'volumes': ['/var/tmp:/var/tmp', '/dev/shm:/dev/shm'], 'mem_limit': '3g'}  # nosec # noqa: S108
        tester.test_docker_image(
            image,
            [install_openvino_dependencies,
             bash('cd /opt/intel/openvino/extras/dl_streamer/samples && '
                  './download_models.sh && cd cpp/draw_face_attributes && mkdir build && '
                  'cd build && cmake ../ && make && '
                  'curl -O https://storage.openvinotoolkit.org/data/test_data/videos/face-demographics-walking.mp4 && '
                  'umask 0000 && ./draw_face_attributes -i face-demographics-walking.mp4 -n -d HDDL && '
                  'rm -f /dev/shm/hddl_*')],
            self.test_draw_face_attributes_cpp_hddl.__name__, **kwargs,
        )

    def test_gst_launch_audio_detect(self, tester, image, install_openvino_dependencies, product_version, bash):
        kwargs = {'mem_limit': '3g'}
        tester.test_docker_image(
            image,
            [install_openvino_dependencies,
             bash('cd /opt/intel/openvino/extras/dl_streamer/samples/gst_launch/audio_detect && '
                  '../../download_models.sh && ./audio_event_detection.sh')],
            self.test_gst_launch_audio_detect.__name__, **kwargs,
        )

    def test_gst_launch_metapublish(self, tester, image, install_openvino_dependencies, bash):
        kwargs = {'mem_limit': '3g'}
        tester.test_docker_image(
            image,
            [install_openvino_dependencies,
             bash('cd /opt/intel/openvino/extras/dl_streamer/samples && '
                  './download_models.sh && cd gst_launch/metapublish && ./metapublish.sh')],
            self.test_gst_launch_metapublish.__name__, **kwargs,
        )
