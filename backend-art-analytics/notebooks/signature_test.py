from signature_detect.loader import Loader

loader = Loader(
    low_threshold=(0, 0, 250), 
    high_threshold=(255, 255, 255))

masks = loader.get_masks(r"D:\data\pictures_training\assiette dessous\23aebc0197400bf2e1c06039718ecea4.jpg")

from signature_detect.extractor import Extractor

extractor = Extractor(
    outlier_weight=3, 
    outlier_bias=100, 
    amplfier=10, 
    min_area_size=10)

labeled_mask = extractor.extract(masks[0])

from signature_detect.cropper import Cropper

cropper = Cropper(
    min_region_size=50, 
    border_ratio=0.05)

results = cropper.run(labeled_mask)

from signature_detect.judger import Judger

judger = Judger(
    size_ratio=[1, 2], 
    pixel_ratio=[0.01, 1])

is_signed = judger.judge(results[1]["cropped_mask"])