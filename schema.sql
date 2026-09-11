-- Online Examination Platform
-- MySQL 8.0+
-- Complete database schema based on the provided 17-table design

CREATE DATABASE IF NOT EXISTS OnlineExaminationDB;
USE OnlineExaminationDB;

SET FOREIGN_KEY_CHECKS = 0;

DROP VIEW IF EXISTS vw_browser_integrity;
DROP VIEW IF EXISTS vw_student_performance;
DROP VIEW IF EXISTS vw_exam_statistics;
DROP VIEW IF EXISTS vw_student_results;
DROP VIEW IF EXISTS vw_question_paper;

DROP TABLE IF EXISTS AuditLog;
DROP TABLE IF EXISTS Notification;
DROP TABLE IF EXISTS Result;
DROP TABLE IF EXISTS StudentAnswer;
DROP TABLE IF EXISTS ExamAttempt;
DROP TABLE IF EXISTS CandidateRegistration;
DROP TABLE IF EXISTS ExamQuestion;
DROP TABLE IF EXISTS QuestionOption;
DROP TABLE IF EXISTS Question;
DROP TABLE IF EXISTS ExamSchedule;
DROP TABLE IF EXISTS Exam;
DROP TABLE IF EXISTS Subject;
DROP TABLE IF EXISTS Faculty;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Department;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Role;

SET FOREIGN_KEY_CHECKS = 1;

