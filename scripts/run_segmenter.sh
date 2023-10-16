ls /home/anb51nh/gt_structure/gt_struct*/data/*/mets.xml | parallel ocrd process -m {} "\"cis-ocropy-binarize -I OCR-D-GT-SEG-BLOCK -O OCR-D-BIN -P level-of-operation page\"" "\"cis-ocropy-segment -I OCR-D-BIN -O OCR-D-LINESPROC -P level-of-operation region\""

