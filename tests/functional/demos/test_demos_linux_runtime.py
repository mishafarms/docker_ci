# -*- coding: utf-8 -*-
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
import pytest


@pytest.mark.usefixtures('_is_image_os', '_is_distribution', '_is_package_url_specified')
@pytest.mark.parametrize('_is_image_os', [('ubuntu18', 'ubuntu20', 'rhel8')], indirect=True)
@pytest.mark.parametrize('_is_distribution', [('data_runtime', 'custom-no-cv')], indirect=True)
class TestDemosLinuxDataRuntime:
    @pytest.mark.usefixtures('_python_ngraph_required')
    @pytest.mark.parametrize('omz_python_demo_path', ['object_detection'], indirect=True)
    def test_detection_ssd_python_cpu(self, tester, image, distribution, dev_root, omz_python_demo_path,
                                      omz_python_demos_requirements_file, bash):
        kwargs = {
            'mem_limit': '3g',
            'volumes': {
                dev_root / 'samples' / 'scripts': {
                    'bind': '/opt/intel/openvino/samples/scripts',
                },
                dev_root / 'extras' / 'open_model_zoo': {
                    'bind': '/opt/intel/openvino/extras/open_model_zoo',
                },
            },
        }
        tester.test_docker_image(
            image,
            [bash(f'python3 -m pip install --no-cache-dir {"opencv-python" if distribution == "custom-no-cv" else ""} '
                  '-r /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/requirements.in '
                  f'-r {omz_python_demos_requirements_file} && '
                  'python3 /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/downloader.py '
                  '--name vehicle-detection-adas-0002 --precision FP16'),
             bash(f'python3 {omz_python_demo_path} '
                  '-m /opt/intel/openvino/intel/vehicle-detection-adas-0002/FP16/vehicle-detection-adas-0002.xml '
                  '-i /opt/intel/openvino/samples/scripts/car_1.bmp -d CPU --no_show -r'),
             ], self.test_detection_ssd_python_cpu.__name__, **kwargs,
        )

    @pytest.mark.gpu
    @pytest.mark.usefixtures('_python_ngraph_required')
    @pytest.mark.parametrize('omz_python_demo_path', ['object_detection'], indirect=True)
    def test_detection_ssd_python_gpu(self, tester, image, distribution, dev_root, omz_python_demo_path,
                                      omz_python_demos_requirements_file, bash):
        kwargs = {
            'devices': ['/dev/dri:/dev/dri'],
            'mem_limit': '3g',
            'volumes': {
                dev_root / 'samples' / 'scripts': {
                    'bind': '/opt/intel/openvino/samples/scripts',
                },
                dev_root / 'extras' / 'open_model_zoo': {
                    'bind': '/opt/intel/openvino/extras/open_model_zoo',
                },
            },
        }
        tester.test_docker_image(
            image,
            [bash(f'python3 -m pip install --no-cache-dir {"opencv-python" if distribution == "custom-no-cv" else ""} '
                  '-r /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/requirements.in '
                  f'-r {omz_python_demos_requirements_file} && '
                  'python3 /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/downloader.py '
                  '--name vehicle-detection-adas-0002 --precision FP16'),
             bash(f'python3 {omz_python_demo_path} '
                  '-m /opt/intel/openvino/intel/vehicle-detection-adas-0002/FP16/vehicle-detection-adas-0002.xml '
                  '-i /opt/intel/openvino/samples/scripts/car_1.bmp -d GPU --no_show -r'),
             ], self.test_detection_ssd_python_gpu.__name__, **kwargs,
        )

    @pytest.mark.vpu
    @pytest.mark.usefixtures('_python_ngraph_required', '_python_vpu_plugin_required')
    @pytest.mark.parametrize('omz_python_demo_path', ['object_detection'], indirect=True)
    @pytest.mark.xfail_log(pattern='Can not init Myriad device: NC_ERROR', reason='Sporadic error on MYRIAD device')
    def test_detection_ssd_python_vpu(self, tester, image, distribution, dev_root, omz_python_demo_path,
                                      omz_python_demos_requirements_file, bash):
        kwargs = {
            'device_cgroup_rules': ['c 189:* rmw'],
            'mem_limit': '3g',
            'volumes': {
                '/dev/bus/usb': {
                    'bind': '/dev/bus/usb',
                },
                dev_root / 'samples' / 'scripts': {
                    'bind': '/opt/intel/openvino/samples/scripts',
                },
                dev_root / 'extras' / 'open_model_zoo': {
                    'bind': '/opt/intel/openvino/extras/open_model_zoo',
                },
            },
        }
        tester.test_docker_image(
            image,
            [bash(f'python3 -m pip install --no-cache-dir {"opencv-python" if distribution == "custom-no-cv" else ""} '
                  '-r /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/requirements.in '
                  f'-r {omz_python_demos_requirements_file} && '
                  'python3 /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/downloader.py '
                  '--name vehicle-detection-adas-0002 --precision FP16'),
             bash(f'python3 {omz_python_demo_path} '
                  '-m /opt/intel/openvino/intel/vehicle-detection-adas-0002/FP16/vehicle-detection-adas-0002.xml '
                  '-i /opt/intel/openvino/samples/scripts/car_1.bmp -d MYRIAD --no_show -r'),
             ], self.test_detection_ssd_python_vpu.__name__, **kwargs,
        )

    @pytest.mark.hddl
    @pytest.mark.usefixtures('_python_ngraph_required', '_is_not_image_os')
    @pytest.mark.parametrize('_is_not_image_os', [('rhel8')], indirect=True)
    @pytest.mark.parametrize('omz_python_demo_path', ['object_detection'], indirect=True)
    def test_detection_ssd_python_hddl(self, tester, image, distribution, dev_root, omz_python_demo_path,
                                       omz_python_demos_requirements_file, bash):
        kwargs = {
            'devices': ['/dev/ion:/dev/ion'],
            'mem_limit': '3g',
            'volumes': {
                '/var/tmp': {'bind': '/var/tmp'},  # nosec # noqa: S108
                '/dev/shm': {'bind': '/dev/shm'},  # nosec # noqa: S108
                dev_root / 'samples' / 'scripts': {
                    'bind': '/opt/intel/openvino/samples/scripts',
                },
                dev_root / 'extras' / 'open_model_zoo': {
                    'bind': '/opt/intel/openvino/extras/open_model_zoo',
                },
            },
        }
        tester.test_docker_image(
            image,
            [bash(f'python3 -m pip install --no-cache-dir {"opencv-python" if distribution == "custom-no-cv" else ""} '
                  '-r /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/requirements.in '
                  f'-r {omz_python_demos_requirements_file} && '
                  'python3 /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/downloader.py '
                  '--name vehicle-detection-adas-0002 --precision FP16'),
             bash(f'umask 0000 && python3 {omz_python_demo_path} '
                  '-m /opt/intel/openvino/intel/vehicle-detection-adas-0002/FP16/vehicle-detection-adas-0002.xml '
                  '-i /opt/intel/openvino/samples/scripts/car_1.bmp -d HDDL --no_show -r && '
                  'rm -f /dev/shm/hddl_*'),
             ], self.test_detection_ssd_python_hddl.__name__, **kwargs,
        )


