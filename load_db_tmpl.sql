SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

-- DROP DATABASE IF EXISTS `cont_mngm`;

CREATE DATABASE IF NOT EXISTS `cont_mngm` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `cont_mngm`;

DROP TABLE IF EXISTS `organizations`;

CREATE TABLE `organizations` (
  `_id` varchar(32) NOT NULL,
  `name` varchar(4096) NOT NULL,
  `owner` varchar(32) NOT NULL,
  `creationDate` datetime NOT NULL,
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `organizations` (`_id`, `name`, `owner`, `creationDate`) VALUES
organizations

DROP TABLE IF EXISTS `proposals-votes`;

CREATE TABLE `proposals-votes` (
  `proposal` varchar(40) NOT NULL,
  `user` varchar(32) NOT NULL,
  `date` datetime NOT NULL,
  `optionLabel` varchar(4096) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `proposals-votes` (`proposal`, `user`, `date`, `optionLabel`) VALUES
proposals-votes


