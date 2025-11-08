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
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `student_id` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `class` char(1) NOT NULL,
  `gender` char(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`student_id`, `name`, `class`, `gender`) VALUES
('PNC2026_004', 'CHROUN NITA', 'A', 'F'),
('PNC2026_005', 'HAN CHANTREA', 'A', 'F'),
('PNC2026_006', 'HAV VICHEKA', 'A', 'F'),
('PNC2026_007', 'HEN NARITH', 'A', 'M'),
('PNC2026_008', 'HENG LIHEANG', 'A', 'M'),
('PNC2026_009', 'HOEURN CHANSAYHA', 'A', 'M'),
('PNC2026_010', 'HO RINA', 'A', 'F'),
('PNC2026_011', 'HUT SREYPOV', 'A', 'F'),
('PNC2026_012', 'KE SOTHIN', 'A', 'M'),
('PNC2026_013', 'KEO SREYDOEURN', 'A', 'F'),
('PNC2026_014', 'KEUN SREYKEO', 'A', 'F'),
('PNC2026_015', 'KHON SREYDETH', 'A', 'F'),
('PNC2026_016', 'KHORN REAM', 'A', 'M'),
('PNC2026_017', 'KHOEURN CHEM', 'A', 'M'),
('PNC2026_018', 'KIM DARIKA', 'A', 'F'),
('PNC2026_019', 'KOEUN PANHA', 'A', 'M'),
('PNC2026_020', 'KREAN VA KHIM', 'A', 'M'),
('PNC2026_021', 'LAKK SOKYANG', 'A', 'F'),
('PNC2026_022', 'LEK SINAT', 'A', 'F'),
('PNC2026_023', 'LEN VANNA', 'A', 'M'),
('PNC2026_024', 'LENG SOKKHOEURN', 'A', 'F'),
('PNC2026_025', 'LIN SREY MAO', 'A', 'F'),
('PNC2026_026', 'LON MOLIKA', 'A', 'F'),
('PNC2026_027', 'LUCH SAMART', 'B', 'F'),
('PNC2026_028', 'MIOK DANE', 'B', 'M'),
('PNC2026_029', 'MOEURN SOPHY', 'B', 'M'),
('PNC2026_030', 'NANG CHHITCHHANUT', 'B', 'F'),
('PNC2026_031', 'NEA PISET', 'B', 'M'),
('PNC2026_032', 'NIM SOKNY', 'B', 'M'),
('PNC2026_033', 'NY SEYHA', 'B', 'M'),
('PNC2026_034', 'PENH BOREY', 'B', 'F'),
('PNC2026_035', 'PHAL SOPHEA', 'B', 'F'),
('PNC2026_036', 'PHAN PHOUN', 'B', 'M'),
('PNC2026_037', 'PHEM SEREY', 'B', 'M'),
('PNC2026_038', 'PHOEURN KOEMSEANG', 'B', 'F'),
('PNC2026_039', 'PHORN YA', 'B', 'M'),
('PNC2026_040', 'PHUONG SAVIN', 'B', 'M'),
('PNC2026_041', 'PINN MAKARA', 'B', 'F'),
('PNC2026_042', 'PO SREYMOM', 'B', 'F'),
('PNC2026_043', 'PON MAKARA', 'B', 'F'),
('PNC2026_044', 'REN RANIT', 'B', 'F'),
('PNC2026_045', 'RIN MESA', 'B', 'M'),
('PNC2026_047', 'SAK VISA', 'B', 'F'),
('PNC2026_048', 'SAN REAKSMEY', 'B', 'M'),
('PNC2026_049', 'SANG SREYROTH', 'B', 'F'),
('PNC2026_050', 'SANN SIV', 'B', 'M'),
('PNC2026_051', 'SAO MARY', 'B', 'F'),
('PNC2026_052', 'SARL LY', 'B', 'M'),
('PNC2026_053', 'SAT VICHET', 'C', 'M'),
('PNC2026_054', 'SEM SREY LEAK', 'C', 'F'),
('PNC2026_055', 'SEN SOKSEYLA', 'C', 'F'),
('PNC2026_056', 'SIENG SOPHAT', 'C', 'M'),
('PNC2026_057', 'SIM SAMNANG', 'C', 'M'),
('PNC2026_058', 'SOENG VICHEKA', 'C', 'F'),
('PNC2026_059', 'SOK LITA', 'C', 'F'),
('PNC2026_060', 'SOK THALITA', 'C', 'F'),
('PNC2026_061', 'SOKHA RATHANA', 'C', 'M'),
('PNC2026_062', 'SONG CHAMROEUN', 'C', 'M'),
('PNC2026_063', 'SOPHORN SOPHEA', 'C', 'F'),
('PNC2026_064', 'SRIN CHANDY', 'C', 'F'),
('PNC2026_065', 'SUONG PHALLA', 'C', 'M'),
('PNC2026_066', 'SVIT SAN', 'C', 'M'),
('PNC2026_067', 'TALAB REACH', 'C', 'M'),
('PNC2026_068', 'THA DARINHIL', 'C', 'M'),
('PNC2026_069', 'TIM TOLA', 'C', 'M'),
('PNC2026_070', 'VAN SIEVMEY', 'C', 'F'),
('PNC2026_071', 'VEN CHANNY', 'C', 'F'),
('PNC2026_073', 'VON SREYVIK', 'C', 'F'),
('PNC2026_074', 'YEANG SOK KEANG', 'C', 'F'),
('PNC2026_075', 'YOM PILIP', 'C', 'M'),
('PNC2026_076', 'YON KUNTHEA', 'C', 'F');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`student_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
