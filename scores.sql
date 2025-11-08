-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 05, 2025 at 06:04 AM
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
-- Table structure for table `scores`
--

CREATE TABLE `scores` (
  `id` int(11) NOT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `term` varchar(20) DEFAULT NULL,
  `quiz` float DEFAULT NULL,
  `homework` float DEFAULT NULL,
  `midterm` float DEFAULT NULL,
  `final` float DEFAULT NULL,
  `average` float DEFAULT NULL,
  `performance_level` varchar(20) DEFAULT NULL,
  `subject` varchar(50) DEFAULT 'General',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `scores`
--

INSERT INTO `scores` (`id`, `student_id`, `term`, `quiz`, `homework`, `midterm`, `final`, `average`, `performance_level`, `subject`, `created_at`) VALUES
(6, 'PNC2026_010', '0', 34, 53, 65, 36, 47, 'Poor', 'General', '2025-11-04 05:43:24'),
(8, 'PNC2026_009', 'Term 3', 56, 78, 87, 98, 79.75, 'Good', 'General', '2025-11-04 05:43:24'),
(9, 'PNC2026_018', 'Term 4', 56, 35, 56, 87, 58.5, 'Average', 'General', '2025-11-04 05:43:24'),
(10, 'PNC2026_004', 'Term 1', 99, 88, 88, 88, 90.75, 'Excellent', 'General', '2025-11-04 05:43:24'),
(36, 'PNC2026_004', 'Term 2', 88, 98, 45, 90, 80.25, 'Good', 'General', '2025-11-04 05:43:24'),
(37, 'PNC2026_006', 'Term 4', 76, 766, 54, 34, 232.5, 'Excellent', 'General', '2025-11-04 05:43:24'),
(38, 'PNC2026_012', 'Term 2', 85.99, 80.9, 90.1, 87.87, 86.215, 'Excellent', 'General', '2025-11-04 05:43:24'),
(39, 'PNC2026_017', 'Term 1', 100, 100, 100, 100, 100, 'Excellent', 'General', '2025-11-04 05:43:24'),
(40, 'PNC2026_028', 'Term 2', 68.68, 68.68, 68.68, 68.68, 68.68, 'Average', 'General', '2025-11-04 05:43:24'),
(41, 'PNC2026_076', 'Term 3', 97.09, 90, 79, 79, 86.2725, 'Excellent', 'General', '2025-11-04 05:43:24'),
(42, 'PNC2026_009', 'Term 2', 87, 67, 67, 87, 77, 'Good', 'General', '2025-11-04 05:43:24'),
(43, 'PNC2026_004', 'Term 2', 75, 65, 65, 65, 67.5, 'Average', 'General', '2025-11-04 05:43:24'),
(44, 'PNC2026_006', 'Term 2', 232, 32, 23, 32, 79.75, 'Good', 'General', '2025-11-04 05:43:24'),
(45, 'PNC2026_004', 'Term 4', 99, 88, 77, 88, 88, 'Good', 'General', '2025-11-05 02:33:56'),
(46, 'PNC2026_068', '5', 78, 90, 56, 100, 81, 'Good', 'General', '2025-11-05 02:53:51'),
(47, 'PNC2026_004', 'Term 3', 56, 76, 78, 77, 71.75, 'Average', 'General', '2025-11-05 03:16:45'),
(48, 'PNC2026_047', 'Term 1', 98, 100, 100, 66, 91, 'Excellent', 'General', '2025-11-05 04:49:10');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `scores`
--
ALTER TABLE `scores`
  ADD PRIMARY KEY (`id`),
  ADD KEY `student_id` (`student_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `scores`
--
ALTER TABLE `scores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=49;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `scores`
--
ALTER TABLE `scores`
  ADD CONSTRAINT `scores_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