-- 1. Role
CREATE TABLE Role (
    RoleID BIGINT AUTO_INCREMENT PRIMARY KEY,
    RoleName VARCHAR(30) NOT NULL UNIQUE,
    Description VARCHAR(255),
    IsActive BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- 2. User
CREATE TABLE User (
    UserID BIGINT AUTO_INCREMENT PRIMARY KEY,
    RoleID BIGINT NOT NULL,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    Phone VARCHAR(15) UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_role
        FOREIGN KEY (RoleID) REFERENCES Role(RoleID)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_user_role ON User(RoleID);
CREATE INDEX idx_user_email ON User(Email);

-- 3. Department
CREATE TABLE Department (
    DepartmentID BIGINT AUTO_INCREMENT PRIMARY KEY,
    DepartmentCode VARCHAR(20) NOT NULL UNIQUE,
    DepartmentName VARCHAR(100) NOT NULL UNIQUE,
    Description VARCHAR(255),
    IsActive BOOLEAN DEFAULT TRUE,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 4. Student
CREATE TABLE Student (
    StudentID BIGINT AUTO_INCREMENT PRIMARY KEY,
    UserID BIGINT NOT NULL UNIQUE,
    DepartmentID BIGINT NOT NULL,
    RollNumber VARCHAR(30) NOT NULL UNIQUE,
    EnrollmentNumber VARCHAR(30) NOT NULL UNIQUE,
    Year SMALLINT NOT NULL,
    Semester SMALLINT NOT NULL,
    IsActive BOOLEAN DEFAULT TRUE,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_student_user
        FOREIGN KEY (UserID) REFERENCES User(UserID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_student_department
        FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_student_year CHECK (Year > 0),
    CONSTRAINT chk_student_semester CHECK (Semester > 0)
) ENGINE=InnoDB;

CREATE INDEX idx_student_department ON Student(DepartmentID);

-- 5. Faculty
CREATE TABLE Faculty (
    FacultyID BIGINT AUTO_INCREMENT PRIMARY KEY,
    UserID BIGINT NOT NULL UNIQUE,
    DepartmentID BIGINT NOT NULL,
    EmployeeID VARCHAR(30) NOT NULL UNIQUE,
    Designation VARCHAR(50),
    IsActive BOOLEAN DEFAULT TRUE,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_faculty_user
        FOREIGN KEY (UserID) REFERENCES User(UserID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_faculty_department
        FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_faculty_department ON Faculty(DepartmentID);

-- 6. Subject
CREATE TABLE Subject (
    SubjectID BIGINT AUTO_INCREMENT PRIMARY KEY,
    DepartmentID BIGINT NOT NULL,
    SubjectCode VARCHAR(20) NOT NULL UNIQUE,
    SubjectName VARCHAR(100) NOT NULL,
    Description TEXT,
    Credits SMALLINT DEFAULT 0,
    IsActive BOOLEAN DEFAULT TRUE,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    CreatedBy BIGINT NULL,
    CONSTRAINT fk_subject_department
        FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_subject_createdby
        FOREIGN KEY (CreatedBy) REFERENCES User(UserID)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_subject_credits CHECK (Credits >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_subject_department ON Subject(DepartmentID);

-- 7. Exam
CREATE TABLE Exam (
    ExamID BIGINT AUTO_INCREMENT PRIMARY KEY,
    SubjectID BIGINT NOT NULL,
    CreatedBy BIGINT NOT NULL,
    ExamCode VARCHAR(30) NOT NULL UNIQUE,
    ExamTitle VARCHAR(150) NOT NULL,
    ExamType VARCHAR(30) NOT NULL,
    TotalMarks DECIMAL(6,2) NOT NULL,
    PassingMarks DECIMAL(6,2) NOT NULL,
    DurationMinutes INT NOT NULL,
    Instructions TEXT,
    MaximumAttempts SMALLINT NOT NULL DEFAULT 1,
    ShuffleQuestions BOOLEAN DEFAULT TRUE,
    ShuffleOptions BOOLEAN DEFAULT TRUE,
    NegativeMarking BOOLEAN DEFAULT FALSE,
    NegativeMarksPerQuestion DECIMAL(5,2) DEFAULT 0,
    ExamStatus ENUM('DRAFT','SCHEDULED','ACTIVE','COMPLETED','CANCELLED') NOT NULL DEFAULT 'DRAFT',
    IsActive BOOLEAN DEFAULT TRUE,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_exam_subject
        FOREIGN KEY (SubjectID) REFERENCES Subject(SubjectID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_exam_createdby
        FOREIGN KEY (CreatedBy) REFERENCES User(UserID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_exam_total_marks CHECK (TotalMarks > 0),
    CONSTRAINT chk_exam_passing_marks CHECK (PassingMarks >= 0 AND PassingMarks <= TotalMarks),
    CONSTRAINT chk_exam_duration CHECK (DurationMinutes > 0),
    CONSTRAINT chk_exam_attempts CHECK (MaximumAttempts >= 1),
    CONSTRAINT chk_exam_negative_marks CHECK (NegativeMarksPerQuestion >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_exam_subject ON Exam(SubjectID);
CREATE INDEX idx_exam_createdby ON Exam(CreatedBy);
CREATE INDEX idx_exam_status ON Exam(ExamStatus);

-- 8. ExamSchedule
CREATE TABLE ExamSchedule (
    ScheduleID BIGINT AUTO_INCREMENT PRIMARY KEY,
    ExamID BIGINT NOT NULL,
    StartTime DATETIME NOT NULL,
    EndTime DATETIME NOT NULL,
    RegistrationStart DATETIME NULL,
    RegistrationEnd DATETIME NULL,
    LateEntryMinutes INT DEFAULT 0,
    ScheduleStatus ENUM('SCHEDULED','ONGOING','COMPLETED','CANCELLED') NOT NULL DEFAULT 'SCHEDULED',
    CONSTRAINT fk_schedule_exam
        FOREIGN KEY (ExamID) REFERENCES Exam(ExamID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_schedule_time CHECK (EndTime > StartTime),
    CONSTRAINT chk_registration_time CHECK (
        RegistrationStart IS NULL OR RegistrationEnd IS NULL OR RegistrationEnd >= RegistrationStart
    ),
    CONSTRAINT chk_late_entry CHECK (LateEntryMinutes >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_schedule_exam ON ExamSchedule(ExamID);
CREATE INDEX idx_schedule_start ON ExamSchedule(StartTime);

-- 9. Question
CREATE TABLE Question (
    QuestionID BIGINT AUTO_INCREMENT PRIMARY KEY,
    SubjectID BIGINT NOT NULL,
    CreatedBy BIGINT NOT NULL,
    QuestionType ENUM('MCQ','MSQ','TRUE_FALSE','SHORT_ANSWER','DESCRIPTIVE') NOT NULL,
    QuestionText TEXT NOT NULL,
    Explanation TEXT,
    DefaultMarks DECIMAL(5,2) NOT NULL,
    NegativeMarks DECIMAL(5,2) DEFAULT 0,
    DifficultyLevel ENUM('EASY','MEDIUM','HARD') NOT NULL,
    IsActive BOOLEAN DEFAULT TRUE,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_question_subject
        FOREIGN KEY (SubjectID) REFERENCES Subject(SubjectID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_question_createdby
        FOREIGN KEY (CreatedBy) REFERENCES User(UserID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_question_marks CHECK (DefaultMarks > 0),
    CONSTRAINT chk_question_negative_marks CHECK (NegativeMarks >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_question_subject ON Question(SubjectID);
CREATE INDEX idx_question_type ON Question(QuestionType);

-- 10. QuestionOption
CREATE TABLE QuestionOption (
    OptionID BIGINT AUTO_INCREMENT PRIMARY KEY,
    QuestionID BIGINT NOT NULL,
    OptionText TEXT NOT NULL,
    OptionOrder INT NOT NULL,
    IsCorrect BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_option_question
        FOREIGN KEY (QuestionID) REFERENCES Question(QuestionID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT uq_question_option_order UNIQUE (QuestionID, OptionOrder),
    CONSTRAINT chk_option_order CHECK (OptionOrder > 0)
) ENGINE=InnoDB;

CREATE INDEX idx_option_question ON QuestionOption(QuestionID);

-- 11. ExamQuestion
CREATE TABLE ExamQuestion (
    ExamQuestionID BIGINT AUTO_INCREMENT PRIMARY KEY,
    ExamID BIGINT NOT NULL,
    QuestionID BIGINT NOT NULL,
    QuestionOrder INT NOT NULL,
    Marks DECIMAL(5,2) NOT NULL,
    NegativeMarks DECIMAL(5,2) DEFAULT 0,
    IsMandatory BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_examquestion_exam
        FOREIGN KEY (ExamID) REFERENCES Exam(ExamID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_examquestion_question
        FOREIGN KEY (QuestionID) REFERENCES Question(QuestionID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_exam_question UNIQUE (ExamID, QuestionID),
    CONSTRAINT uq_exam_question_order UNIQUE (ExamID, QuestionOrder),
    CONSTRAINT chk_examquestion_order CHECK (QuestionOrder > 0),
    CONSTRAINT chk_examquestion_marks CHECK (Marks > 0),
    CONSTRAINT chk_examquestion_negative CHECK (NegativeMarks >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_examquestion_question ON ExamQuestion(QuestionID);

-- 12. CandidateRegistration
CREATE TABLE CandidateRegistration (
    RegistrationID BIGINT AUTO_INCREMENT PRIMARY KEY,
    ExamID BIGINT NOT NULL,
    StudentID BIGINT NOT NULL,
    RegistrationTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    RegistrationStatus ENUM('REGISTERED','CANCELLED','WAITLISTED') NOT NULL DEFAULT 'REGISTERED',
    EligibilityVerified BOOLEAN DEFAULT FALSE,
    Remarks VARCHAR(255),
    CONSTRAINT fk_registration_exam
        FOREIGN KEY (ExamID) REFERENCES Exam(ExamID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_registration_student
        FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT uq_exam_student UNIQUE (ExamID, StudentID)
) ENGINE=InnoDB;

CREATE INDEX idx_registration_student ON CandidateRegistration(StudentID);
CREATE INDEX idx_registration_exam ON CandidateRegistration(ExamID);

-- 13. ExamAttempt
CREATE TABLE ExamAttempt (
    AttemptID BIGINT AUTO_INCREMENT PRIMARY KEY,
    RegistrationID BIGINT NOT NULL,
    AttemptNumber SMALLINT NOT NULL,
    StartTime DATETIME NOT NULL,
    EndTime DATETIME NULL,
    SubmittedAt DATETIME NULL,
    Status ENUM(
        'NOT_STARTED',
        'IN_PROGRESS',
        'SUBMITTED',
        'AUTO_SUBMITTED',
        'EVALUATED',
        'ABANDONED'
    ) NOT NULL DEFAULT 'NOT_STARTED',
    TotalTimeSpentSeconds INT DEFAULT 0,
    IPAddress VARCHAR(45),
    SubmissionMethod ENUM('MANUAL','AUTO') NULL,
    AutoSubmitted BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_attempt_registration
        FOREIGN KEY (RegistrationID) REFERENCES CandidateRegistration(RegistrationID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT uq_registration_attempt UNIQUE (RegistrationID, AttemptNumber),
    CONSTRAINT chk_attempt_number CHECK (AttemptNumber >= 1),
    CONSTRAINT chk_attempt_time CHECK (TotalTimeSpentSeconds >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_attempt_registration ON ExamAttempt(RegistrationID);
CREATE INDEX idx_attempt_status ON ExamAttempt(Status);

-- 14. StudentAnswer
CREATE TABLE StudentAnswer (
    AnswerID BIGINT AUTO_INCREMENT PRIMARY KEY,
    AttemptID BIGINT NOT NULL,
    QuestionID BIGINT NOT NULL,
    SelectedOptionID BIGINT NULL,
    AnswerText TEXT NULL,
    IsMarkedForReview BOOLEAN DEFAULT FALSE,
    IsAnswered BOOLEAN DEFAULT FALSE,
    SubmittedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    TimeSpentSeconds INT DEFAULT 0,
    CONSTRAINT fk_answer_attempt
        FOREIGN KEY (AttemptID) REFERENCES ExamAttempt(AttemptID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_answer_question
        FOREIGN KEY (QuestionID) REFERENCES Question(QuestionID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_answer_option
        FOREIGN KEY (SelectedOptionID) REFERENCES QuestionOption(OptionID)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT uq_attempt_question UNIQUE (AttemptID, QuestionID),
    CONSTRAINT chk_answer_time CHECK (TimeSpentSeconds >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_answer_question ON StudentAnswer(QuestionID);
CREATE INDEX idx_answer_option ON StudentAnswer(SelectedOptionID);

-- 15. Result
CREATE TABLE Result (
    ResultID BIGINT AUTO_INCREMENT PRIMARY KEY,
    AttemptID BIGINT NOT NULL UNIQUE,
    TotalMarksObtained DECIMAL(6,2) NOT NULL DEFAULT 0,
    Percentage DECIMAL(5,2) NOT NULL DEFAULT 0,
    TotalCorrect INT NOT NULL DEFAULT 0,
    TotalWrong INT NOT NULL DEFAULT 0,
    TotalSkipped INT NOT NULL DEFAULT 0,
    Grade VARCHAR(5),
    PassStatus BOOLEAN NOT NULL,
    ResultStatus ENUM('GENERATED','PUBLISHED') NOT NULL DEFAULT 'GENERATED',
    PublishedAt DATETIME NULL,
    PublishedBy BIGINT NULL,
    Remarks TEXT,
    CONSTRAINT fk_result_attempt
        FOREIGN KEY (AttemptID) REFERENCES ExamAttempt(AttemptID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_result_publishedby
        FOREIGN KEY (PublishedBy) REFERENCES User(UserID)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_result_marks CHECK (TotalMarksObtained >= 0),
    CONSTRAINT chk_result_percentage CHECK (Percentage >= 0 AND Percentage <= 100),
    CONSTRAINT chk_result_correct CHECK (TotalCorrect >= 0),
    CONSTRAINT chk_result_wrong CHECK (TotalWrong >= 0),
    CONSTRAINT chk_result_skipped CHECK (TotalSkipped >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_result_publishedby ON Result(PublishedBy);
CREATE INDEX idx_result_status ON Result(ResultStatus);

-- 16. Notification
CREATE TABLE Notification (
    NotificationID BIGINT AUTO_INCREMENT PRIMARY KEY,
    UserID BIGINT NOT NULL,
    Title VARCHAR(150) NOT NULL,
    Message TEXT NOT NULL,
    NotificationType ENUM('EXAM','RESULT','SYSTEM','REMINDER') NOT NULL,
    IsRead BOOLEAN DEFAULT FALSE,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    ReadAt DATETIME NULL,
    IsActive BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_notification_user
        FOREIGN KEY (UserID) REFERENCES User(UserID)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_notification_user ON Notification(UserID);
CREATE INDEX idx_notification_read ON Notification(IsRead);

-- 17. AuditLog
CREATE TABLE AuditLog (
    AuditLogID BIGINT AUTO_INCREMENT PRIMARY KEY,
    UserID BIGINT NULL,
    ExamAttemptID BIGINT NULL,
    Module VARCHAR(50) NOT NULL,
    Action VARCHAR(50) NOT NULL,
    EntityName VARCHAR(50),
    RecordID BIGINT NULL,
    Status VARCHAR(20) NOT NULL,
    IPAddress VARCHAR(45),
    Details TEXT,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user
        FOREIGN KEY (UserID) REFERENCES User(UserID)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_audit_attempt
        FOREIGN KEY (ExamAttemptID) REFERENCES ExamAttempt(AttemptID)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX idx_audit_user ON AuditLog(UserID);
CREATE INDEX idx_audit_attempt ON AuditLog(ExamAttemptID);
CREATE INDEX idx_audit_module_action ON AuditLog(Module, Action);
CREATE INDEX idx_audit_created ON AuditLog(CreatedAt);

-- Initial RBAC roles
INSERT INTO Role (RoleID, RoleName, Description) VALUES
(1, 'ADMIN', 'System administrator'),
(2, 'FACULTY', 'Faculty/examiner'),
(3, 'STUDENT', 'Student/candidate');

-- Views

CREATE OR REPLACE VIEW vw_question_paper AS
SELECT
    e.ExamID,
    e.ExamCode,
    e.ExamTitle,
    eq.ExamQuestionID,
    eq.QuestionOrder,
    q.QuestionID,
    q.QuestionType,
    q.QuestionText,
    eq.Marks,
    eq.NegativeMarks,
    qo.OptionID,
    qo.OptionText,
    qo.OptionOrder
FROM Exam e
JOIN ExamQuestion eq ON e.ExamID = eq.ExamID
JOIN Question q ON eq.QuestionID = q.QuestionID
LEFT JOIN QuestionOption qo ON q.QuestionID = qo.QuestionID
WHERE e.IsActive = TRUE
  AND q.IsActive = TRUE;

CREATE OR REPLACE VIEW vw_student_results AS
SELECT
    s.StudentID,
    u.UserID,
    CONCAT(u.FirstName, ' ', u.LastName) AS StudentName,
    s.RollNumber,
    s.EnrollmentNumber,
    e.ExamID,
    e.ExamCode,
    e.ExamTitle,
    sub.SubjectID,
    sub.SubjectCode,
    sub.SubjectName,
    ea.AttemptID,
    ea.AttemptNumber,
    r.ResultID,
    r.TotalMarksObtained,
    r.Percentage,
    r.TotalCorrect,
    r.TotalWrong,
    r.TotalSkipped,
    r.Grade,
    r.PassStatus,
    r.ResultStatus,
    r.PublishedAt
FROM Student s
JOIN User u ON s.UserID = u.UserID
JOIN CandidateRegistration cr ON s.StudentID = cr.StudentID
JOIN Exam e ON cr.ExamID = e.ExamID
JOIN Subject sub ON e.SubjectID = sub.SubjectID
JOIN ExamAttempt ea ON cr.RegistrationID = ea.RegistrationID
JOIN Result r ON ea.AttemptID = r.AttemptID;

CREATE OR REPLACE VIEW vw_exam_statistics AS
SELECT
    e.ExamID,
    e.ExamCode,
    e.ExamTitle,
    COUNT(DISTINCT cr.RegistrationID) AS TotalCandidates,
    COUNT(DISTINCT ea.AttemptID) AS TotalAttempts,
    COALESCE(AVG(r.TotalMarksObtained), 0) AS AverageMarks,
    COALESCE(MAX(r.TotalMarksObtained), 0) AS HighestMarks,
    COALESCE(MIN(r.TotalMarksObtained), 0) AS LowestMarks,
    SUM(CASE WHEN r.PassStatus = TRUE THEN 1 ELSE 0 END) AS PassCount,
    SUM(CASE WHEN r.PassStatus = FALSE THEN 1 ELSE 0 END) AS FailCount,
    CASE
        WHEN COUNT(r.ResultID) = 0 THEN 0
        ELSE ROUND(
            SUM(CASE WHEN r.PassStatus = TRUE THEN 1 ELSE 0 END) * 100.0
            / COUNT(r.ResultID), 2
        )
    END AS PassPercentage
FROM Exam e
LEFT JOIN CandidateRegistration cr ON e.ExamID = cr.ExamID
LEFT JOIN ExamAttempt ea ON cr.RegistrationID = ea.RegistrationID
LEFT JOIN Result r ON ea.AttemptID = r.AttemptID
GROUP BY e.ExamID, e.ExamCode, e.ExamTitle;

CREATE OR REPLACE VIEW vw_student_performance AS
SELECT
    s.StudentID,
    CONCAT(u.FirstName, ' ', u.LastName) AS StudentName,
    COUNT(DISTINCT ea.AttemptID) AS ExamsAttempted,
    COALESCE(AVG(r.TotalMarksObtained), 0) AS AverageMarks,
    COALESCE(MAX(r.TotalMarksObtained), 0) AS HighestMarks,
    SUM(CASE WHEN r.PassStatus = TRUE THEN 1 ELSE 0 END) AS PassCount,
    SUM(CASE WHEN r.PassStatus = FALSE THEN 1 ELSE 0 END) AS FailCount
FROM Student s
JOIN User u ON s.UserID = u.UserID
LEFT JOIN CandidateRegistration cr ON s.StudentID = cr.StudentID
LEFT JOIN ExamAttempt ea ON cr.RegistrationID = ea.RegistrationID
LEFT JOIN Result r ON ea.AttemptID = r.AttemptID
GROUP BY s.StudentID, u.FirstName, u.LastName;

CREATE OR REPLACE VIEW vw_browser_integrity AS
SELECT
    AuditLogID,
    UserID,
    ExamAttemptID,
    Action,
    Status,
    IPAddress,
    Details,
    CreatedAt
FROM AuditLog
WHERE Module = 'EXAM_MONITORING';


