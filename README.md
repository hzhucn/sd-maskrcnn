# Mask-RCNN Data Pipeline
## Overview
This is a pipeline written to handle the data and run Mask-RCNN on depth-image datasets. It can turn raw images and segmasks to properly sized and transformed images (and corresponding masks), then train Mask-RCNN upon the result. Following that, the pipeline can benchmark the final model weights on a given test dataset, perhaps of real depth images.

The following are the available tasks, or operations that the pipeline can perform.
#### Augment
This operation takes a dataset and injects noise/inpaints images/can apply arbitrary operations upon an image as a pre-processing step.
#### Resize
This operation takes folders of images and corresponding segmasks, and resizes them together to the proper shape as required by Mask-RCNN.
#### Train
This operation runs the training for Mask-RCNN on the standard dataset (described later).
#### Benchmark
This operation, given model weights, runs both COCO benchmarks and Saurabh's benchmarking code on a new, test dataset.
## Requirements
```
- numpy
- scipy
- skimage
- tensorflow-gpu
- jupyter
- opencv-python
- pytest
- keras
- tqdm
- matplotlib
- flask (if labelling images)
```
These can all be installed by running `pip3 install -r requirements.txt`.
(TODO: get version numbers)

Additionally, in order to compute COCO benchmarks, the COCO API must be installed inside the repository root directory.
Get it [here.](https://github.com/cocodataset/cocoapi)
Then, navigate to `cocoapi/PythonAPI/` and run `make install`.


`image-labelling-tool` contains a lightweight web application for labelling segmasks.
More instructions on how to use it are contained in `image-labelling-tool/save_masks.ipynb`.

## Standard Dataset Format
All datasets, both real and sim, are assumed to be in the following format:
```
<dataset root directory>/
    depth_ims/
        image_000000.png
        image_000001.png
        ...
    modal_segmasks/
        image_000000.png
        image_000001.png
        ...
    segmasks/ (optional)
    train_indices.npy
    <other names>_indices.npy
    ...
```
All segmasks inside `modal_segmasks/` must be single-layer .pngs with 0 corresponding to the background and 1, 2, ... corresponding to a particular instance.
To convert from multiple channel segmasks to a single segmask per case, open `clutter/clutter.py`, point `base_dir` to your particular dataset, and run said file.
This will put the "stacked" segmasks in a new directory, `modal_segmasks_project`, which should be renamed.

Additionally, depth images and ground truth segmasks must be the same size; perform the "RESIZE" task in the pipeline to accomplish this.
If using bin-vs-no bin segmasks to toss out spurious predictions, `segmasks/` must contain those segmasks.
These should be binary (0 if bin, 255 if object).

## Benchmark Output Format
Running the "BENCHMARK" option will output a folder containing results, which is structured as follows:

```
bench_<name>/ (results of one benchmarking run)
    modal_segmasks_processed/
    pred_info/
    pred_masks/
        coco_summary.txt
    results_saurabh/
    vis/
    ...
```

COCO performance scores are located in `pred_masks/coco_summary.txt`.
Images of the network's predictions for each test case can be found in `vis/`.
Saurabh's benchmarking outputs (plots, missed images) can be found in `results_saurabh`.

In order to maintain the decoupled nature of the pipeline, the network must write its predictions  and post-processed GT segmasks to disk.
At the moment, these are written in uncompressed Numpy arrays, meaning outputs will become very large.
Until this issue is resolved, we **do not recommend** running the "BENCHMARK" task on datasets larger than 50 images unless there is a lot of disk space free.

## Currently Used Resources and Associated Numbers (as of May 17th, 2018)

### Datasets
We primarily use four datasets for training and benchmarking.

- `/nfs/diskstation/projects/dex-net/segmentation/datasets/no_noise_sim_dataset` contains 10000 simulated depth images (8000 train, 2000 val) generated from the Dex-Net clutter simulator.
- `/nfs/diskstation/projects/dex-net/segmentation/datasets/noisy_sim_dataset` is identical to above (same test cases, same train/val split) except every image is injected with Gaussian noise, SD = 0.001.
- `/nfs/diskstation/projects/dex-net/segmentation/datasets/real_test_cases_easy_04_30_18/images` contains 25 "easy" real test cases taken with the Phoxi, as well as their associated hand-labelled segmentation masks.
- `/nfs/diskstation/projects/dex-net/segmentation/datasets/real_test_cases_04_29_18/images` contains 50 "hard" real test cases, also taken with the Phoxi.

### Models 
We trained one model for each of the noisy and no noise datasets with a learning rate of 0.001 for 80 epochs. 

- No noise: `/nfs/diskstation/projects/dex-net/segmentation/datasets/no_noise_sim_dataset/train_no_noise_lr1e-3_80e/mask_rcnn_clutter_20180506-160851.h5`
- Noise: andrew li
    
TF model checkpoints are also saved in the same folder as the model, so loss curves can be viewed by running Tensorboard in the directory containing the model.

### Results
Full result logs are stored at `/nfs/diskstation/projects/dex-net/segmentation/results_maskrcnn_050418`, with each run bearing a descriptive name.

#### No Noise Injection
| Test Set        | Precision           |Recall   |
| :-----------: |:-------------:|:-----:|
| Simulated Test (no noise)      | 0.528 | 0.688 |
| Simulated Test (noise-injected      | andrew li      | andrew li |
| Real, "easy" |    0.177   |   0.616 |
| Real, "hard" |  0.153 | 0.519 |

#### With Noise Injection
| Test Set        | Precision           |Recall   |
| :-----------: |:-------------:|:-----:|
| Simulated Test (no noise)      | andrew li | andrew li |
| Simulated Test (noise-injected      | andrew li      | andrew li |
| Real, "easy" |    0.461   |   0.643 |
| Real, "hard" |  0.267 | 0.518 |


## Files
Note that most of these files reside within the subfolder "noise".
Saurabh's files have been left mostly intact as much of the pipeline's functionality depends on some parts of his code.

### pipeline.py
This is the main file to run for all tasks (train, benchmark, augment, resize). Run this file with the tag --config [config file name] (in this case, config.ini).

Include in the PYTHONPATH the locations of maskrcnn and clutter folders.

Here is an example run command (GPU selection included). Note that we are running this from the root clutter-det-maskrcnn folder, not the noise folder.
`CUDA_VISIBLE_DEVICES='0' PYTHONPATH='.:maskrcnn/:clutter/' python3 noise/pipeline.py --config noise/config.ini`
### config.ini
This is where all the parameters for each task are specified, as well as the current task to be run. It is sectioned off into sets of parameters for each type of task, as well as a flag at the top to set the task that will be executed when pipeline.py is run. Please read the inline comments of each parameter within config.ini before running pipeline.py.

### pipeline\_utils.py
This file contains some general helper functions that are used in pipeline.py.
### real\_dataset.py/sim\_dataset.py
These files contain subclasses of `ClutterDataset` defined in `clutter/clutter.py`, each contains methods for loading and preprocessing images before they are fed into the model.
### augmentation.py
This file contains the noise and inpainting functions that are used to modify an image dataset before it is resized and trained upon.
### eval\_coco.py/eval\_saurabh.py
These files contain methods for evaluating predictions using COCO metrics and Saurabh's benchmarking code, respectively.
### resize.py
Resizing function for 512x512 images.
### noise.py
This is a standalone file that will look at areas of the image and generate depth histograms for noise analysis.



# Deprecated README text from Saraubh's code:

### Code for running Mask-RCNN on images of object piles.

1. Dependencies: I developed and tested this code base with python3.5. I am using pip, and requirements are in `requirements.txt`. You will want to update your pip (with `pip install -U pip`) and then deactivate and activate before installing these requirements. Also you should install tensorflow with `pip install tensorflow-gpu`.

2. Code for running training.
`CUDA_VISIBLE_DEVICES='2' PYTHONPATH='.:maskrcnn/' python clutter/train_clutter.py --logdir outputs/v3_512_40_flip_depth --im_type depth --task train`

3. Code for benchmarking.
`CUDA_VISIBLE_DEVICES='2' PYTHONPATH='.:maskrcnn/' python clutter/train_clutter.py --logdir outputs/v3_512_40_flip_depth --im_type depth --task bench`

4 Misc. Info.
  - `clutter/clutter.py`, implements the class `ClutterDataset` that has functions for loading the images and the masks from Jeff's dataset.
  - `clutter/clutter.py:74` specifies the path where the data is stored.
  - `clutter/clutter.py` (function `concat_segmasks`) preprocesses the stored masks such that they are faster to load (basically pastes all the modal masks into a single image). So when switching to a new dataset you may want to re-run this function on the new data to use with the data class.
  -
