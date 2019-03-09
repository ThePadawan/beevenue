BEGIN TRANSACTION;

INSERT INTO `tag` VALUES (100, 'u:overwatch');

INSERT INTO `tag` VALUES (1000, 'A');
INSERT INTO `tag` VALUES (1001, 'B');
INSERT INTO `tag` VALUES (1002, 'C');

INSERT INTO `medium` VALUES (1, 'hash1', 'image/jpg', 1.5, 's');
INSERT INTO `medium` VALUES (2, 'hash2', 'image/jpg', 1.5, 's');
INSERT INTO `medium` VALUES (3, 'hash3', 'image/jpg', 1.5, 'e');

-- medium_id, tag_id
INSERT INTO `medium_tag` VALUES (1, 1000);
INSERT INTO `medium_tag` VALUES (1, 1001);

INSERT INTO `medium_tag` VALUES (2, 1001);
INSERT INTO `medium_tag` VALUES (2, 1002);

-- username/password 'admin'/'admin'
INSERT INTO `user` VALUES (1, 'admin', '$2y$12$57DpiLm0eSz9NT8THnsvzOZ8k4rtAZjOOp3zjXpmFI/YoqXG/tiNK', 'admin');
-- username/password 'user'/'user'
INSERT INTO `user` VALUES (2, 'user', '$2y$12$3RES8S3SZWIQEZy2EAyN9.qzAvLpOpuCudaB3Ue.nOfJ7Xkoy4Ica', 'user');

COMMIT;