@pytest.mark.usefixtures('_is_image_os', '_is_distribution', '_is_package_url_specified')
@pytest.mark.parametrize('_is_image_os', [('ubuntu18', 'ubuntu20', 'rhel8')], indirect=True)
@pytest.mark.parametrize('_is_distribution', [('runtime', 'custom-no-cv')], indirect=True)
class TestDemosLinuxRuntime:
    @pytest.mark.parametrize('omz_python_demo_path', ['segmentation'], indirect=True)
    def test_segmentation_python_cpu(self, tester, image, distribution, dev_root, omz_python_demo_path,
                                     omz_python_demos_requirements_file, bash):
        kwargs = {
            'mem_limit': '3g',
            'volumes': {
                dev_root / 'samples' / 'scripts': {
                    'bind': '/opt/intel/openvino/samples/scripts',
                },
                dev_root / 'extras' / 'open_model_zoo': {
                    'bind': '/opt/intel/openvino/extras/open_model_zoo',
                },
            },
        }
        tester.test_docker_image(
            image,
            [bash('python3 -m pip install setuptools && '
                  f'python3 -m pip install --no-cache-dir {"opencv-python" if distribution == "custom-no-cv" else ""} '
                  '-r /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/requirements.in '
                  f'-r {omz_python_demos_requirements_file} && '
                  'python3 /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/downloader.py '
                  '--name semantic-segmentation-adas-0001 --precision FP16'),
             bash(f'python3 {omz_python_demo_path} '
                  '-m /opt/intel/openvino/intel/semantic-segmentation-adas-0001/FP16/'
                  'semantic-segmentation-adas-0001.xml '
                  '-i /opt/intel/openvino/samples/scripts/car_1.bmp -d CPU -at segmentation --no_show'),
             ],
            self.test_segmentation_python_cpu.__name__, **kwargs,
        )

    @pytest.mark.gpu
    @pytest.mark.parametrize('omz_python_demo_path', ['segmentation'], indirect=True)
    def test_segmentation_python_gpu(self, tester, image, distribution, dev_root, omz_python_demo_path,
                                     omz_python_demos_requirements_file, bash):
        kwargs = {
            'devices': ['/dev/dri:/dev/dri'],
            'mem_limit': '3g',
            'volumes': {
                dev_root / 'samples' / 'scripts': {
                    'bind': '/opt/intel/openvino/samples/scripts',
                },
                dev_root / 'extras' / 'open_model_zoo': {
                    'bind': '/opt/intel/openvino/extras/open_model_zoo',
                },
            },
        }
        tester.test_docker_image(
            image,
            [bash('python3 -m pip install setuptools && '
                  f'python3 -m pip install --no-cache-dir {"opencv-python" if distribution == "custom-no-cv" else ""} '
                  '-r /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/requirements.in '
                  f'-r {omz_python_demos_requirements_file} && '
                  'python3 /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/downloader.py '
                  '--name semantic-segmentation-adas-0001 --precision FP16'),
             bash(f'python3 {omz_python_demo_path} '
                  '-m /opt/intel/openvino/intel/semantic-segmentation-adas-0001/FP16/'
                  'semantic-segmentation-adas-0001.xml '
                  '-i /opt/intel/openvino/samples/scripts/car_1.bmp -d GPU -at segmentation --no_show'),
             ],
            self.test_segmentation_python_gpu.__name__, **kwargs,
        )

    @pytest.mark.vpu
    @pytest.mark.usefixtures('_python_vpu_plugin_required')
    @pytest.mark.parametrize('omz_python_demo_path', ['segmentation'], indirect=True)
    @pytest.mark.xfail_log(pattern='Can not init Myriad device: NC_ERROR', reason='Sporadic error on MYRIAD device')
    def test_segmentation_python_vpu(self, tester, image, distribution, dev_root, omz_python_demo_path,
                                     omz_python_demos_requirements_file, bash):
        kwargs = {
            'device_cgroup_rules': ['c 189:* rmw'],
            'mem_limit': '3g',
            'volumes': {
                '/dev/bus/usb': {
                    'bind': '/dev/bus/usb',
                },
                dev_root / 'samples' / 'scripts': {
                    'bind': '/opt/intel/openvino/samples/scripts',
                },
                dev_root / 'extras' / 'open_model_zoo': {
                    'bind': '/opt/intel/openvino/extras/open_model_zoo',
                },
            },
        }
        tester.test_docker_image(
            image,
            [bash('python3 -m pip install setuptools && '
                  f'python3 -m pip install --no-cache-dir {"opencv-python" if distribution == "custom-no-cv" else ""} '
                  '-r /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/requirements.in '
                  f'-r {omz_python_demos_requirements_file} && '
                  'python3 /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/downloader.py '
                  '--name semantic-segmentation-adas-0001 --precision FP16'),
             bash(f'python3 {omz_python_demo_path} '
                  '-m /opt/intel/openvino/intel/semantic-segmentation-adas-0001/FP16/'
                  'semantic-segmentation-adas-0001.xml '
                  '-i /opt/intel/openvino/samples/scripts/car_1.bmp -d MYRIAD -at segmentation --no_show'),
             ],
            self.test_segmentation_python_vpu.__name__, **kwargs,
        )

    @pytest.mark.hddl
    @pytest.mark.usefixtures('_is_not_image_os')
    @pytest.mark.parametrize('_is_not_image_os', [('rhel8')], indirect=True)
    @pytest.mark.parametrize('omz_python_demo_path', ['segmentation'], indirect=True)
    def test_segmentation_python_hddl(self, tester, image, distribution, dev_root, omz_python_demo_path,
                                      omz_python_demos_requirements_file, bash):
        kwargs = {
            'devices': ['/dev/ion:/dev/ion'],
            'mem_limit': '3g',
            'volumes': {
                '/var/tmp': {'bind': '/var/tmp'},  # nosec # noqa: S108
                '/dev/shm': {'bind': '/dev/shm'},  # nosec # noqa: S108
                dev_root / 'samples' / 'scripts': {
                    'bind': '/opt/intel/openvino/samples/scripts',
                },
                dev_root / 'extras' / 'open_model_zoo': {
                    'bind': '/opt/intel/openvino/extras/open_model_zoo',
                },
            },
        }
        tester.test_docker_image(
            image,
            [bash('python3 -m pip install setuptools && '
                  f'python3 -m pip install --no-cache-dir {"opencv-python" if distribution == "custom-no-cv" else ""} '
                  '-r /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/requirements.in '
                  f'-r {omz_python_demos_requirements_file} && '
                  'python3 /opt/intel/openvino/extras/open_model_zoo/tools/model_tools/downloader.py '
                  '--name semantic-segmentation-adas-0001 --precision FP16'),
             bash(f'umask 0000 && python3 {omz_python_demo_path} -at segmentation --no_show '
                  '-m /opt/intel/openvino/intel/semantic-segmentation-adas-0001/FP16/'
                  'semantic-segmentation-adas-0001.xml '
                  '-i /opt/intel/openvino/samples/scripts/car_1.bmp -d HDDL && rm -f /dev/shm/hddl_*'),
             ],
            self.test_segmentation_python_hddl.__name__, **kwargs,
        )
