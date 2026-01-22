-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 17, 2026 at 05:22 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `secure_chat`
--

-- --------------------------------------------------------

--
-- Table structure for table `accounts`
--

CREATE TABLE `accounts` (
  `id` int(11) NOT NULL,
  `username` varchar(80) NOT NULL,
  `password_hash` varchar(200) NOT NULL,
  `public_key` text NOT NULL,
  `status` enum('online','offline') DEFAULT 'offline',
  `last_seen` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `accounts`
--

INSERT INTO `accounts` (`id`, `username`, `password_hash`, `public_key`, `status`, `last_seen`, `created_at`) VALUES
(14, 'admin', 'scrypt:32768:8:1$nqWqDlOerDcxkz9t$13f075ba7525633c067f725f3d65f08f0c4db0987ce05ff6d85cddae81ea2e66ceeb6a77fa22608ab66d701a89a0296613ba695361e5b1eb4ff3f274ef47a9a7', '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnk6C/jQKWClAN7PIs9m9\nKlYsPdOXRyvVRUidCjM2TzzZJdqFvHVj8cEwHolfxjq6DlcUKkAuQF/Q5wQoBByw\nHIjzoL4bvmo0friuy+4Ks9ReaMgd4Ex4OENDYZbHMjr6QqryK9651qV8rFZwJq/n\nTpuryP0DB9/TEkSGv2IVSMTgHIoqibAJsECMD4pdm8KsYAGrpCLHHrI7Sj5t+U+9\nnlwNiZcF/fjr9vRAWdg993lxjlP/pj0SaKuoPgxrbybUH+64TnoxJJFSp79UL1Fb\nCsS8dowybIdO1vPopjocBRwLOOwnbMA8cevuNAwBRYJlXRIrqRL/K48OFTPAqI2R\nQwIDAQAB\n-----END PUBLIC KEY-----', 'online', '2026-01-17 16:07:58', '2026-01-17 16:07:53'),
(15, 'admin1', 'scrypt:32768:8:1$JZJrG2DGbXgK9SZG$be6f4d69606815b6cd6f52d185902d9b668b60893e761cce526b6db9008f24167a6c07a784f25bb45927a34b4e5976197898fccb1ed96e9761e4bdbfe610f606', '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAr18kgd/ZHzvYzJ8Gsbrj\nxCnflu6rubzG8F+wpxiPVoH6C/B1KcuQRxk5exLuwX3GFDfgkufh5/6JWlxJv1in\ng+BxTSB38yTmksWVOd+34+QxcR04gJnLbHncwlBc9aaA+YH9sorvbTRhuIMUdSdH\nTGx/w+fiMFY1sMed+/81qa9yKt1uKVcxCLHhbIpNXojtQIEhc0M44l9o7eP1s7nX\n4r3wvJ9XVnKjX0AYoq1n8sdGP1ciIu1ezPWVlmQjwLY9kbJOHdlvQeH6mfpGgKvp\nw/PswV8oSB6ytj/v81dEo8HHyZTFJbYkRu4zLwPevcgSYrjswF1pmKR3c9mEV/UE\nvwIDAQAB\n-----END PUBLIC KEY-----', 'online', '2026-01-17 16:10:53', '2026-01-17 16:10:49');

-- --------------------------------------------------------

--
-- Table structure for table `chats`
--

CREATE TABLE `chats` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `is_group` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `chats`
--

INSERT INTO `chats` (`id`, `name`, `is_group`, `created_at`) VALUES
(9, 'Nguyen Quang Thinh', 0, '2026-01-17 16:10:54');

-- --------------------------------------------------------

--
-- Table structure for table `chat_members`
--

CREATE TABLE `chat_members` (
  `id` int(11) NOT NULL,
  `chat_id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `joined_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `chat_members`
--

INSERT INTO `chat_members` (`id`, `chat_id`, `account_id`, `joined_at`) VALUES
(17, 9, 15, '2026-01-17 16:10:54'),
(18, 9, 14, '2026-01-17 16:10:54');

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `chat_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `aes_key_encrypted` text NOT NULL,
  `iv` text NOT NULL,
  `tag` text NOT NULL,
  `timestamp` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `messages`
--

INSERT INTO `messages` (`id`, `chat_id`, `sender_id`, `content`, `aes_key_encrypted`, `iv`, `tag`, `timestamp`) VALUES
(60, 9, 15, 'MvU=', '{\"15\": \"aKCnhVAHNIuzkuoN1TCXA+wHPHML/9LarjSiSywbTM+mdeJ9hITHadRbEmRtg7YZSFPpiaUUZCy98P1WCM4DkFKq7d/37Z3BbACJE1StGB7qFatCSeiZymhVFzeficNHk89O8IkpMWanZjBcDWGoDBIu6Cxez1GA7WxWkABNNUt9srxuT2Ch/Z5egBu9peQ1bAKCvy3Js4ZAPhTMfTJMVltTRS/NBlsogiVnXANeTKfVB8B9SyyO6rSXzIfcXQvM9XDXg6NVqhtMJ6et8uEnJiaE448VLVHWV2h0R/mBHblN4RoIXuchftKDx1Ktx8Oy/Ho67w1bKvcWHm5hlon6RA==\", \"14\": \"No4JZOdy+t8n0TBra+SLhwO7x4ABiVH9GRw8lYA2MgHRJ985y0tSCnVamgP1UcpbY9gpUvP/CPNv5ZaeplNPAKoPvsanyP8UE7su8y6gzwOv5IM10uOwHa8iZCqXNGAuFUpizazFy636LPOLckgtCnyJFWv7YX8Ga6W7QuYhe+EeiC1ydLFhw+06LRUJM6SwbCPmbfPikWYpPwWBNY6e/k30dc73VGOL4Tke6pfDk2jQYIlqa/532DlWE6hleCKrMiIjF9hddCmVuY583HxCphuxwvTJecwj+p3ZawxGQ/VobsFT5h+uC45oyb+FW6WIeLW4GTEJUw81xnVVyQhaJw==\"}', 'U7sPwduAf5nNWIq8EIVP2w==', 'g8207BYufIz+yLEAXR4y2A==', '2026-01-17 16:10:57'),
(61, 9, 14, 'ZlQ=', '{\"15\": \"VFPsd4oN6BJMrRkr71LQtqsI+mze0gH2DSaak4kPGYyNgtsYWx2VZLHtqhsBWu/ROu+Gv5+QLsHIzR2G1ajq5Tz/ozQyPv0/IoWfL36aZuUfXnWIl8OrSs7aMTqPbgLGQvgpkjfE4Jvib0WmsN/pbOIypfGpirrDIKAqx3A9Hbs6ICvWRgSCzYfe83vUXV6KKBczm+zg5bYaEABXBOHZs6HGNOl3bZCTpn4eWYr36waQ3pwr63CXKlXXHNt6/CiGkOxWxezYKfjzNy0qkdR3QIY/Ej8srXhFNOiKgs2I65GZF3xtR91kZchCDUJMuZ6cuAZpaZWIphXycg/SHn3DYA==\", \"14\": \"JcucV0/TMuYHbDeJE/epRXZXZoBh/cCc7R2WeTsDtGCoyKTktO8Y3MxYMhCYMoXL0Tb00D+0vXp1bdDceOFm+si+MDcpHRemBC9ZMXRA5mc+FSzkAZi8rWROoZsCu8i+CHppBlUKnO2L29NmQkdtL+mUPGhd25soIvs1Jkuj0q9or2XCB3H05oYAF8dTDuuxIUymbNzdidluu2EZRH7XfBxyHHoQSSrz1jkdFTL8M6uR4xDY6gZKGVHngk5l8Qkbx8M8Vpwql0nvJftLiGRHlByy562m40IVJPqOD7mEjdyIp7wjrNADvA7PJYEZOXA8C9s6AdIbXo4vU9koCAsjwg==\"}', 'kAAt4826/U1oUa8cTdg4/A==', 'LP5+zdka8IHo82cNRkv82g==', '2026-01-17 16:11:07'),
(62, 9, 15, 'AX3n5uc=', '{\"15\": \"ICdej2T/HF7yWsRq0g5BpjtLixi9FndwoIZy4AzINIGMl6Kbe+rq+APDWMO8NcMCEnsi7Sf6nfz77AQG1gT9b1v881+l4QGhLQO+lSgmYrJDRttkJEk1RQ/z6ZAcpsSEXdtj+Fg4wP4v+3oGmGIPQNOyq8g0TkqAbgaW1zHa8ri6RitmCKc+x0byCYe4Tl1C7ej5/O1W5iJORF4YyRg7rp85yriBPrht2YknPSqw9pK3L59m7/Of8j2AbkDznQCiZZcQeXJDyOzK+PUYpt9RKj/JASKCwPfIiyr8o8P2yRixxhRJHotii4ED0UFVs5aCcuXpvebmjm1f/ziG9bOisw==\", \"14\": \"QUjl6YpRNDHXSpinYd+SuCGlMWHAuSRTWlZLTABr0n4ELce2irCjKqYmc4ZA24QCCSyV9t6IK/jQ6KzSfv/TCunNOWXoHWjhpur+QnI0/7ThBgyL5nb88H4o1+3330pbymUeIAc2dzQAst4DvfqDpN++Fb01lckBF1AmrIUGe45mBXnRfAg/aPGCUK0DLlQoWsrmxGbOMTAb57T1P3xX07GYvRQRd/LI+WkJ6hGiF6pnMoZHlIYX0X4iKmM8INKSgfoUZa/6uDqgnLu0RYV3T3aJVy7yA956w9tkQk7H/4pzNhuD+BmeJl/hTsRCb3dxp/ovU609PSjsUj9x8JNrlg==\"}', 'EIeUfQ/fnNz08Pvb9mn7ZQ==', 'KcNrcb1wtYKt3e6NpFUAXg==', '2026-01-17 16:11:16'),
(63, 9, 15, 'Mo+kWrg=', '{\"15\": \"Igg2tbGjgO3OILxf1kEzlvlXGPQQBFEkVi6t009VqVWeBmSnyyEzzzX9mnq0BaJhTUBudhHIH940mkSXZtGSS3rSdok1YlnDJvBLH4ma25SZsFJwnO0dJT2f3QEFSEc6P8JQIFwKpETAC5h/A0EFr/UQVqpXS/8Ikc8FyzGMA4Cu5gfKoAOsyatmLawi9WKOd1oIsP+lAlH2RHxne7V7bHG2NQRMzUmz6fED3QGUU920ZtXSfr/6Uex9RUwtRoX0ObXWMXOWdQZte6wuO1MSwE6eLIAWLMsS5D1j7ecyZxc3MDLbFoUU5dgd4nmlmQYSZbFOWT0ORN0pYSWzXjewOA==\", \"14\": \"lH9mJwUFUFHLf1Bfds5L0s9R0agbLyLi26xUfTR/yyYloKZLd8MYzVz52IreFa9weDouLZpf8/BulviyUXZ/5GWvxUHOwplSner/xRu8Mkg6E1LNFVwqKmr9xHiIhTn5co/Sz29idCtpD4VmOGigSCSnCkdaiT7cAXlHC5wVBjUghVZFq2PekR2biqFacuSBLuZvW252OdxjIRt4joN2jedDJs5gY0YpOs6nsz91J8vL5ZJJMMuwlZPZEtsPa2FE4rUz2G6gcBIiGr/5WtEOTHTAkAkW3Y85uvsp/LBM2kaEdEDyN2FkP7auKnpavp7emrUH+XBxB3e6tHKIteLI1Q==\"}', 'qSF1NVYMOKhr0EtQbs6+7Q==', '1UgYpKJFLQYV4cv3glgXfg==', '2026-01-17 16:13:08');

-- --------------------------------------------------------

--
-- Table structure for table `message_recipients`
--

CREATE TABLE `message_recipients` (
  `id` int(11) NOT NULL,
  `message_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `read_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `message_recipients`
--

INSERT INTO `message_recipients` (`id`, `message_id`, `receiver_id`, `read_at`) VALUES
(1, 60, 15, NULL),
(2, 60, 14, '2026-01-17 16:11:04'),
(3, 61, 15, '2026-01-17 16:11:07'),
(4, 61, 14, NULL),
(5, 62, 15, NULL),
(6, 62, 14, '2026-01-17 16:11:16'),
(7, 63, 15, NULL),
(8, 63, 14, '2026-01-17 16:13:08');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `gender` enum('male','female','other') DEFAULT 'other',
  `date_of_birth` date DEFAULT NULL,
  `avatar_url` varchar(255) DEFAULT NULL,
  `bio` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `account_id`, `full_name`, `gender`, `date_of_birth`, `avatar_url`, `bio`) VALUES
(14, 14, 'Nguyen Quang Thinh', 'other', '2008-01-17', NULL, 'im gay'),
(15, 15, 'Nguyen Viet Hoang', 'other', '2008-01-17', NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `chats`
--
ALTER TABLE `chats`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `chat_members`
--
ALTER TABLE `chat_members`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `chat_id` (`chat_id`,`account_id`),
  ADD KEY `account_id` (`account_id`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `chat_id` (`chat_id`),
  ADD KEY `sender_id` (`sender_id`);

--
-- Indexes for table `message_recipients`
--
ALTER TABLE `message_recipients`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `message_id` (`message_id`,`receiver_id`),
  ADD KEY `receiver_id` (`receiver_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `account_id` (`account_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `accounts`
--
ALTER TABLE `accounts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `chats`
--
ALTER TABLE `chats`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `chat_members`
--
ALTER TABLE `chat_members`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=64;

--
-- AUTO_INCREMENT for table `message_recipients`
--
ALTER TABLE `message_recipients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `chat_members`
--
ALTER TABLE `chat_members`
  ADD CONSTRAINT `chat_members_ibfk_1` FOREIGN KEY (`chat_id`) REFERENCES `chats` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `chat_members_ibfk_2` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`chat_id`) REFERENCES `chats` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `message_recipients`
--
ALTER TABLE `message_recipients`
  ADD CONSTRAINT `message_recipients_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `messages` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `message_recipients_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
