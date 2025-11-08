-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 05, 2025 at 10:48 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.1.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `student_analyze_performance`
--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','student') NOT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `role`, `student_id`, `email`, `created_at`) VALUES
(1, 'admin', 'scrypt:32768:8:1$z7Wq5tXgv9YBr2LH$f4f4d1d1f7e5e7e5c3b1a9f8d6b4a2d8e7f5c3a1b9e7d5f3a1c9e8b6d4f2a8', 'admin', NULL, 'admin@school.edu', '2025-11-01 13:47:34'),
(2, 'PNC2026_004', 'scrypt:32768:8:1$z7Wq5tXgv9YBr2LH$f4f4d1d1f7e5e7e5c3b1a9f8d6b4a2d8e7f5c3a1b9e7d5f3a1c9e8b6d4f2a8', 'student', 'PNC2026_004', 'chroun.nita@student.edu', '2025-11-01 13:47:34'),
(3, 'PNC2026_010', 'scrypt:32768:8:1$z7Wq5tXgv9YBr2LH$f4f4d1d1f7e5e7e5c3b1a9f8d6b4a2d8e7f5c3a1b9e7d5f3a1c9e8b6d4f2a8', 'student', 'PNC2026_010', 'ho.rina@student.edu', '2025-11-01 13:47:34');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `student_id` (`student_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
