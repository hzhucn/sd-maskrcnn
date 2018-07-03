import os
from tqdm import tqdm
import numpy as np
import cv2
import argparse
from autolab_core import YamlConfig
import utils

def resize_images(config):
    
    """Resizes all images so their maximum dimension is config['max_dim']. Saves to new directory."""
    base_dir = config['dataset']['path']

    # directories of images that need resizing
    if config['images']['resize']:
        image_dir = config['dataset']['img_dir']
        image_out_dir = config['dataset']['img_out_dir']
        utils.mkdir_if_missing(os.path.join(base_dir, image_out_dir))
        old_im_path = os.path.join(base_dir, image_dir)
        new_im_path = os.path.join(base_dir, image_out_dir)
        for im_path in tqdm(os.listdir(old_im_path)):
            im_old_path = os.path.join(old_im_path, im_path)
            if '.npy' in im_old_path:
                im = np.load(im_old_path)                
            else:
                im = cv2.imread(im_old_path, cv2.IMREAD_UNCHANGED)
            im = scale_to_square(im, dim=config['images']['max_dim'])
            new_im_file = os.path.join(new_im_path, im_path)
            if '.npy' in im_old_path:
                if config['images']['normalize']:
                    im = cv2.normalize(im, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
                np.save(new_im_file, im)
            else:
                if config['images']['normalize']:
                    im = cv2.normalize(im, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
                cv2.imwrite(new_im_file, im, [cv2.IMWRITE_PNG_COMPRESSION, 0]) # 0 compression

    if config['masks']['resize']:
        mask_dir = config['dataset']['mask_dir']
        mask_out_dir = config['dataset']['mask_out_dir']
        utils.mkdir_if_missing(os.path.join(base_dir, mask_out_dir))
        old_mask_path = os.path.join(base_dir, mask_dir)
        new_mask_path = os.path.join(base_dir, mask_out_dir)
        for mask_path in tqdm(os.listdir(old_mask_path)):
            mask_old_path = os.path.join(old_mask_path, mask_path)
            if '.npy' in mask_old_path:
                mask = np.load(mask_old_path)                
            else:
                mask = cv2.imread(mask_old_path, cv2.IMREAD_UNCHANGED)
            if mask.shape[0] == 0 or mask.shape[1] == 0:
                print("mask empty")
                continue
            mask = scale_to_square(mask, dim=config['masks']['max_dim'])
            new_mask_file = os.path.join(new_mask_path, mask_path)
            if '.npy' in mask_old_path:
                np.save(new_mask_file, mask)
            else:
                cv2.imwrite(new_mask_file, mask, [cv2.IMWRITE_PNG_COMPRESSION, 0]) # 0 compression

def scale_to_square(im, dim=512):
    """Resizes an image to a square image of length dim."""
    scale = 512.0 / max(im.shape[0:2]) # scale so min dimension is 512
    scale_dim = tuple(reversed([int(np.ceil(d * scale)) for d in im.shape[:2]]))
    return cv2.resize(im, scale_dim, interpolation=cv2.INTER_NEAREST)

if __name__ == "__main__":

    # parse the provided configuration file and resize
    conf_parser = argparse.ArgumentParser(description="Resize images for SD Mask RCNN model")
    conf_parser.add_argument("--config", action="store", default="cfg/resize.yaml",
                               dest="conf_file", type=str, help="path to the configuration file")
    conf_args = conf_parser.parse_args()

    # read in config file information from proper section
    config = YamlConfig(conf_args.conf_file)
    resize_images(config)