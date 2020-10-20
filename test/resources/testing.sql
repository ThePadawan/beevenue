BEGIN TRANSACTION;

INSERT INTO `tag` VALUES (100, 'u:overwatch', 's');

INSERT INTO `tag` VALUES (1000, 'A', 's');
INSERT INTO `tag` VALUES (1001, 'B', 's');
INSERT INTO `tag` VALUES (1002, 'C', 's');

INSERT INTO `tag` VALUES (2000, 'u:peter.pan', 's');
INSERT INTO `tag` VALUES (2001, 'c:tinkerbell', 's');
INSERT INTO `tag` VALUES (2002, 'c:peter', 's');

INSERT INTO `tag` VALUES (3001, 's:2d', 's');

INSERT INTO `tag` VALUES (4001, 'tobecensored', 'q');
INSERT INTO `tag` VALUES (4002, 'tobecensoredtoo', 'e');

INSERT INTO `tagImplication` VALUES (2001, 2000);
INSERT INTO `tagImplication` VALUES (2002, 2000);
INSERT INTO `tagImplication` VALUES (4001, 4002);

INSERT INTO `tagAlias` VALUES (1, 2002, 'c:pete');

INSERT INTO `medium` VALUES (1, 'hash1', 'image/jpg', 1.5, 's', NULL);
INSERT INTO `medium` VALUES (2, 'hash2', 'image/jpg', 1.5, 's', NULL);
INSERT INTO `medium` VALUES (3, 'hash3', 'image/jpg', 1.5, 'e', NULL);
INSERT INTO `medium` VALUES (4, 'hash4', 'image/jpg', 1.5, 's', NULL);
INSERT INTO `medium` VALUES (5, 'hash5', 'image/jpg', 1.5, 's', NULL);
INSERT INTO `medium` VALUES (6, 'hash6', 'image/jpg', 1.5, 's', NULL);
INSERT INTO `medium` VALUES (7, 'hash7', 'image/jpg', 1.5, 's', NULL);
INSERT INTO `medium` VALUES (8, 'hash8', 'image/jpg', 1.5, 's', NULL);
INSERT INTO `medium` VALUES (9, 'hash9', 'image/jpg', 1.5, 's', NULL);
INSERT INTO `medium` VALUES (10, 'hash10', 'image/jpg', 1.5, 's', NULL);
INSERT INTO `medium` VALUES (11, 'hash11', 'image/jpg', 1.5, 's', NULL);
INSERT INTO `medium` VALUES (12, 'hash12', 'image/jpg', 1.5, 'q', x'deadbeef');

-- medium_id, tag_id
INSERT INTO `medium_tag` VALUES (1, 1000);
INSERT INTO `medium_tag` VALUES (1, 1001);

INSERT INTO `medium_tag` VALUES (2, 1001);
INSERT INTO `medium_tag` VALUES (2, 1002);

-- A picture of peter and tinkerbell together
INSERT INTO `medium_tag` VALUES (4, 2001);
INSERT INTO `medium_tag` VALUES (4, 2002);
INSERT INTO `medium_tag` VALUES (4, 2000);

-- Make lots of media similar to each other to test the similarity algorithm
INSERT INTO `medium_tag` VALUES (4, 4001);
INSERT INTO `medium_tag` VALUES (5, 4001);
INSERT INTO `medium_tag` VALUES (6, 4001);
INSERT INTO `medium_tag` VALUES (7, 4001);
INSERT INTO `medium_tag` VALUES (8, 4001);
INSERT INTO `medium_tag` VALUES (9, 4001);
INSERT INTO `medium_tag` VALUES (10, 4001);
INSERT INTO `medium_tag` VALUES (11, 4001);

-- username/password 'admin'/'admin'
INSERT INTO `user` VALUES (1, 'admin', '$2y$12$57DpiLm0eSz9NT8THnsvzOZ8k4rtAZjOOp3zjXpmFI/YoqXG/tiNK', 'admin');
-- username/password 'user'/'user'
INSERT INTO `user` VALUES (2, 'user', '$2y$12$3RES8S3SZWIQEZy2EAyN9.qzAvLpOpuCudaB3Ue.nOfJ7Xkoy4Ica', 'user');

COMMIT;